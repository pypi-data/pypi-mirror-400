# Wiktionary Dataset Usage (Tigrinya)

This directory documents how Wiktionary-derived resources are
used to validate the `tigrinya-nlp` library.

## Purpose in v1

In version 1, Wiktionary data is used only for:

- Spot-checking that normalization rules do not collapse
  distinct Tigrinya words incorrectly.
- Spot-checking tokenization decisions
  (e.g., apostrophes, punctuation boundaries, intra-token symbols).
- Providing real lexical examples for manual linguistic inspection.

## Not used for

- Training machine learning models
- Claiming full language coverage
- Building or shipping a lexicon
- Automatic evaluation or benchmarking

## Distribution

No Wiktionary-derived data is included in this repository.
Users must download data themselves if they wish to reproduce validation.
