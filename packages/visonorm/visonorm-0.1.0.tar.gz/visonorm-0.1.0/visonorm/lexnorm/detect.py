import logging
from transformers import AutoTokenizer, AutoModelForMaskedLM

# Configure logger once in your main script
logging.basicConfig(
    level=logging.INFO, 
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
LOGGER = logging.getLogger("visonorm.nsw_detector")

class NswDetector:
    def __init__(self, model_repo=None, device='cpu'):
        """
        Initialize the NSW Detector using HuggingFace model.
        
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

    def detect_nsw(self, input_str):
        """
        Detect Non-Standard Words (NSW) in the input text.
        
        Args:
            input_str (str): Input text to analyze
        
        Returns:
            List of dictionaries containing NSW information:
            [{'index': int, 'start_index': int, 'end_index': int, 'nsw': str, 
              'prediction': str, 'confidence_score': float}, ...]
        """
        if not self.loaded:
            self.logger.warning("Model not loaded yet!")
            return []
        
        # Use the built-in detect_nsw method from the model
        nsw_results = self.model.detect_nsw(self.tokenizer, input_str, device=self.device)
        
        return nsw_results

    def concatenate_nsw_spans(self, nsw_spans):
        """
        Concatenate adjacent NSW spans.
        
        Args:
            nsw_spans: List of NSW span dictionaries
        
        Returns:
            List of concatenated NSW spans
        """
        if not nsw_spans:
            return []
        
        result = []
        current_span = nsw_spans[0].copy()

        for i in range(1, len(nsw_spans)):
            next_span = nsw_spans[i]
            # Check if spans are adjacent
            if 'end_index' in current_span and 'start_index' in next_span:
                if current_span['end_index'] == next_span['start_index']:
                    current_span['nsw'] += next_span['nsw']
                    current_span['end_index'] = next_span['end_index']
                    if 'prediction' in next_span:
                        current_span['prediction'] = current_span.get('prediction', '') + ' ' + next_span.get('prediction', '')
                    continue
            result.append(current_span)
            current_span = next_span.copy()
        result.append(current_span)

        return result
