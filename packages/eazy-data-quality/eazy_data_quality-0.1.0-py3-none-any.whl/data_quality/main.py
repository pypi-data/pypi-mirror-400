import argparse
import os
import sys
import yaml
import copy

from .core.processor_factory import ProcessorFactory
from .utils.logger import setup_logger

logger = setup_logger(__name__)

PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))


def _run_single_eval_with_type(args, eval_type: str, output_suffix: str) -> bool:
    """
    内部函数：在 args 上标记当前 eval_type 和 输出后缀 output_suffix，
    然后执行对应 Processor。

    Processor 内部可以通过:
        args.eval_type           # 当前评估类型（c_relevance / g_relevance / a_relevance 等）
        args.eval_output_suffix  # 文件名后缀（如 c_relevance 或 cga_relevance）
    来决定输出文件名。
    """
    try:
        local_args = copy.copy(args)
        setattr(local_args, "eval_type", eval_type)
        setattr(local_args, "eval_output_suffix", output_suffix)

        processor = ProcessorFactory.get_processor_instance(eval_type)
        success, message = processor(local_args)
        if success:
            logger.info(
                f"Successfully processed evaluation type: {eval_type}, "
                f"output_suffix: {output_suffix}"
            )
            return True
        else:
            logger.error(f"Failed to process evaluation type {eval_type}: {message}")
            return False
    except Exception as e:
        logger.error(
            f"Exception occurred while processing evaluation type {eval_type}: {str(e)}",
            exc_info=True
        )
        return False


def load_model_config(config_path: str):
    with open(config_path, 'r', encoding='utf-8') as f:
        model_config = yaml.safe_load(f)
    return model_config


def parse_args():
    parser = argparse.ArgumentParser(description='Data Quality')

    parser.add_argument(
        '-i', '--input',
        help='输入文件路径',
        default=os.path.join(PROJECT_ROOT, 'test', 'input')
    )
    parser.add_argument(
        '-o', '--output',
        help='输出文件路径',
        default=os.path.join(PROJECT_ROOT, 'test', 'output')
    )
    parser.add_argument(
        '-e', '--eval',
        help='评估方式',
        nargs='+',
        choices=['answer', 'context', 'reward', 'c_relevance', 'cga_relevance'],
        default=['answer', 'context']
    )
    parser.add_argument(
        '--template',
        help='默认使用自带提示词，可以指定自己的提示词，但是必须放在prompt目录下，值为文件名'
    )
    parser.add_argument(
        '--mode',
        help='运行模式',
        choices=['model', 'regex'],
        default='model'
    )
    parser.add_argument(
        '--model_config',
        help='模型参数配置文件路径',
        default=os.path.join(PROJECT_ROOT, 'config', 'model_config.yaml')
    )
    parser.add_argument(
        '--columns_config',
        help='必有列配置文件路径',
        default=os.path.join(PROJECT_ROOT, 'config', 'columns_config.yaml')
    )

    return parser.parse_args()


def process_single_evaluation(args, eval_type: str) -> bool:
    """
    处理单个评估类型：
    - 普通类型：output_suffix = eval_type
      => 输出文件类似 xxx_answer.xlsx / xxx_c_relevance.xlsx 等
    - 组合类型 cga_relevance：
      子类型依然是 c_relevance, g_relevance, a_relevance，
      但统一使用 output_suffix = "cga_relevance"
      => 三个子评估都会写同一个文件 xxx_cga_relevance.xlsx
    """
    if eval_type == "cga_relevance":
        sub_eval_types = ['c_relevance', 'g_relevance', 'a_relevance']
        output_suffix = "cga_relevance"
        logger.info(
            f"Processing composed evaluation type '{eval_type}' "
            f"as sub types: {sub_eval_types}, unified output_suffix: {output_suffix}"
        )
        for sub in sub_eval_types:
            ok = _run_single_eval_with_type(args, sub, output_suffix)
            if not ok:
                logger.error(
                    f"Sub evaluation '{sub}' for composed type '{eval_type}' failed"
                )
                return False
        logger.info(f"Successfully processed composed evaluation type: {eval_type}")
        return True
    else:
        # 普通类型，后缀跟 eval_type 一致
        return _run_single_eval_with_type(args, eval_type, eval_type)


def run(
    input_path: str,
    output_path: str,
    eval_types=None,
    template: str | None = None,
    mode: str = "model",
    model_config_path: str | None = None,
    columns_config_path: str | None = None,
) -> bool:
    """
    库调用入口：直接传参数，不依赖命令行。
    返回 True 表示全部评估成功，False 表示有失败。
    """
    if eval_types is None:
        eval_types = ['answer', 'context']

    # 构造一个简单的 args 对象，复用现有逻辑
    class Args:
        pass

    args = Args()
    args.input = input_path
    args.output = output_path
    args.eval = eval_types
    args.template = template
    args.mode = mode

    base_dir = PROJECT_ROOT

    if model_config_path is None:
        model_config_path = os.path.join(base_dir, 'config', 'model_config.yaml')
    if columns_config_path is None:
        columns_config_path = os.path.join(base_dir, 'config', 'columns_config.yaml')

    args.model_config = load_model_config(model_config_path)
    args.columns_config = load_model_config(columns_config_path)

    logger.info(f"[run] Starting data quality assessment with args: {args.__dict__}")

    success_flags = []
    for eval_type in args.eval:
        success = process_single_evaluation(args, eval_type)
        success_flags.append(success)

    if all(success_flags):
        logger.info("[run] All evaluations completed successfully")
        return True
    else:
        failed_types = [t for t, s in zip(args.eval, success_flags) if not s]
        logger.warning(f"[run] Completed with failures in: {', '.join(failed_types)}")
        return False


def main():
    """
    命令行入口：保留原有使用方式。
    示例：
        python -m data_quality.main -i INPUT_DIR -o OUTPUT_DIR -e answer context
    """
    try:
        args = parse_args()
        args.model_config = load_model_config(args.model_config)
        args.columns_config = load_model_config(args.columns_config)
        logger.info(f"Starting data quality assessment with args: {vars(args)}")

        success_flags = []
        for eval_type in args.eval:
            success = process_single_evaluation(args, eval_type)
            success_flags.append(success)

        if all(success_flags):
            logger.info("All evaluations completed successfully")
        else:
            failed_types = [t for t, s in zip(args.eval, success_flags) if not s]
            logger.warning(f"Completed with failures in: {', '.join(failed_types)}")
            sys.exit(1)

    except Exception as e:
        logger.error(f"Fatal error occurred: {str(e)}", exc_info=True)
        sys.exit(1)


def cli_entry():
    """
    给 pyproject.toml 用的命令行入口。

    安装后可直接使用：
        data-quality -i INPUT_DIR -o OUTPUT_DIR -e answer context
    """
    main()


if __name__ == '__main__':
    # 示例：
    # python -m data_quality.main -i D:\QA问答对生成方案\input_dir_answer -o D:\QA问答对生成方案\output_dir_answer -e answer
    data-quality -i D:\QA问答对生成方案\input_dir_answer -o D:\QA问答对生成方案\output_dir_answer -e answer
    cli_entry()