import torch
from torch.utils.data import Dataset
from torchvision import datasets, transforms
import os
from typing import Optional, Callable

class CIFAR10Dataset:
    def __init__(self, root='./data', train=True, transform=None, download=True):
        if transform is None:
            if train:
                transform = transforms.Compose([
                    transforms.RandomCrop(32, padding=4),
                    transforms.RandomHorizontalFlip(),
                    transforms.ToTensor(),
                    transforms.Normalize((0.4914, 0.4822, 0.4465), (0.2023, 0.1994, 0.2010))
                ])
            else:
                transform = transforms.Compose([
                    transforms.ToTensor(),
                    transforms.Normalize((0.4914, 0.4822, 0.4465), (0.2023, 0.1994, 0.2010))
                ])
        
        self.dataset = datasets.CIFAR10(root=root, train=train, transform=transform, download=download)
        self.classes = ['airplane', 'automobile', 'bird', 'cat', 'deer', 'dog', 'frog', 'horse', 'ship', 'truck']
    
    def __len__(self):
        return len(self.dataset)
    
    def __getitem__(self, idx):
        return self.dataset[idx]

class CIFAR100Dataset:
    def __init__(self, root='./data', train=True, transform=None, download=True):
        if transform is None:
            if train:
                transform = transforms.Compose([
                    transforms.RandomCrop(32, padding=4),
                    transforms.RandomHorizontalFlip(),
                    transforms.RandomRotation(15),
                    transforms.ToTensor(),
                    transforms.Normalize((0.5071, 0.4867, 0.4408), (0.2675, 0.2565, 0.2761))
                ])
            else:
                transform = transforms.Compose([
                    transforms.ToTensor(),
                    transforms.Normalize((0.5071, 0.4867, 0.4408), (0.2675, 0.2565, 0.2761))
                ])
        
        self.dataset = datasets.CIFAR100(root=root, train=train, transform=transform, download=download)
    
    def __len__(self):
        return len(self.dataset)
    
    def __getitem__(self, idx):
        return self.dataset[idx]

class MNISTDataset:
    def __init__(self, root='./data', train=True, transform=None, download=True):
        if transform is None:
            transform = transforms.Compose([
                transforms.ToTensor(),
                transforms.Normalize((0.1307,), (0.3081,))
            ])
        
        self.dataset = datasets.MNIST(root=root, train=train, transform=transform, download=download)
        self.classes = [str(i) for i in range(10)]
    
    def __len__(self):
        return len(self.dataset)
    
    def __getitem__(self, idx):
        return self.dataset[idx]

class FashionMNISTDataset:
    def __init__(self, root='./data', train=True, transform=None, download=True):
        if transform is None:
            transform = transforms.Compose([
                transforms.ToTensor(),
                transforms.Normalize((0.2860,), (0.3530,))
            ])
        
        self.dataset = datasets.FashionMNIST(root=root, train=train, transform=transform, download=download)
        self.classes = ['T-shirt/top', 'Trouser', 'Pullover', 'Dress', 'Coat', 
                       'Sandal', 'Shirt', 'Sneaker', 'Bag', 'Ankle boot']
    
    def __len__(self):
        return len(self.dataset)
    
    def __getitem__(self, idx):
        return self.dataset[idx]

class STL10Dataset:
    def __init__(self, root='./data', split='train', transform=None, download=True):
        if transform is None:
            if split == 'train':
                transform = transforms.Compose([
                    transforms.RandomCrop(96, padding=12),
                    transforms.RandomHorizontalFlip(),
                    transforms.ToTensor(),
                    transforms.Normalize((0.4467, 0.4398, 0.4066), (0.2603, 0.2566, 0.2713))
                ])
            else:
                transform = transforms.Compose([
                    transforms.ToTensor(),
                    transforms.Normalize((0.4467, 0.4398, 0.4066), (0.2603, 0.2566, 0.2713))
                ])
        
        self.dataset = datasets.STL10(root=root, split=split, transform=transform, download=download)
        self.classes = ['airplane', 'bird', 'car', 'cat', 'deer', 'dog', 'horse', 'monkey', 'ship', 'truck']
    
    def __len__(self):
        return len(self.dataset)
    
    def __getitem__(self, idx):
        return self.dataset[idx]

def get_dataset(name='cifar10', root='./data', train=True, download=True):
    name = name.lower()
    
    if name == 'cifar10':
        return CIFAR10Dataset(root=root, train=train, download=download)
    elif name == 'cifar100':
        return CIFAR100Dataset(root=root, train=train, download=download)
    elif name == 'mnist':
        return MNISTDataset(root=root, train=train, download=download)
    elif name == 'fashion_mnist' or name == 'fashionmnist':
        return FashionMNISTDataset(root=root, train=train, download=download)
    elif name == 'stl10':
        split = 'train' if train else 'test'
        return STL10Dataset(root=root, split=split, download=download)
    else:
        raise ValueError(f"Unknown dataset: {name}")

class ImageNetDataset:
    def __init__(self, root='./data/imagenet', split='train', transform=None, download=False):
        if transform is None:
            if split == 'train':
                transform = transforms.Compose([
                    transforms.RandomResizedCrop(224),
                    transforms.RandomHorizontalFlip(),
                    transforms.ColorJitter(0.4, 0.4, 0.4),
                    transforms.ToTensor(),
                    transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225])
                ])
            else:
                transform = transforms.Compose([
                    transforms.Resize(256),
                    transforms.CenterCrop(224),
                    transforms.ToTensor(),
                    transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225])
                ])
        
        try:
            self.dataset = datasets.ImageFolder(os.path.join(root, split), transform=transform)
        except:
            print(f"ImageNet not found at {root}. Please download manually from https://image-net.org/")
            print("Expected structure: {root}/train/ and {root}/val/")
            raise
    
    def __len__(self):
        return len(self.dataset)
    
    def __getitem__(self, idx):
        return self.dataset[idx]

class TinyImageNetDataset:
    def __init__(self, root='./data', train=True, transform=None, download=True):
        if transform is None:
            if train:
                transform = transforms.Compose([
                    transforms.RandomCrop(64, padding=8),
                    transforms.RandomHorizontalFlip(),
                    transforms.ToTensor(),
                    transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225])
                ])
            else:
                transform = transforms.Compose([
                    transforms.ToTensor(),
                    transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225])
                ])
        
        import zipfile
        import urllib.request
        
        data_dir = os.path.join(root, 'tiny-imagenet-200')
        if download and not os.path.exists(data_dir):
            print("Downloading Tiny ImageNet (237 MB)...")
            url = 'http://cs231n.stanford.edu/tiny-imagenet-200.zip'
            zip_path = os.path.join(root, 'tiny-imagenet-200.zip')
            
            try:
                urllib.request.urlretrieve(url, zip_path)
                print("Extracting...")
                with zipfile.ZipFile(zip_path, 'r') as zip_ref:
                    zip_ref.extractall(root)
                os.remove(zip_path)
            except Exception as e:
                print(f"Download failed: {e}")
                print("Please download manually from: http://cs231n.stanford.edu/tiny-imagenet-200.zip")
        
        split = 'train' if train else 'val'
        self.dataset = datasets.ImageFolder(os.path.join(data_dir, split), transform=transform)
    
    def __len__(self):
        return len(self.dataset)
    
    def __getitem__(self, idx):
        return self.dataset[idx]

class Food101Dataset:
    def __init__(self, root='./data', split='train', transform=None, download=True):
        if transform is None:
            if split == 'train':
                transform = transforms.Compose([
                    transforms.RandomResizedCrop(224),
                    transforms.RandomHorizontalFlip(),
                    transforms.RandomRotation(15),
                    transforms.ColorJitter(0.3, 0.3, 0.3),
                    transforms.ToTensor(),
                    transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225])
                ])
            else:
                transform = transforms.Compose([
                    transforms.Resize(256),
                    transforms.CenterCrop(224),
                    transforms.ToTensor(),
                    transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225])
                ])
        
        self.dataset = datasets.Food101(root=root, split=split, transform=transform, download=download)
    
    def __len__(self):
        return len(self.dataset)
    
    def __getitem__(self, idx):
        return self.dataset[idx]

class Caltech256Dataset:
    def __init__(self, root='./data', transform=None, download=True):
        if transform is None:
            transform = transforms.Compose([
                transforms.Resize(256),
                transforms.CenterCrop(224),
                transforms.ToTensor(),
                transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225])
            ])
        
        self.dataset = datasets.Caltech256(root=root, transform=transform, download=download)
    
    def __len__(self):
        return len(self.dataset)
    
    def __getitem__(self, idx):
        return self.dataset[idx]

class OxfordPetsDataset:
    def __init__(self, root='./data', split='trainval', transform=None, download=True):
        if transform is None:
            transform = transforms.Compose([
                transforms.Resize(256),
                transforms.CenterCrop(224),
                transforms.ToTensor(),
                transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225])
            ])
        
        self.dataset = datasets.OxfordIIITPet(root=root, split=split, transform=transform, download=download)
    
    def __len__(self):
        return len(self.dataset)
    
    def __getitem__(self, idx):
        return self.dataset[idx]

def get_dataset(name='cifar10', root='./data', train=True, download=True):
    name = name.lower()
    
    if name == 'cifar10':
        return CIFAR10Dataset(root=root, train=train, download=download)
    elif name == 'cifar100':
        return CIFAR100Dataset(root=root, train=train, download=download)
    elif name == 'mnist':
        return MNISTDataset(root=root, train=train, download=download)
    elif name == 'fashion_mnist' or name == 'fashionmnist':
        return FashionMNISTDataset(root=root, train=train, download=download)
    elif name == 'stl10':
        split = 'train' if train else 'test'
        return STL10Dataset(root=root, split=split, download=download)
    elif name == 'tiny_imagenet' or name == 'tinyimagenet':
        return TinyImageNetDataset(root=root, train=train, download=download)
    elif name == 'imagenet':
        split = 'train' if train else 'val'
        return ImageNetDataset(root=root, split=split, download=download)
    elif name == 'food101':
        split = 'train' if train else 'test'
        return Food101Dataset(root=root, split=split, download=download)
    elif name == 'caltech256':
        return Caltech256Dataset(root=root, download=download)
    elif name == 'oxford_pets' or name == 'oxfordpets':
        split = 'trainval' if train else 'test'
        return OxfordPetsDataset(root=root, split=split, download=download)
    elif name == 'svhn':
        split = 'train' if train else 'test'
        return SVHNDataset(root=root, split=split, download=download)
    elif name == 'kmnist':
        return KMNISTDataset(root=root, train=train, download=download)
    elif name == 'emnist':
        return EMNISTDataset(root=root, train=train, download=download)
    elif name == 'flowers102':
        split = 'train' if train else 'test'
        return Flowers102Dataset(root=root, split=split, download=download)
    elif name == 'places365':
        split = 'train-standard' if train else 'val'
        return Places365Dataset(root=root, split=split, download=download)
    else:
        raise ValueError(f"Unknown dataset: {name}")

def get_num_classes(dataset_name):
    dataset_name = dataset_name.lower()
    if dataset_name in ['cifar10', 'mnist', 'fashion_mnist', 'fashionmnist', 'stl10', 'svhn', 'kmnist']:
        return 10
    elif dataset_name == 'cifar100':
        return 100
    elif dataset_name in ['tiny_imagenet', 'tinyimagenet']:
        return 200
    elif dataset_name == 'imagenet':
        return 1000
    elif dataset_name == 'food101':
        return 101
    elif dataset_name == 'caltech256':
        return 257
    elif dataset_name in ['oxford_pets', 'oxfordpets']:
        return 37
    elif dataset_name == 'emnist':
        return 47  # balanced split
    elif dataset_name == 'flowers102':
        return 102
    elif dataset_name == 'places365':
        return 365
    else:
        return 10


class SVHNDataset:
    def __init__(self, root='./data', split='train', transform=None, download=True):
        if transform is None:
            if split == 'train':
                transform = transforms.Compose([
                    transforms.RandomCrop(32, padding=4),
                    transforms.ToTensor(),
                    transforms.Normalize((0.4377, 0.4438, 0.4728), (0.1980, 0.2010, 0.1970))
                ])
            else:
                transform = transforms.Compose([
                    transforms.ToTensor(),
                    transforms.Normalize((0.4377, 0.4438, 0.4728), (0.1980, 0.2010, 0.1970))
                ])
        
        self.dataset = datasets.SVHN(root=root, split=split, transform=transform, download=download)
        self.classes = [str(i) for i in range(10)]
    
    def __len__(self):
        return len(self.dataset)
    
    def __getitem__(self, idx):
        return self.dataset[idx]

class KMNISTDataset:
    def __init__(self, root='./data', train=True, transform=None, download=True):
        if transform is None:
            transform = transforms.Compose([
                transforms.ToTensor(),
                transforms.Normalize((0.1918,), (0.3483,))
            ])
        
        self.dataset = datasets.KMNIST(root=root, train=train, transform=transform, download=download)
        self.classes = ['o', 'ki', 'su', 'tsu', 'na', 'ha', 'ma', 'ya', 're', 'wo']
    
    def __len__(self):
        return len(self.dataset)
    
    def __getitem__(self, idx):
        return self.dataset[idx]

class EMNISTDataset:
    def __init__(self, root='./data', split='balanced', train=True, transform=None, download=True):
        if transform is None:
            transform = transforms.Compose([
                transforms.ToTensor(),
                transforms.Normalize((0.1751,), (0.3332,))
            ])
        
        self.dataset = datasets.EMNIST(root=root, split=split, train=train, transform=transform, download=download)
    
    def __len__(self):
        return len(self.dataset)
    
    def __getitem__(self, idx):
        return self.dataset[idx]

class Flowers102Dataset:
    def __init__(self, root='./data', split='train', transform=None, download=True):
        if transform is None:
            if split == 'train':
                transform = transforms.Compose([
                    transforms.RandomResizedCrop(224),
                    transforms.RandomHorizontalFlip(),
                    transforms.RandomRotation(30),
                    transforms.ColorJitter(0.4, 0.4, 0.4),
                    transforms.ToTensor(),
                    transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225])
                ])
            else:
                transform = transforms.Compose([
                    transforms.Resize(256),
                    transforms.CenterCrop(224),
                    transforms.ToTensor(),
                    transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225])
                ])
        
        self.dataset = datasets.Flowers102(root=root, split=split, transform=transform, download=download)
    
    def __len__(self):
        return len(self.dataset)
    
    def __getitem__(self, idx):
        return self.dataset[idx]

class Places365Dataset:
    def __init__(self, root='./data/places365', split='train-standard', small=True, transform=None, download=False):
        if transform is None:
            if 'train' in split:
                transform = transforms.Compose([
                    transforms.RandomResizedCrop(224),
                    transforms.RandomHorizontalFlip(),
                    transforms.ToTensor(),
                    transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225])
                ])
            else:
                transform = transforms.Compose([
                    transforms.Resize(256),
                    transforms.CenterCrop(224),
                    transforms.ToTensor(),
                    transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225])
                ])
        
        try:
            self.dataset = datasets.Places365(root=root, split=split, small=small, transform=transform, download=download)
        except:
            print(f"Places365 not found at {root}. Please download manually from http://places2.csail.mit.edu/download.html")
            print("This is a large dataset (~25GB for small version, ~100GB for standard)")
            raise
    
    def __len__(self):
        return len(self.dataset)
    
    def __getitem__(self, idx):
        return self.dataset[idx]

class CombinedDataset(torch.utils.data.Dataset):
    """Combines multiple datasets into one. Useful for multi-domain training."""
    def __init__(self, datasets, sampling_weights=None):
        """
        Args:
            datasets: List of dataset objects
            sampling_weights: Optional list of weights for sampling from each dataset
        """
        self.datasets = datasets
        self.lengths = [len(d) for d in datasets]
        self.total_length = sum(self.lengths)
        self.cumulative_lengths = [0]
        for length in self.lengths:
            self.cumulative_lengths.append(self.cumulative_lengths[-1] + length)
        
        if sampling_weights is None:
            self.sampling_weights = [1.0] * len(datasets)
        else:
            self.sampling_weights = sampling_weights
    
    def __len__(self):
        return self.total_length
    
    def __getitem__(self, idx):
        # Find which dataset this index belongs to
        dataset_idx = 0
        for i, cumlen in enumerate(self.cumulative_lengths[1:]):
            if idx < cumlen:
                dataset_idx = i
                break
        
        local_idx = idx - self.cumulative_lengths[dataset_idx]
        return self.datasets[dataset_idx][local_idx]

def get_class_names(dataset_name):
    """Get class names for a dataset"""
    dataset_name = dataset_name.lower()
    
    class_names_map = {
        'cifar10': ['airplane', 'automobile', 'bird', 'cat', 'deer', 'dog', 'frog', 'horse', 'ship', 'truck'],
        'mnist': ['0', '1', '2', '3', '4', '5', '6', '7', '8', '9'],
        'fashion_mnist': ['T-shirt/top', 'Trouser', 'Pullover', 'Dress', 'Coat', 'Sandal', 'Shirt', 'Sneaker', 'Bag', 'Ankle boot'],
        'fashionmnist': ['T-shirt/top', 'Trouser', 'Pullover', 'Dress', 'Coat', 'Sandal', 'Shirt', 'Sneaker', 'Bag', 'Ankle boot'],
        'stl10': ['airplane', 'bird', 'car', 'cat', 'deer', 'dog', 'horse', 'monkey', 'ship', 'truck'],
        'svhn': ['0', '1', '2', '3', '4', '5', '6', '7', '8', '9'],
        'kmnist': ['o', 'ki', 'su', 'tsu', 'na', 'ha', 'ma', 'ya', 're', 'wo'],
    }
    
    if dataset_name in class_names_map:
        return class_names_map[dataset_name]
    
    # For other datasets, return generic class names
    num_classes = get_num_classes(dataset_name)
    return [f'class_{i}' for i in range(num_classes)]
