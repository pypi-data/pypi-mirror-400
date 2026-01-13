"""
Learned surrogate model for fast architecture evaluation.
"""

import numpy as np

# PyTorch (optional - only if ACCURATE mode)
try:
    import torch
    import torch.nn as nn
    import torch.nn.functional as F
    PYTORCH_AVAILABLE = True
except ImportError:
    PYTORCH_AVAILABLE = False


if PYTORCH_AVAILABLE:
    
    class LearnedSurrogate(nn.Module):
        """
        Lightweight MLP surrogate that learns from evaluation history.
        
        Architecture: Simple 3-layer MLP
        Training: Online updates after each evaluation
        """
        
        def __init__(self, input_dim: int):
            super().__init__()
            self.net = nn.Sequential(
                nn.Linear(input_dim, 64),
                nn.ReLU(),
                nn.Dropout(0.1),
                nn.Linear(64, 32),
                nn.ReLU(),
                nn.Dropout(0.1),
                nn.Linear(32, 1)
            )
            self.optimizer = torch.optim.Adam(self.parameters(), lr=0.001)
            self.trained = False
        
        def forward(self, x):
            return self.net(x).squeeze(-1)
        
        def predict(self, X: np.ndarray) -> float:
            """Predict fitness for a single vector"""
            if not self.trained:
                return 100.0  # Fallback before training
            
            self.eval()
            with torch.no_grad():
                X_tensor = torch.FloatTensor(X).unsqueeze(0)
                pred = self(X_tensor).item()
            return pred
        
        def update(self, X_batch: np.ndarray, y_batch: np.ndarray, epochs: int = 10):
            """Update surrogate with new data"""
            if len(X_batch) < 5:
                return  # Need minimum data
            
            X_tensor = torch.FloatTensor(X_batch)
            y_tensor = torch.FloatTensor(y_batch)
            
            self.train()
            for _ in range(epochs):
                self.optimizer.zero_grad()
                pred = self(X_tensor)
                loss = F.mse_loss(pred, y_tensor)
                loss.backward()
                self.optimizer.step()
            
            self.trained = True

else:
    # Dummy class if PyTorch not available
    class LearnedSurrogate:
        def __init__(self, input_dim: int):
            self.trained = False
        
        def predict(self, X: np.ndarray) -> float:
            return 100.0
        
        def update(self, X_batch: np.ndarray, y_batch: np.ndarray, epochs: int = 10):
            pass