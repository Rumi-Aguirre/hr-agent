"""Tests for the InformationExtractionChain class."""

import pytest
from unittest.mock import Mock, patch, MagicMock
from src.agent.extraction_chain import InformationExtractionChain
from src.agent.models.extracted_info_model import ExtractedInfo

@pytest.fixture
def mock_dependencies():
    """Create patches for all external dependencies."""
    mock_llm = Mock(name="mock_llm")
    mock_chain = Mock(name="mock_chain")
    mock_parser = Mock(name="mock_parser")
    
    # Configure chain mock
    mock_chain.run.return_value = '{"first_name": "Juan", "age": 25, "preferred_schedule": "mañana"}'
    
    # Configure parser mock
    mock_parser.parse.return_value = ExtractedInfo(
        first_name="Juan",
        age=25,
        preferred_schedule="mañana"
    )
    mock_parser.get_format_instructions.return_value = "format instructions"
    
    with patch.multiple('src.agent.extraction_chain', 
                       Ollama=Mock(return_value=mock_llm),
                       LLMChain=Mock(return_value=mock_chain),
                       PydanticOutputParser=Mock(return_value=mock_parser)):
        yield {
            'llm': mock_llm,
            'chain': mock_chain,
            'parser': mock_parser
        }

@pytest.fixture
def extraction_chain(mock_dependencies):
    """Create an InformationExtractionChain instance with mocked dependencies."""
    return InformationExtractionChain()

class TestInformationExtractionChain:
    """Test cases for InformationExtractionChain."""

    def test_initialization(self, extraction_chain, mock_dependencies):
        """Test that InformationExtractionChain initializes correctly."""
        assert extraction_chain.llm is mock_dependencies['llm']
        assert extraction_chain.parser is mock_dependencies['parser']
        assert extraction_chain.chain is mock_dependencies['chain']

    class TestExtractedInfoValidation:
        """Test cases for extracted info validation."""

        def test_valid_complete_info(self, extraction_chain):
            """Test validation of complete valid information."""
            info = ExtractedInfo(
                first_name="Juan",
                age=25,
                preferred_schedule="mañana"
            )
            text = "me llamo Juan, tengo 25 años y prefiero el turno mañana"
            
            validated = extraction_chain._validate_extracted_info(info, text)
            assert validated == {
                "first_name": "Juan",
                "age": 25,
                "preferred_schedule": "mañana"
            }

        def test_valid_partial_info(self, extraction_chain):
            """Test validation of partial valid information."""
            info = ExtractedInfo(
                first_name="Juan",
                age=25
            )
            text = "me llamo Juan y tengo 25 años"
            
            validated = extraction_chain._validate_extracted_info(info, text)
            assert validated == {
                "first_name": "Juan",
                "age": 25
            }

    class TestExtraction:
        """Test cases for the main extract method."""

        def test_empty_input(self, extraction_chain):
            """Test extraction with empty input."""
            assert extraction_chain.extract("") == {}
            assert extraction_chain.extract("  ") == {}
            assert extraction_chain.extract("a") == {}

        def test_successful_extraction(self, extraction_chain, mock_dependencies):
            """Test successful information extraction."""
            text = "me llamo Juan, tengo 25 años y prefiero el turno mañana"
            result = extraction_chain.extract(text)
            
            mock_dependencies['chain'].run.assert_called_once_with(input=text)
            mock_dependencies['parser'].parse.assert_called_once()
            
            assert result == {
                "first_name": "Juan",
                "age": 25,
                "preferred_schedule": "mañana"
            }

        def test_extraction_with_parser_error(self, extraction_chain, mock_dependencies):
            """Test extraction when parser fails."""
            mock_dependencies['parser'].parse.side_effect = ValueError("Invalid format")
            
            result = extraction_chain.extract("some text")
            assert result == {} 