"""
Prompt building utilities for geneset-annotator.
"""

from typing import List, Optional, Dict


class PromptBuilder:
    """Builder for LLM prompts."""
    
    def __init__(
        self,
        system_template: Optional[str] = None,
        user_template: Optional[str] = None,
    ):
        """
        Initialize prompt builder with custom templates.
        
        Parameters
        ----------
        system_template : str, optional
            Custom system prompt template
        user_template : str, optional
            Custom user prompt template
        """
        self.system_template = system_template or self._default_system_template()
        self.user_template = user_template or self._default_user_template()
    
    @staticmethod
    def _default_system_template() -> str:
        return (
            "You are a domain expert in molecular biology and functional genomics. "
            "You specialize in interpreting gene sets and pathway enrichment results "
            "to derive concise, biologically meaningful process-level annotations. "
            "Your outputs should resemble Gene Ontology Biological Process or "
            "mechanism-level descriptions used in scientific literature."
        )
    
    @staticmethod
    def _default_user_template() -> str:
        return (
            "Your task is to infer the most specific and informative biological process "
            "that best characterizes this gene set, based on gene functions and enriched pathways.\n\n"
            "Input information:\n\n"
            "[Gene set]\n"
            "{genes}\n\n"
            "{pathways_section}"
            "{additional_context_section}"
            "Analyze the gene set as follows:\n"
            "1. Identify major functional themes or modules represented by the genes.\n"
            "2. Use the enriched pathways to validate or refine these themes.\n"
            "3. Abstract these findings into a single dominant biological process.\n\n"
            "Output requirements:\n"
            "- Begin with: Process: <concise process name>\n"
            "- Use a specific, mechanism-level process name (3–8 words).\n"
            "- Provide a brief justification (2–4 sentences).\n"
            "- Base all statements on the provided genes and pathways.\n"
            "- If no specific process can be resolved, state:\n"
            "  Process: Unresolved functional program\n"
        )
    
    def build(
        self,
        genes: List[str],
        pathways: Optional[List[str]] = None,
        additional_context: Optional[str] = None,
    ) -> List[Dict[str, str]]:
        """
        Build message list for LLM.
        
        Parameters
        ----------
        genes : List[str]
            Gene symbols
        pathways : List[str], optional
            Enriched pathway terms
        additional_context : str, optional
            Additional context (e.g., PPI info, cell type)
        
        Returns
        -------
        List[Dict[str, str]]
            Messages for LLM API
        """
        # Format genes
        genes_str = ", ".join(genes)
        
        # Format pathways section
        pathways_section = ""
        if pathways is not None and len(pathways) > 0:
            pathways_str = "\n".join(f"- {p}" for p in pathways)
            pathways_section = f"[Enriched pathways]\n{pathways_str}\n\n"
        
        # Format additional context
        additional_context_section = ""
        if additional_context:
            additional_context_section = f"[Additional context]\n{additional_context}\n\n"
        
        # Build user prompt
        user_content = self.user_template.format(
            genes=genes_str,
            pathways_section=pathways_section,
            additional_context_section=additional_context_section
        )
        
        return [
            {"role": "system", "content": self.system_template},
            {"role": "user", "content": user_content}
        ]


class CustomPromptBuilder(PromptBuilder):
    """
    Example of custom prompt builder for specific use cases.
    
    Users can subclass PromptBuilder to customize prompts for:
    - Different output formats (JSON, structured data)
    - Domain-specific requirements (cancer, development, immunity)
    - Multi-language support
    """
    
    def __init__(self, output_format: str = "text"):
        """
        Parameters
        ----------
        output_format : str
            'text', 'json', or 'structured'
        """
        self.output_format = output_format
        super().__init__()
    
    def _default_user_template(self) -> str:
        if self.output_format == "json":
            return (
                "Analyze this gene set and return a JSON object with:\n"
                "- process_name: concise biological process (3-8 words)\n"
                "- confidence: high/medium/low\n"
                "- justification: brief explanation (2-4 sentences)\n"
                "- key_genes: top 5 driver genes\n\n"
                "[Gene set]\n{genes}\n\n"
                "{pathways_section}"
                "{additional_context_section}"
            )
        else:
            return super()._default_user_template()
