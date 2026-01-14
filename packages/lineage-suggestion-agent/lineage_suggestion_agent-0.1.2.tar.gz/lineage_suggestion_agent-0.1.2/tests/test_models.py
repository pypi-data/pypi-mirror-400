import pytest
from pydantic import ValidationError
from lineage_suggestion_agent.models import LineageSuggestion

def test_lineage_suggestion_success():
    """Test successful creation of LineageSuggestion."""
    suggestion_text = "This is a test suggestion."
    suggestion = LineageSuggestion(answer=suggestion_text)
    assert suggestion.answer == suggestion_text

def test_lineage_suggestion_missing_field():
    """Test that LineageSuggestion raises an error if 'answer' is missing."""
    with pytest.raises(ValidationError):
        LineageSuggestion()

def test_lineage_suggestion_incorrect_type():
    """Test that LineageSuggestion raises an error for incorrect data type."""
    with pytest.raises(ValidationError):
        LineageSuggestion(answer=123)
