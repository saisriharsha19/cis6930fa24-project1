import pytest
import spacy, sys, os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from redactor import redact_names, redact_dates, redact_phones, redact_addresses, redact_concept
import en_core_web_lg


nlp = en_core_web_lg.load()

@pytest.fixture
def doc():
    text = "John Doe visited New York on March 10, 2022. Call him at +1 123-456-7890."
    return nlp(text)

def test_redact_names(doc):
    result = redact_names(doc)
    assert "John Doe" not in result
    assert "█" in result

def test_redact_dates(doc):
    result = redact_dates(doc)
    assert "March 10, 2022" not in result
    assert "█" in result

def test_redact_phones():
    text = "Call me at +1 800-555-1234."
    result = redact_phones(text)
    assert "+1 800-555-1234" not in result
    assert "█" in result

def test_redact_addresses(doc):
    result = redact_addresses(doc.text, doc)
    assert "New York" not in result
    assert "█" in result

def test_redact_concept(doc):
    concept = "visit"
    result, count = redact_concept(doc, concept)
    assert "visited" not in result
    assert count == 2
    assert "█" in result
