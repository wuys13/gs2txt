"""
场景3：两阶段处理模式
Scenario 3: Two-Stage Processing Pipeline

运行方式 / Usage:

模式A - 单文件处理 (Single File Mode):
    python scenario3_two_stage.py preprocess      # 预处理单个DEG文件
    python scenario3_two_stage.py annotate        # 注释

模式B - 批量处理 (Batch Mode) [推荐]:
    python scenario3_two_stage.py batch           # 批量预处理多个DEG文件
    python scenario3_two_stage.py annotate        # 注释

一次性运行:
    export LITELLM_API_KEY=your-api-key
    python scenario3_two_stage.py all             # 单文件模式全流程
    python scenario3_two_stage.py batch-all       # 批量模式全流程

说明 / Description:
    这个脚本展示如何使用两阶段处理模式：

    模式A - 单文件处理:
    - 输入: 单个DEG文件（含cluster列）+ 单个富集目录
    - 适合: 一个DEG文件包含多个cluster的情况

    模式B - 批量处理 [推荐]:
    - 输入: DEG文件夹（多个CSV）+ 多个通路文件夹（GO/, KEGG/, Reactome/）
    - 文件匹配: DEG文件名 = 通路文件名 (sample1.csv 匹配各文件夹中的 sample1.csv)
    - 通路合并: 从多个来源合并通路，去重，按P值排序取前N个
    - 适合: 多个独立样本，每个样本有来自不同数据库的富集结果

    优势：
    - 分离数据处理和API调用，节省API成本
    - 可以检查中间结果，确保输入正确
    - 支持从配置文件读取所有参数
    - 支持多个通路来源（GO, KEGG, Reactome等）合并

输入文件格式:
    模式A:
    - DEG文件: CSV, 必须有 gene, cluster 列, 可选 pvalue, logFC 列
    - 富集文件: 每个cluster一个CSV, 文件名为 {cluster}.csv

    模式B (批量):
    - DEG文件夹: 多个CSV文件，每个文件代表一个基因集
    - 通路文件夹: 多个文件夹，每个包含与DEG同名的CSV文件
    - 配置文件: YAML格式，指定 deg_dir 和 pathway_dirs

输出文件格式:
    - 中间结果: gs, genes, pathways, ppis, final_prompt
    - 最终结果: gs, annotation, pathways, PPIs, Final_prompt
"""

import sys
from pathlib import Path

# 添加父目录到路径以便导入gs2txt
sys.path.insert(0, str(Path(__file__).parent.parent))

from gs2txt.pipeline import TwoStagePipeline


# ==============================================
# 阶段一：预处理
# ==============================================
def run_preprocess():
    """
    阶段一：预处理差异基因和富集数据

    输入:
    - ../data/sample_deg.csv: 差异基因文件
    - ../data/enrichment/: 富集结果目录
    - config.yaml: 配置文件

    输出:
    - intermediate.csv: 中间结果文件
    """
    print("\n" + "=" * 60)
    print("阶段一：预处理 (无需API)")
    print("Stage 1: Preprocess (No API Required)")
    print("=" * 60)

    # 可选：添加PPI上下文信息
    ppi_context = {
        "cluster_1": "PPI Hub genes: TP53, BRCA1. Network density: 0.45",
        "cluster_2": "PPI Hub genes: CD4, IL2. Network density: 0.52",
        # cluster_3 没有PPI信息，将使用空值
    }

    # 运行预处理
    TwoStagePipeline.preprocess(
        deg_file="../data/sample_deg.csv",
        enrichment_dir="../data/enrichment/",
        output_file="intermediate.csv",
        config_file="config.yaml",
        group_column="cluster",
        ppi_context=ppi_context  # 可选
    )

    print("\n预处理完成！请检查 intermediate.csv")
    print("Preprocess complete! Check intermediate.csv")


# ==============================================
# 阶段一B：批量预处理
# ==============================================
def run_preprocess_batch(test: bool = False, checkpoint_interval: int = 100):
    """
    阶段一B：批量预处理多个DEG文件

    从配置文件读取：
    - deg_dir: DEG文件夹路径
    - pathway_dirs: 多个通路文件夹路径列表

    输入:
    - ../data/deg/*.csv: 多个差异基因文件
    - ../data/GO/*.csv, ../data/KEGG/*.csv, etc.: 通路文件
    - config.yaml: 配置文件

    输出:
    - intermediate.csv: 中间结果文件（所有样本合并）

    Parameters
    ----------
    test : bool
        测试模式，只处理前3个文件
    checkpoint_interval : int
        每N条保存一次检查点，默认100
    """
    print("\n" + "=" * 60)
    print("阶段一B：批量预处理 (无需API)")
    print("Stage 1B: Batch Preprocess (No API Required)")
    print("=" * 60)

    # 可选：添加PPI上下文信息
    ppi_context = {
        "sample1": "PPI Hub genes: TP53, BRCA1. Network density: 0.45",
        "sample2": "PPI Hub genes: CD4, IL2. Network density: 0.52",
        # sample3 没有PPI信息，将使用空值
    }

    # 运行批量预处理
    TwoStagePipeline.preprocess_batch(
        config_file="config.yaml",
        output_file="intermediate.csv",
        ppi_context=ppi_context,  # 可选
        test=test,  # 测试模式：只处理前3个文件
        checkpoint_interval=checkpoint_interval  # 每N条保存检查点
    )

    print("\n批量预处理完成！请检查 intermediate.csv")
    print("Batch preprocess complete! Check intermediate.csv")


# ==============================================
# 阶段二：注释
# ==============================================
def run_annotate(test: bool = False, checkpoint_interval: int = 100):
    """
    阶段二：调用LLM生成注释

    输入:
    - intermediate.csv: 中间结果文件
    - config.yaml: 配置文件（含LLM设置）

    输出:
    - final_output.csv: 最终结果文件

    Parameters
    ----------
    test : bool
        测试模式，只处理前3行
    checkpoint_interval : int
        每N条保存一次检查点，默认100
    """
    print("\n" + "=" * 60)
    print("阶段二：LLM注释 (需要API)")
    print("Stage 2: LLM Annotation (API Required)")
    print("=" * 60)

    # 运行注释
    TwoStagePipeline.annotate(
        intermediate_file="intermediate.csv",
        output_file="final_output.csv",
        config_file="config.yaml",
        test=test,  # 测试模式：只处理前3行
        checkpoint_interval=checkpoint_interval  # 每N条保存检查点
    )

    print("\n注释完成！查看 final_output.csv")
    print("Annotation complete! Check final_output.csv")


# ==============================================
# 示例：自定义配置
# ==============================================
def example_custom_config():
    """
    示例：使用自定义配置（不依赖配置文件）
    """
    print("\n" + "=" * 60)
    print("示例：使用默认配置（无配置文件）")
    print("=" * 60)

    # 阶段一：使用默认配置
    TwoStagePipeline.preprocess(
        deg_file="../data/sample_deg.csv",
        enrichment_dir="../data/enrichment/",
        output_file="intermediate_default.csv",
        config_file=None,  # 使用默认配置
        group_column="cluster"
    )

    print("预处理完成（使用默认配置）")


# ==============================================
# 示例：检查中间结果
# ==============================================
def example_check_intermediate(
    input_file: str = "intermediate.csv",
    summary_file: str = "intermediate_summary.csv"
):
    """
    示例：检查中间结果内容，并将统计结果保存到CSV

    Parameters
    ----------
    input_file : str
        中间结果文件路径
    summary_file : str
        统计结果输出文件路径
    """
    import pandas as pd

    print("\n" + "=" * 60)
    print("检查中间结果")
    print("=" * 60)

    inter_df = pd.read_csv(input_file)

    print(f"\n共 {len(inter_df)} 个基因集:\n")

    # 收集统计信息
    summary_records = []

    for _, row in inter_df.iterrows():
        gs = row["gs"]

        # 处理 genes 列可能是 NaN 的情况
        genes_str = row["genes"]
        if pd.isna(genes_str) or genes_str == "":
            genes = []
        else:
            genes = str(genes_str).split(",")

        # 处理 pathways 列可能是 NaN 的情况
        pathways_str = row["pathways"]
        if pd.isna(pathways_str) or pathways_str == "":
            pathways = []
        else:
            pathways = str(pathways_str).split(",")

        # 处理 ppis 列
        ppis = row["ppis"] if pd.notna(row["ppis"]) else ""

        # 处理 final_prompt 列可能是 NaN 的情况
        final_prompt = row["final_prompt"]
        if pd.isna(final_prompt):
            prompt_len = 0
        else:
            prompt_len = len(str(final_prompt))

        # 判断是否有效（有基因且有 prompt）
        is_valid = len(genes) > 0 and prompt_len > 0

        print(f"基因集: {gs}")
        print(f"  基因数: {len(genes)}")
        print(f"  通路数: {len(pathways)}")
        print(f"  PPI: {'有' if ppis else '无'}")
        print(f"  Prompt长度: {prompt_len} 字符")
        print(f"  状态: {'有效' if is_valid else '无效（无基因或无prompt）'}")
        print()

        # 记录统计信息
        summary_records.append({
            "gs": gs,
            "gene_count": len(genes),
            "pathway_count": len(pathways),
            "has_ppi": bool(ppis),
            "prompt_length": prompt_len,
            "is_valid": is_valid
        })

    # 创建统计 DataFrame
    summary_df = pd.DataFrame(summary_records)

    # 打印总结
    print("=" * 60)
    print("总结 / Summary")
    print("=" * 60)
    total = len(summary_df)
    valid_count = summary_df["is_valid"].sum()
    invalid_count = total - valid_count
    avg_genes = summary_df["gene_count"].mean()
    avg_pathways = summary_df["pathway_count"].mean()
    ppi_count = summary_df["has_ppi"].sum()

    print(f"  总基因集数: {total}")
    print(f"  有效基因集: {valid_count} ({valid_count/total*100:.1f}%)")
    print(f"  无效基因集: {invalid_count} ({invalid_count/total*100:.1f}%)")
    print(f"  平均基因数: {avg_genes:.1f}")
    print(f"  平均通路数: {avg_pathways:.1f}")
    print(f"  有PPI信息: {ppi_count} ({ppi_count/total*100:.1f}%)")

    # 保存统计结果
    summary_df.to_csv(summary_file, index=False)
    print(f"\n统计结果已保存到: {summary_file}")


# ==============================================
# 主函数
# ==============================================
def main():
    """主函数：根据命令行参数运行不同阶段"""

    if len(sys.argv) < 2:
        print_usage()
        return

    command = sys.argv[1].lower()

    # 解析可选参数
    test_mode = "--test" in sys.argv or "-t" in sys.argv
    checkpoint = 100  # 默认值
    for i, arg in enumerate(sys.argv):
        if arg in ("--checkpoint", "-c") and i + 1 < len(sys.argv):
            try:
                checkpoint = int(sys.argv[i + 1])
            except ValueError:
                pass

    if command == "preprocess":
        run_preprocess()
    elif command == "batch":
        run_preprocess_batch(test=test_mode, checkpoint_interval=checkpoint)
    elif command == "annotate":
        run_annotate(test=test_mode, checkpoint_interval=checkpoint)
    elif command == "all":
        run_preprocess()
        run_annotate(test=test_mode, checkpoint_interval=checkpoint)
    elif command == "batch-all":
        run_preprocess_batch(test=test_mode, checkpoint_interval=checkpoint)
        run_annotate(test=test_mode, checkpoint_interval=checkpoint)
    elif command == "check":
        example_check_intermediate()
    elif command == "default":
        example_custom_config()
    else:
        print(f"未知命令: {command}")
        print_usage()


def print_usage():
    """打印使用说明"""
    print("\n" + "=" * 60)
    print("场景3：两阶段处理模式")
    print("Scenario 3: Two-Stage Processing Pipeline")
    print("=" * 60)

    print("\n用法 / Usage:")
    print("  python scenario3_two_stage.py <command> [options]")

    print("\n命令 / Commands:")
    print("  preprocess  - 模式A：预处理单个DEG文件（无需API）")
    print("  batch       - 模式B：批量预处理多个DEG文件（无需API）[推荐]")
    print("  annotate    - 阶段二：注释（需要API）")
    print("  all         - 模式A全流程（预处理+注释）")
    print("  batch-all   - 模式B全流程（批量预处理+注释）[推荐]")
    print("  check       - 检查中间结果")
    print("  default     - 使用默认配置运行预处理")

    print("\n可选参数 / Options:")
    print("  --test, -t              测试模式：只处理前3条数据")
    print("  --checkpoint N, -c N    每N条保存检查点（默认100）")

    print("\n模式A示例 - 单文件处理 / Single File Mode:")
    print("  python scenario3_two_stage.py preprocess")
    print("  python scenario3_two_stage.py check")
    print("  export LITELLM_API_KEY=your-api-key")
    print("  python scenario3_two_stage.py annotate")

    print("\n模式B示例 - 批量处理 / Batch Mode [推荐]:")
    print("  python scenario3_two_stage.py batch")
    print("  python scenario3_two_stage.py check")
    print("  export LITELLM_API_KEY=your-api-key")
    print("  python scenario3_two_stage.py annotate")

    print("\n测试模式示例 / Test Mode:")
    print("  python scenario3_two_stage.py batch --test")
    print("  python scenario3_two_stage.py annotate --test")
    print("  python scenario3_two_stage.py batch-all -t -c 50")

    print("\n输入文件 / Input Files:")
    print("  模式A:")
    print("    - ../data/sample_deg.csv           差异基因文件")
    print("    - ../data/enrichment/*.csv         富集结果目录")
    print("  模式B:")
    print("    - ../data/deg/*.csv                DEG文件夹")
    print("    - ../data/GO/*.csv                 GO通路文件夹")
    print("    - ../data/KEGG/*.csv               KEGG通路文件夹")
    print("    - ../data/Reactome/*.csv           Reactome通路文件夹")
    print("  配置文件:")
    print("    - config.yaml                      配置文件")

    print("\n输出文件 / Output Files:")
    print("  - intermediate.csv                 中间结果")
    print("  - intermediate_summary.csv         统计汇总（check命令生成）")
    print("  - final_output.csv                 最终结果")

    print("\n配置文件说明 / Config File:")
    print("  查看 config.yaml 了解所有可配置参数")
    print("  批量模式需要配置 input.deg_dir 和 input.pathway_dirs")


if __name__ == "__main__":
    main()
