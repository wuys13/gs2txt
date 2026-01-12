"""
场景1：批量处理CSV文件 - 使用Python API
Scenario 1: Batch Process CSV Files - Using Python API

运行方式 / Usage:
    python scenario1_batch_csv.py

说明 / Description:
    这个脚本展示如何用Python API批量处理CSV文件。
    内部自动循环处理所有数据（单个基因集或多个cluster）。
    输出CSV包含原始列 + annotation列。
"""

import pandas as pd
from gs2txt import GeneSetAnnotator
from gs2txt.llm import LiteLLMProvider
from gs2txt.batch import BatchProcessor


# ==============================================
# 示例1：处理单个基因集CSV
# ==============================================
def example1_single_geneset():
    """处理单个基因集，输出CSV"""
    print("\n" + "=" * 60)
    print("示例1：处理单个基因集CSV")
    print("=" * 60)

    # 配置provider（LiteLLM）
    provider = LiteLLMProvider(
        api_key="your-api-key",          # 替换成你的key
        model_id="gpt-4",
        temperature=0.0
    )

    # 创建annotator
    annotator = GeneSetAnnotator(
        llm_provider=provider,
        enrichment_method="pathway"
    )

    # 创建批处理器
    processor = BatchProcessor(annotator)

    # 处理CSV文件，自动输出结果
    print("读取并处理文件...")
    processor.process_single_file(
        input_path="../data/sample_input.csv",
        output_path="output1_single.csv",
        group_column=None,                # 不分组，作为单个基因集
        max_gene_num=60,
        max_pathway_num=10
    )

    print("✓ 完成！查看 output1_single.csv")
    print("输出包含：原始列 + annotation列")


# ==============================================
# 示例2：处理多cluster CSV（自动循环）
# ==============================================
def example2_multiple_clusters():
    """处理包含多个cluster的CSV，自动循环每个cluster"""
    print("\n" + "=" * 60)
    print("示例2：处理多cluster CSV（自动循环）")
    print("=" * 60)

    provider = LiteLLMProvider(
        api_key="your-api-key",
        model_id="gpt-4",
        temperature=0.0
    )

    annotator = GeneSetAnnotator(
        llm_provider=provider,
        enrichment_method="pathway"
    )

    processor = BatchProcessor(annotator)

    # 处理CSV，按cluster分组
    print("读取并处理文件...")
    processor.process_single_file(
        input_path="../data/sample_clustered_input.csv",
        output_path="output2_clustered.csv",
        group_column="cluster",           # 按cluster分组，自动循环
        max_gene_num=60,
        max_pathway_num=10
    )

    print("✓ 完成！查看 output2_clustered.csv")
    print("输出：每个cluster自动获得annotation")


# ==============================================
# 示例3：自定义参数
# ==============================================
def example3_custom_parameters():
    """使用自定义参数处理CSV"""
    print("\n" + "=" * 60)
    print("示例3：自定义参数")
    print("=" * 60)

    provider = LiteLLMProvider(
        api_key="your-api-key",
        model_id="gpt-4",
        temperature=0.2                   # 调整温度
    )

    annotator = GeneSetAnnotator(
        llm_provider=provider,
        enrichment_method="pathway"
    )

    processor = BatchProcessor(annotator)

    processor.process_single_file(
        input_path="../data/sample_input.csv",
        output_path="output3_custom.csv",
        max_gene_num=100,                 # 更多基因
        max_pathway_num=15                # 更多通路
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

    provider = LiteLLMProvider(
        api_key="your-api-key",
        model_id="gpt-4",
        temperature=0.0
    )

    # enrichment_method=None 跳过富集
    annotator = GeneSetAnnotator(
        llm_provider=provider,
        enrichment_method=None
    )

    processor = BatchProcessor(annotator)

    processor.process_single_file(
        input_path="../data/sample_input.csv",
        output_path="output4_no_enrichment.csv",
        compute_enrichment=False
    )

    print("✓ 完成！查看 output4_no_enrichment.csv")


# ==============================================
# 示例5：手动处理 - 更灵活的控制
# ==============================================
def example5_manual_processing():
    """手动读取CSV、处理、保存（更灵活）"""
    print("\n" + "=" * 60)
    print("示例5：手动处理（完全控制）")
    print("=" * 60)

    # 读取CSV
    df = pd.read_csv("../data/sample_clustered_input.csv")
    print(f"读取到 {len(df)} 行数据")

    provider = LiteLLMProvider(
        api_key="your-api-key",
        model_id="gpt-4",
        temperature=0.0
    )

    annotator = GeneSetAnnotator(llm_provider=provider)

    # 手动按cluster分组并处理
    annotations = {}
    for cluster in df["cluster"].unique():
        print(f"\n处理 {cluster}...")
        cluster_df = df[df["cluster"] == cluster]

        # 调用annotate获取文本
        annotation = annotator.annotate(
            cluster_df,
            max_gene_num=60,
            max_pathway_num=10
        )

        annotations[cluster] = annotation
        print(f"✓ {cluster}: {annotation[:80]}...")

    # 将annotation添加到原始dataframe
    df["annotation"] = df["cluster"].map(annotations)

    # 保存
    output_file = "output5_manual.csv"
    df.to_csv(output_file, index=False)
    print(f"\n✓ 完成！查看 {output_file}")


# ==============================================
# 示例6：使用不同的provider
# ==============================================
def example6_different_providers():
    """展示如何切换provider"""
    print("\n" + "=" * 60)
    print("示例6：使用不同的provider")
    print("=" * 60)

    # 可以选择任意provider
    # 选项1：LiteLLM（推荐）
    provider = LiteLLMProvider(
        api_key="your-api-key",
        model_id="gpt-4",
        temperature=0.0
    )

    # 选项2：OpenAI
    # from gs2txt.llm import OpenAIProvider
    # provider = OpenAIProvider(
    #     api_key="your-openai-key",
    #     model_id="gpt-4",
    #     temperature=0.0
    # )

    # 选项3：Anthropic
    # from gs2txt.llm import AnthropicProvider
    # provider = AnthropicProvider(
    #     api_key="your-anthropic-key",
    #     model_id="claude-sonnet-4-20250514",
    #     temperature=0.0
    # )

    annotator = GeneSetAnnotator(llm_provider=provider)
    processor = BatchProcessor(annotator)

    processor.process_single_file(
        input_path="../data/sample_input.csv",
        output_path="output6_provider.csv"
    )

    print("✓ 完成！")


# ==============================================
# 示例7：添加额外上下文到CSV处理
# ==============================================
def example7_with_context():
    """处理CSV时添加额外上下文"""
    print("\n" + "=" * 60)
    print("示例7：添加额外上下文")
    print("=" * 60)

    df = pd.read_csv("../data/sample_input.csv")

    # 额外的分析结果（例如PPI）
    ppi_context = """
    PPI Network Analysis:
    - Hub genes: TP53, MYC
    - Network density: 0.45
    """

    provider = LiteLLMProvider(
        api_key="your-api-key",
        model_id="gpt-4",
        temperature=0.0
    )

    annotator = GeneSetAnnotator(llm_provider=provider)

    # 传入额外上下文
    annotation = annotator.annotate(
        df,
        additional_context=ppi_context
    )

    # 添加到dataframe
    df["annotation"] = annotation

    output_file = "output7_with_context.csv"
    df.to_csv(output_file, index=False)
    print(f"✓ 完成！查看 {output_file}")


# ==============================================
# 示例8：批量处理多个CSV文件
# ==============================================
def example8_multiple_files():
    """批量处理多个CSV文件"""
    print("\n" + "=" * 60)
    print("示例8：批量处理多个CSV文件")
    print("=" * 60)

    # 多个输入文件
    input_files = [
        "../data/sample_input.csv",
        "../data/sample_clustered_input.csv",
    ]

    provider = LiteLLMProvider(
        api_key="your-api-key",
        model_id="gpt-4",
        temperature=0.0
    )

    annotator = GeneSetAnnotator(llm_provider=provider)
    processor = BatchProcessor(annotator)

    # 处理每个文件
    for i, input_file in enumerate(input_files, 1):
        print(f"\n处理文件 {i}/{len(input_files)}: {input_file}")

        output_file = f"output8_batch_{i}.csv"

        # 自动检测是否需要分组（如果有cluster列）
        df = pd.read_csv(input_file)
        group_column = "cluster" if "cluster" in df.columns else None

        processor.process_single_file(
            input_path=input_file,
            output_path=output_file,
            group_column=group_column
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
    print("=" * 60)

    # 取消注释想运行的示例

    # example1_single_geneset()
    # example2_multiple_clusters()
    # example3_custom_parameters()
    # example4_no_enrichment()
    # example5_manual_processing()
    # example6_different_providers()
    # example7_with_context()
    # example8_multiple_files()

    print("\n" + "=" * 60)
    print("使用说明")
    print("=" * 60)
    print("1. 取消注释上面的函数调用来运行示例")
    print("2. 替换 'your-api-key' 为真实的API key")
    print("3. 输入：CSV文件（必须包含'gene'列）")
    print("4. 输出：原始CSV + annotation列")
    print("5. BatchProcessor自动处理循环（单个或多cluster）")
    print("\n核心API：")
    print("  - processor.process_single_file()  # 一键处理CSV")
    print("  - annotator.annotate()             # 返回文本字符串")
    print("\n提示：建议先从 example1_single_geneset() 开始")


if __name__ == "__main__":
    main()
