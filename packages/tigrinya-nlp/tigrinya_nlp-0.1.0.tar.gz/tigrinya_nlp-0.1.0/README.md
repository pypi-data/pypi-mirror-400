# Tigrinya-NLP

> A lightweight, conservative preprocessing toolkit for Tigrinya (Geʽez script) text.

Tigrinya-NLP provides carefully designed utilities for cleaning, normalization, tokenization, and stopword handling of Tigrinya text.
The library prioritizes linguistic safety, transparency, and reproducibility, making it suitable for downstream NLP tasks without introducing aggressive or opaque transformations.

## ✨ Design Principles

This project is guided by the following principles:

- Conservative by default
- No stemming, lemmatization, or morphological rewriting unless explicitly enabled.

- Script-aware, not model-driven
- Handles Ethiopic punctuation, spacing, and Unicode normalization correctly.

- Explicit normalization choices
- All linguistic mappings are documented, directional, and reversible in intent.

- Tool, not dataset
- This library does not ship corpora or lexicons; it documents how to validate against external resources.

- Low dependency footprint
- Pure Python, no Java, no native extensions, no heavy NLP frameworks.

## 📦 Features (v1)
- 1. Cleaning

- Remove URLs, emojis, and control characters

- Handle mixed-script text safely

- Preserve readable content and line structure

- 2. Unicode & Canonical Normalization

- Unicode normalization (NFC)

- Removal of invisible Unicode characters

- Canonical punctuation spacing

- Whitespace normalization

- Ethiopic question mark (፧ → ?)

- 3. Linguistic Normalization (Optional)

Directional, order-preserving mappings only:

- ሠ-family → ሰ-family

- ጸ-family → ፀ-family

- ኀ-family → ሀ-family

- ❌ No vowel collapsing
- ❌ No morphological changes
- ❌ No phonetic normalization

- 4. Tokenization

- Sentence segmentation

- Word tokenization

- Ethiopic and ASCII punctuation aware

- 5. Stopword Handling (Optional)

- Curated Tigrinya stopword list

- User-extensible

- Applied only when explicitly requested

## 🚫 Explicitly Out of Scope (v1)

To maintain safety and correctness, the following are not included in this version:

- ❌ Stemming

- ❌ Lemmatization

- ❌ Spell correction

- ❌ Morphological analysis

- ❌ Language modeling

- ❌ Dataset redistribution

These may be explored in future versions.

## 🧠 Why Conservative Processing?

Tigrinya is a morphologically rich, low-resource language.
Aggressive normalization (stemming, lemmatization) can:

- Destroy semantic distinctions

- Break proper nouns and loanwords

- Introduce irreversible errors

This library therefore focuses on safe preprocessing layers that improve consistency without changing meaning.

## 📂 Project Structure

```text
tigrinya-nlp/
│
├── src/
│   └── tigrinya_nlp/
│       ├── __init__.py
│       ├── cleaning.py
│       ├── normalization.py
│       ├── tokenization.py
│       ├── stopwords.py
│
├── tests/
│   ├── test_imports.py
│   ├── test_normalization.py
│   ├── test_tokenization.py
│   └── test_cleaning.py
│
├── tools/
│   └── datasets/
│       └── wiktionary/
│           ├── SOURCES.md
│           ├── CHECKLIST.md
│           └── validation_notes.md
│
├── README.md
├── pyproject.toml
└── .gitignore

```

## 🛠 Installation

```bash
pip install tigrinya-nlp
```



or for development:


```bash
pip install -e .
```

## 🚀 Usage Examples

### Normalize text (conservative)

```python
from tigrinya_nlp import normalize

text = "ሠብ ፧ ኣሎ"
print(normalize(text))

```

### Linguistic normalization

```python
normalize(text, mode="linguistic")

```

### Cleaning

```python
from tigrinya_nlp import clean

cleaned = clean("Visit https://example.com ሰብ 😊")

```

### Tokenization

```python
from tigrinya_nlp import sentences, words

sentences(text)
words(text)

```

### Stopword removal

```python
from tigrinya_nlp import remove_stopwords

remove_stopwords(words(text))

```
## 🧪 Testing

```bash
pytest
```


All public APIs are covered by tests to ensure stability across versions.

## 📚 Dataset & Validation Philosophy

This project does not ship datasets.

Instead, it documents:

- How to obtain external linguistic resources (e.g., Wiktionary via Kaikki)

- How to manually and reproducibly validate preprocessing behavior

- How to sanity-check normalization and tokenization decisions

See:

tools/datasets/wiktionary/


This approach ensures:

- Reproducibility

- Licensing safety

- Research credibility

## 📜 License

MIT License

This repository documents how to access external linguistic resources but does not redistribute them.
External resources (e.g., Wiktionary) are governed by their own licenses (typically CC BY-SA).

## 🧭 Roadmap (Future Work)

Potential future phases:

- Optional conservative stemmer (rule-gated)

- Spell-checking utilities

- Evaluation scripts

- Dataset adapters (user-side)

- CLI tools

All future features will maintain the conservative, transparent design philosophy.

## 👤 Author

Developed as part of a research-oriented effort to improve tooling for under-resourced languages, with an emphasis on correctness, safety, and long-term extensibility.
