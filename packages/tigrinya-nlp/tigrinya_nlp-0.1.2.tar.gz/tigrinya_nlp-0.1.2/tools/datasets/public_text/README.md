# Public Text Validation (v1)

This directory describes how to obtain public-text corpora for **development-time**
validation of `tigrinya-nlp` (normalization + tokenization).

## What this is used for (v1)
We use public text to:
- spot-check that normalization rules do not corrupt valid Ethiopic text
- verify tokenization boundaries for Ethiopic punctuation (e.g., ። ፣ ፤ ፦ ፡)
- verify that quotation decisions are respected (e.g., « » are treated as quotations)
- check that punctuation-only tokens remain unchanged

## What this is NOT used for
- training models
- claiming full coverage of the language
- shipping any corpora inside the package

## Local storage (not committed)
Downloaded corpora must be stored locally at:

`data/external/public_text/`

Suggested structure:
- `data/external/public_text/wikipedia/`
- `data/external/public_text/tatoeba/`

## Reproducibility
Record the download date and exact filenames in `VALIDATION_NOTES.md`.
Use `CHECKLIST.md` as a phase gate to ensure the process is repeatable.
