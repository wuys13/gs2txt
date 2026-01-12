"""
Unit tests for gs2txt core functionality.
"""

import pytest
import pandas as pd
from unittest.mock import Mock, patch

from gs2txt import GeneSetAnnotator
from gs2txt.llm.base import BaseLLMProvider
from gs2txt.enrichment.custom import CustomEnrichment


# ============================================
# Fixtures
# ============================================


@pytest.fixture
def sample_deg_df():
    """Sample DEG dataframe."""
    return pd.DataFrame(
        {
            "gene": ["TP53", "MYC", "BRCA1", "EGFR", "KRAS"],
            "logFC": [2.3, 1.8, -1.5, 2.1, 1.9],
            "pvalue": [0.001, 0.002, 0.003, 0.001, 0.002],
        }
    )


@pytest.fixture
def mock_llm_provider():
    """Mock LLM provider for testing."""
    provider = Mock(spec=BaseLLMProvider)
    provider.generate.return_value = (
        "Process: DNA damage response\n"
        "This gene set is enriched for tumor suppressors and oncogenes "
        "involved in cell cycle regulation and apoptosis."
    )
    return provider


@pytest.fixture
def sample_pathways():
    """Sample pathway list."""
    return ["DNA repair", "Apoptosis", "Cell cycle checkpoint"]


# ============================================
# Test Core Functionality
# ============================================


def test_annotator_initialization(mock_llm_provider):
    """Test GeneSetAnnotator initialization."""
    annotator = GeneSetAnnotator(
        llm_provider=mock_llm_provider, enrichment_method=None
    )

    assert annotator.llm_provider == mock_llm_provider
    assert annotator.enrichment is None


def test_basic_annotation(sample_deg_df, mock_llm_provider):
    """Test basic gene set annotation."""
    annotator = GeneSetAnnotator(
        llm_provider=mock_llm_provider, enrichment_method=None
    )

    result = annotator.annotate(sample_deg_df, compute_enrichment=False)

    assert isinstance(result, str)
    assert "Process:" in result
    mock_llm_provider.generate.assert_called_once()


def test_annotation_with_pathways(sample_deg_df, mock_llm_provider, sample_pathways):
    """Test annotation with pre-computed pathways."""
    annotator = GeneSetAnnotator(
        llm_provider=mock_llm_provider, enrichment_method=None
    )

    result = annotator.annotate(
        sample_deg_df, pathways=sample_pathways, compute_enrichment=False
    )

    assert isinstance(result, str)
    # Check that pathways were included in prompt
    call_args = mock_llm_provider.generate.call_args[0][0]
    user_msg = next(m["content"] for m in call_args if m["role"] == "user")
    assert "DNA repair" in user_msg


def test_annotation_with_custom_enrichment(sample_deg_df, mock_llm_provider):
    """Test annotation with custom enrichment."""
    custom_enrichment = CustomEnrichment(
        terms=["Custom pathway 1", "Custom pathway 2"]
    )

    annotator = GeneSetAnnotator(
        llm_provider=mock_llm_provider, enrichment_method=custom_enrichment
    )

    result = annotator.annotate(sample_deg_df)
    assert isinstance(result, str)


def test_empty_gene_list():
    """Test handling of empty gene list."""
    mock_provider = Mock(spec=BaseLLMProvider)
    annotator = GeneSetAnnotator(
        llm_provider=mock_provider, enrichment_method=None
    )

    empty_df = pd.DataFrame({"gene": []})
    result = annotator.annotate(empty_df)

    assert "Unresolved functional program" in result
    mock_provider.generate.assert_not_called()


def test_missing_gene_column():
    """Test error handling for missing gene column."""
    mock_provider = Mock(spec=BaseLLMProvider)
    annotator = GeneSetAnnotator(
        llm_provider=mock_provider, enrichment_method=None
    )

    invalid_df = pd.DataFrame({"not_gene": ["A", "B"]})

    with pytest.raises(ValueError, match="must contain a 'gene' column"):
        annotator.annotate(invalid_df)


def test_max_gene_num_limit(sample_deg_df, mock_llm_provider):
    """Test that max_gene_num is respected."""
    annotator = GeneSetAnnotator(
        llm_provider=mock_llm_provider, enrichment_method=None
    )

    result = annotator.annotate(
        sample_deg_df, max_gene_num=3, compute_enrichment=False
    )

    # Check that only 3 genes were included
    call_args = mock_llm_provider.generate.call_args[0][0]
    user_msg = next(m["content"] for m in call_args if m["role"] == "user")
    genes_in_prompt = user_msg.split("[Gene set]")[1].split("\n\n")[0]
    gene_count = genes_in_prompt.count(",") + 1
    assert gene_count == 3


def test_additional_context(sample_deg_df, mock_llm_provider):
    """Test inclusion of additional context."""
    annotator = GeneSetAnnotator(
        llm_provider=mock_llm_provider, enrichment_method=None
    )

    context = "PPI hub genes: TP53, MYC"
    result = annotator.annotate(
        sample_deg_df, additional_context=context, compute_enrichment=False
    )

    # Verify context was included
    call_args = mock_llm_provider.generate.call_args[0][0]
    user_msg = next(m["content"] for m in call_args if m["role"] == "user")
    assert "PPI hub genes" in user_msg


def test_llm_failure_handling(sample_deg_df):
    """Test graceful handling of LLM errors."""
    mock_provider = Mock(spec=BaseLLMProvider)
    mock_provider.generate.side_effect = Exception("API error")

    annotator = GeneSetAnnotator(
        llm_provider=mock_provider, enrichment_method=None
    )

    result = annotator.annotate(sample_deg_df, compute_enrichment=False)

    assert "Process: Failed" in result
    assert "API error" in result


# ============================================
# Test Enrichment Integration
# ============================================


def test_pathway_enrichment_integration(sample_deg_df, mock_llm_provider):
    """Test integration with pathway enrichment."""
    # Skip if gseapy not installed
    pytest.importorskip("gseapy")

    with patch("gseapy.enrichr") as mock_enrichr:
        # Mock enrichment results
        mock_results = pd.DataFrame(
            {"Term": ["Pathway A", "Pathway B"], "Adjusted P-value": [0.01, 0.02]}
        )
        mock_enrichr.return_value.results = mock_results

        annotator = GeneSetAnnotator(
            llm_provider=mock_llm_provider, enrichment_method="pathway"
        )

        result = annotator.annotate(sample_deg_df, compute_enrichment=True)

        assert isinstance(result, str)
        mock_enrichr.assert_called_once()


# ============================================
# Test Legacy Function
# ============================================


@patch("gs2txt.llm.openai_provider.OpenAIProvider")
def test_legacy_function(mock_provider_class, sample_deg_df):
    """Test backwards-compatible legacy function."""
    from gs2txt import annotate_gene_set_with_llm

    mock_provider = Mock()
    mock_provider.generate.return_value = "Process: Test"
    mock_provider_class.return_value = mock_provider

    result = annotate_gene_set_with_llm(
        deg_df=sample_deg_df, model_id="gpt-4", api_key="test-key"
    )

    assert isinstance(result, str)
    mock_provider_class.assert_called_once()
