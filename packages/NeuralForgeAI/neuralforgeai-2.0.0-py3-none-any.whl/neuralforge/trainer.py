import torch
import torch.nn as nn
import torch.amp as amp
from torch.utils.data import DataLoader
from typing import Optional, Dict, Any, Callable
import time
import os
from tqdm import tqdm
from .utils.logger import Logger
from .utils.metrics import MetricsTracker
from .config import Config

class Trainer:
    def __init__(
        self,
        model: nn.Module,
        train_loader: DataLoader,
        val_loader: Optional[DataLoader],
        optimizer: torch.optim.Optimizer,
        criterion: nn.Module,
        config: Config,
        scheduler: Optional[Any] = None,
        device: Optional[str] = None
    ):
        self.model = model
        self.train_loader = train_loader
        self.val_loader = val_loader
        self.optimizer = optimizer
        self.criterion = criterion
        self.config = config
        self.scheduler = scheduler
        self.device = device or config.device
        
        self.model.to(self.device)
        
        # Enhanced AMP support with GradScaler
        self.scaler = amp.GradScaler('cuda') if config.use_amp and self.device == 'cuda' else None
        self.logger = Logger(config.log_dir, config.model_name)
        self.metrics = MetricsTracker()
        
        self.current_epoch = 0
        self.global_step = 0
        self.best_val_loss = float('inf')
        self.best_val_acc = 0.0
        
        # Gradient accumulation support
        self.accumulation_steps = getattr(config, 'accumulation_steps', 1)
        
        # Compile model for faster execution (PyTorch 2.0+)
        if hasattr(torch, 'compile') and getattr(config, 'compile_model', False):
            try:
                self.model = torch.compile(self.model)
                self.logger.info("Model compiled with torch.compile for faster execution")
            except:
                self.logger.info("torch.compile not available, skipping compilation")
        
        os.makedirs(config.model_dir, exist_ok=True)
        
        self.logger.info(f"Trainer initialized with device: {self.device}")
        self.logger.info(f"Model parameters: {sum(p.numel() for p in model.parameters()):,}")
        self.logger.info(f"Trainable parameters: {sum(p.numel() for p in model.parameters() if p.requires_grad):,}")
        if self.accumulation_steps > 1:
            self.logger.info(f"Gradient accumulation steps: {self.accumulation_steps}")
    
    def train_epoch(self) -> Dict[str, float]:
        self.model.train()
        epoch_loss = 0.0
        correct = 0
        total = 0
        
        pbar = tqdm(self.train_loader, desc=f"Epoch {self.current_epoch + 1}/{self.config.epochs}")
        
        for batch_idx, (inputs, targets) in enumerate(pbar):
            inputs = inputs.to(self.device, non_blocking=True)
            targets = targets.to(self.device, non_blocking=True)
            
            # Gradient accumulation: only zero grad at start of accumulation
            if batch_idx % self.accumulation_steps == 0:
                self.optimizer.zero_grad(set_to_none=True)
            
            if self.scaler is not None:
                with amp.autocast('cuda'):
                    outputs = self.model(inputs)
                    loss = self.criterion(outputs, targets)
                    # Scale loss for gradient accumulation
                    loss = loss / self.accumulation_steps
                
                self.scaler.scale(loss).backward()
                
                # Only step optimizer after accumulation_steps
                if (batch_idx + 1) % self.accumulation_steps == 0:
                    if self.config.grad_clip > 0:
                        self.scaler.unscale_(self.optimizer)
                        torch.nn.utils.clip_grad_norm_(self.model.parameters(), self.config.grad_clip)
                    
                    self.scaler.step(self.optimizer)
                    self.scaler.update()
            else:
                outputs = self.model(inputs)
                loss = self.criterion(outputs, targets)
                # Scale loss for gradient accumulation
                loss = loss / self.accumulation_steps
                loss.backward()
                
                # Only step optimizer after accumulation_steps
                if (batch_idx + 1) % self.accumulation_steps == 0:
                    if self.config.grad_clip > 0:
                        torch.nn.utils.clip_grad_norm_(self.model.parameters(), self.config.grad_clip)
                    
                    self.optimizer.step()
            
            # Track metrics (use original loss value)
            epoch_loss += loss.item() * self.accumulation_steps
            _, predicted = outputs.max(1)
            total += targets.size(0)
            correct += predicted.eq(targets).sum().item()
            
            self.global_step += 1
            
            if batch_idx % 10 == 0:
                pbar.set_postfix({
                    'loss': f'{loss.item() * self.accumulation_steps:.4f}',
                    'acc': f'{100. * correct / total:.2f}%'
                })
        
        avg_loss = epoch_loss / len(self.train_loader)
        accuracy = 100. * correct / total
        
        return {'loss': avg_loss, 'accuracy': accuracy}
    
    def validate(self) -> Dict[str, float]:
        if self.val_loader is None:
            return {}
        
        self.model.eval()
        val_loss = 0.0
        correct = 0
        total = 0
        
        with torch.no_grad():
            for inputs, targets in tqdm(self.val_loader, desc="Validation"):
                inputs = inputs.to(self.device, non_blocking=True)
                targets = targets.to(self.device, non_blocking=True)
                
                if self.scaler is not None:
                    with amp.autocast('cuda'):
                        outputs = self.model(inputs)
                        loss = self.criterion(outputs, targets)
                else:
                    outputs = self.model(inputs)
                    loss = self.criterion(outputs, targets)
                
                val_loss += loss.item()
                _, predicted = outputs.max(1)
                total += targets.size(0)
                correct += predicted.eq(targets).sum().item()
        
        avg_loss = val_loss / len(self.val_loader)
        accuracy = 100. * correct / total
        
        return {'loss': avg_loss, 'accuracy': accuracy}
    
    def train(self):
        self.logger.info("Starting training...")
        start_time = time.time()
        
        for epoch in range(self.config.epochs):
            self.current_epoch = epoch
            epoch_start = time.time()
            
            train_metrics = self.train_epoch()
            val_metrics = self.validate()
            
            if self.scheduler is not None:
                if isinstance(self.scheduler, torch.optim.lr_scheduler.ReduceLROnPlateau):
                    self.scheduler.step(val_metrics.get('loss', train_metrics['loss']))
                else:
                    self.scheduler.step()
            
            current_lr = self.optimizer.param_groups[0]['lr']
            epoch_time = time.time() - epoch_start
            
            self.logger.info(
                f"Epoch {epoch + 1}/{self.config.epochs} | "
                f"Train Loss: {train_metrics['loss']:.4f} | "
                f"Train Acc: {train_metrics['accuracy']:.2f}% | "
                f"Val Loss: {val_metrics.get('loss', 0):.4f} | "
                f"Val Acc: {val_metrics.get('accuracy', 0):.2f}% | "
                f"LR: {current_lr:.6f} | "
                f"Time: {epoch_time:.2f}s"
            )
            
            self.metrics.update({
                'epoch': epoch + 1,
                'train_loss': train_metrics['loss'],
                'train_acc': train_metrics['accuracy'],
                'val_loss': val_metrics.get('loss', 0),
                'val_acc': val_metrics.get('accuracy', 0),
                'lr': current_lr,
                'time': epoch_time
            })
            
            if (epoch + 1) % self.config.checkpoint_freq == 0:
                self.save_checkpoint(f'checkpoint_epoch_{epoch + 1}.pt')
            
            # Save best model based on both loss and accuracy
            if val_metrics:
                if val_metrics['loss'] < self.best_val_loss:
                    self.best_val_loss = val_metrics['loss']
                    self.save_checkpoint('best_model_loss.pt')
                    self.logger.info(f"New best model (loss) saved with val_loss: {self.best_val_loss:.4f}")
                
                if val_metrics['accuracy'] > self.best_val_acc:
                    self.best_val_acc = val_metrics['accuracy']
                    self.save_checkpoint('best_model.pt')
                    self.logger.info(f"New best model (acc) saved with val_acc: {self.best_val_acc:.2f}%")
        
        total_time = time.time() - start_time
        self.logger.info(f"Training completed in {total_time / 3600:.2f} hours")
        
        self.save_checkpoint('final_model.pt')
        self.metrics.save(os.path.join(self.config.log_dir, 'metrics.json'))
    
    def save_checkpoint(self, filename: str):
        checkpoint_path = os.path.join(self.config.model_dir, filename)
        
        checkpoint = {
            'epoch': self.current_epoch,
            'global_step': self.global_step,
            'model_state_dict': self.model.state_dict(),
            'optimizer_state_dict': self.optimizer.state_dict(),
            'best_val_loss': self.best_val_loss,
            'config': self.config,
        }
        
        if self.scheduler is not None:
            checkpoint['scheduler_state_dict'] = self.scheduler.state_dict()
        
        if self.scaler is not None:
            checkpoint['scaler_state_dict'] = self.scaler.state_dict()
        
        torch.save(checkpoint, checkpoint_path)
        self.logger.info(f"Checkpoint saved: {checkpoint_path}")
    
    def load_checkpoint(self, checkpoint_path: str):
        self.logger.info(f"Loading checkpoint: {checkpoint_path}")
        checkpoint = torch.load(checkpoint_path, map_location=self.device)
        
        self.model.load_state_dict(checkpoint['model_state_dict'])
        self.optimizer.load_state_dict(checkpoint['optimizer_state_dict'])
        self.current_epoch = checkpoint['epoch']
        self.global_step = checkpoint['global_step']
        self.best_val_loss = checkpoint['best_val_loss']
        
        if self.scheduler is not None and 'scheduler_state_dict' in checkpoint:
            self.scheduler.load_state_dict(checkpoint['scheduler_state_dict'])
        
        if self.scaler is not None and 'scaler_state_dict' in checkpoint:
            self.scaler.load_state_dict(checkpoint['scaler_state_dict'])
        
        self.logger.info(f"Checkpoint loaded from epoch {self.current_epoch}")
    
    def test(self, test_loader: DataLoader) -> Dict[str, float]:
        self.logger.info("Starting testing...")
        self.model.eval()
        
        test_loss = 0.0
        correct = 0
        total = 0
        
        with torch.no_grad():
            for inputs, targets in tqdm(test_loader, desc="Testing"):
                inputs = inputs.to(self.device, non_blocking=True)
                targets = targets.to(self.device, non_blocking=True)
                
                outputs = self.model(inputs)
                loss = self.criterion(outputs, targets)
                
                test_loss += loss.item()
                _, predicted = outputs.max(1)
                total += targets.size(0)
                correct += predicted.eq(targets).sum().item()
        
        avg_loss = test_loss / len(test_loader)
        accuracy = 100. * correct / total
        
        self.logger.info(f"Test Loss: {avg_loss:.4f} | Test Acc: {accuracy:.2f}%")
        
        return {'loss': avg_loss, 'accuracy': accuracy}