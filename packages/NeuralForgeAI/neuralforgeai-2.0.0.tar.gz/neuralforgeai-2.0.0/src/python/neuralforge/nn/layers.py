import torch
import torch.nn as nn
import torch.nn.functional as F
from typing import Optional

class ConvBlock(nn.Module):
    def __init__(self, in_channels, out_channels, kernel_size=3, stride=1, padding=1, 
                 use_bn=True, activation='relu', drop_rate=0.0):
        super().__init__()
        self.conv = nn.Conv2d(in_channels, out_channels, kernel_size, stride, padding, bias=not use_bn)
        self.bn = nn.BatchNorm2d(out_channels) if use_bn else nn.Identity()
        
        if activation == 'relu':
            self.activation = nn.ReLU(inplace=True)
        elif activation == 'gelu':
            self.activation = nn.GELU()
        elif activation == 'silu':
            self.activation = nn.SiLU(inplace=True)
        elif activation == 'mish':
            self.activation = nn.Mish(inplace=True)
        else:
            self.activation = nn.Identity()
        
        self.dropout = nn.Dropout2d(drop_rate) if drop_rate > 0 else nn.Identity()
    
    def forward(self, x):
        x = self.conv(x)
        x = self.bn(x)
        x = self.activation(x)
        x = self.dropout(x)
        return x

class ResidualBlock(nn.Module):
    def __init__(self, channels, kernel_size=3, drop_rate=0.0):
        super().__init__()
        self.conv1 = ConvBlock(channels, channels, kernel_size, padding=kernel_size // 2, drop_rate=drop_rate)
        self.conv2 = ConvBlock(channels, channels, kernel_size, padding=kernel_size // 2, activation='none')
        self.activation = nn.ReLU(inplace=True)
    
    def forward(self, x):
        residual = x
        x = self.conv1(x)
        x = self.conv2(x)
        x = x + residual
        x = self.activation(x)
        return x

class BottleneckBlock(nn.Module):
    def __init__(self, in_channels, out_channels, stride=1, expansion=4):
        super().__init__()
        mid_channels = out_channels // expansion
        
        self.conv1 = ConvBlock(in_channels, mid_channels, kernel_size=1, padding=0)
        self.conv2 = ConvBlock(mid_channels, mid_channels, kernel_size=3, stride=stride, padding=1)
        self.conv3 = ConvBlock(mid_channels, out_channels, kernel_size=1, padding=0, activation='none')
        
        self.shortcut = nn.Sequential()
        if stride != 1 or in_channels != out_channels:
            self.shortcut = nn.Sequential(
                nn.Conv2d(in_channels, out_channels, kernel_size=1, stride=stride, bias=False),
                nn.BatchNorm2d(out_channels)
            )
        
        self.activation = nn.ReLU(inplace=True)
    
    def forward(self, x):
        residual = self.shortcut(x)
        x = self.conv1(x)
        x = self.conv2(x)
        x = self.conv3(x)
        x = x + residual
        x = self.activation(x)
        return x

class InvertedResidualBlock(nn.Module):
    def __init__(self, in_channels, out_channels, stride=1, expand_ratio=6):
        super().__init__()
        hidden_dim = in_channels * expand_ratio
        self.use_residual = stride == 1 and in_channels == out_channels
        
        layers = []
        if expand_ratio != 1:
            layers.append(ConvBlock(in_channels, hidden_dim, kernel_size=1, padding=0))
        
        layers.extend([
            ConvBlock(hidden_dim, hidden_dim, kernel_size=3, stride=stride, padding=1, activation='relu'),
            nn.Conv2d(hidden_dim, out_channels, kernel_size=1, bias=False),
            nn.BatchNorm2d(out_channels)
        ])
        
        self.conv = nn.Sequential(*layers)
    
    def forward(self, x):
        if self.use_residual:
            return x + self.conv(x)
        return self.conv(x)

class DenseLayer(nn.Module):
    def __init__(self, in_channels, growth_rate, drop_rate=0.0):
        super().__init__()
        self.bn1 = nn.BatchNorm2d(in_channels)
        self.relu1 = nn.ReLU(inplace=True)
        self.conv1 = nn.Conv2d(in_channels, growth_rate * 4, kernel_size=1, bias=False)
        
        self.bn2 = nn.BatchNorm2d(growth_rate * 4)
        self.relu2 = nn.ReLU(inplace=True)
        self.conv2 = nn.Conv2d(growth_rate * 4, growth_rate, kernel_size=3, padding=1, bias=False)
        
        self.dropout = nn.Dropout2d(drop_rate) if drop_rate > 0 else nn.Identity()
    
    def forward(self, x):
        out = self.conv1(self.relu1(self.bn1(x)))
        out = self.conv2(self.relu2(self.bn2(out)))
        out = self.dropout(out)
        return torch.cat([x, out], 1)

class DenseBlock(nn.Module):
    def __init__(self, num_layers, in_channels, growth_rate, drop_rate=0.0):
        super().__init__()
        layers = []
        for i in range(num_layers):
            layers.append(DenseLayer(in_channels + i * growth_rate, growth_rate, drop_rate))
        self.layers = nn.Sequential(*layers)
    
    def forward(self, x):
        return self.layers(x)

class TransitionLayer(nn.Module):
    def __init__(self, in_channels, out_channels):
        super().__init__()
        self.bn = nn.BatchNorm2d(in_channels)
        self.relu = nn.ReLU(inplace=True)
        self.conv = nn.Conv2d(in_channels, out_channels, kernel_size=1, bias=False)
        self.pool = nn.AvgPool2d(kernel_size=2, stride=2)
    
    def forward(self, x):
        x = self.conv(self.relu(self.bn(x)))
        x = self.pool(x)
        return x

class SEBlock(nn.Module):
    def __init__(self, channels, reduction=16):
        super().__init__()
        self.squeeze = nn.AdaptiveAvgPool2d(1)
        self.excitation = nn.Sequential(
            nn.Linear(channels, channels // reduction, bias=False),
            nn.ReLU(inplace=True),
            nn.Linear(channels // reduction, channels, bias=False),
            nn.Sigmoid()
        )
    
    def forward(self, x):
        b, c, _, _ = x.size()
        se = self.squeeze(x).view(b, c)
        se = self.excitation(se).view(b, c, 1, 1)
        return x * se.expand_as(x)

class DepthwiseSeparableConv(nn.Module):
    def __init__(self, in_channels, out_channels, kernel_size=3, stride=1, padding=1):
        super().__init__()
        self.depthwise = nn.Conv2d(in_channels, in_channels, kernel_size, stride, padding, groups=in_channels, bias=False)
        self.pointwise = nn.Conv2d(in_channels, out_channels, kernel_size=1, bias=False)
        self.bn1 = nn.BatchNorm2d(in_channels)
        self.bn2 = nn.BatchNorm2d(out_channels)
        self.relu = nn.ReLU(inplace=True)
    
    def forward(self, x):
        x = self.depthwise(x)
        x = self.bn1(x)
        x = self.relu(x)
        x = self.pointwise(x)
        x = self.bn2(x)
        x = self.relu(x)
        return x

class GhostModule(nn.Module):
    """Ghost Module for efficient feature generation"""
    def __init__(self, in_channels, out_channels, kernel_size=1, ratio=2, dw_size=3, stride=1, activation='relu'):
        super().__init__()
        self.out_channels = out_channels
        init_channels = math.ceil(out_channels / ratio)
        new_channels = init_channels * (ratio - 1)
        
        self.primary_conv = nn.Sequential(
            nn.Conv2d(in_channels, init_channels, kernel_size, stride, kernel_size // 2, bias=False),
            nn.BatchNorm2d(init_channels),
            nn.ReLU(inplace=True) if activation == 'relu' else nn.Identity()
        )
        
        self.cheap_operation = nn.Sequential(
            nn.Conv2d(init_channels, new_channels, dw_size, 1, dw_size // 2, groups=init_channels, bias=False),
            nn.BatchNorm2d(new_channels),
            nn.ReLU(inplace=True) if activation == 'relu' else nn.Identity()
        )
    
    def forward(self, x):
        x1 = self.primary_conv(x)
        x2 = self.cheap_operation(x1)
        return torch.cat([x1, x2], dim=1)

class GhostBottleneck(nn.Module):
    """Ghost Bottleneck for MobileNet-style architectures"""
    def __init__(self, in_channels, hidden_channels, out_channels, kernel_size, stride, use_se=False):
        super().__init__()
        self.stride = stride
        
        self.ghost1 = GhostModule(in_channels, hidden_channels, kernel_size=1)
        
        if stride == 2:
            self.conv_dw = nn.Conv2d(hidden_channels, hidden_channels, kernel_size, stride, 
                                    kernel_size // 2, groups=hidden_channels, bias=False)
            self.bn_dw = nn.BatchNorm2d(hidden_channels)
        
        self.se = SEBlock(hidden_channels) if use_se else nn.Identity()
        
        self.ghost2 = GhostModule(hidden_channels, out_channels, kernel_size=1, activation='none')
        
        if in_channels == out_channels and stride == 1:
            self.shortcut = nn.Identity()
        else:
            self.shortcut = nn.Sequential(
                nn.Conv2d(in_channels, in_channels, kernel_size, stride, kernel_size // 2, 
                         groups=in_channels, bias=False),
                nn.BatchNorm2d(in_channels),
                nn.Conv2d(in_channels, out_channels, 1, 1, 0, bias=False),
                nn.BatchNorm2d(out_channels)
            )
    
    def forward(self, x):
        residual = x
        
        x = self.ghost1(x)
        
        if self.stride == 2:
            x = self.conv_dw(x)
            x = self.bn_dw(x)
        
        x = self.se(x)
        x = self.ghost2(x)
        
        x += self.shortcut(residual)
        return x

class FusedMBConv(nn.Module):
    """Fused MBConv block from EfficientNetV2"""
    def __init__(self, in_channels, out_channels, expand_ratio=4, kernel_size=3, stride=1, se_ratio=0.25):
        super().__init__()
        self.stride = stride
        self.use_residual = stride == 1 and in_channels == out_channels
        hidden_dim = in_channels * expand_ratio
        
        layers = []
        
        # Fused expansion and depthwise
        layers.append(nn.Conv2d(in_channels, hidden_dim, kernel_size, stride, kernel_size // 2, bias=False))
        layers.append(nn.BatchNorm2d(hidden_dim))
        layers.append(nn.SiLU(inplace=True))
        
        # Squeeze and excitation
        if se_ratio > 0:
            layers.append(SEBlock(hidden_dim, int(in_channels * se_ratio)))
        
        # Project
        layers.append(nn.Conv2d(hidden_dim, out_channels, 1, 1, 0, bias=False))
        layers.append(nn.BatchNorm2d(out_channels))
        
        self.conv = nn.Sequential(*layers)
        self.drop_path = nn.Identity()  # Could add stochastic depth here
    
    def forward(self, x):
        if self.use_residual:
            return x + self.drop_path(self.conv(x))
        return self.conv(x)

class CoordAttention(nn.Module):
    """Coordinate Attention for efficient mobile networks"""
    def __init__(self, in_channels, out_channels, reduction=32):
        super().__init__()
        self.pool_h = nn.AdaptiveAvgPool2d((None, 1))
        self.pool_w = nn.AdaptiveAvgPool2d((1, None))
        
        hidden_dim = max(8, in_channels // reduction)
        
        self.conv1 = nn.Conv2d(in_channels, hidden_dim, 1, 1, 0, bias=False)
        self.bn1 = nn.BatchNorm2d(hidden_dim)
        self.act = nn.SiLU(inplace=True)
        
        self.conv_h = nn.Conv2d(hidden_dim, out_channels, 1, 1, 0, bias=False)
        self.conv_w = nn.Conv2d(hidden_dim, out_channels, 1, 1, 0, bias=False)
    
    def forward(self, x):
        identity = x
        n, c, h, w = x.size()
        
        x_h = self.pool_h(x)
        x_w = self.pool_w(x).permute(0, 1, 3, 2)
        
        y = torch.cat([x_h, x_w], dim=2)
        y = self.conv1(y)
        y = self.bn1(y)
        y = self.act(y)
        
        x_h, x_w = torch.split(y, [h, w], dim=2)
        x_w = x_w.permute(0, 1, 3, 2)
        
        a_h = self.conv_h(x_h).sigmoid()
        a_w = self.conv_w(x_w).sigmoid()
        
        return identity * a_h * a_w

class SqueezeExcitation(nn.Module):
    """Enhanced Squeeze-and-Excitation block"""
    def __init__(self, in_channels, se_ratio=0.25, activation='relu'):
        super().__init__()
        squeezed_channels = max(1, int(in_channels * se_ratio))
        
        self.se = nn.Sequential(
            nn.AdaptiveAvgPool2d(1),
            nn.Conv2d(in_channels, squeezed_channels, 1),
            nn.SiLU() if activation == 'silu' else nn.ReLU(inplace=True),
            nn.Conv2d(squeezed_channels, in_channels, 1),
            nn.Sigmoid()
        )
    
    def forward(self, x):
        return x * self.se(x)

class ChannelShuffle(nn.Module):
    """Channel Shuffle operation for ShuffleNet"""
    def __init__(self, groups):
        super().__init__()
        self.groups = groups
    
    def forward(self, x):
        batch_size, num_channels, height, width = x.size()
        channels_per_group = num_channels // self.groups
        
        x = x.view(batch_size, self.groups, channels_per_group, height, width)
        x = x.transpose(1, 2).contiguous()
        x = x.view(batch_size, -1, height, width)
        
        return x

class ShuffleNetBlock(nn.Module):
    """ShuffleNet V2 basic block"""
    def __init__(self, in_channels, out_channels, stride=1):
        super().__init__()
        self.stride = stride
        branch_features = out_channels // 2
        
        if stride == 1:
            assert in_channels == out_channels
        
        if stride > 1:
            self.branch1 = nn.Sequential(
                nn.Conv2d(in_channels, in_channels, 3, stride, 1, groups=in_channels, bias=False),
                nn.BatchNorm2d(in_channels),
                nn.Conv2d(in_channels, branch_features, 1, 1, 0, bias=False),
                nn.BatchNorm2d(branch_features),
                nn.ReLU(inplace=True)
            )
        
        self.branch2 = nn.Sequential(
            nn.Conv2d(in_channels if stride > 1 else branch_features, branch_features, 1, 1, 0, bias=False),
            nn.BatchNorm2d(branch_features),
            nn.ReLU(inplace=True),
            nn.Conv2d(branch_features, branch_features, 3, stride, 1, groups=branch_features, bias=False),
            nn.BatchNorm2d(branch_features),
            nn.Conv2d(branch_features, branch_features, 1, 1, 0, bias=False),
            nn.BatchNorm2d(branch_features),
            nn.ReLU(inplace=True)
        )
        
        self.channel_shuffle = ChannelShuffle(2)
    
    def forward(self, x):
        if self.stride == 1:
            x1, x2 = x.chunk(2, dim=1)
            out = torch.cat([x1, self.branch2(x2)], dim=1)
        else:
            out = torch.cat([self.branch1(x), self.branch2(x)], dim=1)
        
        return self.channel_shuffle(out)

class MBConvBlock(nn.Module):
    """Mobile Inverted Bottleneck Convolution (MBConv) from EfficientNet"""
    def __init__(self, in_channels, out_channels, expand_ratio, kernel_size, stride, se_ratio=0.25, drop_rate=0.0):
        super().__init__()
        self.use_residual = stride == 1 and in_channels == out_channels
        hidden_dim = in_channels * expand_ratio
        
        layers = []
        
        if expand_ratio != 1:
            layers.extend([
                nn.Conv2d(in_channels, hidden_dim, 1, bias=False),
                nn.BatchNorm2d(hidden_dim),
                nn.SiLU(inplace=True)
            ])
        
        layers.extend([
            nn.Conv2d(hidden_dim, hidden_dim, kernel_size, stride, kernel_size // 2, 
                     groups=hidden_dim, bias=False),
            nn.BatchNorm2d(hidden_dim),
            nn.SiLU(inplace=True)
        ])
        
        if se_ratio > 0:
            layers.append(SqueezeExcitation(hidden_dim, se_ratio, activation='silu'))
        
        layers.extend([
            nn.Conv2d(hidden_dim, out_channels, 1, bias=False),
            nn.BatchNorm2d(out_channels)
        ])
        
        self.conv = nn.Sequential(*layers)
        self.drop_path = nn.Dropout2d(drop_rate) if drop_rate > 0 and self.use_residual else nn.Identity()
    
    def forward(self, x):
        if self.use_residual:
            return x + self.drop_path(self.conv(x))
        return self.conv(x)

import math
