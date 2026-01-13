import torch
from contextlib import nullcontext
from visonorm.utils import suppress_output, clear_console
from transformers import AutoTokenizer, AutoModelForSequenceClassification

class EmotionRecognition:
    MODEL_MAP = {
        "phobert-v1": "visolex/emotion-phobert-v1",
        "phobert-v2": "visolex/emotion-phobert-v2",        
        "xlm-roberta": "visolex/emotion-xlm-roberta",
        "bartpho": "visolex/emotion-bartpho",
        "mbert": "visolex/emotion-mbert",
        "vit5": "visolex/emotion-vit5",
        "visobert": "visolex/emotion-visobert",
        "sphobert": "visolex/emotion-sphobert",
        "roberta-gru": "visolex/emotion-roberta-gru",
        #"textcnn": "visolex/emotion-textcnn",
        #"bilstm": "visolex/emotion-bilstm",
    }
    
    @staticmethod
    def list_models():
        """
        List all available models for emotion recognition.
        Returns:
            dict: Dictionary with model names as keys and HuggingFace paths as values.
        """
        return EmotionRecognition.MODEL_MAP.copy()
    
    @staticmethod
    def list_model_names():
        """
        List all available model names for emotion recognition.
        Returns:
            list: List of available model names.
        """
        return list(EmotionRecognition.MODEL_MAP.keys())

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
        self.label_map = {
            0: "Anger", 1: "Disgust", 2: "Enjoyment", 3: "Fear",
            4: "Other", 5: "Sadness", 6: "Surprise"
        }

    def predict(self, text):
        """
        Predict emotion labels for the input text.
        Args:
            text (str): Input text.
        Returns:
            str: Predicted emotion label.
        """
        inputs = self.tokenizer(text, return_tensors="pt", truncation=True, max_length=256)
        with torch.no_grad():
            outputs = self.model(**inputs)
            predicted_class = outputs.logits.argmax(dim=-1).item()
        # Handle cases where prediction index is not in label_map
        if predicted_class not in self.label_map:
            return f"Label_{predicted_class}"  # Return generic label if not found
        return self.label_map[predicted_class]
    
    def __call__(self, text):   
        return self.predict(text)