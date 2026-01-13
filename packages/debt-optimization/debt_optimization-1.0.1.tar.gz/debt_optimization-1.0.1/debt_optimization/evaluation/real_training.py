"""
Real PyTorch training evaluator with successive halving.
"""

import numpy as np
from typing import Dict

# PyTorch (optional)
try:
    import torch
    import torch.nn as nn
    import torch.nn.functional as F
    from torch.utils.data import DataLoader, TensorDataset, Subset
    PYTORCH_AVAILABLE = True
except ImportError:
    PYTORCH_AVAILABLE = False


if PYTORCH_AVAILABLE:
    
    class DynamicNet(nn.Module):
        """PyTorch model with skip connections"""
        
        def __init__(self, arch, input_dim: int = 784, output_dim: int = 10):
            super().__init__()
            self.arch = arch
            
            self.layers = nn.ModuleList()
            self.dropouts = nn.ModuleList()
            
            prev_units = input_dim
            for i in range(arch.n_layers):
                self.layers.append(nn.Linear(prev_units, arch.layer_units[i]))
                self.dropouts.append(nn.Dropout(arch.dropouts[i]))
                prev_units = arch.layer_units[i]
            
            self.output = nn.Linear(prev_units, output_dim)
        
        def forward(self, x):
            for i, (layer, dropout) in enumerate(zip(self.layers, self.dropouts)):
                identity = x if self.arch.use_skip[i] and x.shape[-1] == self.arch.layer_units[i] else None
                
                x = layer(x)
                
                act = self.arch.activations[i]
                if act == 'relu':
                    x = F.relu(x)
                elif act == 'tanh':
                    x = torch.tanh(x)
                elif act == 'elu':
                    x = F.elu(x)
                elif act == 'gelu':
                    x = F.gelu(x)
                
                x = dropout(x)
                
                if identity is not None:
                    x = x + identity
            
            return self.output(x)
    
    
    class RealTrainingEvaluator:
        """Real PyTorch training evaluator with Successive Halving"""
        
        def __init__(self, device: str = 'cpu', enable_successive_halving: bool = True):
            self.device = device
            self.cache = {}
            self.enable_successive_halving = enable_successive_halving
            
            # Successive Halving state
            self.sh_survivors = set()  # Hashes of architectures that passed low fidelity
            self.sh_promoted = set()   # Promoted to medium
            
            # Create synthetic dataset
            self.train_dataset, self.val_dataset = self._create_synthetic_data()
        
        def _create_synthetic_data(self, n_samples: int = 5000):
            """Synthetic MNIST-like data"""
            X_train = torch.randn(n_samples, 784)
            y_train = torch.randint(0, 10, (n_samples,))
            X_val = torch.randn(n_samples // 5, 784)
            y_val = torch.randint(0, 10, (n_samples // 5,))
            
            return TensorDataset(X_train, y_train), TensorDataset(X_val, y_val)
        
        def should_evaluate_fidelity(self, arch, fidelity: str) -> bool:
            """Successive Halving: Check if architecture earned this fidelity"""
            if not self.enable_successive_halving:
                return True
            
            arch_hash = arch.get_hash()
            
            if fidelity == 'low':
                return True
            elif fidelity == 'medium':
                return arch_hash in self.sh_survivors
            elif fidelity == 'high':
                return arch_hash in self.sh_promoted
            
            return False
        
        def promote_architecture(self, arch, from_fidelity: str, fitness: float):
            """Promote architecture to next fidelity tier if good enough"""
            if not self.enable_successive_halving:
                return
            
            arch_hash = arch.get_hash()
            
            # Threshold-based promotion (can be made adaptive)
            if from_fidelity == 'low' and fitness < 2.5:  # Good enough for medium
                self.sh_survivors.add(arch_hash)
            elif from_fidelity == 'medium' and fitness < 2.0:  # Good enough for high
                self.sh_promoted.add(arch_hash)
        
        def evaluate(self, arch, fidelity: str = 'low') -> float:
            """Train and return validation loss with Successive Halving"""
            
            # Check if allowed by Successive Halving
            if not self.should_evaluate_fidelity(arch, fidelity):
                return 999.0  # Reject without evaluation
            
            # Fidelity configs
            configs = {
                'low': {'epochs': 2, 'data_frac': 0.2, 'batch_size': 256},
                'medium': {'epochs': 5, 'data_frac': 0.5, 'batch_size': 128},
                'high': {'epochs': 10, 'data_frac': 1.0, 'batch_size': 64}
            }
            
            config = configs[fidelity]
            cache_key = (arch.get_hash(), fidelity)
            
            if cache_key in self.cache:
                return self.cache[cache_key]
            
            # Subsample
            if config['data_frac'] < 1.0:
                n_samples = int(len(self.train_dataset) * config['data_frac'])
                indices = np.random.choice(len(self.train_dataset), n_samples, replace=False)
                train_subset = Subset(self.train_dataset, indices)
            else:
                train_subset = self.train_dataset
            
            train_loader = DataLoader(train_subset, batch_size=config['batch_size'], shuffle=True)
            val_loader = DataLoader(self.val_dataset, batch_size=config['batch_size'])
            
            # Build and train
            model = DynamicNet(arch).to(self.device)
            optimizer = torch.optim.Adam(model.parameters(), lr=0.001)
            criterion = nn.CrossEntropyLoss()
            
            model.train()
            for epoch in range(config['epochs']):
                for X_batch, y_batch in train_loader:
                    X_batch, y_batch = X_batch.to(self.device), y_batch.to(self.device)
                    optimizer.zero_grad()
                    loss = criterion(model(X_batch), y_batch)
                    loss.backward()
                    optimizer.step()
            
            # Validate
            model.eval()
            val_losses = []
            with torch.no_grad():
                for X_batch, y_batch in val_loader:
                    X_batch, y_batch = X_batch.to(self.device), y_batch.to(self.device)
                    val_losses.append(criterion(model(X_batch), y_batch).item())
            
            val_loss = np.mean(val_losses)
            self.cache[cache_key] = val_loss
            
            # Promote if good enough
            self.promote_architecture(arch, fidelity, val_loss)
            
            return val_loss

else:
    # Dummy class if PyTorch not available
    class RealTrainingEvaluator:
        def __init__(self, device: str = 'cpu', enable_successive_halving: bool = True):
            raise RuntimeError("RealTrainingEvaluator requires PyTorch")