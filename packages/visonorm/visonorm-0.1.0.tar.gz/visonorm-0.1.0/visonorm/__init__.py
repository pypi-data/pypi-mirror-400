"""
ViSoNorm - Vietnamese Social Media Lexical Normalization Toolkit
"""

import os
import sys
from functools import lru_cache

__author__ = """Ha Dung Nguyen"""
__email__ = 'dungngh@uit.edu.vn'

# Check python version
try:
    version_info = sys.version_info
    if version_info < (3, 10, 0):
        raise RuntimeError("ViSoNorm requires Python 3.10 or later")
except Exception:
    pass

###########################################################
# METADATA
###########################################################

# Version
try:
    version_file = os.path.join(os.path.dirname(__file__), 'VERSION')
    with open(version_file, 'r') as infile:
        __version__ = infile.read().strip()
except NameError:
    __version__ = 'unknown (running code interactively?)'
except IOError as ex:
    __version__ = "unknown (%s)" % ex

###########################################################
# CORE COMPONENTS
###########################################################

# Lexical Normalization Components
from .lexnorm.basic_normalizer import BasicNormalizer
from .lexnorm.detect import NswDetector
from .lexnorm.emoji_handler import EmojiHandler
from .lexnorm.normalize import ViSoLexNormalizer

# Task Components
from .tasks.spam_review_detection import SpamReviewDetection
from .tasks.hate_speech_span_detection import HateSpeechSpanDetection
from .tasks.hate_speech_detection import HateSpeechDetection
from .tasks.emotion_recognition import EmotionRecognition
from .tasks.aspect_sentiment_analysis import AspectSentimentAnalysis

# Dataset Functions
from .datasets.registry import DatasetRegistry
from .datasets.downloader import DatasetDownloader

# Legacy imports for backward compatibility
# Note: ViSoLexTrainer is deprecated, use module-based training instead
# from .framework_components.trainer import ViSoLexTrainer
from .lexnorm import detect_nsw, normalize_sentence, basic_normalizer
from .dictionary import Dictionary

###########################################################
# DATASET FUNCTIONS
###########################################################

def list_datasets():
    """
    List all available datasets.
    Returns:
        list: List of dataset names.
    """
    return DatasetRegistry.list_datasets()

def load_dataset(name: str, force_download: bool = False):
    """
    Download (if needed) and load a dataset as a DataFrame.
    Args:
        name (str): Dataset name.
        force_download (bool): Force re-download even if cached.
    Returns:
        pd.DataFrame: Loaded dataset.
    """
    return DatasetDownloader.load_dataset(name, force_download)

def get_dataset_info(name: str):
    """
    Retrieve dataset metadata by name.
    Args:
        name (str): Dataset name.
    Returns:
        dict: Metadata for the dataset.
    """
    return DatasetRegistry.get_dataset_info(name)

###########################################################
# PUBLIC API
###########################################################

__all__ = [
    # Core Normalization Components
    'BasicNormalizer',
    'NswDetector', 
    'EmojiHandler',
    'ViSoLexNormalizer',
    
    # Task Components
    'SpamReviewDetection',
    'HateSpeechSpanDetection',
    'HateSpeechDetection',
    'EmotionRecognition',
    'AspectSentimentAnalysis',
    
    # Dataset Functions
    'list_datasets',
    'load_dataset',
    'get_dataset_info',
    
    # Legacy components for backward compatibility
    'detect_nsw',
    'normalize_sentence',
    # 'ViSoLexTrainer',  # Deprecated - use module-based training instead
    'Dictionary'
]