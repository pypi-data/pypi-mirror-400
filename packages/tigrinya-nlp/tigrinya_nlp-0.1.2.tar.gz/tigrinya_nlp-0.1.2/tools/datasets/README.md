# Dataset & Lexicon Tooling

This project does **not** ship datasets.

Instead, this directory documents how external linguistic resources can be
**obtained, prepared, and used reproducibly** to evaluate and extend the
`tigrinya-nlp` preprocessing pipeline.

This design choice keeps the library lightweight, avoids licensing issues,
and allows users and researchers to bring their own data.

---

## Why datasets matter for this library

The library implements deterministic linguistic operations such as:

- Tigrinya-specific text cleaning
- Unicode and linguistic normalization
- Tokenization and sentence segmentation
- Stopword filtering

To validate that these operations behave correctly on **real language**, we
need reference linguistic resources (e.g., word lists, text samples, examples).

This folder provides **instructions**, not bundled data.

---

## Supported resource types

### 1. Lexical resources (word-level)
Used to:
- sanity-check normalization
- ensure tokenization does not break valid words
- support future lexicon-aware features

Examples:
- Wiktionary / Kaikki Tigrinya dictionaries
- Frequency-based word lists (optional)

See: `wiktionary/`

---

### 2. Public text corpora (sentence-level)
Used to:
- validate sentence boundary detection
- test punctuation and quotation handling
- evaluate real-world formatting

Examples:
- Tigrinya Wikipedia
- Public news or institutional texts

See: `public_text/`

---

### 3. Hand-curated gold examples
Used to:
- define expected behavior precisely
- prevent regressions across versions
- encode linguistic edge cases explicitly

See: `examples/`

---

## Local data layout (recommended)

Raw data (downloaded by the user):
