import os
import re
import yaml
from typing import List, Dict, Set, Union


class YamlVariableExtractor:
    """
    用于从yaml模板文件中提取大括号变量（如{question}、{context}等）的工具类。
    """

    def __init__(self, yaml_path_or_content: Union[str, bytes], is_file: bool = True):
        """
        :param yaml_path_or_content: yaml文件路径(默认)或yaml内容本身
        :param is_file: 如果为True，则参数是文件路径；否则为yaml内容字符串
        """
        if is_file:
            with open(yaml_path_or_content, 'r', encoding='utf-8') as f:
                self.yaml_content = f.read()
        else:
            self.yaml_content = yaml_path_or_content
        self.templates = self._parse_templates()

    def _parse_templates(self) -> List[str]:
        """
        解析yaml文件，提取所有value为字符串的字段（即模板内容）。
        """
        data = yaml.safe_load(self.yaml_content)
        templates = []
        if isinstance(data, dict):
            for v in data.values():
                if isinstance(v, str):
                    templates.append(v)
        return templates

    def extract_variables(self) -> list:
        """
        提取所有模板中的变量名（去重）。
        :return: 变量名集合，如{'question', 'context'}
        """
        pattern = r'\{(\w+)\}'
        variables = []
        for template in self.templates:
            found = re.findall(pattern, template)
            variables.extend(found)
        # 顺序去重
        return list(dict.fromkeys(variables))

    def extract_variables_with_template(self) -> Dict[str, List[str]]:
        """
        返回每个模板字符串对应的变量列表。
        :return: {模板内容: [变量1, 变量2]}
        """
        pattern = r'\{(\w+)\}'
        result = {}
        for template in self.templates:
            found = re.findall(pattern, template)
            result[template] = found
        return result


# 使用示例
if __name__ == "__main__":
    current_dir = os.path.dirname(os.path.abspath(__file__))
    yaml_path = os.path.join(current_dir, '../config/reward_prompt.yaml')
    yaml_path = os.path.normpath(yaml_path)
    extractor = YamlVariableExtractor(yaml_path)
    print(extractor.extract_variables())
    # print(extractor.extract_variables_with_template())