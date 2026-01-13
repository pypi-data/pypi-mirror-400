def test_import_package():
    import tigrinya_nlp
    assert tigrinya_nlp is not None


def test_public_api():
    from tigrinya_nlp import (
        CleaningConfig,
        StopwordConfig,
        clean,
        normalize,
        remove_stopwords,
        sentences,
        stopwords_for_config,
        words,
    )

    assert callable(clean)
    assert callable(normalize)
    assert callable(sentences)
    assert callable(words)
    assert callable(remove_stopwords)
    assert callable(stopwords_for_config)
    assert CleaningConfig is not None
    assert StopwordConfig is not None
