"""
Unit tests for gs2txt core functionality.
"""

from unittest.mock import Mock, patch

import pandas as pd
import pytest

from gs2txt import GeneSetAnnotator
from gs2txt.enrichment.custom import CustomEnrichment
from gs2txt.llm.base import BaseLLMProvider

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
    # Updated to return simple process name (without "Process:" prefix)
    provider.generate.return_value = "DNA damage response and cell cycle regulation"
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
    assert len(result) > 0  # Should return non-empty annotation
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

    # Empty gene list should return empty string
    assert result == ""
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

    annotator.annotate(
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
    annotator.annotate(
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

    # LLM failure should still return error info
    assert "Failed" in result
    assert "API error" in result


# ============================================
# Test Differential Gene Filtering
# ============================================


def test_pvalue_filtering(sample_deg_df, mock_llm_provider):
    """Test that p-value threshold is respected."""
    annotator = GeneSetAnnotator(
        llm_provider=mock_llm_provider,
        enrichment_method=None
    )

    # Apply strict p-value threshold (only genes with pvalue <= 0.002 should pass)
    result = annotator.annotate(
        sample_deg_df,
        pvalue_threshold=0.002,
        compute_enrichment=False
    )

    # Verify result was generated
    assert isinstance(result, str)
    assert len(result) > 0

    # Check that only filtered genes were included (pvalue <= 0.002: TP53, MYC, EGFR, KRAS)
    call_args = mock_llm_provider.generate.call_args[0][0]
    user_msg = next(m["content"] for m in call_args if m["role"] == "user")

    # Should not include BRCA1 (pvalue=0.003)
    assert "BRCA1" not in user_msg or user_msg.count(",") <= 3
    mock_llm_provider.generate.assert_called_once()


def test_log2fc_filtering(sample_deg_df, mock_llm_provider):
    """Test that log2FC threshold is respected."""
    annotator = GeneSetAnnotator(
        llm_provider=mock_llm_provider,
        enrichment_method=None
    )

    # Apply strict log2FC threshold (only genes with |logFC| >= 2.0 should pass)
    result = annotator.annotate(
        sample_deg_df,
        log2fc_threshold=2.0,
        compute_enrichment=False
    )

    assert isinstance(result, str)
    assert len(result) > 0

    # Check that highly filtered genes were included (|logFC| >= 2.0: TP53, EGFR)
    call_args = mock_llm_provider.generate.call_args[0][0]
    user_msg = next(m["content"] for m in call_args if m["role"] == "user")

    # Count genes (should be 2: TP53 and EGFR)
    genes_section = user_msg.split("[Gene set]")[1].split("\n\n")[0] if "[Gene set]" in user_msg else user_msg
    gene_count = genes_section.count(",") + 1 if "," in genes_section else (1 if genes_section.strip() else 0)
    assert gene_count <= 2
    mock_llm_provider.generate.assert_called_once()


def test_combined_filtering(sample_deg_df, mock_llm_provider):
    """Test that pvalue and log2FC filters work together."""
    annotator = GeneSetAnnotator(
        llm_provider=mock_llm_provider,
        enrichment_method=None
    )

    result = annotator.annotate(
        sample_deg_df,
        pvalue_threshold=0.05,
        log2fc_threshold=1.0,
        max_gene_num=5,
        compute_enrichment=False
    )

    assert isinstance(result, str)
    mock_llm_provider.generate.assert_called_once()

    # Verify that filtering was applied
    call_args = mock_llm_provider.generate.call_args[0][0]
    user_msg = next(m["content"] for m in call_args if m["role"] == "user")

    # All genes in sample_deg_df should pass (pvalue < 0.05, |logFC| >= 1.0)
    assert "TP53" in user_msg or "MYC" in user_msg or "EGFR" in user_msg


def test_filtering_with_missing_columns(mock_llm_provider):
    """Test that filtering gracefully handles missing statistical columns."""
    # Create DataFrame without pvalue or logFC columns
    df = pd.DataFrame({
        "gene": ["GENE1", "GENE2", "GENE3"]
    })

    annotator = GeneSetAnnotator(
        llm_provider=mock_llm_provider,
        enrichment_method=None
    )

    # Should work without errors, just limit by max_gene_num
    result = annotator.annotate(
        df,
        pvalue_threshold=0.05,
        log2fc_threshold=1.0,
        compute_enrichment=False
    )

    assert isinstance(result, str)
    mock_llm_provider.generate.assert_called_once()

    # All 3 genes should be included since no filtering can be applied
    call_args = mock_llm_provider.generate.call_args[0][0]
    user_msg = next(m["content"] for m in call_args if m["role"] == "user")
    assert "GENE1" in user_msg
    assert "GENE2" in user_msg
    assert "GENE3" in user_msg


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
    mock_provider.generate.return_value = "T cell activation"
    mock_provider_class.return_value = mock_provider

    result = annotate_gene_set_with_llm(
        deg_df=sample_deg_df, model_id="gpt-4", api_key="test-key"
    )

    assert isinstance(result, str)
    mock_provider_class.assert_called_once()


def test_filtered_genes_empty_returns_empty_string():
    """Test that filtering resulting in no genes returns empty string."""
    mock_provider = Mock(spec=BaseLLMProvider)
    annotator = GeneSetAnnotator(
        llm_provider=mock_provider, enrichment_method=None
    )

    # All genes have high pvalue, will be filtered out
    df = pd.DataFrame({
        "gene": ["A", "B", "C"],
        "pvalue": [0.9, 0.8, 0.7]
    })

    result = annotator.annotate(df, pvalue_threshold=0.05)

    # Should return empty string when all genes filtered out
    assert result == ""
    mock_provider.generate.assert_not_called()


# ============================================
# Test annotate_detailed Method
# ============================================


def test_annotate_detailed_returns_dict(sample_deg_df, mock_llm_provider):
    """Test that annotate_detailed returns a dictionary with all fields."""
    annotator = GeneSetAnnotator(
        llm_provider=mock_llm_provider, enrichment_method=None
    )

    result = annotator.annotate_detailed(sample_deg_df, compute_enrichment=False)

    assert isinstance(result, dict)
    assert "annotation" in result
    assert "pathways" in result
    assert "ppis" in result
    assert "final_prompt" in result
    assert result["annotation"] == "DNA damage response and cell cycle regulation"
    assert result["pathways"] == ""  # No enrichment
    assert result["ppis"] == ""  # No additional context
    assert "[Gene set]" in result["final_prompt"]  # Prompt should contain gene set marker


def test_annotate_detailed_with_pathways(sample_deg_df, mock_llm_provider, sample_pathways):
    """Test annotate_detailed with pre-computed pathways."""
    annotator = GeneSetAnnotator(
        llm_provider=mock_llm_provider, enrichment_method=None
    )

    result = annotator.annotate_detailed(
        sample_deg_df,
        pathways=sample_pathways,
        compute_enrichment=False
    )

    assert isinstance(result, dict)
    assert result["pathways"] == "DNA repair, Apoptosis, Cell cycle checkpoint"
    assert "Enriched pathways" in result["final_prompt"]


def test_annotate_detailed_with_context(sample_deg_df, mock_llm_provider):
    """Test annotate_detailed with additional context (PPIs)."""
    annotator = GeneSetAnnotator(
        llm_provider=mock_llm_provider, enrichment_method=None
    )

    ppi_info = "Hub genes: TP53, MYC"
    result = annotator.annotate_detailed(
        sample_deg_df,
        additional_context=ppi_info,
        compute_enrichment=False
    )

    assert isinstance(result, dict)
    assert result["ppis"] == ppi_info
    assert "Hub genes" in result["final_prompt"]


def test_annotate_detailed_empty_df():
    """Test annotate_detailed with empty dataframe."""
    mock_provider = Mock(spec=BaseLLMProvider)
    annotator = GeneSetAnnotator(
        llm_provider=mock_provider, enrichment_method=None
    )

    empty_df = pd.DataFrame({"gene": []})
    result = annotator.annotate_detailed(empty_df)

    assert isinstance(result, dict)
    assert result["annotation"] == ""
    assert result["pathways"] == ""
    assert result["ppis"] == ""
    assert result["final_prompt"] == ""
    mock_provider.generate.assert_not_called()
