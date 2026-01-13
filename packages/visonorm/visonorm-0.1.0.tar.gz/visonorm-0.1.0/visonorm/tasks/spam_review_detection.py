import torch
from transformers import AutoTokenizer, AutoModelForSequenceClassification
from contextlib import nullcontext
from visonorm.utils import suppress_output, clear_console

class SpamReviewDetection:
    MODEL_MAP = {
        "phobert-v1": "visolex/phobert-v1-spam-binary",
        "phobert-v1-multiclass": "visolex/phobert-v1-spam-multiclass",
        "phobert-v2": "visolex/phobert-v2-spam-binary",
        "phobert-v2-multiclass": "visolex/phobert-v2-spam-multiclass",
        "visobert": "visolex/visobert-spam-binary",
        "visobert-multiclass": "visolex/visobert-spam-multiclass",
        "bartpho": "visolex/bartpho-spam-binary",
        "bartpho-multiclass": "visolex/bartpho-spam-multiclass",
        "xlm-r": "visolex/xlm-r-spam-binary",
        "xlm-r-multiclass": "visolex/xlm-r-spam-multiclass",
        "mbert": "visolex/mbert-spam-binary",
        "mbert-multiclass": "visolex/mbert-spam-multiclass",
        "vit5": "visolex/vit5-spam-binary",
        "vit5-multiclass": "visolex/vit5-spam-multiclass",
        "textcnn": "visolex/textcnn-spam-binary",
        "textcnn-multiclass": "visolex/textcnn-spam-multiclass",
        "bilstm": "visolex/bilstm-spam-binary",
        "bilstm-multiclass": "visolex/bilstm-spam-multiclass",
        "roberta-gru": "visolex/roberta-gru-spam-binary",
        "roberta-gru-multiclass": "visolex/roberta-gru-spam-multiclass",
        "sphobert": "visolex/sphobert-spam-binary",
        "sphobert-multiclass": "visolex/sphobert-spam-multiclass",
    }
    
    @staticmethod
    def list_models():
        """
        List all available models for spam review detection.
        Returns:
            dict: Dictionary with model names as keys and HuggingFace paths as values.
        """
        return SpamReviewDetection.MODEL_MAP.copy()
    
    @staticmethod
    def list_model_names():
        """
        List all available model names for spam review detection.
        Returns:
            list: List of available model names.
        """
        return list(SpamReviewDetection.MODEL_MAP.keys())
    
    def __init__(self, model_name, silent=True, clear_output=True):
        if model_name not in self.MODEL_MAP:
            available = self.list_model_names()
            raise ValueError(f"Model '{model_name}' not found. Available models: {available}")
        model_path = self.MODEL_MAP[model_name]
        ctx = suppress_output() if silent else nullcontext()
        with ctx:
            try:
                self.tokenizer = AutoTokenizer.from_pretrained(model_path, trust_remote_code=True)
                self.model = AutoModelForSequenceClassification.from_pretrained(model_path, trust_remote_code=True)
            except Exception as e:
                # Try without trust_remote_code if it fails
                try:
                    self.tokenizer = AutoTokenizer.from_pretrained(model_path)
                    self.model = AutoModelForSequenceClassification.from_pretrained(model_path)
                except Exception as e2:
                    raise RuntimeError(f"Failed to load model '{model_name}' from '{model_path}'. "
                                     f"Error: {str(e2)}. Please check if the model exists on HuggingFace Hub.")
        if clear_output:
            clear_console()
        # Determine label map based on model type
        if "multiclass" in model_name:
            # Multiclass models typically have more labels
            # You may need to adjust this based on your actual model
            self.label_map = {0: "Non-spam", 1: "Spam", 2: "Promotional"}  # Adjust as needed
        else:
            self.label_map = {0: "Non-spam", 1: "Spam"}

    def predict(self, text):
        """
        Detect spam reviews in the input text.
        Args:
            text (str): Input text.
        Returns:
            str: Spam label (e.g., "Spam", "Non-spam").
        """
        inputs = self.tokenizer(text, return_tensors="pt", truncation=True, max_length=256)
        with torch.no_grad():
            outputs = self.model(**inputs)
            pred = outputs.logits.argmax(dim=-1).item()
        # Handle cases where prediction index is not in label_map
        if pred not in self.label_map:
            return f"Label_{pred}"  # Return generic label if not found
        return self.label_map[pred]
    
    def __call__(self, text, model_name):
        return self.predict(text)