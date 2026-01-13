from typing import Any, Type, List
from ..core.base import BaseProcessor
import importlib


class ProcessorFactory:
    """处理器工厂类，负责创建不同类型的处理器实例"""

    PROCESSOR_MAP = {
        'answer': ('data_quality.core.answer_processor', 'AnswerProcessor'),
        'context': ('data_quality.core.context_processor', 'ContextProcessor'),
        'reward': ('data_quality.core.reward_processor', 'RewardProcessor'),
        'c_relevance': ('data_quality.core.context_relevance_processor', 'ContextRelevanceProcessor'),
        'g_relevance': ('data_quality.core.groundedness_processor', 'GroundednessProcessor'),
        'a_relevance': ('data_quality.core.answer_relevance_processor', 'AnswerRelevanceProcessor'),
        # 可以扩展更多处理器映射
    }

    COMPOSED_EVAL_MAP = {
        # cga_relevance 等价于顺序执行 c_relevance -> g_relevance -> a_relevance
        'cga_relevance': ['c_relevance', 'g_relevance', 'a_relevance'],
    }

    @staticmethod
    def is_composed_eval(eval_type: str) -> bool:
        """判断是否为组合评估类型"""
        return eval_type in ProcessorFactory.COMPOSED_EVAL_MAP

    @staticmethod
    def get_sub_eval_types(eval_type: str) -> List[str]:
        """
        对于组合类型返回子类型列表，
        对于普通类型则返回 [eval_type]
        """
        if ProcessorFactory.is_composed_eval(eval_type):
            return ProcessorFactory.COMPOSED_EVAL_MAP[eval_type]
        return [eval_type]

    @staticmethod
    def get_processor_class(eval_type: str) -> Type[BaseProcessor]:
        """
        获取单一评估类型对应的处理器类。
        组合类型不应该直接调用本方法，而是先拆分子类型再调用。
        """
        try:
            module_name, class_name = ProcessorFactory.PROCESSOR_MAP[eval_type]
        except KeyError:
            raise ValueError(f"Unsupported evaluation type: {eval_type}")

        try:
            module = importlib.import_module(module_name)
            return getattr(module, class_name)
        except ImportError as e:
            raise ImportError(f"Failed to import module '{module_name}' for type '{eval_type}': {e}")
        except AttributeError as e:
            raise AttributeError(f"Module '{module_name}' has no class '{class_name}': {e}")

    @staticmethod
    def get_processor_instance(eval_type: str, *args, **kwargs) -> BaseProcessor:
        """根据评估类型获取对应的处理器实例"""
        processor_cls = ProcessorFactory.get_processor_class(eval_type)
        return processor_cls(*args, **kwargs)