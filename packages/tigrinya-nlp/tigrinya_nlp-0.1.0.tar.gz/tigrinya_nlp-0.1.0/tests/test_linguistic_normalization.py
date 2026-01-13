from tigrinya_nlp.normalization import normalize, normalize_tigrinya_letters


def test_sa_family_normalization_to_se_family():
    # ሠ-family should normalize to ሰ-family (same order mapping)
    text = "ሠ ሡ ሢ ሣ ሤ ሥ ሦ"
    out = normalize_tigrinya_letters(text)
    assert out == "ሰ ሱ ሲ ሳ ሴ ስ ሶ"


def test_tsa_family_normalization_to_psa_family():
    # ጸ-family should normalize to ፀ-family (same order mapping)
    text = "ጸጹጺጻጼጽጾ"
    out = normalize_tigrinya_letters(text)
    assert out == "ፀፁፂፃፄፅፆ"


def test_kha_family_normalization_to_ha_family():
    # ኀ-family should normalize to ሀ-family (same order mapping)
    text = "ኀኁኂኃኄኅኆ"
    out = normalize_tigrinya_letters(text)
    assert out == "ሀሁሂሃሄህሆ"


def test_ha_family_preserved():
    # Canonical forms should remain unchanged
    text = "ሀሁሂሃሄህሆ"
    out = normalize_tigrinya_letters(text)
    assert out == text


def test_hha_family_not_normalized():
    # ሐ is distinct and must NOT be changed
    # (and we do not touch the ሐ-family at all)
    text = "ሐሑሒሓሔሕሖ"
    out = normalize_tigrinya_letters(text)
    assert out == text


def test_linguistic_mode_applies_letter_normalization():
    # linguistic mode should apply the family mappings
    text = "ጸብሓን ኀብሪ ሠኒ"
    out = normalize(text, mode="linguistic")
    assert "ጸ" not in out
    assert "ኀ" not in out
    assert "ሠ" not in out
    assert "ፀ" in out
    assert "ሀ" in out
    assert "ሰ" in out


def test_conservative_mode_does_not_apply_letter_normalization():
    text = "ጸብሓን ኀብሪ ሠኒ"
    out = normalize(text, mode="conservative")
    assert out == text


def test_linguistic_normalization_is_idempotent():
    text = "ሠብ ጸብሓን ኀብሪ"
    once = normalize(text, mode="linguistic")
    twice = normalize(once, mode="linguistic")
    assert once == twice


def test_question_mark_canonicalization_still_applies_in_linguistic_mode():
    text = "ንስኻ ከመይ ኢኻ፧ ሠኒ እዩ"
    out = normalize(text, mode="linguistic")
    assert "?" in out
    assert "፧" not in out
