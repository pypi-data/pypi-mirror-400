import pytest

from tigrinya_nlp.cleaning import CleaningConfig, clean


# ------------------------------------------------------------
# Default / research behavior
# ------------------------------------------------------------

def test_research_default_removes_emojis():
    text = "ብጣዕሚ ጽቡቕ እዩ 😀🔥"
    out = clean(text)
    assert "😀" not in out
    assert "🔥" not in out


def test_research_default_removes_urls():
    text = "እዚ https://example.com እዩ።"
    out = clean(text)
    assert "http" not in out


# ------------------------------------------------------------
# Social media preset
# ------------------------------------------------------------

def test_social_media_preserves_emojis():
    text = "ብጣዕሚ ጽቡቕ እዩ 😀🔥"
    cfg = CleaningConfig.social_media()
    out = clean(text, config=cfg)
    assert "😀" in out
    assert "🔥" in out


def test_social_media_preserves_mentions_and_hashtags():
    text = "@user እዚ #ጉዳይ ኣገዳሲ እዩ።"
    cfg = CleaningConfig.social_media()
    out = clean(text, config=cfg)
    assert "@user" in out
    assert "#ጉዳይ" in out


def test_social_media_preserves_repeated_punctuation():
    text = "እዚ ጽቡቕ እዩ!!!!!"
    cfg = CleaningConfig.social_media()
    out = clean(text, config=cfg)
    assert "!!!!!" in out


# ------------------------------------------------------------
# Emotion-aware preset
# ------------------------------------------------------------

def test_emotion_aware_preserves_emojis_and_emphasis():
    text = "ብጣዕሚ ጽቡቕ እዩ 😀🔥!!!"
    cfg = CleaningConfig.emotion_aware()
    out = clean(text, config=cfg)

    assert "😀" in out
    assert "🔥" in out
    assert "!!!" in out


def test_emotion_aware_removes_mentions():
    text = "@user ብጣዕሚ ጽቡቕ እዩ 😀"
    cfg = CleaningConfig.emotion_aware()
    out = clean(text, config=cfg)

    assert "@user" not in out
    assert "😀" in out


def test_emotion_aware_preserves_hashtags():
    text = "ብጣዕሚ ጽቡቕ እዩ #ሓጎስ"
    cfg = CleaningConfig.emotion_aware()
    out = clean(text, config=cfg)

    assert "#ሓጎስ" in out


# ------------------------------------------------------------
# Formal text preset
# ------------------------------------------------------------

def test_formal_text_removes_noise():
    text = "@user ብጣዕሚ ጽቡቕ እዩ 😀 https://example.com"
    cfg = CleaningConfig.formal_text()
    out = clean(text, config=cfg)

    assert "@user" not in out
    assert "😀" not in out
    assert "http" not in out


def test_formal_text_collapses_punctuation():
    text = "እዚ ጽቡቕ እዩ!!!!!"
    cfg = CleaningConfig.formal_text()
    out = clean(text, config=cfg)
    assert "!!" not in out
    assert "!" in out


# ------------------------------------------------------------
# Language-sensitive invariants
# ------------------------------------------------------------

def test_slash_abbreviation_preserved():
    text = "ዶ/ር ሰለሞን ኣብ ቤት እዩ።"
    out = clean(text)
    assert "ዶ/ር" in out


def test_numbers_and_latin_preserved():
    text = "Meeting 2024 ኣብ Addis Ababa"
    out = clean(text)
    assert "2024" in out
    assert "Addis" in out


def test_whitespace_cleanup_after_removals():
    text = "እዚ 😀   https://example.com   እዩ።"
    out = clean(text)
    assert "  " not in out
    assert out.startswith("እዚ")
    assert out.endswith("እዩ።")


# ------------------------------------------------------------
# Error handling
# ------------------------------------------------------------

def test_type_error_on_non_string():
    with pytest.raises(TypeError):
        clean(123)  # type: ignore
