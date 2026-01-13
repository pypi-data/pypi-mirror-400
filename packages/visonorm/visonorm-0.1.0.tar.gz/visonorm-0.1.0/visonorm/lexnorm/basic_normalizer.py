from visonorm.module.utils.regex_expression import Protected, emoji_pattern, emoji_list, tone_dict_map
from visonorm.module.utils.text_preprocessing import case_folding, tone_normalization, split_emoji_text, split_emoji_emoji, simple_tokenize, remove_dot_not_end, remove_emojis

class BasicNormalizer:
    def __init__(self):
        """Initialize BasicNormalizer with optional logging (if needed)."""
        self.logger = None  # Placeholder for logger if needed in the future.
    
    def case_folding(self, input_str: str, mode: str = 'lower') -> str:
        """
        Perform case folding on the input string.
        
        Args:
            input_str (str): Input text to be case-folded.
            mode (str): "lower", "upper", or "capitalize".
        
        Returns:
            str: Case-folded text.
        """
        if mode == 'lower':
            return input_str.lower()
        elif mode == 'upper':
            return input_str.upper()
        elif mode == 'capitalize':
            return input_str.title()
        else:
            raise ValueError("Invalid mode. Choose 'lower', 'upper', or 'capitalize'.")

    def tone_normalization(self, input_str: str) -> str:
        """
        Normalize tones in the input string based on a predefined mapping.
        
        Args:
            input_str (str): Input text to be normalized.
        
        Returns:
            str: Tone-normalized text.
        """
        input_str = tone_normalization(input_str, tone_dict_map)
        return input_str
    
    def remove_redundant_dots(self, input_str: str) -> str:
        """
        Remove redundant dots from the input string, except if at the end or followed by an uppercase letter.
        
        Args:
            input_str (str): Input text to be processed.
        
        Returns:
            str: Processed text with redundant dots removed.
        """
        tokens = input_str.split()
        tokens = remove_dot_not_end(tokens)
        return ' '.join(tokens)
    
    def remove_emojis(self, input_str: str) -> str:
        """
        Remove emojis from the input string.
        
        Args:
            input_str (str): Input text to be processed.
        
        Returns:
            str: Processed text with emojis removed.
        """
        return remove_emojis(input_str)

    def basic_normalizer(
        self, 
        input_str: str, 
        case_folding: bool = True,
        mode: str = 'lower',
        tone_normalization: bool = True,
        remove_emoji: bool = False,
        split_emoji: bool = True) -> str:
        """
        Normalize the input string with basic preprocessing steps.
        Args:
            input_str (str): Input text to be normalized.
            case_folding (bool): Whether to apply case folding.
            mode (str): Case folding mode ('lower', 'upper', 'capitalize').
            remove_redundant_dots (bool): Whether to remove redundant dots.
            tone_normalization (bool): Whether to apply tone normalization.
            split_emoji (bool): Whether to split emojis in the text.
        Returns:
            str: Normalized text.
        """
        if case_folding:
            input_str = self.case_folding(input_str, mode)
        #if tone_normalization:
            #input_str = self.tone_normalization(input_str)
        if remove_emoji:
            input_str = self.remove_emojis(input_str)
        if split_emoji:
            input_str = split_emoji_text(input_str, emoji_list)
        tokens = simple_tokenize(input_str, [Protected], emoji_pattern)
        tokens = split_emoji_emoji(tokens, emoji_list)
        #input_str = ' '.join(filter(str.strip, tokens))
        return tokens   


        
