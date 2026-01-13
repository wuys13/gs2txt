# 🧬 gs2txt

> LLM-powered biological process annotation for gene sets

[![PyPI version](https://badge.fury.io/py/gs2txt.svg)](https://badge.fury.io/py/gs2txt)
[![Tests](https://github.com/wuys13/gs2txt/workflows/tests/badge.svg)](https://github.com/wuys13/gs2txt/actions)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

**gs2txt** uses large language models to generate concise, biologically meaningful descriptions of gene sets. It intelligently combines gene functions with pathway enrichment results to infer the dominant biological process.

---

## ✨ Features

- 🤖 **Multiple LLM providers**: OpenAI, Anthropic Claude, LiteLLM, or custom
- 🧪 **Flexible enrichment**: Built-in pathway enrichment or bring your own
- 🔧 **Customizable prompts**: Tailor prompts for specific domains or output formats
- 📊 **Batch processing**: Process multiple gene sets from CSV files
- 🐍 **Simple API**: One-line annotation or full programmatic control
- 🧪 **Well tested**: Comprehensive test suite with >90% coverage

---

## 🚀 Quick Start

### Installation

```bash
pip install gs2txt
```

### Basic Usage

```python
import pandas as pd
from gs2txt import GeneSetAnnotator
from gs2txt.llm import OpenAIProvider

# Your differential expression results
deg_df = pd.DataFrame({
    "gene": ["TP53", "MYC", "BRCA1", "EGFR", "KRAS"],
    "logFC": [2.3, 1.8, -1.5, 2.1, 1.9]
})

# Setup LLM provider
provider = OpenAIProvider(
    api_key="your-openai-key",
    model_id="gpt-4",
    temperature=0.0
)

# Create annotator
annotator = GeneSetAnnotator(llm_provider=provider)

# Generate annotation
result = annotator.annotate(deg_df)
print(result)
```

**Output:**

```
Process: DNA damage response and cell cycle regulation

This gene set is enriched for critical tumor suppressors (TP53, BRCA1) 
and oncogenes (MYC, EGFR, KRAS) that collectively regulate cell cycle 
checkpoints and apoptotic responses to genomic stress.
```

---

## 🖥️ Command-Line Interface

### CLI Installation

After installing gs2txt, the `gs2txt` command will be available:

```bash
pip install gs2txt
# or for development
pip install -e .
```

### CLI Usage

Process gene sets from CSV files directly from the command line:

```bash
gs2txt --input genes.csv --output results.csv --api-key YOUR_API_KEY
```

#### Required Arguments

- `-i, --input`: Input CSV file containing gene data (must have a 'gene' column)
- `-o, --output`: Output CSV file path for annotated results

#### LLM Configuration

- `--provider`: LLM provider (`openai`, `anthropic`, `litellm`; default: `openai`)
- `--api-key`: API key (or set `GS2TXT_API_KEY` environment variable)
- `--model`: Model ID (default: `gpt-4`)
- `--temperature`: Sampling temperature (default: `0.0`)

#### Annotation Parameters

- `--max-genes`: Maximum number of genes to include (default: `60`)
- `--max-pathways`: Maximum number of pathways to include (default: `10`)
- `--enrichment`: Enrichment method (`pathway`, `none`; default: `pathway`)
- `--group-by`: Column name to group by (e.g., `cluster`, `celltype`)

#### Example Commands

**Basic usage with OpenAI:**
```bash
gs2txt --input data/deg_results.csv --output data/annotated_results.csv \
       --api-key sk-xxx --model gpt-4
```

**Process multiple clusters:**
```bash
# Input CSV should have 'gene' and 'cluster' columns
gs2txt --input data/clusters.csv --output data/cluster_annotations.csv \
       --api-key sk-xxx --group-by cluster
```

**Use Anthropic Claude:**
```bash
gs2txt --input genes.csv --output results.csv \
       --provider anthropic --api-key sk-ant-xxx \
       --model claude-sonnet-4-20250514
```

**Use environment variables:**
```bash
export GS2TXT_API_KEY=sk-xxx
export GS2TXT_PROVIDER=openai
export GS2TXT_MODEL=gpt-4

gs2txt --input genes.csv --output results.csv
```

#### Input File Format

The input CSV must contain a `gene` column:

```csv
gene,logFC,pvalue
TP53,2.3,0.001
MYC,1.8,0.002
BRCA1,-1.5,0.003
```

For grouped processing, add a grouping column:

```csv
cluster,gene,logFC
cluster_1,TP53,2.3
cluster_1,MYC,1.8
cluster_2,CD4,1.5
cluster_2,CD8A,1.2
```

#### Output Format

The output CSV will contain all original columns plus an `annotation` column with the LLM-generated biological process descriptions.

---

## 📋 Usage Scenarios (使用场景)

gs2txt 提供三种使用场景，适应不同需求：

### Scenario 1: Batch CSV Processing (批量处理 CSV)

**适用场景**：处理单个或多个 CSV 文件，自动输出结果到新 CSV

```bash
cd examples
export LITELLM_API_KEY=your-api-key
python scenario1_batch_csv.py
```

**示例脚本**：[`examples/scenario1_batch_csv.py`](examples/scenario1_batch_csv.py)

**特点**：
- 使用 `BatchProcessor` 一键处理
- 支持单文件和多 cluster 分组处理
- 自动输出 CSV：`gs, annotation` 格式

```python
from gs2txt import GeneSetAnnotator
from gs2txt.llm import LiteLLMProvider
from gs2txt.batch import BatchProcessor

provider = LiteLLMProvider(api_key="...", model_id="gpt-4")
annotator = GeneSetAnnotator(llm_provider=provider)
processor = BatchProcessor(annotator)

# 处理单个文件
processor.process_single_file(
    input_path="genes.csv",
    output_path="output.csv",
    group_column="cluster",  # 可选：按 cluster 分组
    max_gene_num=60,
    pvalue_threshold=0.05
)
```

---

### Scenario 2: Python API (代码集成)

**适用场景**：在代码中集成 gs2txt，获取文本结果进行进一步处理

```bash
cd examples
export LITELLM_API_KEY=your-api-key
python scenario2_api.py
```

**示例脚本**：[`examples/scenario2_api.py`](examples/scenario2_api.py)

**特点**：
- `annotate()` 返回字符串，灵活处理
- 支持预计算通路、额外上下文
- 可自定义过滤参数

```python
from gs2txt import GeneSetAnnotator
from gs2txt.llm import LiteLLMProvider

provider = LiteLLMProvider(api_key="...", model_id="gpt-4")
annotator = GeneSetAnnotator(llm_provider=provider)

# 直接获取注释文本
result = annotator.annotate(
    deg_df,
    max_gene_num=60,
    pvalue_threshold=0.05,
    additional_context="PPI Hub genes: TP53, MYC"  # 可选
)
print(result)  # 字符串：生物学过程描述
```

---

### Scenario 3: Two-Stage Pipeline (两阶段处理) ⭐推荐

**适用场景**：大规模数据处理，需要检查中间结果，分离数据预处理和 API 调用

```bash
cd examples

# 阶段一：预处理（无需 API）
python scenario3_two_stage.py batch

# 检查中间结果
python scenario3_two_stage.py check

# 阶段二：注释（需要 API）
export LITELLM_API_KEY=your-api-key
python scenario3_two_stage.py annotate
```

**示例脚本**：[`examples/scenario3_two_stage.py`](examples/scenario3_two_stage.py)

**特点**：
- **阶段一**：读取 DEG + 通路文件，过滤，保存中间结果（无需 API）
- **阶段二**：读取中间结果，调用 LLM，生成最终注释（需要 API）
- 支持多个 DEG 文件夹和多个通路来源（GO, KEGG, Reactome）
- YAML 配置文件控制所有参数

**配置文件** (`config.yaml`)：
```yaml
input:
  deg_dir: "../data/deg/"           # DEG 文件夹
  pathway_dirs:                      # 多个通路文件夹
    - "../data/GO/"
    - "../data/KEGG/"
    - "../data/Reactome/"

gene_filter:
  pvalue_threshold: 0.05
  log2fc_threshold: 1.0
  max_gene_num: 60

pathway_filter:
  pvalue_threshold: 0.05
  max_pathway_num: 10

llm:
  provider: "litellm"
  model_id: "gpt-4"
  api_key_env: "LITELLM_API_KEY"
```

**代码调用**：
```python
from gs2txt.pipeline import TwoStagePipeline

# 阶段一：批量预处理
TwoStagePipeline.preprocess_batch(
    config_file="config.yaml",
    output_file="intermediate.csv"
)

# 阶段二：LLM 注释
TwoStagePipeline.annotate(
    intermediate_file="intermediate.csv",
    output_file="final_output.csv",
    config_file="config.yaml"
)
```

**输出格式**：
- 中间结果：`gs, genes, pathways, ppis, final_prompt`
- 最终结果：`gs, annotation, pathways, PPIs, Final_prompt`

---

## 📖 Usage Examples

### Example 1: Use Anthropic Claude

```python
from gs2txt.llm import AnthropicProvider

provider = AnthropicProvider(
    api_key="your-anthropic-key",
    model_id="claude-sonnet-4-20250514",
    temperature=0.0
)

annotator = GeneSetAnnotator(llm_provider=provider)
result = annotator.annotate(deg_df)
```

### Example 2: All Available Parameters

```python
from gs2txt import GeneSetAnnotator
from gs2txt.llm import OpenAIProvider

# Configure LLM provider with all options
provider = OpenAIProvider(
    api_key="your-openai-key",
    model_id="gpt-4",              # Model to use
    temperature=0.0,                # Sampling temperature (0.0-1.0)
    base_url=None                   # Optional: custom API endpoint
)

# Create annotator with all options
annotator = GeneSetAnnotator(
    llm_provider=provider,
    enrichment_method="pathway",    # "pathway", "custom", or None
    prompt_builder=None             # Optional: custom PromptBuilder
)

# Annotate with all parameters
result = annotator.annotate(
    deg_df,                         # DataFrame with 'gene' column
    max_gene_num=60,                # Maximum genes to include
    max_pathway_num=10,             # Maximum pathways to include
    pathways=None,                  # Optional: pre-computed pathway list
    compute_enrichment=True,        # Whether to run enrichment
    additional_context=None         # Optional: extra context string
)

print(result)  # Returns: str (LLM annotation text)
```

### Example 3: Use pre-computed pathways

```python
pathways = [
    "T cell activation",
    "Immune response",
    "Cytokine signaling"
]

# Pathways will be used directly, enrichment will be skipped
result = annotator.annotate(
    deg_df,
    pathways=pathways
)
```

### Example 3: Add PPI or other context

```python
ppi_context = """
PPI Network Analysis:
- Hub genes: TP53, MYC, EGFR
- Main module: DNA damage response
"""

result = annotator.annotate(
    deg_df,
    additional_context=ppi_context
)
```

### Example 4: Batch process multiple gene sets

```python
# Process multiple gene sets
gene_sets = {
    "cluster_1": deg_df_1,
    "cluster_2": deg_df_2,
    "cluster_3": deg_df_3
}

results = {}
for name, df in gene_sets.items():
    results[name] = annotator.annotate(df)
    print(f"{name}: {results[name]}")
```

### Example 5: Custom prompt template

```python
from gs2txt.prompts.builder import PromptBuilder

custom_builder = PromptBuilder(
    system_template="You are a cancer genomics expert...",
    user_template="Identify the cancer hallmark: {genes}..."
)

annotator = GeneSetAnnotator(
    llm_provider=provider,
    prompt_builder=custom_builder
)
```

---

## 🔧 Advanced Configuration

### Custom LLM Provider

Implement your own LLM provider:

```python
from gs2txt.llm.base import BaseLLMProvider

class MyCustomProvider(BaseLLMProvider):
    def generate(self, messages):
        # Your custom LLM call
        return response_text
  
    def validate_config(self):
        return True

provider = MyCustomProvider(model_id="my-model")
annotator = GeneSetAnnotator(provider)
```

### Custom Enrichment Method

```python
from gs2txt.enrichment import BaseEnrichment
import pandas as pd

class MyEnrichment(BaseEnrichment):
    def enrich(self, genes: list, **kwargs) -> pd.DataFrame:
        # Your enrichment logic
        # Return DataFrame with 'Term' and 'Adjusted P-value' columns
        return pd.DataFrame({
            "Term": ["pathway1", "pathway2"],
            "Adjusted P-value": [0.01, 0.02]
        })

annotator = GeneSetAnnotator(
    llm_provider=provider,
    enrichment_method=MyEnrichment()
)
```

---

## 🧪 Testing

```bash
# Install dev dependencies
pip install -e ".[dev]"

# Run tests
pytest

# With coverage
pytest --cov=gs2txt --cov-report=html
```

---

## 📚 Documentation

Full documentation is available at: **https://wuys13.github.io/gs2txt/**

- [Getting Started](https://wuys13.github.io/gs2txt/getting-started/quickstart/)
- [Usage Scenarios](https://wuys13.github.io/gs2txt/scenarios/scenario1/)
- [API Reference](https://wuys13.github.io/gs2txt/api/annotator/)
- [Changelog](https://wuys13.github.io/gs2txt/changelog/)

---

---

## 🤝 Contributing

Contributions welcome! Please see [CONTRIBUTING.md](CONTRIBUTING.md).

### Development Setup

```bash
git clone https://github.com/wuys13/gs2txt.git
cd gs2txt
pip install -e ".[dev]"
pre-commit install
```

---

## 📄 License

MIT License - see [LICENSE](LICENSE) file.

---

## 🙏 Acknowledgments

- Inspired by the need for interpretable functional genomics
- Built on top of excellent tools: GSEApy
- Thanks to the single-cell genomics community

---

## 📧 Contact

- **Issues**: [GitHub Issues](https://github.com/wuys13/gs2txt/issues)
- **Discussions**: [GitHub Discussions](https://github.com/wuys13/gs2txt/discussions)
- **Email**: 80359555@qq.com

---

## ⭐ Citation

If you use geneset-annotator in your research, please cite:

```bibtex
@software{gs2txt,
  title = {gs2txt: LLM-powered gene set annotation},
  author = {Yushuai Wu},
  year = {2025},
  url = {https://github.com/wuys13/gs2txt}
}
```
