"""
Tests for TwoStagePipeline.
"""

import os
from pathlib import Path

import pandas as pd
import pytest
import yaml

from gs2txt.pipeline import TwoStagePipeline


# ============================================
# Fixtures
# ============================================


@pytest.fixture
def sample_deg_data():
    """Sample DEG data."""
    return pd.DataFrame({
        "gene": ["TP53", "MYC", "BRCA1", "CD4", "CD8A"],
        "pvalue": [0.001, 0.01, 0.02, 0.03, 0.04],
        "logFC": [2.5, -1.8, 1.5, 2.0, -1.2]
    })


@pytest.fixture
def sample_pathway_data():
    """Sample pathway enrichment data."""
    return pd.DataFrame({
        "Term": ["Cell cycle regulation", "Immune response", "DNA repair"],
        "Adjusted P-value": [0.001, 0.005, 0.02]
    })


@pytest.fixture
def test_data_dir(tmp_path, sample_deg_data, sample_pathway_data):
    """
    Create test directory structure with DEG and pathway files.

    Structure:
    tmp_path/
    ├── deg/
    │   ├── sample1.csv
    │   └── sample2.csv
    ├── GO/
    │   ├── sample1.csv
    │   └── sample2.csv
    └── KEGG/
        └── sample1.csv
    """
    # Create directories
    deg_dir = tmp_path / "deg"
    go_dir = tmp_path / "GO"
    kegg_dir = tmp_path / "KEGG"

    deg_dir.mkdir()
    go_dir.mkdir()
    kegg_dir.mkdir()

    # Create DEG files
    sample_deg_data.to_csv(deg_dir / "sample1.csv", index=False)
    sample_deg_data.to_csv(deg_dir / "sample2.csv", index=False)

    # Create pathway files
    sample_pathway_data.to_csv(go_dir / "sample1.csv", index=False)
    sample_pathway_data.to_csv(go_dir / "sample2.csv", index=False)

    # KEGG only has sample1
    kegg_pathway = pd.DataFrame({
        "Term": ["Metabolic pathway", "Signal transduction"],
        "Adjusted P-value": [0.003, 0.01]
    })
    kegg_pathway.to_csv(kegg_dir / "sample1.csv", index=False)

    return tmp_path


@pytest.fixture
def config_with_relative_paths(tmp_path):
    """Create config file with relative paths (to be used with base_dir)."""
    config = {
        "input": {
            "deg_dir": "deg/",
            "pathway_dirs": ["GO/", "KEGG/"]
        },
        "gene_filter": {
            "gene_column": "gene",
            "pvalue_threshold": 0.05,
            "log2fc_threshold": 1.0,
            "max_gene_num": 60
        },
        "pathway_filter": {
            "pvalue_threshold": 0.05,
            "max_pathway_num": 10
        },
        "llm": {
            "provider": "openai",
            "model_id": "gpt-4",
            "temperature": 0.0
        }
    }
    config_file = tmp_path / "config_relative.yaml"
    with open(config_file, "w") as f:
        yaml.dump(config, f)
    return str(config_file)


@pytest.fixture
def config_with_absolute_paths(tmp_path, test_data_dir):
    """Create config file with absolute paths (backward compatible mode)."""
    config = {
        "input": {
            "deg_dir": str(test_data_dir / "deg"),
            "pathway_dirs": [
                str(test_data_dir / "GO"),
                str(test_data_dir / "KEGG")
            ]
        },
        "gene_filter": {
            "gene_column": "gene",
            "pvalue_threshold": 0.05,
            "log2fc_threshold": 1.0,
            "max_gene_num": 60
        },
        "pathway_filter": {
            "pvalue_threshold": 0.05,
            "max_pathway_num": 10
        },
        "llm": {
            "provider": "openai",
            "model_id": "gpt-4",
            "temperature": 0.0
        }
    }
    config_file = tmp_path / "config_absolute.yaml"
    with open(config_file, "w") as f:
        yaml.dump(config, f)
    return str(config_file)


# ============================================
# Test preprocess() with base_dir parameters
# ============================================


def test_preprocess_with_base_dirs(test_data_dir, config_with_relative_paths, tmp_path):
    """Test preprocess with deg_base_dir and pathway_base_dir."""
    output_file = str(tmp_path / "intermediate.csv")

    result = TwoStagePipeline.preprocess(
        config_file=config_with_relative_paths,
        output_file=output_file,
        deg_base_dir=str(test_data_dir),
        pathway_base_dir=str(test_data_dir),
        test=True  # Only process first 3 files
    )

    # Check output file exists
    assert Path(output_file).exists()

    # Check result DataFrame structure
    assert "gs" in result.columns
    assert "genes" in result.columns
    assert "pathways" in result.columns
    assert "final_prompt" in result.columns

    # Should have processed files
    assert len(result) > 0

    # Check genes were filtered and included
    assert result["genes"].notna().any()


def test_preprocess_backward_compatible(test_data_dir, config_with_absolute_paths, tmp_path):
    """Test preprocess without base_dir parameters (backward compatible)."""
    output_file = str(tmp_path / "intermediate.csv")

    result = TwoStagePipeline.preprocess(
        config_file=config_with_absolute_paths,
        output_file=output_file,
        test=True
    )

    # Check output file exists
    assert Path(output_file).exists()

    # Check result DataFrame structure
    assert "gs" in result.columns
    assert "genes" in result.columns
    assert "pathways" in result.columns

    # Should have processed files
    assert len(result) > 0


def test_preprocess_batch_alias(test_data_dir, config_with_absolute_paths, tmp_path):
    """Test that preprocess_batch is an alias for preprocess."""
    output_file = str(tmp_path / "intermediate.csv")

    # Use preprocess_batch (alias)
    result = TwoStagePipeline.preprocess_batch(
        config_file=config_with_absolute_paths,
        output_file=output_file,
        test=True
    )

    assert Path(output_file).exists()
    assert len(result) > 0


def test_preprocess_merges_pathways_from_multiple_dirs(test_data_dir, config_with_relative_paths, tmp_path):
    """Test that pathways from multiple directories are merged."""
    output_file = str(tmp_path / "intermediate.csv")

    result = TwoStagePipeline.preprocess(
        config_file=config_with_relative_paths,
        output_file=output_file,
        deg_base_dir=str(test_data_dir),
        pathway_base_dir=str(test_data_dir),
        test=True
    )

    # sample1 has pathways from both GO and KEGG
    sample1_row = result[result["gs"] == "sample1"]
    if len(sample1_row) > 0:
        pathways = sample1_row["pathways"].iloc[0]
        # Should contain pathways from both sources
        assert pathways != ""
        # Check that at least some pathways are present
        pathway_list = pathways.split(",") if pathways else []
        assert len(pathway_list) > 0


def test_preprocess_test_mode(test_data_dir, config_with_absolute_paths, tmp_path):
    """Test that test mode limits processing to 3 files."""
    output_file = str(tmp_path / "intermediate.csv")

    result = TwoStagePipeline.preprocess(
        config_file=config_with_absolute_paths,
        output_file=output_file,
        test=True
    )

    # Should process at most 3 files
    assert len(result) <= 3


def test_preprocess_missing_deg_dir(config_with_relative_paths, tmp_path):
    """Test error when DEG directory doesn't exist."""
    output_file = str(tmp_path / "intermediate.csv")

    with pytest.raises(FileNotFoundError, match="DEG directory not found"):
        TwoStagePipeline.preprocess(
            config_file=config_with_relative_paths,
            output_file=output_file,
            deg_base_dir="/nonexistent/path",
            pathway_base_dir="/nonexistent/path"
        )


def test_preprocess_checkpoint_created_and_removed(test_data_dir, config_with_absolute_paths, tmp_path):
    """Test that checkpoint file is created and removed on success."""
    output_file = str(tmp_path / "intermediate.csv")
    checkpoint_file = output_file + ".checkpoint"

    TwoStagePipeline.preprocess(
        config_file=config_with_absolute_paths,
        output_file=output_file,
        checkpoint_interval=1,  # Checkpoint every record
        test=True
    )

    # Output should exist
    assert Path(output_file).exists()
    # Checkpoint should be removed after successful completion
    assert not Path(checkpoint_file).exists()


def test_preprocess_with_ppi_context(test_data_dir, config_with_absolute_paths, tmp_path):
    """Test preprocess with PPI context."""
    output_file = str(tmp_path / "intermediate.csv")
    ppi_context = {
        "sample1": "Hub genes: TP53, MYC; Network density: high"
    }

    result = TwoStagePipeline.preprocess(
        config_file=config_with_absolute_paths,
        output_file=output_file,
        ppi_context=ppi_context,
        test=True
    )

    # Check PPI context was included
    sample1_row = result[result["gs"] == "sample1"]
    if len(sample1_row) > 0:
        assert sample1_row["ppis"].iloc[0] == ppi_context["sample1"]


# ============================================
# Test _filter_genes
# ============================================


def test_filter_genes_basic(sample_deg_data):
    """Test basic gene filtering."""
    genes = TwoStagePipeline._filter_genes(
        sample_deg_data,
        gene_column="gene",
        pvalue_threshold=0.05,
        log2fc_threshold=1.0
    )

    # Should filter by both pvalue and log2fc
    assert len(genes) > 0
    assert all(isinstance(g, str) for g in genes)


def test_filter_genes_respects_max(sample_deg_data):
    """Test that max_gene_num is respected."""
    genes = TwoStagePipeline._filter_genes(
        sample_deg_data,
        gene_column="gene",
        pvalue_threshold=0.05,
        log2fc_threshold=0.0,  # Accept all genes
        max_gene_num=2
    )

    assert len(genes) <= 2


def test_filter_genes_sorts_by_pvalue(sample_deg_data):
    """Test that genes are sorted by p-value."""
    genes = TwoStagePipeline._filter_genes(
        sample_deg_data,
        gene_column="gene",
        pvalue_threshold=0.05,
        log2fc_threshold=0.0
    )

    # First gene should be the one with lowest pvalue
    assert genes[0] == "TP53"  # pvalue=0.001


# ============================================
# Test _filter_pathways
# ============================================


def test_filter_pathways_basic(sample_pathway_data):
    """Test basic pathway filtering."""
    pathways = TwoStagePipeline._filter_pathways(
        sample_pathway_data,
        pvalue_threshold=0.05
    )

    assert len(pathways) > 0
    assert all(isinstance(p, str) for p in pathways)


def test_filter_pathways_respects_threshold(sample_pathway_data):
    """Test that p-value threshold is respected."""
    pathways = TwoStagePipeline._filter_pathways(
        sample_pathway_data,
        pvalue_threshold=0.01
    )

    # Only pathways with pvalue <= 0.01
    # Cell cycle (0.001) and Immune response (0.005)
    assert len(pathways) == 2
    assert "Cell cycle regulation" in pathways
    assert "Immune response" in pathways


def test_filter_pathways_respects_max(sample_pathway_data):
    """Test that max_pathway_num is respected."""
    pathways = TwoStagePipeline._filter_pathways(
        sample_pathway_data,
        pvalue_threshold=0.05,
        max_pathway_num=1
    )

    assert len(pathways) == 1
