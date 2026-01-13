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
    >>> # Stage 1: Preprocess (no API needed)
    >>> TwoStagePipeline.preprocess(
    ...     deg_file="deg.csv",
    ...     enrichment_dir="enrichment/",
    ...     output_file="intermediate.csv",
    ...     config_file="config.yaml"
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
    def preprocess(
        deg_file: str,
        enrichment_dir: str,
        output_file: str,
        config_file: Optional[str] = None,
        group_column: str = "cluster",
        ppi_context: Optional[dict[str, str]] = None,
    ) -> pd.DataFrame:
        """
        Stage 1: Preprocess DEG and enrichment data.

        Reads differential expression genes and enrichment files,
        filters them according to config, builds prompts, and saves
        intermediate results for later annotation.

        Parameters
        ----------
        deg_file : str
            Path to differential expression genes CSV file.
            Must contain 'gene' column and group_column (e.g., 'cluster').
            Optional: 'pvalue', 'logFC' columns for filtering.
        enrichment_dir : str
            Directory containing enrichment CSV files.
            Files should be named as {cluster_name}.csv
            (e.g., cluster_1.csv, cluster_2.csv)
        output_file : str
            Path to save intermediate results CSV.
        config_file : str, optional
            Path to YAML config file. If None, uses default config.
        group_column : str
            Column name for grouping gene sets (default: "cluster")
        ppi_context : dict, optional
            Dictionary mapping cluster names to PPI context strings.
            Example: {"cluster_1": "Hub genes: TP53, MYC"}

        Returns
        -------
        pd.DataFrame
            Intermediate results with columns:
            gs, genes, pathways, ppis, final_prompt

        Examples
        --------
        >>> TwoStagePipeline.preprocess(
        ...     deg_file="deg.csv",
        ...     enrichment_dir="enrichment/",
        ...     output_file="intermediate.csv",
        ...     config_file="config.yaml",
        ...     group_column="cluster"
        ... )
        """
        # Load config
        if config_file:
            config = PipelineConfig.from_yaml(config_file)
        else:
            config = PipelineConfig.default()

        # Read DEG file
        print(f"Reading DEG file: {deg_file}")
        deg_df = pd.read_csv(deg_file)

        if "gene" not in deg_df.columns:
            raise ValueError("DEG file must contain a 'gene' column")

        if group_column not in deg_df.columns:
            raise ValueError(f"DEG file must contain '{group_column}' column")

        # Get unique clusters
        clusters = deg_df[group_column].unique()
        print(f"Found {len(clusters)} clusters: {list(clusters)}")

        # Prepare enrichment directory
        enrichment_path = Path(enrichment_dir)
        if not enrichment_path.exists():
            raise FileNotFoundError(f"Enrichment directory not found: {enrichment_dir}")

        # Initialize prompt builder
        prompt_builder = PromptBuilder()

        # Process each cluster
        results = []
        for cluster in tqdm(clusters, desc="Preprocessing clusters"):
            # Filter genes for this cluster
            cluster_df = deg_df[deg_df[group_column] == cluster]
            genes = TwoStagePipeline._filter_genes(
                cluster_df,
                pvalue_threshold=config.gene_pvalue_threshold,
                log2fc_threshold=config.gene_log2fc_threshold,
                pvalue_column=config.gene_pvalue_column,
                log2fc_column=config.gene_log2fc_column,
                max_gene_num=config.max_gene_num,
            )

            # Skip if no genes after filtering
            if not genes:
                print(f"Warning: No genes for cluster '{cluster}' after filtering")
                results.append({
                    "gs": cluster,
                    "genes": "",
                    "pathways": "",
                    "ppis": "",
                    "final_prompt": ""
                })
                continue

            # Load enrichment file for this cluster
            pathways = []
            enrichment_file = enrichment_path / f"{cluster}.csv"
            if enrichment_file.exists():
                enr_df = pd.read_csv(enrichment_file)
                pathways = TwoStagePipeline._filter_pathways(
                    enr_df,
                    pvalue_threshold=config.pathway_pvalue_threshold,
                    pvalue_column=config.pathway_pvalue_column,
                    term_column=config.pathway_term_column,
                    max_pathway_num=config.max_pathway_num,
                )
            else:
                print(f"Warning: Enrichment file not found for '{cluster}': {enrichment_file}")

            # Get PPI context if provided
            ppi = ""
            if ppi_context and cluster in ppi_context:
                ppi = ppi_context[cluster]

            # Build prompt
            messages = prompt_builder.build(
                genes=genes,
                pathways=pathways if pathways else None,
                additional_context=ppi if ppi else None,
            )
            final_prompt = next(
                (m["content"] for m in messages if m["role"] == "user"), ""
            )

            # Record result
            results.append({
                "gs": cluster,
                "genes": ",".join(genes),
                "pathways": ",".join(pathways) if pathways else "",
                "ppis": ppi,
                "final_prompt": final_prompt
            })

        # Create DataFrame and save
        result_df = pd.DataFrame(results)
        result_df.to_csv(output_file, index=False)
        print(f"Intermediate results saved to: {output_file}")

        return result_df

    @staticmethod
    def annotate(
        intermediate_file: str,
        output_file: str,
        config_file: Optional[str] = None,
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

        Returns
        -------
        pd.DataFrame
            Final results with columns:
            gs, annotation, pathways, PPIs, Final_prompt

        Examples
        --------
        >>> TwoStagePipeline.annotate(
        ...     intermediate_file="intermediate.csv",
        ...     output_file="output.csv",
        ...     config_file="config.yaml"
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

        # Get system prompt
        prompt_builder = PromptBuilder()
        system_prompt = prompt_builder.system_template

        # Process each row
        results = []
        for _, row in tqdm(inter_df.iterrows(), total=len(inter_df), desc="Generating annotations"):
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

        # Create DataFrame and save
        result_df = pd.DataFrame(results)
        result_df.to_csv(output_file, index=False)
        print(f"Final results saved to: {output_file}")

        return result_df

    @staticmethod
    def preprocess_batch(
        config_file: str,
        output_file: str = "intermediate.csv",
        ppi_context: Optional[dict[str, str]] = None,
    ) -> pd.DataFrame:
        """
        Batch preprocess: Scan DEG folder, find matching pathway files in multiple folders.

        This method:
        1. Scans deg_dir for all CSV files
        2. For each DEG file, finds matching pathway files in all pathway_dirs
        3. Merges and deduplicates pathways from all sources
        4. Builds prompts and saves intermediate results

        Parameters
        ----------
        config_file : str
            Path to YAML config file with input paths
        output_file : str
            Path to save intermediate results CSV
        ppi_context : dict, optional
            Dictionary mapping gene set names to PPI context strings

        Returns
        -------
        pd.DataFrame
            Intermediate results with columns:
            gs, genes, pathways, ppis, final_prompt

        Examples
        --------
        >>> TwoStagePipeline.preprocess_batch(
        ...     config_file="config.yaml",
        ...     output_file="intermediate.csv"
        ... )
        """
        # Load config
        config = PipelineConfig.from_yaml(config_file)

        if not config.deg_dir:
            raise ValueError("deg_dir must be specified in config file")

        deg_path = Path(config.deg_dir)
        if not deg_path.exists():
            raise FileNotFoundError(f"DEG directory not found: {config.deg_dir}")

        # Scan DEG folder for CSV files
        deg_files = sorted(deg_path.glob("*.csv"))
        if not deg_files:
            raise ValueError(f"No CSV files found in DEG directory: {config.deg_dir}")

        print(f"Found {len(deg_files)} DEG files in {config.deg_dir}")
        print(f"Pathway directories: {config.pathway_dirs}")

        # Initialize prompt builder
        prompt_builder = PromptBuilder()

        # Process each DEG file
        results = []
        for deg_file in tqdm(deg_files, desc="Processing DEG files"):
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
            for pathway_dir in config.pathway_dirs:
                pathway_file = Path(pathway_dir) / f"{gs_name}.csv"
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

        # Create DataFrame and save
        result_df = pd.DataFrame(results)
        result_df.to_csv(output_file, index=False)
        print(f"Intermediate results saved to: {output_file}")
        print(f"Processed {len(results)} gene sets")

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
