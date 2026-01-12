"""
场景1：批量处理CSV文件 - 使用Python API
Scenario 1: Batch Process CSV Files - Using Python API

运行方式 / Usage:
    export LITELLM_API_KEY=your-api-key
    python scenario1_batch_csv.py

说明 / Description:
    这个脚本展示如何用Python API批量处理CSV文件。
    内部自动循环处理所有数据（单个基因集或多个cluster）。
    输出CSV只包含 gs 和 annotation 两列。

    重要：基因处理逻辑
    - 单个基因集 = 所有基因作为一个整体列表进行富集分析和LLM输入
    - 不是单个基因循环，而是整个基因列表作为一个单元处理

    输出格式：
    - gs列：基因集名称（来自cluster列或文件名）
    - annotation列：LLM生成的生物学过程描述（2-4句话）
"""

import os
from pathlib import Path
import pandas as pd
from openai import OpenAI
from gs2txt import GeneSetAnnotator
from gs2txt.llm import LiteLLMProvider
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
# 示例1：处理单个基因集CSV（使用BatchProcessor）
# ==============================================
def example1_single_geneset():
    """
    处理单个基因集，输出CSV

    输出格式：gs, annotation（一行）
    - gs: 文件名（去掉后缀）
    - annotation: LLM生成的描述文本
    """
    print("\n" + "=" * 60)
    print("示例1：处理单个基因集CSV")
    print("=" * 60)

    provider = create_default_provider()
    annotator = GeneSetAnnotator(
        llm_provider=provider,
        enrichment_method="pathway"
    )
    processor = BatchProcessor(annotator)

    # 使用BatchProcessor处理（自动使用文件名作为gs）
    processor.process_single_file(
        input_path="../data/sample_input.csv",
        output_path="output1_single.csv",
        group_column=None,  # 无分组，整个文件作为一个基因集
        max_gene_num=60,
        max_pathway_num=10,
        pvalue_threshold=0.05,
        log2fc_threshold=1.0
    )

    print("✓ 完成！查看 output1_single.csv")
    print("输出格式：gs, annotation（一行）")


# ==============================================
# 示例2：处理多cluster CSV（自动循环）
# ==============================================
def example2_multiple_clusters():
    """
    处理包含多个cluster的CSV，自动循环每个cluster

    输出格式：gs, annotation（每个cluster一行）
    - gs: cluster名称
    - annotation: 该cluster的LLM描述
    """
    print("\n" + "=" * 60)
    print("示例2：处理多cluster CSV")
    print("=" * 60)

    provider = create_default_provider()
    annotator = GeneSetAnnotator(
        llm_provider=provider,
        enrichment_method="pathway"
    )
    processor = BatchProcessor(annotator)

    # 使用BatchProcessor按cluster分组处理
    processor.process_single_file(
        input_path="../data/sample_clustered_input.csv",
        output_path="output2_clustered.csv",
        group_column="cluster",  # 按cluster列分组
        max_gene_num=50,
        max_pathway_num=10,
        pvalue_threshold=0.05,
        log2fc_threshold=0.5
    )

    print("✓ 完成！查看 output2_clustered.csv")
    print("输出格式：gs, annotation（每个cluster一行）")


# ==============================================
# 示例3：自定义过滤参数
# ==============================================
def example3_custom_parameters():
    """展示如何自定义差异基因过滤参数"""
    print("\n" + "=" * 60)
    print("示例3：自定义过滤参数")
    print("=" * 60)

    provider = create_default_provider()
    annotator = GeneSetAnnotator(
        llm_provider=provider,
        enrichment_method="pathway"
    )
    processor = BatchProcessor(annotator)

    # 使用更严格的过滤参数
    processor.process_single_file(
        input_path="../data/sample_input.csv",
        output_path="output3_custom.csv",
        group_column=None,
        max_gene_num=100,
        max_pathway_num=15,
        pvalue_threshold=0.01,      # 更严格的P值
        log2fc_threshold=1.5        # 更高的FC阈值
    )

    print("✓ 完成！查看 output3_custom.csv")


# ==============================================
# 示例4：跳过富集分析（更快）
# ==============================================
def example4_no_enrichment():
    """跳过富集分析，直接用基因列表"""
    print("\n" + "=" * 60)
    print("示例4：跳过富集分析（更快）")
    print("=" * 60)

    provider = create_default_provider()

    # enrichment_method=None 跳过富集
    annotator = GeneSetAnnotator(
        llm_provider=provider,
        enrichment_method=None
    )
    processor = BatchProcessor(annotator)

    processor.process_single_file(
        input_path="../data/sample_input.csv",
        output_path="output4_no_enrichment.csv",
        group_column=None,
        max_gene_num=60,
        pvalue_threshold=0.05,
        compute_enrichment=False
    )

    print("✓ 完成！查看 output4_no_enrichment.csv")


# ==============================================
# 示例5：手动处理并添加额外上下文
# ==============================================
def example5_with_context():
    """处理CSV时添加额外上下文（如PPI分析结果）"""
    print("\n" + "=" * 60)
    print("示例5：添加额外上下文")
    print("=" * 60)

    df = pd.read_csv("../data/sample_input.csv")
    gs_name = "sample_input"  # 使用文件名

    # 额外的分析结果（例如PPI）
    ppi_context = """
    PPI Network Analysis:
    - Hub genes: TP53, MYC
    - Network density: 0.45
    """

    provider = create_default_provider()
    annotator = GeneSetAnnotator(llm_provider=provider)

    # 手动调用annotate并传入额外上下文
    annotation = annotator.annotate(
        df,
        max_gene_num=60,
        pvalue_threshold=0.05,
        additional_context=ppi_context
    )

    # 创建输出DataFrame
    result_df = pd.DataFrame([{"gs": gs_name, "annotation": annotation}])
    result_df.to_csv("output5_with_context.csv", index=False)

    print("✓ 完成！查看 output5_with_context.csv")


# ==============================================
# 示例6：使用不同的provider
# ==============================================
def example6_different_providers():
    """展示如何切换到其他provider（OpenAI/Anthropic）"""
    print("\n" + "=" * 60)
    print("示例6：使用不同的provider")
    print("=" * 60)

    # 默认：LiteLLM（推荐）
    provider = create_default_provider()

    # 选项2：OpenAI
    # from gs2txt.llm import OpenAIProvider
    # provider = OpenAIProvider(
    #     api_key=os.getenv("OPENAI_API_KEY"),
    #     model_id="gpt-4",
    #     temperature=0.0
    # )

    # 选项3：Anthropic
    # from gs2txt.llm import AnthropicProvider
    # provider = AnthropicProvider(
    #     api_key=os.getenv("ANTHROPIC_API_KEY"),
    #     model_id="claude-sonnet-4-20250514",
    #     temperature=0.0
    # )

    annotator = GeneSetAnnotator(llm_provider=provider)
    processor = BatchProcessor(annotator)

    processor.process_single_file(
        input_path="../data/sample_input.csv",
        output_path="output6_provider.csv",
        group_column=None,
        max_gene_num=60,
        pvalue_threshold=0.05
    )

    print("✓ 完成！查看 output6_provider.csv")


# ==============================================
# 示例7：批量处理多个CSV文件
# ==============================================
def example7_multiple_files():
    """批量处理多个CSV文件"""
    print("\n" + "=" * 60)
    print("示例7：批量处理多个CSV文件")
    print("=" * 60)

    # 多个输入文件
    input_files = [
        ("../data/sample_input.csv", None),           # 单个基因集
        ("../data/sample_clustered_input.csv", "cluster"),  # 按cluster分组
    ]

    provider = create_default_provider()
    annotator = GeneSetAnnotator(llm_provider=provider)
    processor = BatchProcessor(annotator)

    # 处理每个文件
    for i, (input_file, group_col) in enumerate(input_files, 1):
        print(f"\n处理文件 {i}/{len(input_files)}: {input_file}")

        output_file = f"output7_batch_{i}.csv"
        processor.process_single_file(
            input_path=input_file,
            output_path=output_file,
            group_column=group_col,
            max_gene_num=50,
            pvalue_threshold=0.05
        )

        print(f"✓ 完成！保存到 {output_file}")


# ==============================================
# 主函数
# ==============================================
def main():
    """运行所有示例"""
    print("\n" + "=" * 60)
    print("场景1：批量处理CSV文件（Python API）")
    print("默认使用 LiteLLM provider")
    print("推荐配置：base_url=https://litellm.thesaisai.com/")
    print("推荐模型：us.anthropic.claude-haiku-4-5-20251001-v1:0")
    print("=" * 60)

    # 取消注释想运行的示例

    example1_single_geneset()
    # example2_multiple_clusters()
    # example3_custom_parameters()
    # example4_no_enrichment()
    # example5_with_context()
    # example6_different_providers()
    # example7_multiple_files()

    print("\n" + "=" * 60)
    print("使用说明")
    print("=" * 60)
    print("1. 设置环境变量: export LITELLM_API_KEY=your-api-key")
    print("2. 取消注释上面的函数调用来运行示例")
    print("3. 输入：CSV文件（必须包含'gene'列，可选'pvalue'和'logFC'列）")
    print("\n输出格式（新）：")
    print("  gs,annotation")
    print("  sample_input,\"This gene set is involved in...\"")
    print("  cluster_1,\"These genes regulate...\"")
    print("\n重要概念：")
    print("  - 单个基因集 = 所有基因作为一个整体列表处理")
    print("  - 输出只有两列：gs（基因集名称）和 annotation（描述）")
    print("  - gs来源：有cluster列用cluster值，否则用文件名")
    print("\n差异基因过滤参数（可自定义）：")
    print("  - pvalue_threshold: P值阈值（默认0.05）")
    print("  - log2fc_threshold: Log2FoldChange绝对值阈值（默认1.0）")
    print("  - max_gene_num: 最大基因数量限制（默认60）")
    print("\n核心API：")
    print("  - processor.process_single_file()  # 一键处理CSV")
    print("  - processor.process_grouped_data() # 处理分组数据")
    print("  - processor.process_single_geneset() # 处理单个基因集")
    print("\n提示：建议先从 example1_single_geneset() 开始")


if __name__ == "__main__":
    main()
