# Custom Prompts

Customize prompts for domain-specific applications.

## PromptBuilder Class

The `PromptBuilder` class constructs prompts sent to the LLM.

```python
from gs2txt.prompts.builder import PromptBuilder

builder = PromptBuilder(
    system_template="Your system prompt...",
    user_template="Your user prompt with {genes} and {pathways}..."
)
```

## Default Templates

### System Prompt

```
You are an expert in genomics and bioinformatics. Your task is to analyze
gene sets and provide concise, biologically meaningful descriptions of
their function based on the genes and their enriched pathways.
```

### User Prompt

```
Analyze the following gene set and provide a brief description of the
dominant biological process or function.

Genes: {genes}

Enriched Pathways: {pathways}

Additional Context: {additional_context}

Provide a concise description (2-3 sentences) of the main biological
theme represented by this gene set.
```

## Template Variables

Available variables for user templates:

| Variable | Description | Example |
|----------|-------------|---------|
| `{genes}` | Comma-separated gene list | `"TP53, MYC, BRCA1"` |
| `{pathways}` | Newline-separated pathways | `"DNA damage\nCell cycle"` |
| `{additional_context}` | Extra context string | `"Hub genes: TP53"` |

## Custom Templates

### Cancer Research

```python
from gs2txt.prompts.builder import PromptBuilder

cancer_builder = PromptBuilder(
    system_template="""You are a cancer genomics expert specializing in
tumor biology and oncogenic pathways. Analyze gene sets to identify
cancer hallmarks and potential therapeutic targets.""",

    user_template="""Analyze this cancer-related gene set:

Differentially Expressed Genes: {genes}

Enriched Cancer Pathways: {pathways}

PPI Network Information: {additional_context}

Identify:
1. The primary cancer hallmark(s) represented
2. Key driver genes
3. Potential therapeutic implications

Keep your response concise (3-4 sentences)."""
)

annotator = GeneSetAnnotator(
    llm_provider=provider,
    prompt_builder=cancer_builder
)
```

### Immunology

```python
immuno_builder = PromptBuilder(
    system_template="""You are an immunology expert. Analyze immune cell
gene signatures to identify cell types, activation states, and immune
processes.""",

    user_template="""Analyze this immune gene signature:

Genes: {genes}

Immune Pathways: {pathways}

Cell Context: {additional_context}

Describe:
1. The immune cell type(s) involved
2. Activation or differentiation state
3. Key immune processes

Response should be 2-3 sentences."""
)
```

### Drug Response

```python
drug_builder = PromptBuilder(
    system_template="""You are a pharmacogenomics expert. Analyze gene
expression changes to identify drug response mechanisms and potential
biomarkers.""",

    user_template="""Analyze drug-induced gene expression changes:

Responsive Genes: {genes}

Affected Pathways: {pathways}

Drug Information: {additional_context}

Identify:
1. Primary mechanism of drug action
2. Potential resistance mechanisms
3. Suggested biomarkers

Keep response to 3-4 sentences."""
)
```

## Advanced Customization

### Structured Output

Request structured responses:

```python
structured_builder = PromptBuilder(
    system_template="You are a genomics expert. Always respond in JSON format.",

    user_template="""Analyze this gene set and return JSON:

Genes: {genes}
Pathways: {pathways}

Return:
{{
  "biological_process": "string",
  "confidence": "high/medium/low",
  "key_genes": ["list"],
  "summary": "string"
}}"""
)
```

### Multi-language Support

```python
chinese_builder = PromptBuilder(
    system_template="你是一位基因组学专家。请用中文分析基因集并给出简洁的生物学描述。",

    user_template="""分析以下基因集：

基因: {genes}

富集通路: {pathways}

请用2-3句话描述该基因集的主要生物学功能。"""
)
```

### Comparative Analysis

```python
comparative_builder = PromptBuilder(
    system_template="""You are a comparative genomics expert. Analyze
gene sets in the context of provided reference data.""",

    user_template="""Compare this gene set to known signatures:

Query Genes: {genes}

Enriched Pathways: {pathways}

Reference Context: {additional_context}

Describe:
1. Similarity to known signatures
2. Unique features of this gene set
3. Biological interpretation"""
)
```

## Using with GeneSetAnnotator

```python
from gs2txt import GeneSetAnnotator
from gs2txt.llm import OpenAIProvider
from gs2txt.prompts.builder import PromptBuilder

# Create custom builder
builder = PromptBuilder(
    system_template="Your system prompt...",
    user_template="Your user template with {genes}..."
)

# Create annotator with custom prompts
provider = OpenAIProvider(api_key="...", model_id="gpt-4")
annotator = GeneSetAnnotator(
    llm_provider=provider,
    prompt_builder=builder
)

# Use as normal
result = annotator.annotate(
    deg_df,
    additional_context="Extra context here"
)
```

## Tips

1. **Be specific** in your system prompt about the expected output format
2. **Include examples** in complex prompts for better results
3. **Test with different LLMs** - some may interpret prompts differently
4. **Use additional_context** for sample-specific information
5. **Keep prompts concise** to stay within token limits
