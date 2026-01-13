# 🇪🇷 Tigrinya NLP Toolkit

Tigrinya NLP Toolkit is a lightweight, practical, and easy-to-use preprocessing library for Tigrinya text (Ethiopic/Ge'ez script).
It provides safe, transparent utilities for cleaning, normalization, tokenization, and stopword removal.

Perfect for research, machine learning, and NLP pipelines that need reliable Tigrinya preprocessing without aggressive or irreversible changes.

## 🌍 Why Tigrinya Needs Its Own NLP Toolkit

Tigrinya is morphologically rich and written in Ethiopic script.
General-purpose NLP tools often struggle with:

- Ethiopic punctuation and spacing
- Unicode normalization inconsistencies
- Script-specific word boundaries
- Mixed-script or noisy social text

This toolkit provides a conservative, language-aware preprocessing pipeline built specifically for Tigrinya.

## ⚙️ What Is tigrinya-nlp?

tigrinya-nlp is a modular Python package for end-to-end Tigrinya preprocessing.

### 🧩 Core Components
- Cleaner: removes URLs, emojis, mentions, hashtags, and repeated punctuation (configurable)
- Normalizer: Unicode NFC, invisible character removal, punctuation spacing, whitespace fixes
- Tokenizer: sentence and word tokenization with Ethiopic-aware punctuation rules
- Stopword Processor: curated stopword lists with configurable categories

### ✅ Intentionally Out of Scope (for now)
- Stemming
- Lemmatization
- Spell correction
- Morphological analysis

## 📦 Installation

Option 1: Install from PyPI (Recommended)
```bash
pip install tigrinya-nlp
```

Option 2: Install Latest Development Version
```bash
git clone https://github.com/makda-tsegazeab/tigrinya-nlp.git
cd tigrinya-nlp
pip install .
```

## 🧪 Full Demo: End-to-End Tigrinya Text Preprocessing

```python
from tigrinya_nlp import clean, normalize, words, remove_stopwords

sample_text = "ዝተረፈ ጽሑፍ ብቕልጡፍ ንኣብዚ ልኣኹ https://example.com 😄"

# Step 1: Cleaning
cleaned = clean(sample_text)

# Step 2: Normalization (conservative)
normalized = normalize(cleaned)

# Step 3: Tokenization
tokens = words(normalized)

# Step 4: Stopword removal (optional)
filtered = remove_stopwords(tokens)

print(filtered)
```

## 🧭 Step-by-Step Usage

### 🧹 Step 1: Cleaning
```python
from tigrinya_nlp import clean, CleaningConfig

text = "Visit https://example.com ኣብዚ 😄 @user #topic"
cleaned = clean(text)

# Social media-friendly policy (keeps emojis/hashtags)
social = clean(text, config=CleaningConfig.social_media())
```
✔️ URLs removed ✔️ emojis/hashtags configurable

### 🔤 Step 2: Normalization
```python
from tigrinya_nlp import normalize

text = "ማሕበራዊ ሚዲያ (ፌስቡክ፣ ትዊተር፣ ቴሌግራም) ዝተለጠፈ ጽሑፍ ንኹሉ ይበጽሕ። ግን ብኸመይ?"
conservative = normalize(text)
linguistic = normalize(text, mode="linguistic")
```
✔️ Standardized Unicode ✔️ clean punctuation spacing

### 🧩 Step 3: Tokenization
```python
from tigrinya_nlp import sentences, words

text = "እዚ መዓዝ ኮይኑ? ዝገርም ነገር !"
print(sentences(text))
print(words(text))
```
✔️ Sentence + word tokens with Ethiopic-aware rules

### 🪶 Step 4: Stopword Removal
```python
from tigrinya_nlp import remove_stopwords, StopwordConfig

tokens = ["እዚ", "ጽሑፍ", "እዩ", "።"]
minimal = remove_stopwords(tokens)
topic = remove_stopwords(tokens, config=StopwordConfig.topic_modeling())
```
✔️ Removes high-frequency filler words (configurable)

## 🧾 Module Summary

| Step | Module | Purpose |
| --- | --- | --- |
| 1 | Cleaning | Removes URLs, emojis, mentions, hashtags, repeated punctuation |
| 2 | Normalization | Unicode NFC, control chars, punctuation spacing, whitespace |
| 3 | Tokenization | Sentence + word tokens with Ethiopic-aware rules |
| 4 | Stopwords | Configurable removal with protected negation |

## 🧠 Design Philosophy

- Conservative by default
- Script-aware, not model-driven
- Explicit, documented normalization mappings
- Pure Python, minimal dependencies

## 🧪 Testing

```bash
pytest
```

## 📜 License

MIT License

## ✍️ Author

Makda Tsegazeab Mammo
