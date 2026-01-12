"""
Tests for batch processing.
"""

import pytest
import pandas as pd
from unittest.mock import Mock

from gs2txt.batch import BatchProcessor


# ============================================
# Fixtures
# ============================================


@pytest.fixture
def mock_annotator():
    """Mock annotator for testing."""
    annotator = Mock()
    annotator.annotate.return_value = "Process: Test annotation"
    return annotator


# ============================================
# Test Batch Processor
# ============================================


def test_batch_processor_init(mock_annotator):
    """Test BatchProcessor initialization."""
    processor = BatchProcessor(mock_annotator)
    assert processor.annotator == mock_annotator


def test_process_grouped_data(mock_annotator):
    """Test grouped data processing."""
    df = pd.DataFrame({
        "cluster": ["A", "A", "B", "B"],
        "gene": ["TP53", "MYC", "CD4", "CD8A"]
    })

    processor = BatchProcessor(mock_annotator)
    result = processor.process_grouped_data(df, "cluster")

    assert "annotation" in result.columns
    assert mock_annotator.annotate.call_count == 2  # 2 clusters
    assert len(result) == 4
    assert result["annotation"].notna().all()


def test_process_grouped_data_with_kwargs(mock_annotator):
    """Test that kwargs are passed to annotate."""
    df = pd.DataFrame({
        "cluster": ["A", "A"],
        "gene": ["TP53", "MYC"]
    })

    processor = BatchProcessor(mock_annotator)
    processor.process_grouped_data(
        df,
        "cluster",
        max_gene_num=50,
        max_pathway_num=5
    )

    # Verify annotate was called with kwargs
    mock_annotator.annotate.assert_called_once()
    call_kwargs = mock_annotator.annotate.call_args[1]
    assert call_kwargs["max_gene_num"] == 50
    assert call_kwargs["max_pathway_num"] == 5


def test_process_grouped_data_handles_errors(mock_annotator):
    """Test that errors in annotation are handled gracefully."""
    mock_annotator.annotate.side_effect = Exception("Test error")

    df = pd.DataFrame({
        "cluster": ["A", "A"],
        "gene": ["TP53", "MYC"]
    })

    processor = BatchProcessor(mock_annotator)
    result = processor.process_grouped_data(df, "cluster")

    assert "annotation" in result.columns
    assert "Failed" in result["annotation"].iloc[0]


def test_process_single_geneset(mock_annotator):
    """Test single gene set processing."""
    df = pd.DataFrame({
        "gene": ["TP53", "MYC", "BRCA1"]
    })

    processor = BatchProcessor(mock_annotator)
    result = processor.process_single_geneset(df)

    assert "annotation" in result.columns
    assert mock_annotator.annotate.call_count == 1
    assert len(result) == 3
    # All rows should have same annotation
    assert result["annotation"].nunique() == 1


def test_process_single_geneset_with_kwargs(mock_annotator):
    """Test that kwargs are passed to annotate."""
    df = pd.DataFrame({
        "gene": ["TP53", "MYC"]
    })

    processor = BatchProcessor(mock_annotator)
    processor.process_single_geneset(
        df,
        max_gene_num=100
    )

    call_kwargs = mock_annotator.annotate.call_args[1]
    assert call_kwargs["max_gene_num"] == 100


def test_process_single_geneset_handles_errors(mock_annotator):
    """Test error handling in single gene set processing."""
    mock_annotator.annotate.side_effect = Exception("Test error")

    df = pd.DataFrame({
        "gene": ["TP53"]
    })

    processor = BatchProcessor(mock_annotator)
    result = processor.process_single_geneset(df)

    assert "annotation" in result.columns
    assert "Failed" in result["annotation"].iloc[0]


def test_process_single_file_grouped(mock_annotator, tmp_path):
    """Test processing file with grouping."""
    # Create test CSV
    csv_file = tmp_path / "input.csv"
    csv_file.write_text("cluster,gene\nA,TP53\nA,MYC\nB,CD4\n")

    output_file = tmp_path / "output.csv"

    processor = BatchProcessor(mock_annotator)
    processor.process_single_file(
        str(csv_file),
        str(output_file),
        group_column="cluster"
    )

    assert output_file.exists()
    result = pd.read_csv(output_file)
    assert "annotation" in result.columns
    assert mock_annotator.annotate.call_count == 2  # 2 clusters


def test_process_single_file_ungrouped(mock_annotator, tmp_path):
    """Test processing file without grouping."""
    csv_file = tmp_path / "input.csv"
    csv_file.write_text("gene\nTP53\nMYC\n")

    output_file = tmp_path / "output.csv"

    processor = BatchProcessor(mock_annotator)
    processor.process_single_file(
        str(csv_file),
        str(output_file)
    )

    assert output_file.exists()
    result = pd.read_csv(output_file)
    assert "annotation" in result.columns
    assert mock_annotator.annotate.call_count == 1
