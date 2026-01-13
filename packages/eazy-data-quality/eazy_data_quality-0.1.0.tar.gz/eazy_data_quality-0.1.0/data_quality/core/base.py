from abc import ABC, abstractmethod
from typing import Any, Optional, Tuple

class BaseProcessor(ABC):
    """
    处理器的抽象基类，定义处理流程的模板方法
    """

    def pre_process(self, input_data: Any) -> Any:
        # 默认空实现
        return input_data

    @abstractmethod
    def core_process(self, processed_data: Any) -> Any:
        pass

    def post_process(self, result: Any) -> Tuple[bool, str]:
        """
        后置处理，返回 (True, "") 或 (False, "错误原因")
        默认实现：如果 result 为 True/非空，表示成功，否则失败
        """
        if result is True or (isinstance(result, (list, dict, str)) and result):
            return True, ""
        elif isinstance(result, tuple) and len(result) == 2 and isinstance(result[0], bool):
            return result  # 子类已自定义格式
        else:
            return False, str(result) if result else "Unknown error"

    def execute(self, input_data: Optional[Any] = None) -> Tuple[bool, str]:
        """
        执行处理，返回 (True, "") 或 (False, "原因")
        """
        try:
            pre_processed = self.pre_process(input_data)
            core_result = self.core_process(pre_processed)
            final_result = self.post_process(core_result)
            # 保证返回为 (bool, str)
            if isinstance(final_result, tuple) and len(final_result) == 2 and isinstance(final_result[0], bool):
                return final_result
            else:
                # 容错，万一post_process返回不是元组
                return bool(final_result), "" if final_result else "处理失败"
        except Exception as e:
            return False, str(e)

    def __call__(self, *args, **kwargs) -> Tuple[bool, str]:
        return self.execute(*args, **kwargs)