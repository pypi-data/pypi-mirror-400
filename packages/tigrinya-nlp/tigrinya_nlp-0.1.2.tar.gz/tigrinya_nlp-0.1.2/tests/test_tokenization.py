import pytest

from tigrinya_nlp.tokenization import sentences, words


def test_sentences_basic_boundaries():
    text = "ኣብ ቤት እየ። ንስኻ ከመይ ኢኻ? ጽቡቕ!"
    out = sentences(text)
    assert out == ["ኣብ ቤት እየ።", "ንስኻ ከመይ ኢኻ?", "ጽቡቕ!"]


def test_sentences_dot_not_boundary():
    text = "ቁ. 1 ኣብ ዝርዝር ኣሎ። ካልእ ኣሎ?"
    out = sentences(text)
    assert out == ["ቁ. 1 ኣብ ዝርዝር ኣሎ።", "ካልእ ኣሎ?"]


def test_words_punctuation_separated():
    text = "ኣብ ቤት። ንስኻ ከመይ ኢኻ?"
    out = words(text)
    assert out == ["ኣብ", "ቤት", "።", "ንስኻ", "ከመይ", "ኢኻ", "?"]


def test_words_slash_abbreviation_preserved():
    text = "ዶ/ር ሰለሞን ኣብ ቤት እዩ።"
    out = words(text)
    assert "ዶ/ር" in out
    assert "/" not in out  # slash should not be separated as its own token


def test_words_apostrophe_preserved_inside_token():
    # Decision: apostrophe is intra-token punctuation, like English contractions.
    text = "don't won't I'm"
    out = words(text)
    assert "don't" in out
    assert "won't" in out
    assert "I'm" in out
    assert "'" not in out  # apostrophe should not be separated as its own token


def test_words_word_separator_splits_words():
    text = "ኣብ፡ቤት፡እዩ።"
    out = words(text)
    assert out == ["ኣብ", "ቤት", "እዩ", "።"]


def test_words_word_separator_preserved_in_time():
    text = "ሰዓት 08፡30 እዩ።"
    out = words(text)
    assert "08፡30" in out
    assert "08" not in out
    assert "30" not in out


def test_words_guillemets_as_quotes_separated():
    text = "ኣበበ፦ «ከመይ ኢኻ?»"
    out = words(text)
    assert "«" in out
    assert "»" in out
    assert "?" in out
    assert "ከመይ" in out
    assert "ኢኻ" in out


def test_type_error_on_non_string():
    with pytest.raises(TypeError):
        words(123)  # type: ignore
    with pytest.raises(TypeError):
        sentences(123)  # type: ignore
