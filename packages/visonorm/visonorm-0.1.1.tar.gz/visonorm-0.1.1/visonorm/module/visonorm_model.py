#!/usr/bin/env python3
"""
ViSoNorm Model Factory - Unified interface for all ViSoNorm architectures.

This module provides a factory function to automatically select the appropriate
ViSoNorm model class based on the model name, treating all architectures equally:

- ViSoBERT (XLMRoberta-based)
- PhoBERT (Roberta-based) 
- BartPho (Bart-based)

Each architecture is implemented in its own dedicated file for better organization
and maintainability.
"""

# Import all ViSoNorm model classes
from .visonorm_visobert_model import ViSoNormViSoBERTForMaskedLM
from .visonorm_phobert_model import ViSoNormPhoBERTForMaskedLM
from .visonorm_bartpho_model import ViSoNormBartPhoForMaskedLM


def get_visonorm_model_class(model_name_or_path):
    """
    Factory function to get the appropriate ViSoNorm model class based on the model name.
    
    This function treats all three architectures equally and automatically detects
    the correct model class based on the model name or path.
    
    Args:
        model_name_or_path: HuggingFace model identifier or path
        
    Returns:
        The appropriate ViSoNorm model class
        
    Examples:
        >>> # ViSoBERT model
        >>> model_class = get_visonorm_model_class("hadung1802/visobert-normalizer")
        >>> model = model_class.from_pretrained("hadung1802/visobert-normalizer")
        
        >>> # PhoBERT model  
        >>> model_class = get_visonorm_model_class("your-org/phobert-normalizer")
        >>> model = model_class.from_pretrained("your-org/phobert-normalizer")
        
        >>> # BartPho model
        >>> model_class = get_visonorm_model_class("your-org/bartpho-normalizer")
        >>> model = model_class.from_pretrained("your-org/bartpho-normalizer")
    """
    model_name_lower = model_name_or_path.lower()
    
    # BartPho detection (check for 'bartpho' or 'bart' keywords)
    if 'bartpho' in model_name_lower or 'bart' in model_name_lower:
        return ViSoNormBartPhoForMaskedLM
    
    # PhoBERT detection (check for 'phobert' or 'roberta' keywords)
    elif 'phobert' in model_name_lower or 'roberta' in model_name_lower:
        return ViSoNormPhoBERTForMaskedLM
    
    # ViSoBERT detection (check for 'visobert' or 'xlm' keywords)
    elif 'visobert' in model_name_lower or 'xlm' in model_name_lower:
        return ViSoNormViSoBERTForMaskedLM
    
    else:
        # Default fallback to ViSoBERT for unknown models
        # This maintains backward compatibility
        return ViSoNormViSoBERTForMaskedLM


def list_supported_architectures():
    """
    List all supported ViSoNorm architectures.
    
    Returns:
        Dictionary mapping architecture names to their model classes
    """
    return {
        'visobert': ViSoNormViSoBERTForMaskedLM,
        'phobert': ViSoNormPhoBERTForMaskedLM,
        'bartpho': ViSoNormBartPhoForMaskedLM,
    }


def get_architecture_info():
    """
    Get information about all supported architectures.
    
    Returns:
        Dictionary with architecture information
    """
    return {
        'visobert': {
            'name': 'ViSoBERT',
            'base_model': 'XLMRobertaModel',
            'description': 'Vietnamese Social Media BERT - Default architecture',
            'model_class': ViSoNormViSoBERTForMaskedLM,
            'keywords': ['visobert', 'xlm']
        },
        'phobert': {
            'name': 'PhoBERT', 
            'base_model': 'RobertaModel',
            'description': 'PhoBERT-based ViSoNorm model',
            'model_class': ViSoNormPhoBERTForMaskedLM,
            'keywords': ['phobert', 'roberta']
        },
        'bartpho': {
            'name': 'BartPho',
            'base_model': 'BartModel', 
            'description': 'BartPho-based ViSoNorm model',
            'model_class': ViSoNormBartPhoForMaskedLM,
            'keywords': ['bartpho', 'bart']
        }
    }


# Export all model classes and factory functions
__all__ = [
    "ViSoNormViSoBERTForMaskedLM",
    "ViSoNormPhoBERTForMaskedLM", 
    "ViSoNormBartPhoForMaskedLM",
    "get_visonorm_model_class",
    "list_supported_architectures",
    "get_architecture_info"
]