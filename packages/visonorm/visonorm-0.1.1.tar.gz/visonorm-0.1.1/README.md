# 📦 ViSoNorm Toolkit — Vietnamese Text Normalization & Processing

**ViSoNorm** is a specialized toolkit for **Vietnamese text normalization and processing**, optimized for **NLP** environments and easily installable via **PyPI**. Resources (datasets, models) are stored and managed directly on **Hugging Face Hub** and **GitHub Releases**.

[![PyPI version](https://badge.fury.io/py/visonorm.svg)](https://badge.fury.io/py/visonorm)
[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

---

## 🚀 Key Features

### 1. 🔧 **BasicNormalizer** — Basic Text Normalization

* **Case folding**: convert entire text to lowercase/uppercase/capitalize.
* **Tone normalization**: normalize Vietnamese tone marks.
* **Basic preprocessing**: remove extra whitespace, special characters, sentence formatting.

### 2. 😀 **EmojiHandler** — Emoji Processing

* **Detect emojis**: detect emojis in text.
* **Split emoji text**: separate emojis from sentences.
* **Remove emojis**: remove all emojis.

### 3. ✏️ **Lexical Normalization** — Social Media Text Normalization

* **ViSoLexNormalizer**: Normalize text using deep learning models from HuggingFace.
* **NswDetector**: Detect non-standard words (NSW).
* **detect_nsw()**: Utility function to detect NSW.
* **normalize_sentence()**: Utility function to normalize sentences.

### 4. 📊 **Resource Management** — Dataset Management

* `list_datasets()` — List available datasets.
* `load_dataset()` — Load dataset from GitHub Releases.
* `get_dataset_info()` — View detailed dataset information.

### 5. 🧠 **Task Models** — Task Processing Models

* **SpamReviewDetection** — Spam detection.
* **HateSpeechDetection** — Hate speech detection.
* **HateSpeechSpanDetection** — Hate speech span detection.
* **EmotionRecognition** — Emotion recognition.
* **AspectSentimentAnalysis** — Aspect-based sentiment analysis.

---

## 📥 Installation

### Install from PyPI (Recommended)

```bash
pip install visonorm
```

### Requirements

- Python >= 3.10
- PyTorch >= 1.10.0
- Transformers >= 4.0.0
- scikit-learn >= 0.24.0
- pandas >= 1.3.0

---

## 📚 Usage Guide

### 1. 🔧 BasicNormalizer — Basic Text Normalization

```python
from visonorm import BasicNormalizer

# Initialize BasicNormalizer
normalizer = BasicNormalizer()

# Example text
text = "Hôm nay tôi rất VUI 😊 và HẠNH PHÚC 🎉!"

# Case folding
print(normalizer.case_folding(text, mode='lower'))
# Output: hôm nay tôi rất vui 😊 và hạnh phúc 🎉!

print(normalizer.case_folding(text, mode='upper'))
# Output: HÔM NAY TÔI RẤT VUI 😊 VÀ HẠNH PHÚC 🎉!

print(normalizer.case_folding(text, mode='capitalize'))
# Output: Hôm Nay Tôi Rất Vui 😊 Và Hạnh Phúc 🎉!

# Tone normalization
text2 = "Bận xong rồi. Xoã đi :)"
print(normalizer.tone_normalization(text2))
# Output: Bận xong rồi. Xõa đi :)

# Basic normalization with options
normalized = normalizer.basic_normalizer(
    text,
    case_folding=True,
    mode='lower',
    remove_emoji=False,
    split_emoji=True
)
print(normalized)
# Output: ['hôm', 'nay', 'tôi', 'rất', 'vui', '😊', 'và', 'hạnh', 'phúc', '🎉', '!']

# Remove emojis
normalized_no_emoji = normalizer.basic_normalizer(
    text,
    case_folding=True,
    remove_emoji=True
)
print(normalized_no_emoji)
# Output: ['hôm', 'nay', 'tôi', 'rất', 'vui', 'và', 'hạnh', 'phúc', '!']
```

### 2. 😊 EmojiHandler — Emoji Processing

```python
from visonorm import EmojiHandler

# Initialize EmojiHandler
emoji_handler = EmojiHandler()

text = "Hôm nay tôi rất vui 😊🎉😊 và hạnh phúc 🎉!"

# Detect emojis
emojis = emoji_handler.detect_emoji(text)
print(f"Detected emojis: {emojis}")
# Output: Detected emojis: ['😊🎉😊', '🎉']

# Split emoji text
split_text = emoji_handler.split_emoji_text(text)
print(f"Split emoji text: {split_text}")
# Output: Hôm nay tôi rất vui 😊 🎉 😊 và hạnh phúc 🎉 !

# Split consecutive emojis
text_consecutive = "Hôm nay tôi rất vui 😊🎉😊"
split_consecutive = emoji_handler.split_emoji_emoji(text_consecutive)
print(f"Split consecutive: {split_consecutive}")
# Output: Hôm nay tôi rất vui 😊 🎉 😊

# Remove emojis
text_no_emoji = emoji_handler.remove_emojis(text)
print(f"Text without emojis: {text_no_emoji}")
# Output: Hôm nay tôi rất vui và hạnh phúc !
```

### 3. ✏️ Lexical Normalization — Social Media Text Normalization

#### Using ViSoLexNormalizer

```python
from visonorm import ViSoLexNormalizer

# Initialize with default model (visolex/visobert-normalizer-mix100)
normalizer = ViSoLexNormalizer()

# Or specify a specific model from HuggingFace
# normalizer = ViSoLexNormalizer(model_repo="visolex/visobert-normalizer-mix100")
# normalizer = ViSoLexNormalizer(model_repo="visolex/bartpho-normalizer-mix100")

# Normalize sentence
input_str = "sv dh gia dinh chua cho di lam :))"
normalized = normalizer.normalize_sentence(input_str)
print(f"Original: {input_str}")
print(f"Normalized: {normalized}")
# Output:
# Original: sv dh gia dinh chua cho di lam :))
# Normalized: sinh viên đại học gia đình chưa cho đi làm :))

# Normalize and detect NSW simultaneously
nsw_spans, normalized_text = normalizer.normalize_sentence(input_str, detect_nsw=True)
print(f"Normalized: {normalized_text}")
print("Detected NSW:")
for nsw in nsw_spans:
    print(f"  - '{nsw['nsw']}' → '{nsw['prediction']}' (confidence: {nsw['confidence_score']})")
# Output:
# Normalized: sinh viên đại học gia đình chưa cho đi làm :))
# Detected NSW:
#   - 'sv' → 'sinh viên' (confidence: 1.0)
#   - 'dh' → 'đại học' (confidence: 1.0)
#   - 'dinh' → 'đình' (confidence: 1.0)
#   - 'chua' → 'chưa' (confidence: 1.0)
#   - 'di' → 'đi' (confidence: 1.0)
#   - 'lam' → 'làm' (confidence: 1.0)
```

#### Using NswDetector

```python
from visonorm import NswDetector

# Initialize detector
detector = NswDetector()

# Detect NSW
input_str = "sv dh gia dinh chua cho di lam"
nsw_spans = detector.detect_nsw(input_str)
for nsw in nsw_spans:
    print(f"NSW: '{nsw['nsw']}' → '{nsw['prediction']}' (confidence: {nsw['confidence_score']})")
```

#### Using Utility Functions

```python
from visonorm import detect_nsw, normalize_sentence

# Detect NSW
nsw_spans = detect_nsw("sv dh gia dinh chua cho di lam")

# Normalize sentence
normalized = normalize_sentence("sv dh gia dinh chua cho di lam")

# Normalize and detect NSW
nsw_spans, normalized = normalize_sentence("sv dh gia dinh chua cho di lam", detect_nsw=True)
```

### 4. 📊 Resource Management — Dataset Management

Datasets are stored on **GitHub Releases** and automatically downloaded when needed.

```python
from visonorm import list_datasets, load_dataset, get_dataset_info

# List all available datasets
datasets = list_datasets()
print("Available datasets:")
for i, dataset in enumerate(datasets, 1):
    print(f"{i}. {dataset}")

# Get detailed information about a dataset
info = get_dataset_info("ViLexNorm")
print(f"URL: {info['url']}")
print(f"Type: {info['type']}")

# Load dataset (auto-cached)
df = load_dataset("ViLexNorm")
print(f"Dataset shape: {df.shape}")
print(df.head())

# Force re-download dataset
df = load_dataset("ViLexNorm", force_download=True)
```

**Available datasets:**

- **ViLexNorm**: Vietnamese Lexical Normalization Dataset
- **ViHSD**: Vietnamese Hate Speech Detection Dataset
- **ViHOS**: Vietnamese Hate and Offensive Speech Dataset
- **UIT-VSMEC**: Vietnamese Social Media Emotion Corpus
- **ViSpamReviews**: Vietnamese Spam Review Detection Dataset
- **UIT-ViSFD**: Vietnamese Sentiment and Emotion Detection Dataset
- **UIT-ViCTSD**: Vietnamese Customer Review Sentiment Dataset
- **ViTHSD**: Vietnamese Toxic Hate Speech Detection Dataset
- **BKEE**: Vietnamese Emotion Recognition Dataset
- **UIT-ViQuAD**: Vietnamese Question Answering Dataset

### 5. 🧠 Task Models — Task Processing Models

All task models are stored on **HuggingFace Hub** at [https://huggingface.co/visolex](https://huggingface.co/visolex).

#### SpamReviewDetection — Spam Detection

```python
from visonorm import SpamReviewDetection

# View available models
models = SpamReviewDetection.list_models()
print("Available models:", SpamReviewDetection.list_model_names())

# Initialize with phobert-v1 model (binary classification)
spam_detector = SpamReviewDetection("phobert-v1")

# Or use other models
# spam_detector = SpamReviewDetection("phobert-v1-multiclass")  # Multiclass model

# Detect spam
text = "Sản phẩm rất tốt, chất lượng cao!"
result = spam_detector.predict(text)
print(f"Text: {text}")
print(f"Result: {result}")
# Output: Result: Non-spam
```

#### HateSpeechDetection — Hate Speech Detection

```python
from visonorm import HateSpeechDetection

# View available models
print("Available models:", HateSpeechDetection.list_model_names())

# Initialize detector
hate_detector = HateSpeechDetection("phobert-v1")
# Or: HateSpeechDetection("phobert-v2"), HateSpeechDetection("visobert"), etc.

# Detect hate speech
text = "Văn bản cần kiểm tra hate speech"
result = hate_detector.predict(text)
print(f"Result: {result}")
# Output: Result: CLEAN
```

#### HateSpeechSpanDetection — Hate Speech Span Detection

```python
from visonorm import HateSpeechSpanDetection

# View available models
print("Available models:", HateSpeechSpanDetection.list_model_names())

# Initialize detector
hate_span_detector = HateSpeechSpanDetection("phobert-v1")
# Or: HateSpeechSpanDetection("vihate-t5"), HateSpeechSpanDetection("visobert"), etc.

# Detect span
text = "Nói cái lồn gì mà khó nghe"
result = hate_span_detector.predict(text)
print(f"Result: {result}")
# Output: {'tokens': [...], 'text': '...'}
```

#### EmotionRecognition — Emotion Recognition

```python
from visonorm import EmotionRecognition

# View available models
print("Available models:", EmotionRecognition.list_model_names())

# Initialize detector
emotion_detector = EmotionRecognition("phobert-v2")
# Or: EmotionRecognition("phobert-v1"), EmotionRecognition("visobert"), etc.

# Recognize emotion
text = "Tôi rất vui mừng và hạnh phúc!"
emotion = emotion_detector.predict(text)
print(f"Emotion: {emotion}")
# Output: Emotion: Enjoyment
```

#### AspectSentimentAnalysis — Aspect-based Sentiment Analysis

```python
from visonorm import AspectSentimentAnalysis

# View available domains
print("Available domains:", AspectSentimentAnalysis.list_domains())

# View available models for a specific domain
print("Models for smartphone:", AspectSentimentAnalysis.list_model_names("smartphone"))
print("Models for restaurant:", AspectSentimentAnalysis.list_model_names("restaurant"))
print("Models for hotel:", AspectSentimentAnalysis.list_model_names("hotel"))

# Initialize with smartphone domain and phobert model
absa = AspectSentimentAnalysis("smartphone", "phobert")
# Or use other models: "phobert-v2", "bartpho", "vit5", "visobert", etc.

# Or other domains
# absa = AspectSentimentAnalysis("restaurant", "phobert-v1")
# absa = AspectSentimentAnalysis("hotel", "phobert-v1")

# Analyze sentiment
text = "Điện thoại có camera rất tốt nhưng pin nhanh hết"
aspects = absa.predict(text, threshold=0.25)
print(f"Aspects: {aspects}")
# Output: [('BATTERY', 'neutral'), ('FEATURES', 'neutral'), ('PERFORMANCE', 'positive'), ...]
```

### 6. 🎯 Advanced Usage — Advanced Usage

#### Combining Multiple Functions

```python
from visonorm import BasicNormalizer, EmojiHandler, ViSoLexNormalizer

def process_text_advanced(text):
    """Process text with multiple steps"""
    print(f"Original text: {text}")
    
    # Step 1: Emoji processing
    emoji_handler = EmojiHandler()
    emojis = emoji_handler.detect_emoji(text)
    print(f"Detected emojis: {emojis}")
    
    # Step 2: Basic normalization
    normalizer = BasicNormalizer()
    normalized = normalizer.basic_normalizer(text, case_folding=True)
    print(f"Basic normalized: {normalized}")
    
    # Step 3: Lexical normalization with deep learning
    lex_normalizer = ViSoLexNormalizer()
    final_normalized = lex_normalizer.normalize_sentence(text)
    print(f"Lexical normalized: {final_normalized}")
    
    return {
        'original': text,
        'emojis': emojis,
        'basic_normalized': normalized,
        'lexical_normalized': final_normalized
    }

# Test
result = process_text_advanced("Hôm nay tôi rất😊 VUI 😊😊 và HẠNH PHÚC!")
```

---

## 🌐 Resources

### HuggingFace Hub

All models and resources are published on HuggingFace Hub:

- **Organization**: [https://huggingface.co/visolex](https://huggingface.co/visolex)
- **Models**: View full list at [https://huggingface.co/visolex](https://huggingface.co/visolex)

**Available normalization models:**

- `visolex/visobert-normalizer-mix100` (default)


### GitHub Releases

Datasets are stored as GitHub Releases and automatically downloaded when used:

- **Repository**: [https://github.com/AnhHoang0529/visonorm](https://github.com/AnhHoang0529/visonorm)
- **Releases**: [https://github.com/AnhHoang0529/visonorm/releases](https://github.com/AnhHoang0529/visonorm/releases)


---

## 📝 Citation

If you use ViSoNorm in your research, please cite:

```bibtex

@article{nguyen_weakly_2025,
	title = {A {Weakly} {Supervised} {Data} {Labeling} {Framework} for {Machine} {Lexical} {Normalization} in {Vietnamese} {Social} {Media}},
	volume = {17},
	issn = {1866-9964},
	url = {https://doi.org/10.1007/s12559-024-10356-3},
	doi = {10.1007/s12559-024-10356-3},
	number = {1},
	journal = {Cognitive Computation},
	author = {Nguyen, Dung Ha and Nguyen, Anh Thi Hoang and Van Nguyen, Kiet},
	month = jan,
	year = {2025},
	pages = {57},
}

@inproceedings{nguyen-etal-2025-visolex,
    title = "{V}i{S}o{L}ex: An Open-Source Repository for {V}ietnamese Social Media Lexical Normalization",
    author = "Nguyen, Anh Thi-Hoang  and
      Nguyen, Dung Ha  and
      Nguyen, Kiet Van",
    editor = "Rambow, Owen  and
      Wanner, Leo  and
      Apidianaki, Marianna  and
      Al-Khalifa, Hend  and
      Eugenio, Barbara Di  and
      Schockaert, Steven  and
      Mather, Brodie  and
      Dras, Mark",
    booktitle = "Proceedings of the 31st International Conference on Computational Linguistics: System Demonstrations",
    month = jan,
    year = "2025",
    address = "Abu Dhabi, UAE",
    publisher = "Association for Computational Linguistics",
    url = "https://aclanthology.org/2025.coling-demos.18/",
    pages = "183--188",
}

```

---
## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

## 👥 Authors

- **Anh Thi-Hoang Nguyen** - *Maintainer* - [anhnth@uit.edu.vn](mailto:anhnth@uit.edu.vn)
- **Ha Dung Nguyen** - *Maintainer* - [dungngh@uit.edu.vn](mailto:dungngh@uit.edu.vn)

---

## 🙏 Acknowledgments

- HuggingFace for hosting models and providing the transformers library
- The Vietnamese NLP community for datasets and feedback

---

## 📞 Contact & Support

- **GitHub Issues**: [https://github.com/AnhHoang0529/visonorm/issues](https://github.com/AnhHoang0529/visonorm/issues)
- **Email**: anhnth@uit.edu.vn
- **HuggingFace**: [https://huggingface.co/visolex](https://huggingface.co/visolex)

---

## 🔗 Links

- **GitHub Repository**: [https://github.com/AnhHoang0529/visonorm](https://github.com/AnhHoang0529/visonorm)
- **PyPI Package**: [https://pypi.org/project/visonorm/](https://pypi.org/project/visonorm/)
- **HuggingFace Hub**: [https://huggingface.co/visolex](https://huggingface.co/visolex)
- **Documentation**: [https://github.com/AnhHoang0529/visonorm](https://github.com/AnhHoang0529/visonorm)
