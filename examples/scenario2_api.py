"""
场景2：Python API调用 - 返回文本结果
Scenario 2: Python API - Returns text results

运行方式 / Usage:
    python scenario2_api.py

说明 / Description:
    这个脚本展示如何在Python代码中调用gs2txt API。
    annotate()方法返回字符串文本，可以直接使用或进一步处理。
"""

import pandas as pd
from gs2txt import GeneSetAnnotator
from gs2txt.llm import LiteLLMProvider, OpenAIProvider, AnthropicProvider


# ==============================================
# 示例1：基本用法 - LiteLLM（推荐）
# ==============================================
def example1_basic_litellm():
    """最简单的用法 - 使用LiteLLM"""
    print("\n" + "=" * 60)
    print("示例1：基本用法（LiteLLM）")
    print("=" * 60)

    # 准备基因数据
    deg_df = pd.DataFrame({
        "gene": ["TP53", "MYC", "BRCA1", "EGFR", "KRAS"],
        "logFC": [2.3, 1.8, -1.5, 2.1, 1.9]
    })

    # 配置LiteLLM provider（默认）
    provider = LiteLLMProvider(
        api_key="your-api-key",          # 替换成你的key
        model_id="gpt-4",
        temperature=0.0
    )

    # 创建annotator
    annotator = GeneSetAnnotator(
        llm_provider=provider,
        enrichment_method="pathway"       # 自动富集分析
    )

    # 调用 - 返回字符串
    result = annotator.annotate(deg_df)

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
        "logFC": [2.3, 1.8, -1.5]
    })

    # Provider配置
    provider = LiteLLMProvider(
        api_key="your-api-key",
        model_id="gpt-4",                 # 模型ID
        temperature=0.0,                   # 温度参数(0.0-1.0)
        base_url=None                      # 可选：自定义API端点
    )

    # Annotator配置
    annotator = GeneSetAnnotator(
        llm_provider=provider,
        enrichment_method="pathway",       # "pathway" 或 None
        prompt_builder=None                # 可选：自定义prompt
    )

    # 完整的annotate参数
    result = annotator.annotate(
        deg_df,                            # DataFrame，必须有'gene'列
        max_gene_num=60,                   # 最多使用多少个基因
        max_pathway_num=10,                # 最多使用多少个通路
        pathways=None,                     # 可选：预计算的通路列表
        compute_enrichment=True,           # 是否运行富集分析
        additional_context=None            # 可选：额外上下文
    )

    print(f"\n✓ 结果:\n{result}\n")


# ==============================================
# 示例3：批量处理多个基因集
# ==============================================
def example3_batch_processing():
    """批量处理多个cluster"""
    print("\n" + "=" * 60)
    print("示例3：批量处理多个基因集")
    print("=" * 60)

    # 多个基因集（例如从聚类分析得到）
    gene_sets = {
        "cluster_1": pd.DataFrame({"gene": ["TP53", "MYC", "BRCA1"]}),
        "cluster_2": pd.DataFrame({"gene": ["CD4", "CD8A", "IL2"]}),
        "cluster_3": pd.DataFrame({"gene": ["EGFR", "KRAS", "BRAF"]}),
    }

    provider = LiteLLMProvider(
        api_key="your-api-key",
        model_id="gpt-4",
        temperature=0.0
    )

    annotator = GeneSetAnnotator(
        llm_provider=provider,
        enrichment_method="pathway"
    )

    # 循环处理每个基因集
    results = {}
    for name, df in gene_sets.items():
        print(f"\n处理 {name}...")
        result = annotator.annotate(df, max_gene_num=60)
        results[name] = result
        print(f"✓ {name}: {result[:80]}...")  # 只打印前80字符

    return results


# ==============================================
# 示例4：处理CSV文件中的分组数据
# ==============================================
def example4_process_csv_with_groups():
    """从CSV读取并按cluster分组处理"""
    print("\n" + "=" * 60)
    print("示例4：处理CSV中的分组数据")
    print("=" * 60)

    # 读取CSV
    df = pd.read_csv("../data/sample_clustered_input.csv")

    provider = LiteLLMProvider(
        api_key="your-api-key",
        model_id="gpt-4",
        temperature=0.0
    )

    annotator = GeneSetAnnotator(llm_provider=provider)

    # 按cluster分组处理
    annotations = {}
    for cluster, group_df in df.groupby("cluster"):
        print(f"\n处理 {cluster}...")
        annotation = annotator.annotate(
            group_df,
            max_gene_num=60,
            max_pathway_num=10
        )
        annotations[cluster] = annotation
        print(f"✓ {cluster}: {annotation[:80]}...")

    # 将结果添加回原始dataframe
    df["annotation"] = df["cluster"].map(annotations)

    # 保存
    output_file = "output_with_annotations.csv"
    df.to_csv(output_file, index=False)
    print(f"\n✓ 结果已保存到: {output_file}")


# ==============================================
# 示例5：跳过富集分析（更快）
# ==============================================
def example5_no_enrichment():
    """跳过富集分析，直接用基因列表"""
    print("\n" + "=" * 60)
    print("示例5：跳过富集分析（更快）")
    print("=" * 60)

    deg_df = pd.DataFrame({
        "gene": ["TP53", "MYC", "BRCA1"],
        "logFC": [2.3, 1.8, -1.5]
    })

    provider = LiteLLMProvider(
        api_key="your-api-key",
        model_id="gpt-4",
        temperature=0.0
    )

    # enrichment_method=None 跳过富集
    annotator = GeneSetAnnotator(
        llm_provider=provider,
        enrichment_method=None             # 不做富集分析
    )

    result = annotator.annotate(
        deg_df,
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

    provider = LiteLLMProvider(
        api_key="your-api-key",
        model_id="gpt-4",
        temperature=0.0
    )

    annotator = GeneSetAnnotator(
        llm_provider=provider,
        enrichment_method=None             # 跳过内部富集
    )

    # 直接使用预计算的通路
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
        "logFC": [2.3, 1.8, -1.5, 2.1, 1.9]
    })

    # PPI网络分析或其他上下文信息
    ppi_context = """
    PPI Network Analysis:
    - Hub genes: TP53, MYC, EGFR
    - Network density: 0.45
    - Main module: DNA damage response
    - Highly connected subnetwork detected
    """

    provider = LiteLLMProvider(
        api_key="your-api-key",
        model_id="gpt-4",
        temperature=0.0
    )

    annotator = GeneSetAnnotator(llm_provider=provider)

    # 传入额外上下文
    result = annotator.annotate(
        deg_df,
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
        "logFC": [2.3, 1.8, -1.5]
    })

    # OpenAI provider
    provider = OpenAIProvider(
        api_key="your-openai-key",
        model_id="gpt-4",
        temperature=0.0
    )

    annotator = GeneSetAnnotator(llm_provider=provider)
    result = annotator.annotate(deg_df)

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
        "logFC": [2.3, 1.8, -1.5]
    })

    # Anthropic provider
    provider = AnthropicProvider(
        api_key="your-anthropic-key",
        model_id="claude-sonnet-4-20250514",
        temperature=0.0
    )

    annotator = GeneSetAnnotator(llm_provider=provider)
    result = annotator.annotate(deg_df)

    print(f"\n✓ 结果:\n{result}\n")


# ==============================================
# 主函数
# ==============================================
def main():
    """运行所有示例"""
    print("\n" + "=" * 60)
    print("场景2：Python API调用示例")
    print("默认使用 LiteLLM provider")
    print("=" * 60)

    # 取消注释想运行的示例

    # example1_basic_litellm()
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
    print("1. 取消注释上面的函数调用来运行示例")
    print("2. 替换 'your-api-key' 为真实的API key")
    print("3. annotate() 返回字符串，可以直接使用或保存")
    print("4. 支持三种provider：LiteLLM（推荐）、OpenAI、Anthropic")
    print("5. 所有参数都有默认值，可以根据需要调整")
    print("\n提示：建议先从 example1_basic_litellm() 开始")


if __name__ == "__main__":
    main()
