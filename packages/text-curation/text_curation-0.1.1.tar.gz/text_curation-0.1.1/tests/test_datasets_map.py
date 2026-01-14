from text_curation._core.document import Document
from text_curation._blocks.normalization import NormalizationBlock

def normalize(text):
    doc = Document(text)
    NormalizationBlock().apply(doc)
    return doc.text

def text_unicode_and_whitespace():
    assert normalize("A\u00A0B") == "A B"

def test_quotes_and_dashes():
    assert normalize("“hello-world”") == '"hello-world"'

def test_zero__width_and_control_chars():
    assert normalize("a\u200bb\x07c") == "abc"

def test_newline_normalization():
    assert normalize("a\r\n\r\n\r\nb") == "a\n\nb"

def test_trim():
    assert normalize("  hello  ") == "hello"