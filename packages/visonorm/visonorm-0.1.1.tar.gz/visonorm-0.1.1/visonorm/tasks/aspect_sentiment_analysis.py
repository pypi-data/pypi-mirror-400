import torch
from transformers import AutoTokenizer, AutoModel
from contextlib import nullcontext
from visonorm.utils import suppress_output, clear_console

class AspectSentimentAnalysis:
    MODEL_MAP = {
        "smartphone": {
            "phobert-v1": "visolex/phobert-absa-smartphone",
            "phobert-v2": "visolex/phobert-v2-absa-smartphone",
            "bartpho": "visolex/bartpho-absa-smartphone",
            "vit5": "visolex/vit5-absa-smartphone",
            "mbert": "visolex/mbert-absa-smartphone",
            "visobert": "visolex/visobert-absa-smartphone",
            #"bilstm": "visolex/bilstm-absa-smartphone",
            "xlm-roberta": "visolex/xlm-roberta-absa-smartphone",
            #"textcnn": "visolex/textcnn-absa-smartphone"
        },
        "restaurant": {
            "phobert-v1": "visolex/phobert-v1-absa-restaurant",
            "phobert-v2": "visolex/phobert-v2-absa-restaurant",            
            "bartpho": "visolex/bartpho-absa-restaurant",
            #"bilstm": "visolex/bilstm-absa-restaurant",
            "vit5": "visolex/vit5-absa-restaurant",
            "mbert": "visolex/mbert-absa-restaurant",
            "visobert": "visolex/visobert-absa-restaurant",
            "xlm-roberta": "visolex/xlm-roberta-absa-restaurant",
            #"textcnn": "visolex/textcnn-absa-restaurant"
        },
        "hotel": {
            "phobert-v1": "visolex/phobert-v1-absa-hotel",
            "phobert-v2": "visolex/phobert-v2-absa-hotel",            
            "bartpho": "visolex/bartpho-absa-hotel",
            "vit5": "visolex/vit5-absa-hotel",
            "mbert": "visolex/mbert-absa-hotel",
            "visobert": "visolex/visobert-absa-hotel",
            #"bilstm": "visolex/bilstm-absa-hotel",
            "xlm-roberta": "visolex/xlm-roberta-absa-hotel",
            #"textcnn": "visolex/textcnn-absa-hotel"
        }
    }

    DOMAIN_ASPECT_LABELS = {
        "smartphone": [
            "BATTERY", "CAMERA", "DESIGN", "FEATURES", "GENERAL",
            "PERFORMANCE", "PRICE", "SCREEN", "SERandACC", "STORAGE"
        ],
        "hotel": [
            "FACILITIES#CLEANLINESS", "FACILITIES#COMFORT", "FACILITIES#DESIGN&FEATURES",
            "FACILITIES#GENERAL", "FACILITIES#MISCELLANEOUS", "FACILITIES#PRICES",
            "FACILITIES#QUALITY", "FOOD&DRINKS#MISCELLANEOUS", "FOOD&DRINKS#PRICES",
            "FOOD&DRINKS#QUALITY", "FOOD&DRINKS#STYLE&OPTIONS", "HOTEL#CLEANLINESS",
            "HOTEL#COMFORT", "HOTEL#DESIGN&FEATURES", "HOTEL#GENERAL",
            "HOTEL#MISCELLANEOUS", "HOTEL#PRICES", "HOTEL#QUALITY", "LOCATION#GENERAL",
            "ROOMS#CLEANLINESS", "ROOMS#COMFORT", "ROOMS#DESIGN&FEATURES",
            "ROOMS#GENERAL", "ROOMS#MISCELLANEOUS", "ROOMS#PRICES", "ROOMS#QUALITY",
            "ROOM_AMENITIES#CLEANLINESS", "ROOM_AMENITIES#COMFORT",
            "ROOM_AMENITIES#DESIGN&FEATURES", "ROOM_AMENITIES#GENERAL",
            "ROOM_AMENITIES#MISCELLANEOUS", "ROOM_AMENITIES#PRICES",
            "ROOM_AMENITIES#QUALITY", "SERVICE#GENERAL"
        ],
        "restaurant": [
            "AMBIENCE#GENERAL", "DRINKS#PRICES", "DRINKS#QUALITY", "DRINKS#STYLE&OPTIONS",
            "FOOD#PRICES", "FOOD#QUALITY", "FOOD#STYLE&OPTIONS", "LOCATION#GENERAL",
            "RESTAURANT#GENERAL", "RESTAURANT#MISCELLANEOUS", "RESTAURANT#PRICES",
            "SERVICE#GENERAL"
        ]
    }

    @staticmethod
    def list_domains():
        """
        List all available domains for aspect sentiment analysis.
        Returns:
            list: List of available domain names.
        """
        return list(AspectSentimentAnalysis.MODEL_MAP.keys())
    
    @staticmethod
    def list_models(domain=None):
        """
        List all available models for aspect sentiment analysis.
        Args:
            domain (str, optional): Domain name. If None, returns all models for all domains.
        Returns:
            dict: Dictionary with domain names as keys and model dictionaries as values,
                  or if domain is specified, returns model dictionary for that domain.
        """
        if domain is None:
            return AspectSentimentAnalysis.MODEL_MAP.copy()
        if domain not in AspectSentimentAnalysis.MODEL_MAP:
            available = AspectSentimentAnalysis.list_domains()
            raise ValueError(f"Domain '{domain}' not found. Available domains: {available}")
        return AspectSentimentAnalysis.MODEL_MAP[domain].copy()
    
    @staticmethod
    def list_model_names(domain):
        """
        List all available model names for a specific domain.
        Args:
            domain (str): Domain name.
        Returns:
            list: List of available model names for the specified domain.
        """
        if domain not in AspectSentimentAnalysis.MODEL_MAP:
            available = AspectSentimentAnalysis.list_domains()
            raise ValueError(f"Domain '{domain}' not found. Available domains: {available}")
        return list(AspectSentimentAnalysis.MODEL_MAP[domain].keys())

    def __init__(self, domain, model_name="phobert", sentiment_labels=["POSITIVE", "NEGATIVE", "NEUTRAL"], silent=True, clear_output=True):
        if domain not in self.MODEL_MAP:
            available = self.list_domains()
            raise ValueError(f"Domain '{domain}' not found. Available domains: {available}")
        if model_name not in self.MODEL_MAP[domain]:
            available = self.list_model_names(domain)
            raise ValueError(f"Model '{model_name}' not found for domain '{domain}'. Available models: {available}")
        model_path = self.MODEL_MAP[domain][model_name]
        ctx = suppress_output() if silent else nullcontext()
        with ctx:
            self.tokenizer = AutoTokenizer.from_pretrained(model_path, trust_remote_code=True)
            self.model = AutoModel.from_pretrained(model_path, trust_remote_code=True)
        if clear_output:
            clear_console()
        self.aspect_labels = self.DOMAIN_ASPECT_LABELS.get(domain, [])
        self.sentiment_labels = sentiment_labels

    def predict(self, text, threshold=0.5):
        """
        Perform aspect-based sentiment analysis on the input text.
        Args:
            text (str): Input text.
            threshold (float): Confidence threshold for predictions.
        Returns:
            list: List of tuples (aspect, sentiment).
        """
        inputs = self.tokenizer(text, return_tensors="pt", padding=True, truncation=True, max_length=256)
        inputs.pop("token_type_ids", None)
        with torch.no_grad():
            out = self.model(**inputs)
        logits = out.logits.squeeze(0)
        probs = torch.softmax(logits, dim=-1)
        none_id = probs.size(-1) - 1
        results = []
        for i, aspect in enumerate(self.aspect_labels):
            prob_i = probs[i]
            pred_id = int(prob_i.argmax().item())
            if pred_id != none_id and pred_id < len(self.sentiment_labels):
                score = prob_i[pred_id].item()
                if score >= threshold:
                    results.append((aspect, self.sentiment_labels[pred_id].lower()))
        return results
    
    def __call__(self, text, domain, model_name="phobert", threshold=0.5):
        """
        Call the predict method with the specified domain and model name.
        Args:
            text (str): Input text.
            domain (str): Domain to use for aspect-based sentiment analysis.
            model_name (str): Model name to use.
            threshold (float): Confidence threshold for predictions.
        Returns:
            list: List of tuples (aspect, sentiment).
        """
        return self.predict(text, threshold)