import pytest

from tigrinya_nlp.stopwords import StopwordConfig, remove_stopwords, stopwords_for_config


def test_minimal_default_removes_only_function_words():
    cfg = StopwordConfig.minimal()
    sw = stopwords_for_config(cfg)

    # default includes function words
    assert "ኣብ" in sw
    assert "እና" in sw
    assert "እዩ" in sw

    # default does NOT include demonstratives/pronouns/question words/focus
    assert "እዚ" not in sw
    assert "ኣነ" not in sw
    assert "እንታይ" not in sw
    assert "ጥራይ" not in sw


def test_negation_is_protected_in_minimal():
    cfg = StopwordConfig.minimal()
    tokens = ["ኣይ", "እዩ", "ኣብ", "ቤት"]
    out = remove_stopwords(tokens, config=cfg)
    # 'እዩ' and 'ኣብ' removed, but negation preserved
    assert out == ["ኣይ", "ቤት"]


def test_minimal_does_not_remove_demonstratives_by_default():
    cfg = StopwordConfig.minimal()
    tokens = ["እዚ", "ቤት", "እዩ"]
    out = remove_stopwords(tokens, config=cfg)
    assert out == ["እዚ", "ቤት"]


def test_topic_modeling_removes_demonstratives_and_focus():
    cfg = StopwordConfig.topic_modeling()
    tokens = ["እዚ", "ቤት", "ጥራይ", "እዩ"]
    out = remove_stopwords(tokens, config=cfg)
    assert out == ["ቤት"]


def test_qa_sensitive_keeps_question_words():
    cfg = StopwordConfig.qa_sensitive()
    tokens = ["እንታይ", "እዩ", "ኣብ", "ቤት", "?"]
    out = remove_stopwords(tokens, config=cfg)
    # remove only function words (እዩ, ኣብ), keep question word and punctuation
    assert out == ["እንታይ", "ቤት", "?"]


def test_keep_punctuation_false_removes_punct_tokens():
    cfg = StopwordConfig.minimal(keep_punctuation=False)
    tokens = ["ኣብ", "ቤት", "።", "እዩ"]
    out = remove_stopwords(tokens, config=cfg)
    assert out == ["ቤት"]


def test_extra_stopwords_supported():
    cfg = StopwordConfig.minimal(extra_stopwords={"ቤት"})
    tokens = ["ኣብ", "ቤት", "እዩ"]
    out = remove_stopwords(tokens, config=cfg)
    assert out == []


def test_short_forms_in_function_words():
    cfg = StopwordConfig.minimal()
    tokens = ["'ያ", "'ዮም", "ቤት"]
    out = remove_stopwords(tokens, config=cfg)
    assert out == ["ቤት"]


def test_custom_can_remove_pronouns_if_user_enables():
    cfg = StopwordConfig.custom(remove_pronouns=True)
    tokens = ["ኣነ", "ኣብ", "ቤት"]
    out = remove_stopwords(tokens, config=cfg)
    assert out == ["ቤት"]


def test_custom_still_protects_negation_by_default():
    cfg = StopwordConfig.custom(remove_demonstratives=True, remove_pronouns=True, remove_question_words=True)
    tokens = ["ኣይ", "እዚ", "ኣብ", "ቤት"]
    out = remove_stopwords(tokens, config=cfg)
    assert out == ["ኣይ", "ቤት"]


def test_allow_remove_protected_is_explicit():
    cfg = StopwordConfig.custom(
        remove_function_words=True,
        extra_stopwords={"ኣይ"},
        allow_remove_protected=True,  # explicit override
        protected_words={"ኣይ"},
    )
    tokens = ["ኣይ", "ኣብ", "ቤት"]
    out = remove_stopwords(tokens, config=cfg)
    # now 'ኣይ' can be removed
    assert out == ["ቤት"]


def test_error_on_non_string_token():
    cfg = StopwordConfig.minimal()
    with pytest.raises(TypeError):
        remove_stopwords(["ቤት", 123], config=cfg)  # type: ignore
