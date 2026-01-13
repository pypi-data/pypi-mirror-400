from tigrinya_nlp.normalization import normalize


def test_idempotence():
    text = "ኣበበ፦ \"ከመይ ኢኻ?\""
    out = normalize(text)

    # normalization should be idempotent
    assert normalize(out) == out


def test_traditional_question_mark_normalized():
    text = "ንስኻ ከመይ ኢኻ፧"
    out = normalize(text)

    assert "?" in out
    assert "፧" not in out
    assert out.endswith("?")


def test_mixed_question_marks():
    text = "እዚ ጽቡቕ እዩ፧ ወይ ኣይኮነን?"
    out = normalize(text)

    # both questions should use '?'
    assert "፧" not in out
    assert out.count("?") == 2


def test_colon_and_preface_preserved():
    text = "ዝስዕብ ነገራት፥ ሻይ፣ ቡና እና ማይ።"
    out = normalize(text)

    assert "፥" in out
    assert "፣" in out
    assert "።" in out


def test_preface_colon_spacing():
    text = "ኣበበ፦\"ክመጽእ እየ\""
    out = normalize(text)

    # ensure spacing after preface colon
    assert "፦ " in out


def test_sarcasm_mark_preserved():
    text = "ብጣዕሚ ጎበዝ እዩ¡"
    out = normalize(text)

    assert "¡" in out


def test_slash_preserved_for_abbreviation():
    text = "ዶ/ር ሰለሞን ኣብ ቤት እዩ።"
    out = normalize(text)

    assert "/" in out
    assert "ዶ/ር" in out


def test_whitespace_normalization():
    text = "ኣብ   ቤት።ንስኻ\t\tከመይ ኢኻ?"
    out = normalize(text)

    # no repeated spaces
    assert "  " not in out

    # space after sentence terminator when text follows
    assert "። " in out

    # question mark at end should not force trailing space
    assert out.endswith("?")
