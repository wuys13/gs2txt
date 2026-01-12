"""
场景2：Python API调用 - 返回文本结果
Scenario 2: Python API - Returns text results

运行方式 / Usage:
    export LITELLM_API_KEY=your-api-key
    python scenario2_api.py

说明 / Description:
    这个脚本展示如何在Python代码中调用gs2txt API。
    annotate()方法返回字符串文本，可以直接使用或进一步处理。

    重要：基因处理逻辑
    - 所有基因作为一个整体列表进行富集分析和LLM输入
    - 不是单个基因循环，而是整个基因列表作为一个单元处理

    输出格式：
    - annotate() 返回字符串：LLM生成的生物学过程描述（2-4句话）
    - 不含 "Process:" 或 "Justification:" 等标签
"""

import os
import pandas as pd
from pathlib import Path
from gs2txt import GeneSetAnnotator
from gs2txt.llm import LiteLLMProvider, OpenAIProvider, AnthropicProvider
from gs2txt.batch import BatchProcessor


# ==============================================
# 配置默认的LiteLLM Provider
# ==============================================
def create_default_provider():
    """创建默认的LiteLLM provider（使用推荐配置）"""
    LITELLM_API_KEY = os.getenv("LITELLM_API_KEY")

    if not LITELLM_API_KEY:
        raise ValueError(
            "需要设置 LITELLM_API_KEY 环境变量\n"
            "请运行: export LITELLM_API_KEY=your-api-key"
        )

    model_id = "us.anthropic.claude-haiku-4-5-20251001-v1:0"

    # 创建LiteLLMProvider
    provider = LiteLLMProvider(
        api_key=LITELLM_API_KEY,
        model_id=model_id,
        temperature=0.0,
        base_url="https://litellm.thesaisai.com/"
    )

    return provider


# ==============================================
# 示例1：基本用法 - LiteLLM（推荐）
# ==============================================
def example1_basic_litellm():
    """
    最简单的用法 - 使用LiteLLM

    注意：所有基因作为一个整体列表进行富集分析和LLM输入
    返回值：字符串（生物学过程描述，不含标签）
    """
    print("\n" + "=" * 60)
    print("示例1：基本用法（LiteLLM）")
    print("=" * 60)

    # 准备基因数据
    deg_df = pd.DataFrame({
        "gene": ["TP53", "MYC", "BRCA1", "EGFR", "KRAS"],
        "logFC": [2.3, 1.8, -1.5, 2.1, 1.9],
        "pvalue": [0.001, 0.002, 0.003, 0.001, 0.002]
    })

    # 配置LiteLLM provider
    provider = create_default_provider()

    # 创建annotator
    annotator = GeneSetAnnotator(
        llm_provider=provider,
        enrichment_method="pathway"       # 自动富集分析
    )

    # 调用 - 返回字符串（所有基因作为整体，内置过滤）
    result = annotator.annotate(
        deg_df,
        pvalue_threshold=0.05,
        log2fc_threshold=1.0
    )

    print(f"\n✓ 结果类型: {type(result)}")  # <class 'str'>
    print(f"✓ 结果内容:\n{result}\n")


# ==============================================
# 示例2：使用所有可配置参数
# ==============================================
def example2_all_parameters():
    """展示所有可用参数"""
    print("\n" + "=" * 60)
    print("示例2：所有可配置参数")
    print("=" * 60)

    deg_df = pd.DataFrame({
        "gene": ["TP53", "MYC", "BRCA1"],
        "logFC": [2.3, 1.8, -1.5],
        "pvalue": [0.001, 0.002, 0.003]
    })

    # Provider配置
    provider = create_default_provider()

    # Annotator配置
    annotator = GeneSetAnnotator(
        llm_provider=provider,
        enrichment_method="pathway",       # "pathway" 或 None
        prompt_builder=None                # 可选：自定义prompt
    )

    # 完整的annotate参数（所有基因作为整体，内置过滤）
    result = annotator.annotate(
        deg_df,                            # DataFrame，必须有'gene'列
        max_gene_num=60,                   # 最多使用多少个基因
        max_pathway_num=10,                # 最多使用多少个通路
        pathways=None,                     # 可选：预计算的通路列表
        compute_enrichment=True,           # 是否运行富集分析
        additional_context=None,           # 可选：额外上下文
        pvalue_threshold=0.05,             # P值阈值（内置过滤）
        log2fc_threshold=1.0               # Log2FC阈值（内置过滤）
    )

    print(f"\n✓ 结果:\n{result}\n")


# ==============================================
# 示例3：批量处理多个基因集并保存CSV
# ==============================================
def example3_batch_processing():
    """
    批量处理多个cluster，输出到CSV

    输出格式：gs, annotation（每个cluster一行）
    """
    print("\n" + "=" * 60)
    print("示例3：批量处理多个基因集")
    print("=" * 60)

    # 多个基因集（例如从聚类分析得到）
    gene_sets = {
        "cluster_1": pd.DataFrame({"gene": ["TP53", "MYC", "BRCA1"]}),
        "cluster_2": pd.DataFrame({"gene": ["CD4", "CD8A", "IL2"]}),
        "cluster_3": pd.DataFrame({"gene": ["EGFR", "KRAS", "BRAF"]}),
    }

    provider = create_default_provider()

    annotator = GeneSetAnnotator(
        llm_provider=provider,
        enrichment_method="pathway"
    )

    # 循环处理每个基因集（每个基因集作为整体）
    results = []
    for name, df in gene_sets.items():
        print(f"\n处理 {name}（所有基因作为整体）...")
        annotation = annotator.annotate(df, max_gene_num=60)
        results.append({"gs": name, "annotation": annotation})
        print(f"✓ {name}: {annotation[:80]}...")  # 只打印前80字符

    # 保存为CSV
    result_df = pd.DataFrame(results)
    result_df.to_csv("output_batch.csv", index=False)
    print(f"\n✓ 结果已保存到: output_batch.csv")
    print("输出格式：gs, annotation")

    return results


# ==============================================
# 示例4：处理CSV文件中的分组数据
# ==============================================
def example4_process_csv_with_groups():
    """
    从CSV读取并按cluster分组处理

    输出格式：gs, annotation（每个cluster一行）
    """
    print("\n" + "=" * 60)
    print("示例4：处理CSV中的分组数据")
    print("=" * 60)

    provider = create_default_provider()
    annotator = GeneSetAnnotator(llm_provider=provider)
    processor = BatchProcessor(annotator)

    # 使用BatchProcessor处理（自动分组）
    processor.process_single_file(
        input_path="../data/sample_clustered_input.csv",
        output_path="output_with_annotations.csv",
        group_column="cluster",
        max_gene_num=50,
        max_pathway_num=10,
        pvalue_threshold=0.05
    )

    print("✓ 结果已保存到: output_with_annotations.csv")
    print("输出格式：gs, annotation（每个cluster一行）")


# ==============================================
# 示例5：跳过富集分析（更快）
# ==============================================
def example5_no_enrichment():
    """跳过富集分析，直接用基因列表（所有基因作为整体）"""
    print("\n" + "=" * 60)
    print("示例5：跳过富集分析（更快）")
    print("=" * 60)

    deg_df = pd.DataFrame({
        "gene": ["TP53", "MYC", "BRCA1"],
        "logFC": [2.3, 1.8, -1.5],
        "pvalue": [0.001, 0.002, 0.003]
    })

    provider = create_default_provider()

    # enrichment_method=None 跳过富集
    annotator = GeneSetAnnotator(
        llm_provider=provider,
        enrichment_method=None             # 不做富集分析
    )

    # 所有基因作为整体进行注释（不做富集，内置过滤）
    result = annotator.annotate(
        deg_df,
        pvalue_threshold=0.05,
        compute_enrichment=False           # 确保不运行富集
    )

    print(f"\n✓ 结果:\n{result}\n")


# ==============================================
# 示例6：使用预计算的通路
# ==============================================
def example6_precomputed_pathways():
    """使用已有的通路结果"""
    print("\n" + "=" * 60)
    print("示例6：使用预计算的通路")
    print("=" * 60)

    deg_df = pd.DataFrame({
        "gene": ["CD4", "CD8A", "IL2", "IFNG", "TNF"]
    })

    # 预先计算的通路（例如从其他富集分析得到）
    pathways = [
        "T cell activation",
        "Immune response",
        "Cytokine signaling"
    ]

    provider = create_default_provider()

    annotator = GeneSetAnnotator(
        llm_provider=provider,
        enrichment_method=None             # 跳过内部富集
    )

    # 直接使用预计算的通路（所有基因作为整体）
    result = annotator.annotate(
        deg_df,
        pathways=pathways,                 # 传入通路列表
        compute_enrichment=False
    )

    print(f"\n✓ 结果:\n{result}\n")


# ==============================================
# 示例7：添加额外上下文
# ==============================================
def example7_with_additional_context():
    """添加PPI或其他分析结果作为上下文"""
    print("\n" + "=" * 60)
    print("示例7：添加额外上下文信息")
    print("=" * 60)

    deg_df = pd.DataFrame({
        "gene": ["TP53", "MYC", "BRCA1", "EGFR", "KRAS"],
        "logFC": [2.3, 1.8, -1.5, 2.1, 1.9],
        "pvalue": [0.001, 0.002, 0.003, 0.001, 0.002]
    })

    # PPI网络分析或其他上下文信息
    ppi_context = """
    PPI Network Analysis:
    - Hub genes: TP53, MYC, EGFR
    - Network density: 0.45
    - Main module: DNA damage response
    - Highly connected subnetwork detected
    """

    provider = create_default_provider()

    annotator = GeneSetAnnotator(llm_provider=provider)

    # 传入额外上下文（所有基因作为整体，内置过滤）
    result = annotator.annotate(
        deg_df,
        pvalue_threshold=0.05,
        additional_context=ppi_context     # 添加上下文信息
    )

    print(f"\n✓ 结果:\n{result}\n")


# ==============================================
# 示例8：使用其他provider（OpenAI）
# ==============================================
def example8_use_openai():
    """使用OpenAI provider"""
    print("\n" + "=" * 60)
    print("示例8：使用OpenAI provider")
    print("=" * 60)

    deg_df = pd.DataFrame({
        "gene": ["TP53", "MYC", "BRCA1"],
        "logFC": [2.3, 1.8, -1.5],
        "pvalue": [0.001, 0.002, 0.003]
    })

    # OpenAI provider
    provider = OpenAIProvider(
        api_key=os.getenv("OPENAI_API_KEY"),
        model_id="gpt-4",
        temperature=0.0
    )

    annotator = GeneSetAnnotator(llm_provider=provider)

    # 所有基因作为整体进行注释（内置过滤）
    result = annotator.annotate(
        deg_df,
        pvalue_threshold=0.05
    )

    print(f"\n✓ 结果:\n{result}\n")


# ==============================================
# 示例9：使用Anthropic Claude
# ==============================================
def example9_use_anthropic():
    """使用Anthropic Claude"""
    print("\n" + "=" * 60)
    print("示例9：使用Anthropic Claude")
    print("=" * 60)

    deg_df = pd.DataFrame({
        "gene": ["TP53", "MYC", "BRCA1"],
        "logFC": [2.3, 1.8, -1.5],
        "pvalue": [0.001, 0.002, 0.003]
    })

    # Anthropic provider
    provider = AnthropicProvider(
        api_key=os.getenv("ANTHROPIC_API_KEY"),
        model_id="claude-sonnet-4-20250514",
        temperature=0.0
    )

    annotator = GeneSetAnnotator(llm_provider=provider)

    # 所有基因作为整体进行注释（内置过滤）
    result = annotator.annotate(
        deg_df,
        pvalue_threshold=0.05
    )

    print(f"\n✓ 结果:\n{result}\n")


# ==============================================
# 主函数
# ==============================================
def main():
    """运行所有示例"""
    print("\n" + "=" * 60)
    print("场景2：Python API调用示例")
    print("默认使用 LiteLLM provider")
    print("推荐配置：base_url=https://litellm.thesaisai.com/")
    print("推荐模型：us.anthropic.claude-haiku-4-5-20251001-v1:0")
    print("=" * 60)

    # 取消注释想运行的示例

    example1_basic_litellm()
    # example2_all_parameters()
    # example3_batch_processing()
    # example4_process_csv_with_groups()
    # example5_no_enrichment()
    # example6_precomputed_pathways()
    # example7_with_additional_context()
    # example8_use_openai()
    # example9_use_anthropic()

    print("\n" + "=" * 60)
    print("使用说明")
    print("=" * 60)
    print("1. 设置环境变量: export LITELLM_API_KEY=your-api-key")
    print("2. 取消注释上面的函数调用来运行示例")
    print("3. annotate() 返回字符串，可以直接使用或保存")
    print("4. 支持三种provider：LiteLLM（推荐）、OpenAI、Anthropic")
    print("5. 所有参数都有默认值，可以根据需要调整")
    print("\n输出格式（新）：")
    print("  - annotate() 返回纯文本描述（2-4句话）")
    print("  - 不含 'Process:' 或 'Justification:' 等标签")
    print("  - 保存CSV时格式：gs, annotation")
    print("\n重要概念：")
    print("  - 所有基因作为一个整体列表进行处理")
    print("  - 不是单个基因循环，而是整个基因列表作为一个单元")
    print("  - 富集分析和LLM输入都使用完整的基因列表")
    print("\n差异基因过滤参数（可自定义）：")
    print("  - pvalue_threshold: P值阈值（默认0.05）")
    print("  - log2fc_threshold: Log2FoldChange绝对值阈值（默认1.0）")
    print("  - max_gene_num: 最大基因数量限制（默认60）")
    print("\n核心API：")
    print("  - annotator.annotate() # 返回文本字符串")
    print("  - processor.process_single_file() # 一键处理CSV")
    print("\n提示：建议先从 example1_basic_litellm() 开始")


if __name__ == "__main__":
    main()
