from typing import List
from visonorm.module.utils.regex_expression import Protected, Emoji_Protected, emoji_list, tone_dict_map
from visonorm.module.utils.text_preprocessing import split_emoji_text, split_emoji_emoji, detect_emoji, remove_emojis
class EmojiHandler:
    def __init__(self):
        """Initialize EmojiHandler with optional logging (if needed)."""
        self.logger = None  # Placeholder for logger if needed in the future.

    def split_emoji_text(self, input_str: str):
        """
        Split text by emojis and return a list of strings.
        
        Args:
            input_str (str): Input text to be split.
        
        Returns:
            str: Text with emojis separated.
        """
        return split_emoji_text(input_str, emoji_list=emoji_list)

    def split_emoji_emoji(self, input_str: str) -> List[str]:
        """
        Split consecutive emojis in the input string.
        
        Args:
            input_str (str): Input text containing emojis.
        
        Returns:
            List[str]: List of strings with consecutive emojis split.
        """
        return split_emoji_emoji(input_str.split(), emoji_list=emoji_list)

    def detect_emoji(self, input_str: str) -> List[str]:
        """
        Detect emojis in the input string.
        
        Args:
            input_str (str): Input text to detect emojis.
        
        Returns:
            List[str]: List of detected emojis.
        """
        return detect_emoji(input_str)
    
    def remove_emojis(self, input_str: str) -> str:
        """
        Remove emojis from the input string.
        
        Args:
            input_str (str): Input text from which emojis will be removed.
        
        Returns:
            str: Text with emojis removed.
        """
        return remove_emojis(input_str)