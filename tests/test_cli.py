"""
Tests for CLI interface.
"""

from unittest.mock import Mock, patch

import pytest

from gs2txt.cli import create_parser, main

# ============================================
# Test Argument Parser
# ============================================


def test_create_parser():
    """Test argument parser creation."""
    parser = create_parser()
    args = parser.parse_args([
        "--input", "test.csv",
        "--output", "out.csv",
        "--api-key", "sk-test"
    ])

    assert args.input == "test.csv"
    assert args.output == "out.csv"
    assert args.api_key == "sk-test"


def test_parser_defaults():
    """Test default argument values."""
    parser = create_parser()
    args = parser.parse_args([
        "--input", "test.csv",
        "--output", "out.csv"
    ])

    assert args.provider == "openai"
    assert args.model == "gpt-4"
    assert args.temperature == 0.0
    assert args.max_genes == 60
    assert args.max_pathways == 10
    assert args.enrichment == "pathway"


def test_parser_all_arguments():
    """Test parser with all arguments."""
    parser = create_parser()
    args = parser.parse_args([
        "--input", "test.csv",
        "--output", "out.csv",
        "--provider", "anthropic",
        "--api-key", "sk-ant-test",
        "--model", "claude-3",
        "--temperature", "0.5",
        "--max-genes", "100",
        "--max-pathways", "15",
        "--enrichment", "none",
        "--group-by", "cluster"
    ])

    assert args.provider == "anthropic"
    assert args.api_key == "sk-ant-test"
    assert args.model == "claude-3"
    assert args.temperature == 0.5
    assert args.max_genes == 100
    assert args.max_pathways == 15
    assert args.enrichment == "none"
    assert args.group_by == "cluster"


# ============================================
# Test Main CLI Function
# ============================================


@patch("gs2txt.cli.BatchProcessor")
@patch("gs2txt.cli.OpenAIProvider")
@patch("sys.argv", ["gs2txt", "--input", "test.csv", "--output", "out.csv", "--api-key", "sk-test"])
def test_main_basic(mock_provider_class, mock_processor_class):
    """Test main CLI entry point with basic arguments."""
    mock_provider = Mock()
    mock_provider_class.return_value = mock_provider

    mock_processor = Mock()
    mock_processor_class.return_value = mock_processor

    main()

    # Verify provider was created
    mock_provider_class.assert_called_once()
    call_kwargs = mock_provider_class.call_args[1]
    assert call_kwargs["api_key"] == "sk-test"
    assert call_kwargs["model_id"] == "gpt-4"

    # Verify processor was called
    mock_processor.process_single_file.assert_called_once()


@patch("gs2txt.cli.AnthropicProvider")
@patch("sys.argv", [
    "gs2txt",
    "--input", "test.csv",
    "--output", "out.csv",
    "--provider", "anthropic",
    "--api-key", "sk-ant-test"
])
def test_main_anthropic_provider(mock_provider_class):
    """Test CLI with Anthropic provider."""
    mock_provider = Mock()
    mock_provider_class.return_value = mock_provider

    with patch("gs2txt.cli.BatchProcessor"):
        main()

    mock_provider_class.assert_called_once()


@patch("gs2txt.cli.LiteLLMProvider")
@patch("sys.argv", [
    "gs2txt",
    "--input", "test.csv",
    "--output", "out.csv",
    "--provider", "litellm",
    "--api-key", "sk-test"
])
def test_main_litellm_provider(mock_provider_class):
    """Test CLI with LiteLLM provider."""
    mock_provider = Mock()
    mock_provider_class.return_value = mock_provider

    with patch("gs2txt.cli.BatchProcessor"):
        main()

    mock_provider_class.assert_called_once()


@patch("sys.argv", ["gs2txt", "--input", "test.csv", "--output", "out.csv"])
def test_main_missing_api_key():
    """Test error when API key is missing."""
    with pytest.raises(SystemExit) as exc_info:
        main()

    assert exc_info.value.code == 1


@patch("gs2txt.cli.OpenAIProvider")
@patch("sys.argv", [
    "gs2txt",
    "--input", "test.csv",
    "--output", "out.csv",
    "--api-key", "sk-test",
    "--group-by", "cluster"
])
def test_main_with_grouping(mock_provider_class):
    """Test CLI with group-by parameter."""
    mock_provider = Mock()
    mock_provider_class.return_value = mock_provider

    with patch("gs2txt.cli.BatchProcessor") as mock_processor_class:
        mock_processor = Mock()
        mock_processor_class.return_value = mock_processor

        main()

        # Verify group_column was passed
        call_kwargs = mock_processor.process_single_file.call_args[1]
        assert call_kwargs["group_column"] == "cluster"


@patch("gs2txt.cli.OpenAIProvider")
@patch("sys.argv", [
    "gs2txt",
    "--input", "test.csv",
    "--output", "out.csv",
    "--api-key", "sk-test",
    "--max-genes", "100",
    "--max-pathways", "20"
])
def test_main_with_custom_parameters(mock_provider_class):
    """Test CLI with custom annotation parameters."""
    mock_provider = Mock()
    mock_provider_class.return_value = mock_provider

    with patch("gs2txt.cli.BatchProcessor") as mock_processor_class:
        mock_processor = Mock()
        mock_processor_class.return_value = mock_processor

        main()

        # Verify parameters were passed
        call_kwargs = mock_processor.process_single_file.call_args[1]
        assert call_kwargs["max_gene_num"] == 100
        assert call_kwargs["max_pathway_num"] == 20


@patch("gs2txt.cli.OpenAIProvider")
@patch("gs2txt.cli.BatchProcessor")
@patch("sys.argv", [
    "gs2txt",
    "--input", "nonexistent.csv",
    "--output", "out.csv",
    "--api-key", "sk-test"
])
def test_main_file_not_found(mock_processor_class, mock_provider_class):
    """Test error handling when input file doesn't exist."""
    mock_provider = Mock()
    mock_provider_class.return_value = mock_provider

    mock_processor = Mock()
    mock_processor.process_single_file.side_effect = FileNotFoundError("File not found")
    mock_processor_class.return_value = mock_processor

    with pytest.raises(SystemExit) as exc_info:
        main()

    assert exc_info.value.code == 1
