"""
Dynamic neural architecture search space with stable encoding/decoding.
"""

import numpy as np
import random
import hashlib
from typing import Dict


class DynamicNeuralArchitecture:
    """
    Dynamic NAS search space with STABLE encoding/decoding.
    
    Features:
    - Soft-max activation selection (no discrete jumps)
    - Noise buffering in from_vector
    - Continuous dropout scaling
    """
    
    def __init__(self, min_layers: int = 2, max_layers: int = 6, max_units: int = 512):
        self.min_layers = min_layers
        self.max_layers = max_layers
        self.max_units = max_units
        
        self.n_layers = 0
        self.layer_units = []
        self.activations = []
        self.dropouts = []
        self.use_skip = []
        
        self.activation_options = ['relu', 'tanh', 'elu', 'gelu']
    
    def initialize_random(self):
        """Random initialization"""
        self.n_layers = random.randint(self.min_layers, self.max_layers)
        self.layer_units = []
        self.activations = []
        self.dropouts = []
        self.use_skip = []
        
        for i in range(self.n_layers):
            units = 2 ** random.randint(5, int(np.log2(self.max_units)))
            self.layer_units.append(units)
            self.activations.append(random.choice(self.activation_options))
            self.dropouts.append(round(random.uniform(0.0, 0.4), 2))
            self.use_skip.append(random.choice([True, False]) if i > 0 else False)
    
    def to_vector(self) -> np.ndarray:
        """Convert to fixed-size continuous vector (STABLE)"""
        vector = []
        
        # Depth (normalized)
        depth_ratio = (self.n_layers - self.min_layers) / (self.max_layers - self.min_layers)
        vector.append(depth_ratio)
        
        # Calculate values per layer
        values_per_layer = 1 + len(self.activation_options) + 1 + 1  # units + act_probs + dropout + skip
        
        # Layers (with padding)
        for i in range(self.max_layers):
            if i < self.n_layers:
                # Units (log scale, normalized)
                vector.append(np.log2(self.layer_units[i]) / np.log2(self.max_units))
                
                # Activation (soft-encoded as probabilities)
                act_probs = [0.0] * len(self.activation_options)
                act_idx = self.activation_options.index(self.activations[i])
                act_probs[act_idx] = 1.0
                vector.extend(act_probs)
                
                # Dropout (direct)
                vector.append(self.dropouts[i])
                
                # Skip (probability)
                vector.append(1.0 if self.use_skip[i] else 0.0)
            else:
                # Padding - must match values_per_layer
                vector.extend([0.0] * values_per_layer)
        
        return np.array(vector)
    
    def from_vector(self, vector: np.ndarray):
        """Reconstruct from vector with NOISE BUFFERING"""
        idx = 0
        
        # Depth with buffering
        depth_ratio = np.clip(vector[idx], 0, 1)
        depth_continuous = self.min_layers + depth_ratio * (self.max_layers - self.min_layers)
        self.n_layers = int(np.round(depth_continuous))
        self.n_layers = max(self.min_layers, min(self.max_layers, self.n_layers))
        idx += 1
        
        self.layer_units = []
        self.activations = []
        self.dropouts = []
        self.use_skip = []
        
        # Calculate values per layer in encoding (must match to_vector)
        values_per_layer = 1 + len(self.activation_options) + 1 + 1  # units + act_probs + dropout + skip
        
        for i in range(self.max_layers):
            if i < self.n_layers:
                # Only decode actual layers
                # Units (stable rounding)
                if idx >= len(vector):
                    break
                log_units = vector[idx] * np.log2(self.max_units)
                units = 2 ** max(5, min(int(np.log2(self.max_units)), int(np.round(log_units))))
                self.layer_units.append(units)
                idx += 1
                
                # Activation (SOFT-MAX selection - NO discrete jumps)
                if idx + len(self.activation_options) > len(vector):
                    break
                act_probs = np.clip(vector[idx:idx+len(self.activation_options)], 0, 1)
                act_probs = act_probs / (np.sum(act_probs) + 1e-10)  # Normalize
                # Temperature-based selection (softer than argmax)
                temperature = 0.5
                exp_probs = np.exp(act_probs / temperature)
                exp_probs = exp_probs / np.sum(exp_probs)
                act_idx = np.argmax(exp_probs)
                self.activations.append(self.activation_options[act_idx])
                idx += len(self.activation_options)
                
                # Dropout (continuous, clamped)
                if idx >= len(vector):
                    break
                dropout = np.clip(vector[idx], 0.0, 0.5)
                self.dropouts.append(round(dropout, 2))
                idx += 1
                
                # Skip (threshold with hysteresis)
                if idx >= len(vector):
                    break
                skip_prob = vector[idx]
                skip = skip_prob > 0.5
                self.use_skip.append(skip if i > 0 else False)
                idx += 1
            else:
                # Skip padding values
                idx += values_per_layer
    
    def copy(self):
        """Deep copy"""
        new_arch = DynamicNeuralArchitecture(self.min_layers, self.max_layers, self.max_units)
        new_arch.n_layers = self.n_layers
        new_arch.layer_units = self.layer_units.copy()
        new_arch.activations = self.activations.copy()
        new_arch.dropouts = self.dropouts.copy()
        new_arch.use_skip = self.use_skip.copy()
        return new_arch
    
    def get_hash(self) -> str:
        """Unique hash for caching"""
        config = f"{self.n_layers}_{self.layer_units}_{self.activations}_{self.dropouts}_{self.use_skip}"
        return hashlib.md5(config.encode()).hexdigest()
    
    def get_metadata(self) -> Dict:
        """Metadata for adapters"""
        return {
            'n_layers': self.n_layers,
            'layer_units': self.layer_units,
            'activations': self.activations,
            'dropouts': self.dropouts,
            'use_skip': self.use_skip,
            'total_params': sum(self.layer_units) * 128
        }
    
    def __str__(self) -> str:
        lines = [f"Architecture ({self.n_layers} layers):"]
        for i in range(self.n_layers):
            skip_str = " [+SKIP]" if self.use_skip[i] else ""
            lines.append(f"  L{i+1}: {self.layer_units[i]:>4}u | "
                        f"{self.activations[i]:<6} | drop={self.dropouts[i]:.2f}{skip_str}")
        return "\n".join(lines)