import torch
from transformers import AutoTokenizer, AutoModelForTokenClassification
from contextlib import nullcontext
from visonorm.utils import suppress_output, clear_console

class HateSpeechSpanDetection:
    MODEL_MAP = {
        "vihate-t5": "visolex/vihate-t5-hsd-span",
        #"textcnn": "visolex/textcnn-hsd-span",
        #"bilstm": "visolex/bilstm-hsd-span",
        "roberta-gru": "visolex/roberta-gru-hsd-span",
        "phobert-v1": "visolex/phobert-v1-hsd-span",
        "phobert-v2": "visolex/phobert-v2-hsd-span",
        "visobert": "visolex/visobert-hsd-span",
        "bartpho": "visolex/bartpho-hsd-span",
        "xlm-r": "visolex/xlm-r-hsd-span",
        "mbert": "visolex/mbert-hsd-span",
        "vit5": "visolex/vit5-hsd-span",
        "sphobert": "visolex/sphobert-hsd-span",
    }
    
    @staticmethod
    def list_models():
        """
        List all available models for hate speech span detection.
        Returns:
            dict: Dictionary with model names as keys and HuggingFace paths as values.
        """
        return HateSpeechSpanDetection.MODEL_MAP.copy()
    
    @staticmethod
    def list_model_names():
        """
        List all available model names for hate speech span detection.
        Returns:
            list: List of available model names.
        """
        return list(HateSpeechSpanDetection.MODEL_MAP.keys())
    def __init__(self, model_name, silent=True, clear_output=True):
        if model_name not in self.MODEL_MAP:
            available = self.list_model_names()
            raise ValueError(f"Model '{model_name}' not found. Available models: {available}")
        model_path = self.MODEL_MAP[model_name]
        ctx = suppress_output() if silent else nullcontext()
        with ctx:
            try:
                self.tokenizer = AutoTokenizer.from_pretrained(model_path, trust_remote_code=True)
                self.model = AutoModelForTokenClassification.from_pretrained(model_path, trust_remote_code=True)
            except Exception as e:
                # Try without trust_remote_code if it fails
                try:
                    self.tokenizer = AutoTokenizer.from_pretrained(model_path)
                    self.model = AutoModelForTokenClassification.from_pretrained(model_path)
                except Exception as e2:
                    raise RuntimeError(f"Failed to load model '{model_name}' from '{model_path}'. "
                                     f"Error: {str(e2)}. Please check if the model exists on HuggingFace Hub.")
        if clear_output:
            clear_console()

    def predict(self, text):
        """
        Detect spans of hate speech in the input text.
        Args:
            text (str): Input text.
        Returns:
            dict: Tokens and their corresponding span labels.
        """
        inputs = self.tokenizer(text, return_tensors="pt", truncation=True, padding=True)
        with torch.no_grad():
            outputs = self.model(**inputs)
        logits = outputs.logits
        probs = torch.sigmoid(logits)
        preds = (probs > 0.5).long().squeeze().tolist()
        tokens = self.tokenizer.convert_ids_to_tokens(inputs['input_ids'][0])
        span_labels = [p[0] for p in preds]
        span_tokens = [token for token, label in zip(tokens, span_labels) if label == 1 and token not in ['<s>', '</s>']]
        return {"tokens": span_tokens, "text": self.tokenizer.convert_tokens_to_string(span_tokens)}
    
    def __call__(self, text, model_name):
        """
        Call the predict method with the specified model name.
        Args:
            text (str): Input text.
            model_name (str): Model name to use.
        Returns:
            dict: Tokens and their corresponding span labels.
        """
        return self.predict(text)