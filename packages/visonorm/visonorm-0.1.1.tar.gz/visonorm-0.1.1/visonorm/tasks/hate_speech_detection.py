import torch
from contextlib import nullcontext
from visonorm.utils import suppress_output, clear_console
from transformers import AutoTokenizer, AutoModelForSequenceClassification

class HateSpeechDetection:
    MODEL_MAP = {
        "phobert-v1": "visolex/phobert-v1-hsd", # PhoBERT v1
        "phobert-v2": "visolex/hsd-phobert-v2", # PhoBERT v2
        "bartpho": "visolex/bartpho-hsd",         # BART Pho
        "visobert": "visolex/visobert-hsd",        # ViSoBERT
        "vihate-t5": "visolex/vihate-t5-hsd",       # ViHateT5
        "xlm-r": "visolex/xlm-r-hsd",           # XLM-R Large
        "roberta-gru": "visolex/roberta-gru-hsd",     # RoBERTa-GRU Hybrid
        #"textcnn": "visolex/textcnn-hsd",
        #"bilstm": "visolex/bilstm-hsd",
        "mbert": "visolex/mbert-hsd",
        "sphobert": "visolex/sphobert-hsd",
    }
    
    @staticmethod
    def list_models():
        """
        List all available models for hate speech detection.
        Returns:
            dict: Dictionary with model names as keys and HuggingFace paths as values.
        """
        return HateSpeechDetection.MODEL_MAP.copy()
    
    @staticmethod
    def list_model_names():
        """
        List all available model names for hate speech detection.
        Returns:
            list: List of available model names.
        """
        return list(HateSpeechDetection.MODEL_MAP.keys())
    def __init__(self, model_name, silent=True, clear_output=True):
        if model_name not in self.MODEL_MAP:
            available = self.list_model_names()
            raise ValueError(f"Model '{model_name}' not found. Available models: {available}")
        model_path = self.MODEL_MAP[model_name]
        ctx = suppress_output() if silent else nullcontext()
        with ctx:
            # Try multiple loading strategies
            loaded = False
            last_error = None
            
            # Strategy 1: Try with trust_remote_code and safetensors
            try:
                self.tokenizer = AutoTokenizer.from_pretrained(model_path, trust_remote_code=True)
                self.model = AutoModelForSequenceClassification.from_pretrained(
                    model_path, 
                    trust_remote_code=True,
                    use_safetensors=True
                )
                loaded = True
            except Exception as e1:
                last_error = e1
                # Strategy 2: Try with trust_remote_code but without safetensors
                try:
                    self.tokenizer = AutoTokenizer.from_pretrained(model_path, trust_remote_code=True)
                    self.model = AutoModelForSequenceClassification.from_pretrained(
                        model_path, 
                        trust_remote_code=True,
                        use_safetensors=False
                    )
                    loaded = True
                except Exception as e2:
                    last_error = e2
                    # Strategy 3: Try without trust_remote_code, with safetensors
                    try:
                        self.tokenizer = AutoTokenizer.from_pretrained(model_path)
                        self.model = AutoModelForSequenceClassification.from_pretrained(
                            model_path,
                            use_safetensors=True
                        )
                        loaded = True
                    except Exception as e3:
                        last_error = e3
                        # Strategy 4: Try without trust_remote_code, without safetensors
                        try:
                            self.tokenizer = AutoTokenizer.from_pretrained(model_path)
                            self.model = AutoModelForSequenceClassification.from_pretrained(
                                model_path,
                                use_safetensors=False
                            )
                            loaded = True
                        except Exception as e4:
                            last_error = e4
            
            if not loaded:
                raise RuntimeError(
                    f"Failed to load model '{model_name}' from '{model_path}'. "
                    f"Last error: {str(last_error)}. "
                    f"Please check if the model exists on HuggingFace Hub: https://huggingface.co/{model_path}"
                )
        if clear_output:
            clear_console()
        self.label_map = {0: "CLEAN", 1: "OFFENSIVE", 2: "HATE"}

    def predict(self, text):
        """
        Detect hate speech in the input text.
        Args:
            text (str): Input text.
        Returns:
            str: Hate speech label (e.g., "CLEAN", "OFFENSIVE", "HATE").
        """
        inputs = self.tokenizer(text, return_tensors="pt", truncation=True, max_length=256)
        with torch.no_grad():
            outputs = self.model(**inputs)
            logits = outputs.logits
            pred = logits.argmax(dim=-1).item()
        # Handle cases where prediction index is not in label_map
        if pred not in self.label_map:
            return f"Label_{pred}"  # Return generic label if not found
        return self.label_map[pred]
    def __call__(self, text):
        """
        Call the predict method with the specified model name.
        Args:
            text (str): Input text.
            model_name (str): Model name to use.
        Returns:
            str: Hate speech label.
        """
        return self.predict(text)