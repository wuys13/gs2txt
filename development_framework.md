gs2txt/
├── src/

│   ├── __init__.py
│   ├── core.py                    # 核心注释逻辑
│   ├── llm/
│   │   ├── __init__.py
│   │   ├── base.py                # LLM 抽象基类
│   │   ├── openai_provider.py     # OpenAI 实现
│   │   ├── anthropic_provider.py  # Anthropic 实现
│   │   └── litellm_provider.py    # LiteLLM 实现
│   ├── enrichment/
│   │   ├── __init__.py
│   │   ├── pathway.py             # Pathway enrichment
│   │   ├── ppi.py                 # PPI 网络分析
│   │   └── go.py                  # GO enrichment
│   ├── prompts/
│   │   ├── __init__.py
│   │   ├── templates.py           # Prompt 模板
│   │   └── builder.py             # Prompt 构建器
│   ├── batch.py                   # 批处理逻辑
│   ├── cli.py                     # 命令行接口
│   └── utils.py                   # 工具函数
├── tests/
│   ├── __init__.py
│   ├── test_core.py
│   ├── test_llm_providers.py
│   ├── test_enrichment.py
│   └── fixtures/
│       ├── sample_degs.csv
│       └── sample_pathways.json
├── examples/
│   ├── basic_usage.py
│   ├── custom_llm.py
│   ├── batch_processing.py
│   └── notebooks/
│       └── tutorial.ipynb
├── docs/
│   ├── quickstart.md
│   ├── api_reference.md
│   ├── advanced_usage.md
│   └── custom_providers.md
├── data/                          # 示例数据
│   └── pathways/
├── pyproject.toml
├── README.md
├── LICENSE
└── CHANGELOG.md
