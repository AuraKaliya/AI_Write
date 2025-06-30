import os,json,re
from pydantic import BaseModel
from typing import Dict, Any, List, Optional
from world_setting import WorldSetting,BaseWorldSetting

class SettingExtractor:
    """
    SettingExtractor 用于加载完整的世界设定数据，并提供基于关键词的检索功能，
    同时支持 JSON 文本与对象之间的转换。
    """
    
    def __init__(
        self,
        source: str,
        settings: Optional[Dict[str, Any]] = None
    ):
        """
        初始化方式：
          - 如果只传了 source（字符串），且 settings=None，视作文件路径 -> 从文件加载。
          - 如果同时传 source（字符标识）和 settings（完整字典），直接使用该字典。
        """
        # 情况 A: 直接传入字典，绕过文件加载
        if settings is not None:
            if not isinstance(settings, dict):
                raise ValueError("当提供 settings 时，settings 必须是 Dict[str, Any]")
            filepath = source
            self.settings = settings

        # 情况 B: 只传 source，视作 JSON 文件路径
        else:
            filepath = source
            if not os.path.isfile(filepath):
                raise FileNotFoundError(f"文件 {filepath} 不存在")
            self.filepath = filepath
            with open(filepath, 'r', encoding='utf-8') as f:
                self.settings = json.load(f)

    def get_setting(self, keywords: List[str]) -> WorldSetting:
        """
        根据输入的关键词列表，从完整的世界设定数据中查找相关设定，
        返回一个 WorldSetting 对象。策略如下：

        - 使用完整的 base_world_setting 数据；
        - 在 related_settings 中筛选出名称或描述中包含任一关键词的记录；
        - 生成 WorldSetting 实例返回。
        """
        base_setting_data = self.settings.get("base_world_setting", {})
        if not base_setting_data:
            raise ValueError("缺少 'base_world_setting' 数据")

        # 使用 Pydantic V2 的方式解析 base_world_setting
        base_world_setting = BaseWorldSetting.model_validate(base_setting_data)

        # 获取所有 related_settings 数据（假设为字典格式）
        all_related_settings = self.settings.get("related_settings", {})

        # 根据关键词筛选相关设定
        filtered_settings = {}
        for name, description in all_related_settings.items():
            for kw in keywords:
                if kw in name or kw in description:
                    filtered_settings[name] = description
                    break  # 一个关键词匹配即可，避免重复添加

        return WorldSetting(
            base_world_setting=base_world_setting,
            related_settings=filtered_settings
        )


    def to_json(self) -> str:
        """
        返回完整世界设定数据的 JSON 文本表示
        """
        return json.dumps(self.settings, ensure_ascii=False, indent=2)

    @classmethod
    def from_json(cls, json_text: str) -> "SettingExtractor":
        """
        根据传入的 JSON 文本生成一个 SettingExtractor 实例。
        注意：此方法创建的实例没有关联具体文件路径。
        """
        data = json.loads(json_text)
        instance = cls.__new__(cls)  # bypass __init__
        instance.filepath = None
        instance.settings = data
        return instance


# --------------------------------------------------------------------------------
# 示例说明（仅用于测试，可根据实际情况调整）

if __name__ == "__main__":
    #测试setting extractor
    print("当前工作路径：", os.getcwd())
    filepath = "testData/world_setting.json"
    try:
        whole_setting = SettingExtractor(filepath)
        print("完整世界设定：")
        print(whole_setting.to_json())

        # 根据关键词查询相关设定
        query_keywords = [""]
        relevant_setting = whole_setting.get_setting(query_keywords)

        print("\n查询结果，生成的 WorldSetting 对象：")
        print(json.dumps(
            relevant_setting.model_dump(),
            indent=2,
            ensure_ascii=False
        ))

    except Exception as e:
        print("发生错误：", e)
