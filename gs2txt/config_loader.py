"""
YAML configuration loader for gs2txt two-stage pipeline.
"""

import os
from pathlib import Path
from typing import Optional, List
from dataclasses import dataclass, field

try:
    import yaml
except ImportError:
    yaml = None


@dataclass
class PipelineConfig:
    """
    Configuration for two-stage pipeline.

    Attributes
    ----------
    gene_pvalue_threshold : float
        P-value threshold for gene filtering (default 0.05)
    gene_log2fc_threshold : float
        Log2FC threshold for gene filtering (default 1.0)
    gene_pvalue_column : str
        Column name for p-values in DEG file (default "pvalue")
    gene_log2fc_column : str
        Column name for log2FC in DEG file (default "logFC")
    max_gene_num : int
        Maximum number of genes to include (default 60)
    pathway_pvalue_threshold : float
        P-value threshold for pathway filtering (default 0.05)
    pathway_pvalue_column : str
        Column name for p-values in enrichment file (default "Adjusted P-value")
    pathway_term_column : str
        Column name for pathway terms (default "Term")
    max_pathway_num : int
        Maximum number of pathways to include (default 10)
    llm_provider : str
        LLM provider name (default "litellm")
    llm_model_id : str
        Model identifier (default "gpt-4")
    llm_temperature : float
        Temperature for LLM (default 0.0)
    llm_base_url : str, optional
        Base URL for LLM API
    llm_api_key : str, optional
        API key for LLM (or loaded from environment)
    deg_dir : str, optional
        Directory containing DEG CSV files (for batch processing)
    pathway_dirs : List[str]
        List of directories containing pathway enrichment files
    """

    # Input paths (for batch processing)
    deg_dir: Optional[str] = None
    pathway_dirs: List[str] = field(default_factory=list)

    # Gene filtering
    gene_pvalue_threshold: float = 0.05
    gene_log2fc_threshold: float = 1.0
    gene_pvalue_column: str = "pvalue"
    gene_log2fc_column: str = "logFC"
    max_gene_num: int = 60

    # Pathway filtering
    pathway_pvalue_threshold: float = 0.05
    pathway_pvalue_column: str = "Adjusted P-value"
    pathway_term_column: str = "Term"
    max_pathway_num: int = 10

    # LLM configuration
    llm_provider: str = "litellm"
    llm_model_id: str = "gpt-4"
    llm_temperature: float = 0.0
    llm_base_url: Optional[str] = None
    llm_api_key: Optional[str] = None

    @classmethod
    def from_yaml(cls, file_path: str) -> "PipelineConfig":
        """
        Load configuration from a YAML file.

        Parameters
        ----------
        file_path : str
            Path to YAML configuration file

        Returns
        -------
        PipelineConfig
            Configuration instance with values from YAML

        Raises
        ------
        ImportError
            If PyYAML is not installed
        FileNotFoundError
            If config file does not exist

        Examples
        --------
        >>> config = PipelineConfig.from_yaml("config.yaml")
        >>> print(config.max_gene_num)
        60
        """
        if yaml is None:
            raise ImportError(
                "PyYAML is required for YAML config loading. "
                "Install with: pip install pyyaml"
            )

        file_path = Path(file_path)
        if not file_path.exists():
            raise FileNotFoundError(f"Config file not found: {file_path}")

        with open(file_path, "r", encoding="utf-8") as f:
            data = yaml.safe_load(f)

        if data is None:
            data = {}

        # Parse nested structure
        input_config = data.get("input", {})
        gene_filter = data.get("gene_filter", {})
        pathway_filter = data.get("pathway_filter", {})
        llm_config = data.get("llm", {})

        # Get API key from environment if specified
        api_key = llm_config.get("api_key")
        api_key_env = llm_config.get("api_key_env")
        if api_key_env and not api_key:
            api_key = os.getenv(api_key_env)

        return cls(
            # Input paths
            deg_dir=input_config.get("deg_dir"),
            pathway_dirs=input_config.get("pathway_dirs", []),
            # Gene filtering
            gene_pvalue_threshold=gene_filter.get("pvalue_threshold", 0.05),
            gene_log2fc_threshold=gene_filter.get("log2fc_threshold", 1.0),
            gene_pvalue_column=gene_filter.get("pvalue_column", "pvalue"),
            gene_log2fc_column=gene_filter.get("log2fc_column", "logFC"),
            max_gene_num=gene_filter.get("max_gene_num", 60),
            # Pathway filtering
            pathway_pvalue_threshold=pathway_filter.get("pvalue_threshold", 0.05),
            pathway_pvalue_column=pathway_filter.get("pvalue_column", "Adjusted P-value"),
            pathway_term_column=pathway_filter.get("term_column", "Term"),
            max_pathway_num=pathway_filter.get("max_pathway_num", 10),
            # LLM configuration
            llm_provider=llm_config.get("provider", "litellm"),
            llm_model_id=llm_config.get("model_id", "gpt-4"),
            llm_temperature=llm_config.get("temperature", 0.0),
            llm_base_url=llm_config.get("base_url"),
            llm_api_key=api_key,
        )

    @classmethod
    def default(cls) -> "PipelineConfig":
        """
        Create a default configuration.

        Returns
        -------
        PipelineConfig
            Configuration instance with default values
        """
        return cls()

    def to_dict(self) -> dict:
        """
        Convert configuration to dictionary.

        Returns
        -------
        dict
            Configuration as nested dictionary
        """
        result = {}

        # Only include input section if paths are set
        if self.deg_dir or self.pathway_dirs:
            result["input"] = {
                "deg_dir": self.deg_dir,
                "pathway_dirs": self.pathway_dirs,
            }

        result["gene_filter"] = {
            "pvalue_threshold": self.gene_pvalue_threshold,
            "log2fc_threshold": self.gene_log2fc_threshold,
            "pvalue_column": self.gene_pvalue_column,
            "log2fc_column": self.gene_log2fc_column,
            "max_gene_num": self.max_gene_num,
        }
        result["pathway_filter"] = {
            "pvalue_threshold": self.pathway_pvalue_threshold,
            "pvalue_column": self.pathway_pvalue_column,
            "term_column": self.pathway_term_column,
            "max_pathway_num": self.max_pathway_num,
        }
        result["llm"] = {
            "provider": self.llm_provider,
            "model_id": self.llm_model_id,
            "temperature": self.llm_temperature,
            "base_url": self.llm_base_url,
            # Note: api_key is not exported for security
        }

        return result

    def save_yaml(self, file_path: str) -> None:
        """
        Save configuration to a YAML file.

        Parameters
        ----------
        file_path : str
            Path to save YAML configuration file
        """
        if yaml is None:
            raise ImportError(
                "PyYAML is required for YAML config saving. "
                "Install with: pip install pyyaml"
            )

        with open(file_path, "w", encoding="utf-8") as f:
            yaml.dump(self.to_dict(), f, default_flow_style=False, allow_unicode=True)
