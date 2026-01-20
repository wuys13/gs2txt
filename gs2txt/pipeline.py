"""
Two-stage processing pipeline for gs2txt.

Stage 1 (Preprocess): Read DEG + enrichment files, filter, build prompts, save intermediate
Stage 2 (Annotate): Read intermediate, call LLM, save final results
"""

from pathlib import Path
from typing import Optional

import pandas as pd
from tqdm import tqdm

from .config_loader import PipelineConfig
from .prompts.builder import PromptBuilder


class TwoStagePipeline:
    """
    Two-stage processing pipeline for gene set annotation.

    This pipeline separates data preprocessing from LLM annotation,
    allowing users to:
    1. Preprocess data without API access (stage 1)
    2. Review intermediate results before annotation
    3. Run annotation separately when API is available (stage 2)

    Examples
    --------
    >>> # Stage 1: Preprocess with base directories (no API needed)
    >>> # config.yaml contains: deg_dir="deg/", pathway_dirs=["GO/", "KEGG/"]
    >>> TwoStagePipeline.preprocess(
    ...     config_file="config.yaml",
    ...     output_file="intermediate.csv",
    ...     deg_base_dir="/data/project1/",      # -> /data/project1/deg/
    ...     pathway_base_dir="/data/project1/"   # -> /data/project1/GO/, etc.
    ... )

    >>> # Stage 1: Preprocess with absolute paths in config (backward compatible)
    >>> TwoStagePipeline.preprocess(
    ...     config_file="config.yaml",
    ...     output_file="intermediate.csv"
    ... )

    >>> # Stage 2: Annotate (API needed)
    >>> TwoStagePipeline.annotate(
    ...     intermediate_file="intermediate.csv",
    ...     output_file="output.csv",
    ...     config_file="config.yaml"
    ... )
    """

    @staticmethod
    def _filter_genes(
        df: pd.DataFrame,
        pvalue_threshold: float = 0.05,
        log2fc_threshold: float = 1.0,
        pvalue_column: str = "pvalue",
        log2fc_column: str = "logFC",
        max_gene_num: int = 60,
    ) -> list[str]:
        """
        Filter genes by statistical criteria.

        Parameters
        ----------
        df : pd.DataFrame
            DataFrame with gene column and optional statistical columns
        pvalue_threshold : float
            P-value threshold (genes with pvalue <= threshold)
        log2fc_threshold : float
            Log2FC threshold (genes with |log2FC| >= threshold)
        pvalue_column : str
            Column name for p-values
        log2fc_column : str
            Column name for log2FC
        max_gene_num : int
            Maximum number of genes

        Returns
        -------
        List[str]
            Filtered gene names
        """
        result = df.copy()

        # P-value filtering
        if pvalue_column in result.columns:
            result = result[result[pvalue_column] <= pvalue_threshold]

        # Log2FC filtering (support both column names)
        fc_col = None
        if log2fc_column in result.columns:
            fc_col = log2fc_column
        elif "log2FoldChange" in result.columns:
            fc_col = "log2FoldChange"

        if fc_col is not None:
            result = result[abs(result[fc_col]) >= log2fc_threshold]

        # Sort by p-value
        if pvalue_column in result.columns:
            result = result.sort_values(pvalue_column)

        # Extract gene names
        genes = result["gene"].dropna().astype(str).tolist()[:max_gene_num]
        return genes

    @staticmethod
    def _filter_pathways(
        df: pd.DataFrame,
        pvalue_threshold: float = 0.05,
        pvalue_column: str = "Adjusted P-value",
        term_column: str = "Term",
        max_pathway_num: int = 10,
    ) -> list[str]:
        """
        Filter pathways by p-value.

        Parameters
        ----------
        df : pd.DataFrame
            Enrichment results DataFrame
        pvalue_threshold : float
            P-value threshold
        pvalue_column : str
            Column name for p-values
        term_column : str
            Column name for pathway terms
        max_pathway_num : int
            Maximum number of pathways

        Returns
        -------
        List[str]
            Filtered pathway terms
        """
        result = df.copy()

        # P-value filtering
        if pvalue_column in result.columns:
            result = result[result[pvalue_column] <= pvalue_threshold]
            result = result.sort_values(pvalue_column)

        # Extract terms
        if term_column not in result.columns:
            # Try common alternatives
            for alt in ["Term", "term", "Pathway", "pathway", "Name", "name"]:
                if alt in result.columns:
                    term_column = alt
                    break

        if term_column in result.columns:
            terms = result[term_column].dropna().astype(str).tolist()[:max_pathway_num]
            return terms

        return []

    @staticmethod
    def annotate(
        intermediate_file: str,
        output_file: str,
        config_file: Optional[str] = None,
        test: bool = False,
        checkpoint_interval: int = 100,
    ) -> pd.DataFrame:
        """
        Stage 2: Generate annotations using LLM.

        Reads intermediate results from stage 1, calls LLM to generate
        annotations, and saves final results.

        Parameters
        ----------
        intermediate_file : str
            Path to intermediate CSV from preprocess stage.
        output_file : str
            Path to save final results CSV.
        config_file : str, optional
            Path to YAML config file. If None, uses default config.
        test : bool
            If True, only process the first 3 rows (for testing).
            Default: False
        checkpoint_interval : int
            Save intermediate results every N records to prevent data loss.
            Default: 100. Set to 0 to disable checkpointing.

        Returns
        -------
        pd.DataFrame
            Final results with columns:
            gs, annotation, pathways, PPIs, Final_prompt

        Examples
        --------
        >>> # Normal annotation
        >>> TwoStagePipeline.annotate(
        ...     intermediate_file="intermediate.csv",
        ...     output_file="output.csv",
        ...     config_file="config.yaml"
        ... )

        >>> # Test mode: only process first 3 rows
        >>> TwoStagePipeline.annotate(
        ...     intermediate_file="intermediate.csv",
        ...     output_file="output.csv",
        ...     test=True
        ... )

        >>> # Custom checkpoint interval
        >>> TwoStagePipeline.annotate(
        ...     intermediate_file="intermediate.csv",
        ...     output_file="output.csv",
        ...     checkpoint_interval=50  # Save every 50 records
        ... )
        """
        # Load config
        if config_file:
            config = PipelineConfig.from_yaml(config_file)
        else:
            config = PipelineConfig.default()

        # Create LLM provider
        provider = TwoStagePipeline._create_provider(config)

        # Read intermediate file
        print(f"Reading intermediate file: {intermediate_file}")
        inter_df = pd.read_csv(intermediate_file)

        # Test mode: only process first 3 rows
        if test:
            inter_df = inter_df.head(3)
            print("Test mode: processing only first 3 rows")

        # Get system prompt
        prompt_builder = PromptBuilder()
        system_prompt = prompt_builder.system_template

        # Checkpoint file path
        checkpoint_file = output_file + ".checkpoint" if checkpoint_interval > 0 else None

        # Process each row
        results = []
        for idx, (_, row) in enumerate(tqdm(inter_df.iterrows(), total=len(inter_df), desc="Generating annotations")):
            gs = row["gs"]
            row.get("genes", "")
            pathways = row.get("pathways", "")
            ppis = row.get("ppis", "")
            final_prompt = row.get("final_prompt", "")

            # Skip empty rows
            if not final_prompt or pd.isna(final_prompt):
                results.append({
                    "gs": gs,
                    "annotation": "",
                    "pathways": pathways,
                    "PPIs": ppis,
                    "Final_prompt": final_prompt
                })
                continue

            # Build messages and call LLM
            messages = [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": final_prompt}
            ]

            try:
                annotation = provider.generate(messages)
            except Exception as e:
                print(f"Warning: LLM call failed for '{gs}': {e}")
                annotation = f"Error: {str(e)}"

            results.append({
                "gs": gs,
                "annotation": annotation,
                "pathways": pathways,
                "PPIs": ppis,
                "Final_prompt": final_prompt
            })

            # Checkpoint: save intermediate results periodically
            if checkpoint_file and checkpoint_interval > 0:
                if (idx + 1) % checkpoint_interval == 0:
                    checkpoint_df = pd.DataFrame(results)
                    checkpoint_df.to_csv(checkpoint_file, index=False)
                    print(f"Checkpoint saved at {len(results)} records: {checkpoint_file}")

        # Create DataFrame and save final results
        result_df = pd.DataFrame(results)
        result_df.to_csv(output_file, index=False)
        print(f"Final results saved to: {output_file}")

        # Remove checkpoint file if exists (processing completed successfully)
        if checkpoint_file:
            checkpoint_path = Path(checkpoint_file)
            if checkpoint_path.exists():
                checkpoint_path.unlink()
                print("Checkpoint file removed (processing complete)")

        return result_df

    @staticmethod
    def preprocess(
        config_file: str,
        output_file: str = "intermediate.csv",
        deg_base_dir: Optional[str] = None,
        pathway_base_dir: Optional[str] = None,
        ppi_context: Optional[dict[str, str]] = None,
        test: bool = False,
        checkpoint_interval: int = 100,
    ) -> pd.DataFrame:
        """
        Stage 1: Preprocess DEG and enrichment data.

        Scans DEG folder, finds matching pathway files in multiple folders,
        filters them according to config, builds prompts, and saves
        intermediate results for later annotation.

        This method:
        1. Scans deg_dir for all CSV files
        2. For each DEG file, finds matching pathway files in all pathway_dirs
        3. Merges and deduplicates pathways from all sources
        4. Builds prompts and saves intermediate results

        Parameters
        ----------
        config_file : str
            Path to YAML config file with input paths (deg_dir, pathway_dirs)
        output_file : str
            Path to save intermediate results CSV
        deg_base_dir : str, optional
            Base directory for DEG files. If provided, the final DEG path
            will be: deg_base_dir / config.deg_dir
            If None, config.deg_dir is used as-is (backward compatible)
        pathway_base_dir : str, optional
            Base directory for pathway files. If provided, the final pathway
            paths will be: pathway_base_dir / each pathway_dir in config
            If None, pathway_dirs are used as-is (backward compatible)
        ppi_context : dict, optional
            Dictionary mapping gene set names to PPI context strings
        test : bool
            If True, only process the first 3 DEG files (for testing).
            Default: False
        checkpoint_interval : int
            Save intermediate results every N records to prevent data loss.
            Default: 100. Set to 0 to disable checkpointing.

        Returns
        -------
        pd.DataFrame
            Intermediate results with columns:
            gs, genes, pathways, ppis, final_prompt

        Examples
        --------
        >>> # With base directories (relative paths in config)
        >>> # config.yaml contains: deg_dir="deg/", pathway_dirs=["GO/", "KEGG/"]
        >>> TwoStagePipeline.preprocess(
        ...     config_file="config.yaml",
        ...     output_file="intermediate.csv",
        ...     deg_base_dir="/data/project1/",      # -> /data/project1/deg/
        ...     pathway_base_dir="/data/project1/"   # -> /data/project1/GO/, etc.
        ... )

        >>> # Without base directories (absolute paths in config, backward compatible)
        >>> # config.yaml contains: deg_dir="/abs/path/deg/", pathway_dirs=["/abs/path/GO/"]
        >>> TwoStagePipeline.preprocess(
        ...     config_file="config.yaml",
        ...     output_file="intermediate.csv"
        ... )

        >>> # Test mode: only process first 3 files
        >>> TwoStagePipeline.preprocess(
        ...     config_file="config.yaml",
        ...     output_file="intermediate.csv",
        ...     test=True
        ... )
        """
        # Load config
        config = PipelineConfig.from_yaml(config_file)

        if not config.deg_dir:
            raise ValueError("deg_dir must be specified in config file")

        # Resolve DEG directory path
        if deg_base_dir:
            deg_path = Path(deg_base_dir) / config.deg_dir
        else:
            deg_path = Path(config.deg_dir)

        if not deg_path.exists():
            raise FileNotFoundError(f"DEG directory not found: {deg_path}")

        # Resolve pathway directory paths
        resolved_pathway_dirs: list[Path] = []
        for pdir in config.pathway_dirs:
            if pathway_base_dir:
                resolved_pathway_dirs.append(Path(pathway_base_dir) / pdir)
            else:
                resolved_pathway_dirs.append(Path(pdir))

        # Scan DEG folder for CSV files
        deg_files = sorted(deg_path.glob("*.csv"))
        if not deg_files:
            raise ValueError(f"No CSV files found in DEG directory: {deg_path}")

        # Test mode: only process first 3 files
        if test:
            deg_files = deg_files[:3]
            print("Test mode: processing only first 3 files")

        print(f"Found {len(deg_files)} DEG files in {deg_path}")
        print(f"Pathway directories: {[str(p) for p in resolved_pathway_dirs]}")

        # Initialize prompt builder
        prompt_builder = PromptBuilder()

        # Checkpoint file path
        checkpoint_file = output_file + ".checkpoint" if checkpoint_interval > 0 else None

        # Process each DEG file
        results = []
        for idx, deg_file in enumerate(tqdm(deg_files, desc="Processing DEG files")):
            gs_name = deg_file.stem  # filename without extension

            # Read and filter genes
            try:
                deg_df = pd.read_csv(deg_file)
            except Exception as e:
                print(f"Warning: Failed to read {deg_file}: {e}")
                continue

            if "gene" not in deg_df.columns:
                print(f"Warning: No 'gene' column in {deg_file}, skipping")
                continue

            genes = TwoStagePipeline._filter_genes(
                deg_df,
                pvalue_threshold=config.gene_pvalue_threshold,
                log2fc_threshold=config.gene_log2fc_threshold,
                pvalue_column=config.gene_pvalue_column,
                log2fc_column=config.gene_log2fc_column,
                max_gene_num=config.max_gene_num,
            )

            # Skip if no genes after filtering
            if not genes:
                print(f"Warning: No genes for '{gs_name}' after filtering")
                results.append({
                    "gs": gs_name,
                    "genes": "",
                    "pathways": "",
                    "ppis": "",
                    "final_prompt": ""
                })
                continue

            # Find and merge pathways from all pathway directories
            all_pathways_with_pval = []  # List of (term, pvalue) tuples
            for pathway_dir in resolved_pathway_dirs:
                pathway_file = pathway_dir / f"{gs_name}.csv"
                if pathway_file.exists():
                    try:
                        enr_df = pd.read_csv(pathway_file)

                        # Get p-value column
                        pval_col = config.pathway_pvalue_column
                        if pval_col not in enr_df.columns:
                            for alt in ["Adjusted P-value", "padj", "FDR", "q-value", "pvalue"]:
                                if alt in enr_df.columns:
                                    pval_col = alt
                                    break

                        # Get term column
                        term_col = config.pathway_term_column
                        if term_col not in enr_df.columns:
                            for alt in ["Term", "term", "Pathway", "pathway", "Name", "name"]:
                                if alt in enr_df.columns:
                                    term_col = alt
                                    break

                        # Filter by p-value and collect
                        if pval_col in enr_df.columns and term_col in enr_df.columns:
                            filtered = enr_df[enr_df[pval_col] <= config.pathway_pvalue_threshold]
                            for _, row in filtered.iterrows():
                                all_pathways_with_pval.append((
                                    str(row[term_col]),
                                    float(row[pval_col])
                                ))
                    except Exception as e:
                        print(f"Warning: Failed to read {pathway_file}: {e}")

            # Sort by p-value, deduplicate, take top N
            all_pathways_with_pval.sort(key=lambda x: x[1])
            seen = set()
            unique_pathways = []
            for term, _ in all_pathways_with_pval:
                if term not in seen:
                    seen.add(term)
                    unique_pathways.append(term)
                    if len(unique_pathways) >= config.max_pathway_num:
                        break

            # Get PPI context if provided
            ppi = ""
            if ppi_context and gs_name in ppi_context:
                ppi = ppi_context[gs_name]

            # Build prompt
            messages = prompt_builder.build(
                genes=genes,
                pathways=unique_pathways if unique_pathways else None,
                additional_context=ppi if ppi else None,
            )
            final_prompt = next(
                (m["content"] for m in messages if m["role"] == "user"), ""
            )

            # Record result
            results.append({
                "gs": gs_name,
                "genes": ",".join(genes),
                "pathways": ",".join(unique_pathways) if unique_pathways else "",
                "ppis": ppi,
                "final_prompt": final_prompt
            })

            # Checkpoint: save intermediate results periodically
            if checkpoint_file and checkpoint_interval > 0:
                if (idx + 1) % checkpoint_interval == 0:
                    checkpoint_df = pd.DataFrame(results)
                    checkpoint_df.to_csv(checkpoint_file, index=False)
                    print(f"Checkpoint saved at {len(results)} records: {checkpoint_file}")

        # Create DataFrame and save final results
        result_df = pd.DataFrame(results)
        result_df.to_csv(output_file, index=False)
        print(f"Intermediate results saved to: {output_file}")
        print(f"Processed {len(results)} gene sets")

        # Remove checkpoint file if exists (processing completed successfully)
        if checkpoint_file:
            checkpoint_path = Path(checkpoint_file)
            if checkpoint_path.exists():
                checkpoint_path.unlink()
                print(f"Checkpoint file removed (processing complete)")

        return result_df

    @staticmethod
    def _create_provider(config: PipelineConfig):
        """
        Create LLM provider based on config.

        Parameters
        ----------
        config : PipelineConfig
            Configuration with LLM settings

        Returns
        -------
        BaseLLMProvider
            Configured LLM provider instance
        """
        provider_name = config.llm_provider.lower()

        if provider_name == "openai":
            from .llm.openai_provider import OpenAIProvider
            return OpenAIProvider(
                api_key=config.llm_api_key,
                model_id=config.llm_model_id,
                temperature=config.llm_temperature,
                base_url=config.llm_base_url,
            )
        elif provider_name == "anthropic":
            from .llm.anthropic_provider import AnthropicProvider
            return AnthropicProvider(
                api_key=config.llm_api_key,
                model_id=config.llm_model_id,
                temperature=config.llm_temperature,
            )
        elif provider_name == "litellm":
            from .llm.litellm_provider import LiteLLMProvider
            return LiteLLMProvider(
                api_key=config.llm_api_key,
                model_id=config.llm_model_id,
                temperature=config.llm_temperature,
                base_url=config.llm_base_url,
            )
        else:
            raise ValueError(f"Unknown LLM provider: {provider_name}")

    # Alias for backward compatibility
    preprocess_batch = preprocess
