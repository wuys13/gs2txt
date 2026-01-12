"""
Tests for CSV I/O handlers.
"""

import pytest
import pandas as pd
from pathlib import Path

from gs2txt.io import CSVReader, CSVWriter


# ============================================
# Test CSV Reader
# ============================================


def test_csv_reader_valid_file(tmp_path):
    """Test reading valid CSV file."""
    csv_file = tmp_path / "test.csv"
    csv_file.write_text("gene,logFC\nTP53,2.3\nMYC,1.8\n")

    df = CSVReader.read_gene_file(str(csv_file))

    assert "gene" in df.columns
    assert len(df) == 2
    assert df["gene"].tolist() == ["TP53", "MYC"]


def test_csv_reader_missing_gene_column(tmp_path):
    """Test error on missing gene column."""
    csv_file = tmp_path / "test.csv"
    csv_file.write_text("not_gene,value\nA,1\n")

    with pytest.raises(ValueError, match="gene"):
        CSVReader.read_gene_file(str(csv_file))


def test_csv_reader_file_not_found():
    """Test error when file doesn't exist."""
    with pytest.raises(FileNotFoundError):
        CSVReader.read_gene_file("nonexistent.csv")


def test_csv_reader_with_group_column(tmp_path):
    """Test reading file with group column validation."""
    csv_file = tmp_path / "test.csv"
    csv_file.write_text("cluster,gene,logFC\nA,TP53,2.3\nA,MYC,1.8\n")

    df = CSVReader.read_gene_file(str(csv_file), group_column="cluster")

    assert "gene" in df.columns
    assert "cluster" in df.columns
    assert len(df) == 2


def test_csv_reader_missing_group_column(tmp_path):
    """Test error when specified group column doesn't exist."""
    csv_file = tmp_path / "test.csv"
    csv_file.write_text("gene,logFC\nTP53,2.3\n")

    with pytest.raises(ValueError, match="Group column"):
        CSVReader.read_gene_file(str(csv_file), group_column="cluster")


# ============================================
# Test CSV Writer
# ============================================


def test_csv_writer(tmp_path):
    """Test writing results to CSV."""
    df = pd.DataFrame({
        "gene": ["TP53", "MYC"],
        "annotation": ["Process 1", "Process 2"]
    })

    output_file = tmp_path / "output.csv"
    CSVWriter.write_results(df, str(output_file))

    assert output_file.exists()
    result = pd.read_csv(output_file)
    assert len(result) == 2
    assert "annotation" in result.columns


def test_csv_writer_creates_parent_dir(tmp_path):
    """Test that writer creates parent directories."""
    df = pd.DataFrame({
        "gene": ["TP53"],
        "annotation": ["Process 1"]
    })

    output_file = tmp_path / "subdir" / "output.csv"
    CSVWriter.write_results(df, str(output_file))

    assert output_file.exists()
    assert output_file.parent.exists()


def test_csv_writer_empty_dataframe():
    """Test error when trying to write empty dataframe."""
    empty_df = pd.DataFrame()

    with pytest.raises(ValueError, match="empty"):
        CSVWriter.write_results(empty_df, "output.csv")


def test_csv_writer_none_dataframe():
    """Test error when dataframe is None."""
    with pytest.raises(ValueError, match="empty"):
        CSVWriter.write_results(None, "output.csv")
