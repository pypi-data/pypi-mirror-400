"""
Binary predictor for NSW (Non-Standard Word) detection.
"""

import torch.nn as nn


class BinaryPredictor(nn.Module):
    """
    Binary predictor for detecting non-standard words (NSW).
    
    Args:
        input_dim: Input dimension from encoder
        dense_dim: Hidden dimension for first dense layer (optional)
        dense_dim_2: Hidden dimension for second dense layer (optional)
        verbose: Verbosity level
    """
    
    def __init__(self, input_dim, dense_dim=None, dense_dim_2=None, verbose=1):
        super(BinaryPredictor, self).__init__()
        self.verbose = verbose
        self.dense_2 = None
        self.dense = None
        dim_predictor = input_dim
        
        if dense_dim is not None:
            if dense_dim > 0:
                self.dense = nn.Linear(input_dim, dense_dim)
                dim_predictor = dense_dim
                if dense_dim_2 is not None:
                    if dense_dim_2 > 0:
                        self.dense_2 = nn.Linear(dense_dim, dense_dim_2)
                        dim_predictor = dense_dim_2
        else:
            assert dense_dim_2 is None or dense_dim_2 == 0, "ERROR: dense_dim_2 cannot be not null if dense_dim is None"
        
        self.predictor = nn.Linear(dim_predictor, out_features=2)

    def forward(self, encoder_state_projected):
        """
        Forward pass for binary prediction.
        
        Args:
            encoder_state_projected: Encoder output [batch, seq_len, hidden_dim]
            
        Returns:
            Binary predictions [batch, seq_len, 2]
        """
        if self.dense is not None:
            intermediary = nn.ReLU()(self.dense(encoder_state_projected))
            if self.dense_2 is not None:
                intermediary = nn.ReLU()(self.dense_2(intermediary))
        else:
            intermediary = encoder_state_projected
        
        # Binary classification output [batch, seq_len, 2]
        hidden_state_normalize_not = self.predictor(intermediary)
        
        return hidden_state_normalize_not
