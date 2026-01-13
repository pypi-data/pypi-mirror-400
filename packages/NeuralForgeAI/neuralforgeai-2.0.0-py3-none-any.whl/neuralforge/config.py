import json
import os
from typing import Any, Dict, Optional
from dataclasses import dataclass, asdict

@dataclass
class Config:
    # Model and training basics
    model_name: str = "neuralforge_model"
    batch_size: int = 32
    epochs: int = 100
    learning_rate: float = 0.001
    weight_decay: float = 0.0001
    optimizer: str = "adamw"
    scheduler: str = "cosine"
    warmup_epochs: int = 5
    grad_clip: float = 1.0
    
    # Data loading
    data_path: str = "./data"
    num_workers: int = 4
    pin_memory: bool = True
    persistent_workers: bool = True  # v2.0: Keep workers alive between epochs
    prefetch_factor: int = 2  # v2.0: Prefetch batches for faster loading
    
    # Model saving and logging
    model_dir: str = "./models"
    log_dir: str = "./logs"
    checkpoint_freq: int = 10
    
    # Performance optimizations (v2.0)
    use_amp: bool = True  # Mixed precision training
    accumulation_steps: int = 1  # Gradient accumulation for larger effective batch size
    compile_model: bool = False  # PyTorch 2.0+ model compilation
    device: str = "cuda"
    seed: int = 42
    
    # Neural Architecture Search
    nas_enabled: bool = False
    nas_population_size: int = 20
    nas_generations: int = 50
    nas_mutation_rate: float = 0.1
    
    # Model architecture
    image_size: int = 224
    num_classes: int = 1000
    
    def save(self, path: str):
        os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path, 'w') as f:
            json.dump(asdict(self), f, indent=2)
    
    @classmethod
    def load(cls, path: str) -> 'Config':
        with open(path, 'r') as f:
            data = json.load(f)
        return cls(**data)
    
    def update(self, **kwargs):
        for key, value in kwargs.items():
            if hasattr(self, key):
                setattr(self, key, value)
    
    def __str__(self) -> str:
        return json.dumps(asdict(self), indent=2)