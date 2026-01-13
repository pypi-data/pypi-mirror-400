import re
from itertools import chain
from typing import List, Dict, Any
from .regex_expression import (
    EdgePunctLeft, EdgePunctRight, Protected, Emoji_Protected, emoji_pattern, emoji_list, tone_dict_map
)

# Utility: Tone normalization
def tone_normalization(text: str, tone_map: Dict[str, str] = tone_dict_map) -> str:
    """
    Replace text based on a tone mapping dictionary.
    
    Args:
        text (str): Input text to be normalized.
        tone_map (dict): Mapping dictionary with replacement rules.
    
    Returns:
        str: Normalized text.
    """
    for original, replacement in tone_map.items():
        text = text.replace(replacement, original)
    return text

# Utility: Remove redundant dots not at the end of the list
def remove_dot_not_end(lst: List[str]) -> List[str]:
    """
    Remove dots ('.') from the list except if at the end or followed by an uppercase letter.
    
    Args:
        lst (list): Input list of strings.
    
    Returns:
        list: Modified list with redundant dots removed.
    """
    for i, elem in enumerate(lst):
        if elem == '.':
            if i != len(lst) - 1 and (i == 0 or not (lst[i + 1][0].isupper() if lst[i + 1] and len(lst[i + 1]) > 0 else False)):
                lst[i] = ''
    return lst

# Utility: Flatten nested lists
def flatten(lst: List[Any]) -> List[Any]:
    """
    Recursively flatten a nested list.
    
    Args:
        lst (list): Input list (potentially nested).
    
    Returns:
        list: Flattened list.
    """
    return list(chain.from_iterable(flatten(item) if isinstance(item, list) else [item] for item in lst))

# Tokenization helpers
def split_edge_punctuation(text: str, edge_punct_left: re.Pattern = EdgePunctLeft, edge_punct_right: re.Pattern = EdgePunctRight) -> str:
    """
    Split text by edge punctuation rules.
    
    Args:
        text (str): Input text.
        edge_punct_left (Pattern): Regex for punctuation on the left.
        edge_punct_right (Pattern): Regex for punctuation on the right.
    
    Returns:
        str: Modified text.
    """
    text = edge_punct_left.sub(r"\1\2 \3", text)
    text = edge_punct_right.sub(r"\1 \2\3", text)
    return text

def add_non_empty(target: List[str], source: List[str]) -> List[str]:
    """
    Add non-empty strings from one list to another.
    
    Args:
        target (list): List to append to.
        source (list): List with potential elements to append.
    
    Returns:
        list: Combined list with non-empty elements added.
    """
    for item in source:
        stripped_item = item.strip()
        if stripped_item:
            target.append(stripped_item)
    return target

# Emoji handling
def split_emoji_text(text: str, emoji_list: List[str]) -> str:
    """
    Separate emojis from text.
    
    Args:
        text (str): Input text.
        emoji_list (list): List of emoji characters.
    
    Returns:
        str: Text with emojis separated and extra whitespace removed.
    """
    # Split text and add spaces around emojis
    result = []
    for char in text:
        if char in emoji_list:
            result.append(f' {char} ')
        else:
            result.append(char)
    
    # Join and remove extra whitespace
    joined_text = ''.join(result)
    # Remove multiple consecutive spaces and trim leading/trailing whitespace
    cleaned_text = re.sub(r'\s+', ' ', joined_text).strip()
    return cleaned_text

def split_emoji_emoji(text_array: List[str], emoji_list: List[str]) -> List[str]:
    """
    Split emojis that are grouped together in words.
    
    Args:
        text_array (list): List of strings or words.
        emoji_list (list): List of emoji characters.
    
    Returns:
        list: Modified list with separated emojis.
    """
    result = []
    for word in text_array:
        if any(char in emoji_list for char in word):
            for char in word:
                result.append(char if char in emoji_list else word)
        else:
            result.append(word)
    return ' '.join(result)


# Main tokenization logic
def simple_tokenize(text: str, protected_patterns: List[re.Pattern], emoji_pattern: re.Pattern) -> List[str]:
    """
    Tokenize text while protecting specific patterns and emojis.
    
    Args:
        text (str): Input text to tokenize.
        protected_patterns (list): List of regex patterns to protect.
        emoji_pattern (Pattern): Regex pattern for emojis.
    
    Returns:
        list: Tokenized text as a list of strings.
    """
    split_punct_text = split_edge_punctuation(text)

    # Detect spans of protected patterns and emojis
    bad_spans = []
    bads = []
    for pattern in protected_patterns:
        for match in pattern.finditer(split_punct_text):
            if match.start() != match.end():
                bads.append([split_punct_text[match.start():match.end()]])
                bad_spans.append((match.start(), match.end()))

    # Find indices for "good" (non-protected) spans
    indices = [0]
    for start, end in bad_spans:
        indices.extend([start, end])
    indices.append(len(split_punct_text))

    # Extract good and bad spans
    split_goods = [
        split_punct_text[indices[i]:indices[i + 1]].strip().split()
        for i in range(0, len(indices), 2)
    ]

    # Interleave good and bad spans
    result = []
    for i, bad in enumerate(bads):
        result = add_non_empty(result, split_goods[i])
        result = add_non_empty(result, bad)
    result = add_non_empty(result, split_goods[-1])
    return result

# Case folding utility
def case_folding(text, mode="lower"):
        """
        Perform case folding on the input text.
        Args:
            text (str): Input text.
            mode (str): "lower", "upper", or "capitalize".
        Returns:
            str: Case-folded text.
        """
        if mode == "lower":
            return text.lower()
        elif mode == "upper":
            return text.upper()
        elif mode == "capitalize":
            return text.title()
        else:
            raise ValueError("Invalid mode. Choose 'lower', 'upper', or 'capitalize'.")



def detect_emoji(text: str) -> List[str]:
    """
    Detect emojis in the text while respecting protected patterns.
    
    Args:
        text (str): Input text to check for emojis.
 
    
    Returns:
        list: List of detected emojis.
    """
    splitPunctText = split_edge_punctuation(text)

    textLength = len(splitPunctText)

    bads = []
    badSpans = []
    for match in Emoji_Protected.finditer(splitPunctText):
        # The spans of the "bads" should not be split.
        if (match.start() != match.end()): #unnecessary?
            bads.append( [splitPunctText[match.start():match.end()]] )
            badSpans.append( (match.start(), match.end()) )

    indices = [0]
    for start, end in badSpans:
        indices.extend([start, end])
    indices.append(textLength)

    result = []

    for i, bad in enumerate(bads):
        result = add_non_empty(result, bad)
    
    return result

def remove_emojis(text: str) -> str:
    """
    Remove emojis from the text.
    
    Args:
        text (str): Input text from which emojis will be removed.
    
    Returns:
        str: Text with emojis removed.
    """
    splitPunctText = split_edge_punctuation(text)

    textLength = len(splitPunctText)

    bads = []
    badSpans = []

    for match in Emoji_Protected.finditer(splitPunctText):
        # The spans of the "bads" should not be split.
        if (match.start() != match.end()):
            bads.append([splitPunctText[match.start():match.end()]])
            badSpans.append((match.start(), match.end()))
    indices = [0]
    for start, end in badSpans:
        indices.extend([start, end])
    indices.append(textLength)

    split_goods = [
        splitPunctText[indices[i]:indices[i + 1]].strip().split()
        for i in range(0, len(indices), 2)
    ]

    result = []

    for i, good in enumerate(split_goods):
        result = add_non_empty(result, good)

    return ' '.join(result)

