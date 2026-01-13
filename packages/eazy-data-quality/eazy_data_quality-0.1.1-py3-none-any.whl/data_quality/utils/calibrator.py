import json
import itertools
import pandas as pd
import re
from openpyxl.styles import PatternFill
import hashlib

import random
from typing import Any, Optional, Tuple, List, Dict
from ..evaluators.reward import RewardEvalProcessor
from ..models.qwen_model import Qwen72BChat
from ..utils.logger import setup_logger
logger = setup_logger(__name__)

class DynamicCalibrator:
    """动态评分校准器"""

    def __init__(self):
        self.dim_distributions = {
            'relevance': {'counts': [0] * 5, 'mean': 3.0},
            'accuracy': {'counts': [0] * 5, 'mean': 3.0},
            'directness': {'counts': [0] * 5, 'mean': 3.0},
            'comprehensiveness': {'counts': [0] * 5, 'mean': 3.0}
        }

    def update(self, scores: dict):
        """更新分数分布"""
        for dim, score in scores.items():
            self.dim_distributions[dim]['counts'][score - 1] += 1
            total = sum(self.dim_distributions[dim]['counts'])
            self.dim_distributions[dim]['mean'] = (
                sum((i + 1) * count for i, count in enumerate(self.dim_distributions[dim]['counts'])) / total
            )

    def adjust(self, raw_scores: dict) -> dict:
        """基于分布动态调整"""
        adjusted = {}
        for dim, score in raw_scores.items():
            z_score = (score - self.dim_distributions[dim]['mean']) / 1.0
            if z_score > 1.5 and self.dim_distributions[dim]['counts'][4] < 2:
                adjusted[dim] = min(5, score + 1)
            elif z_score < -1.5 and self.dim_distributions[dim]['counts'][0] < 2:
                adjusted[dim] = max(1, score - 1)
            else:
                adjusted[dim] = score
        return adjusted


class ScoreCalibrationTool:
    """评分校准工具类"""

    def __init__(self, weights=None):
        self.calibrator = DynamicCalibrator()
        # 支持自定义权重
        self.weights = weights or {
            'relevance': 0.25,
            'accuracy': 0.5,
            'directness': 0.1,
            'comprehensiveness': 0.15
        }

    def parse_and_calibrate(self, response: str) -> dict:
        """
        解析响应、进行动态分数校准，并返回最终带总分的结构化数据
        :param response: json字符串，包含comparison->dimensions和overall字段
        :return: 校准后数据（dict），解析异常时返回None
        """
        try:
            parsed_data = json.loads(response)
            raw_scores = parsed_data['comparison']['dimensions']

            # 对A、B答案分别校准
            for ans in ['A', 'B']:
                adjusted = self.calibrator.adjust({
                    dim: raw_scores[dim][ans]
                    for dim in raw_scores
                })
                for dim in raw_scores:
                    raw_scores[dim][ans] = adjusted[dim]

            # 更新分布
            for ans in ['A', 'B']:
                self.calibrator.update({dim: raw_scores[dim][ans] for dim in raw_scores})

            # 重新计算权重总分
            for ans in ['A', 'B']:
                total = sum(raw_scores[dim][ans] * self.weights.get(dim, 0) for dim in raw_scores)
                parsed_data['comparison']['overall'][ans] = round(total, 1)

            return parsed_data
        except Exception as e:
            logger.error(f"解析失败: {str(e)}")
            return None


def pairwise_evaluate(question: str, reference: str, answers: List[str], processor: RewardEvalProcessor) -> List[Dict]:
    """优化后的两两评估（增加元数据存储）"""
    comparisons = []
    pairs = list(itertools.combinations(enumerate(answers), 2))

    for (idx_a, ans_a), (idx_b, ans_b) in pairs:
        # 随机打乱回答顺序消除位置偏差
        if random.random() < 0.5:
            ans_a, ans_b = ans_b, ans_a
            idx_a, idx_b = idx_b, idx_a
        prompt = processor.user_format(question.strip(), reference.strip(), ans_a.strip(), ans_b.strip())

        response = Qwen72BChat().chat(prompt)
        if not response:
            continue

        parsed_data = ScoreCalibrationTool().parse_and_calibrate(response)
        if parsed_data:
            comparisons.append({
                "pair": (idx_a, idx_b),
                "scores": {
                    idx_a: parsed_data["comparison"]["overall"]["A"],
                    idx_b: parsed_data["comparison"]["overall"]["B"]
                },
                "metadata": {
                    "comparison": parsed_data["comparison"],
                    "reasoning": parsed_data["reasoning"],
                    "prompt": prompt
                }
            })

    return comparisons


def hybrid_ranking(answers: List[str], comparisons: List[Dict]) -> List[Dict]:
    """混合排名算法"""
    # Elo部分初始化
    elo_ratings = {idx: 1500 for idx in range(len(answers))}
    K = 32

    # Borda部分初始化
    borda_counts = {idx: 0 for idx in range(len(answers))}

    for comp in comparisons:
        # 更新Elo评分
        idx_a, idx_b = comp['pair']
        score_diff = comp['scores'][idx_a] - comp['scores'][idx_b]
        expected = 1 / (1 + 10 ** ((elo_ratings[idx_b] - elo_ratings[idx_a]) / 400))
        elo_ratings[idx_a] += K * (score_diff / 5 - expected)
        elo_ratings[idx_b] += K * (-score_diff / 5 - (1 - expected))

        # 更新Borda计数
        if score_diff > 0:
            borda_counts[idx_a] += 1
        else:
            borda_counts[idx_b] += 1

    # 计算混合分数（各占50%权重）
    max_elo = max(elo_ratings.values()) or 1  # 避免除以零
    max_borda = max(borda_counts.values()) or 1
    combined_scores = {
        idx: 0.5 * (elo_ratings[idx] / max_elo) + 0.5 * (borda_counts[idx] / max_borda)
        for idx in elo_ratings
    }

    # 修正排序部分：使用索引列表并按综合分数和Elo降序排列
    ranked_indices = sorted(
        range(len(answers)),
        key=lambda x: (-combined_scores[x], -elo_ratings[x])
    )

    # 生成排名结果
    return [
        {
            "rank": i + 1,
            "index": idx,  # 新增原始索引
            "answer": answers[idx],
            "elo": elo_ratings[idx],
            "borda": borda_counts[idx],
            "combined_score": combined_scores[idx]
        }
        for i, idx in enumerate(ranked_indices)
    ]


def generate_color(text):
    """更稳定的颜色生成"""
    hash_str = hashlib.sha3_256(text.encode()).hexdigest()[:9]
    return f"FF{hash_str[:6]}"


def apply_cell_color(worksheet, df, column_name, color_map):
    """通用颜色应用函数"""
    col_idx = df.columns.get_loc(column_name) + 1
    for row_idx in range(2, len(df)+2):
        cell = worksheet.cell(row=row_idx, column=col_idx)
        if cell.value in color_map:
            cell.fill = color_map[cell.value]


if __name__ == "__main__":
    tool = ScoreCalibrationTool()
    # result = tool.parse_and_calibrate(json_str)