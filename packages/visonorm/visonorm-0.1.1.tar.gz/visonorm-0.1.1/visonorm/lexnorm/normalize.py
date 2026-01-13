import logging
from transformers import AutoTokenizer, AutoModelForMaskedLM
from .detect import NswDetector

# Configure logger once in your main script
logging.basicConfig(
    level=logging.INFO, 
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
LOGGER = logging.getLogger("visonorm.normalizer")

class ViSoLexNormalizer:
    def __init__(self, model_repo=None, device='cpu'):
        """
        Initialize the ViSoNorm Normalizer using HuggingFace model.
        
        Args:
            model_repo (str, optional): HuggingFace model repository. 
                If None, uses default model "visolex/visobert-normalizer-mix100"
            device (str): Device to run inference on ('cpu' or 'cuda')
        """
        if model_repo is None:
            model_repo = "visolex/visobert-normalizer-mix100"
        
        self.model_repo = model_repo
        self.device = device
        self.logger = LOGGER
        self.loaded = False
        
        # Load tokenizer and model
        self.logger.info(f"Loading tokenizer and model from {model_repo}...")
        self.tokenizer = AutoTokenizer.from_pretrained(model_repo)
        self.model = AutoModelForMaskedLM.from_pretrained(model_repo, trust_remote_code=True)
        self.model.to(device)
        self.loaded = True
        self.logger.info("✅ Model loaded successfully!")

    def normalize_sentence(self, input_str, detect_nsw=False):
        """
        Normalize a sentence and optionally detect NSW tokens.
        
        Args:
            input_str (str): Input text to normalize
            detect_nsw (bool): If True, also return NSW detection results
        
        Returns:
            If detect_nsw=False: normalized text string
            If detect_nsw=True: tuple of (nsw_spans, normalized_text)
                where nsw_spans is a list of dictionaries with NSW information
        """
        if not self.loaded:
            self.logger.warning("Model not loaded yet!")
            return input_str if not detect_nsw else ([], input_str)
        
        # Use the built-in normalize_text method from the model
        normalized_text, source_tokens, predicted_tokens = self.model.normalize_text(
            self.tokenizer, input_str, device=self.device
        )
        
        if detect_nsw:
            # Use the built-in detect_nsw method from the model
            nsw_results = self.model.detect_nsw(self.tokenizer, input_str, device=self.device)
            return nsw_results, normalized_text
        else:
            return normalized_text
