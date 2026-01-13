from .basic_normalizer import BasicNormalizer
from .detect import NswDetector
from .emoji_handler import EmojiHandler
from .normalize import ViSoLexNormalizer


def detect_nsw(input_str, model_repo=None, device='cpu'):
    """
    Detect Non-Standard Words (NSW) in the input text.
    
    Args:
        input_str (str): Input text to analyze
        model_repo (str, optional): HuggingFace model repository
        device (str): Device to run inference on ('cpu' or 'cuda')
    
    Returns:
        List of dictionaries containing NSW information
    """
    detector = NswDetector(model_repo=model_repo, device=device)
    nsw_spans = detector.detect_nsw(input_str)
    return nsw_spans

def normalize_sentence(input_str, detect_nsw=False, model_repo=None, device='cpu'):
    """
    Normalize a sentence and optionally detect NSW tokens.
    
    Args:
        input_str (str): Input text to normalize
        detect_nsw (bool): If True, also return NSW detection results
        model_repo (str, optional): HuggingFace model repository
        device (str): Device to run inference on ('cpu' or 'cuda')
    
    Returns:
        If detect_nsw=False: normalized text string
        If detect_nsw=True: tuple of (nsw_spans, normalized_text)
    """
    normalizer = ViSoLexNormalizer(model_repo=model_repo, device=device)
    return normalizer.normalize_sentence(input_str, detect_nsw)

__all__ = [
    'BasicNormalizer',
    'NswDetector', 
    'EmojiHandler',
    'ViSoLexNormalizer',
    'detect_nsw',
    'normalize_sentence'
]