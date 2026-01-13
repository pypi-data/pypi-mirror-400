import itertools
import json
import os
from pathlib import Path
import random
from typing import Any, Optional, Tuple, List, Dict

from ..core.base import BaseProcessor
from ..data.data_factory import DataHandlerFactory
from ..evaluators.reward import RewardEvalProcessor
from ..main import PROJECT_ROOT
from ..models.qwen_model import Qwen72BChat
from ..utils.calibrator import pairwise_evaluate, hybrid_ranking, generate_color, apply_cell_color
from ..utils.logger import setup_logger

import pandas as pd
import re
from openpyxl.styles import PatternFill
import hashlib

logger = setup_logger(__name__)


class RewardProcessor(BaseProcessor):
    def pre_process(self, args):
        input_path = Path(args.input)
        data_list = []
        if input_path.is_dir():
            excel_files = list(input_path.glob("*.xlsx")) + list(input_path.glob("*.xls"))
        elif input_path.is_file():
            excel_files = [input_path]
        else:
            raise FileNotFoundError(f"输入路径不存在: {input_path}")

        for file in excel_files:
            handler = DataHandlerFactory.get_handler(str(file))
            data = handler.read()
            data_list.append({'filename': str(file.name), 'data': data})

        return {'args': args, 'data_list': data_list}

    def core_process(self, processed_data):
        args = processed_data['args']
        data_list = processed_data['data_list']

        # 处理输出目录
        output_dir = None
        if hasattr(args, 'output') and args.output:
            output_dir = Path(args.output)
            output_dir.mkdir(parents=True, exist_ok=True)

        # 处理每个文件
        for item in data_list:
            filename = item['filename']
            data_df = item['data']
            if data_df.empty:
                logger.warning(f"{filename} 为空，跳过。")
                continue

            # 处理prompt模板
            if not hasattr(args, 'template') or args.template is None:
                template_name = "reward_prompt.yaml"
            else:
                template_name = args.template if args.template.endswith(".yaml") else args.template + ".yaml"
            yaml_path = os.path.join(PROJECT_ROOT, "prompt", template_name)
            logger.info(f"Using prompt yaml: {yaml_path}")

            processor = RewardEvalProcessor(
                yaml_path=yaml_path,
                required_columns=['问题', '上下文', '答案1', '答案2']
            )

            # 列兼容
            if '参考信息' not in data_df.columns:
                if '上下文' in data_df.columns:
                    data_df = data_df.rename(columns={'上下文': '参考信息'})
                else:
                    raise ValueError(f"{filename} 缺少'参考信息'或'上下文'列")

            grouped = data_df.groupby(['问题', '参考信息'])

            results = []
            comparison_details = []
            for (question, reference), group in grouped:
                if '模型回答' not in group.columns:
                    raise ValueError(f"{filename} 缺少'模型回答'列")
                answers = group['模型回答'].tolist()
                comparisons = pairwise_evaluate(question, reference, answers, processor)
                ranked_answers = hybrid_ranking(answers, comparisons)
                win_counts = {i: 0 for i in range(len(answers))}
                match_counts = {i: 0 for i in range(len(answers))}

                for comp in comparisons:
                    idx_a, idx_b = comp["pair"]
                    a_score = comp["scores"][idx_a]
                    b_score = comp["scores"][idx_b]

                    match_counts[idx_a] += 1
                    match_counts[idx_b] += 1

                    if a_score > b_score:
                        win_counts[idx_a] += 1
                    else:
                        win_counts[idx_b] += 1

                results.extend([{
                    "问题": question,
                    "参考信息": reference,
                    "排名": item["rank"],
                    "回答": item["answer"],
                    "胜率": round(win_counts[item["index"]] / match_counts[item["index"]], 2)
                    if match_counts[item["index"]] > 0 else 0.0
                } for item in ranked_answers])

                for comp in comparisons:
                    idx_a, idx_b = comp["pair"]
                    detail = {
                        "问题": question,
                        "参考信息": reference,
                        "回答A内容": answers[idx_a],
                        "回答B内容": answers[idx_b],
                        "A_总分": comp["scores"][idx_a],
                        "B_总分": comp["scores"][idx_b],
                        "更好回答": "A" if comp["scores"][idx_a] > comp["scores"][idx_b] else "B",
                        "分析理由": comp["metadata"]["reasoning"],
                        "各维度评分": json.dumps(comp["metadata"]["comparison"]["dimensions"]),
                        "评估Prompt": comp["metadata"]["prompt"]
                    }
                    comparison_details.append(detail)

            results_df = pd.DataFrame(results)
            comp_details_df = pd.DataFrame(comparison_details)

            all_answers = pd.concat([
                comp_details_df['回答A内容'],
                comp_details_df['回答B内容'],
                results_df['回答']
            ]).unique()

            color_map = {ans: PatternFill(
                start_color=generate_color(ans),
                end_color=generate_color(ans),
                fill_type='solid'
            ) for ans in all_answers}

            # === 拼接输出文件名 ===
            base, ext = os.path.splitext(filename)
            if output_dir:
                out_base = output_dir / base
            else:
                out_base = Path(filename).parent / base

            output_path1 = f"{out_base}_对比详情{ext}"
            output_path2 = f"{out_base}_综合排名{ext}"

            with pd.ExcelWriter(output_path1, engine='openpyxl') as writer:
                comp_details_df.to_excel(writer, index=False, sheet_name='对比详情')
                worksheet = writer.sheets['对比详情']
                apply_cell_color(worksheet, comp_details_df, '回答A内容', color_map)
                apply_cell_color(worksheet, comp_details_df, '回答B内容', color_map)

            with pd.ExcelWriter(output_path2, engine='openpyxl') as writer:
                results_df.to_excel(writer, index=False, sheet_name='综合排名')
                worksheet = writer.sheets['综合排名']
                apply_cell_color(worksheet, results_df, '回答', color_map)

            logger.info(f"{filename} 处理完成，输出: {output_path1}, {output_path2}")

        return True


