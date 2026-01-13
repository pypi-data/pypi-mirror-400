from typing import Any, Optional, Tuple

from ..core.base import BaseProcessor
from ..data.data_factory import DataHandlerFactory
from ..evaluators.AnswerRelevance import AnswerRelevanceEvalProcessor
from ..main import PROJECT_ROOT
from ..models.qwen_model import Qwen72BChat
from ..utils.logger import setup_logger
import re
from pathlib import Path
import os
import pandas as pd

logger = setup_logger(__name__)


def extract_score(text: str) -> float:
    """统一评分提取逻辑"""
    match = re.search(r"评分:\s*(\d+\.?\d*)", text)
    return float(match.group(1)) if match else 0.0

class AnswerRelevanceProcessor(BaseProcessor):
    def pre_process(self, args) -> Any:
        """
        读取目录下所有支持的文件并返回
        返回list: [{'filename': 文件名, 'data': pandas.DataFrame}]
        """
        input_path = Path(args.input)
        data_list = []
        support_exts = {"xlsx", "xls", "json", "jsonl", "txt", "csv"}

        if input_path.is_dir():
            files = [p for p in input_path.glob('**/*') if p.suffix.lower().lstrip('.') in support_exts]
        elif input_path.is_file():
            if input_path.suffix.lower().lstrip('.') in support_exts:
                files = [input_path]
            else:
                raise ValueError(f"文件格式不支持：{input_path.name}")
        else:
            raise ValueError(f"输入路径不存在: {args.input}")

        if not files:
            raise ValueError(f"目录下没有可处理的文件: {args.input}")
        eval_output_suffix = getattr(args, "eval_output_suffix", "a_relevance")

        for file in files:
            handler = DataHandlerFactory.get_handler(str(file))
            data = handler.read()
            new_filename = f"{file.stem}_{eval_output_suffix}{file.suffix}"
            data_list.append({'filename': new_filename, 'data': data})
        return {'args': args, 'data_list': data_list}


    def core_process(self, pre_data):
        """对所有文件的数据组装prompt"""
        args = pre_data['args']
        data_list = pre_data['data_list']
        columns_config = getattr(args, "columns_config", {}) or {}
        required_columns_keys = ["truth_context", "question", "truth_answer"]
        required_columns = [columns_config[k] for k in required_columns_keys if k in columns_config]

        if args.template is None:
            template_name = "answer_relevance_prompt.yaml"
        else:
            template_name = args.template if args.template.endswith(".yaml") else args.template + ".yaml"
        yaml_path = os.path.join(PROJECT_ROOT, "prompt", template_name)
        logger.info(f"Using prompt yaml: {yaml_path}")

        processor = AnswerRelevanceEvalProcessor(
            yaml_path=yaml_path,
            required_columns=required_columns
        )

        result_list = []
        for item in data_list:
            input_data = item['data']
            all_prompts = processor.process(input_data)
            result_list.append({
                'filename': item['filename'],
                'input_data': input_data,
                'all_prompts': all_prompts
            })

        return {'args': args, 'result_list': result_list}

    def post_process(self, result: Any) -> Tuple[bool, str]:
        if isinstance(result, tuple) and isinstance(result[0], bool):
            return result

        try:
            args = result['args']
            result_list = result['result_list']

            model_config = getattr(args, "model_config", {}) or {}
            qwen_chat_keys = ["base_url", "model_name", "api_key", "retry_times", "temperature"]
            qwen_chat_kwargs = {k: model_config[k] for k in qwen_chat_keys if k in model_config and model_config[k] is not None}

            columns_config = getattr(args, "columns_config", {}) or {}
            col_score = columns_config.get('answer_relevance_score', '答案相关性（问题和答案）分数')
            col_score_desc = columns_config.get('answer_relevance_description', '答案相关性得分说明')
            col_prompt = columns_config.get('prompt_with_context', '带上下文的提示词')

            output_dir = Path(args.output)
            output_dir.mkdir(parents=True, exist_ok=True)

            for item in result_list:
                scores = []
                results = []
                prompt = []
                all_prompts = item['all_prompts']
                input_data = item['input_data']

                if args.mode == "model":
                    for system_prompt, user_prompt in all_prompts:
                        result_text = Qwen72BChat(**qwen_chat_kwargs).chat(
                            system_prompt=system_prompt,
                            user_prompt=user_prompt
                        )
                        score = extract_score(result_text)
                        results.append(result_text)
                        scores.append(score)
                        prompt.append(system_prompt + "\n" + user_prompt)
                elif args.mode == "regex":
                    # todo
                    pass

                input_data[col_score] = scores
                input_data[col_score_desc] = results
                input_data[col_prompt] = prompt

                output_file = output_dir / item['filename']
                handler = DataHandlerFactory.get_handler(str(output_file))

                # 如果文件已存在，读出旧数据并追加/覆盖列（用于 cga_relevance 多轮写同一文件）
                if output_file.exists():
                    try:
                        existing_data = handler.read()
                        for col in [col_score, col_score_desc, col_prompt]:
                            existing_data[col] = input_data[col]
                        input_data = existing_data
                        logger.info(f"Merging results into existing file {output_file}")
                    except Exception as e:
                        logger.warning(
                            f"Failed to merge with existing file {output_file}, overwrite it. Error: {e}"
                        )

                handler.write(input_data)

                logger.info(f"Results successfully written to {output_file}")

            return True, ""
        except Exception as e:
            logger.error(f"Post processing failed: {str(e)}", exc_info=True)
            return False, f"后处理异常: {str(e)}"






