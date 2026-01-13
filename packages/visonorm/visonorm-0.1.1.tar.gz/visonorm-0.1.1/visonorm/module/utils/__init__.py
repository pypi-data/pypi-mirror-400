"""
Utility modules for text preprocessing, regex expressions, and logging.
"""
from .text_preprocessing import (
    tone_normalization,
    remove_dot_not_end,
    flatten,
    split_edge_punctuation,
    add_non_empty,
    split_emoji_text,
    split_emoji_emoji,
    simple_tokenize,
    case_folding,
    detect_emoji,
    remove_emojis
)

from .regex_expression import (
    Protected,
    Emoji_Protected,
    emoji_pattern,
    emoji_list,
    tone_dict_map,
    EdgePunctLeft,
    EdgePunctRight
)

# Re-export Logger functions  
try:
    from ..Logger import get_logger
except ImportError:
    # Fallback if Logger is not available
    import os
    import logging
    def get_logger(logfile, name='mylogger', level=logging.DEBUG, format='%(asctime)s %(levelname)s %(message)s'):
        log_dir = os.path.dirname(logfile)
        if log_dir:
            os.makedirs(log_dir, exist_ok=True)
        logger = logging.getLogger(name)
        logger.setLevel(level)
        fileHandler = logging.FileHandler(logfile)
        fileHandler.setFormatter(logging.Formatter(format))
        logger.addHandler(fileHandler)
        consoleHandler = logging.StreamHandler()
        consoleHandler.setFormatter(logging.Formatter(format))
        logger.addHandler(consoleHandler)
        logger.propagate = False
        return logger

__all__ = [
    # Text preprocessing functions
    'tone_normalization',
    'remove_dot_not_end',
    'flatten',
    'split_edge_punctuation',
    'add_non_empty',
    'split_emoji_text',
    'split_emoji_emoji',
    'simple_tokenize',
    'case_folding',
    'detect_emoji',
    'remove_emojis',
    # Regex expressions
    'Protected',
    'Emoji_Protected',
    'emoji_pattern',
    'emoji_list',
    'tone_dict_map',
    'EdgePunctLeft',
    'EdgePunctRight',
    # Logger
    'get_logger',
]

