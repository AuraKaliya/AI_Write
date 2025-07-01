from pydantic import BaseModel
from typing import List, Dict, Any, Optional
import json
import os
from .chapter_outline_setting import NovelOutline,StageOutline,ChapterOutline

class OutlineManager:
    """
    OutlineManager 用于加载完整的小说大纲数据（包含大纲、细纲、章纲），
    并提供基于标识的检索功能，同时支持 JSON 文本与对象之间的转换。
    
    数据结构:
    {
        "novel_outline": {...},  # NovelOutline 数据
        "stage_outlines": {...}, # 字典: {stage_name: StageOutline}
        "chapter_outlines": {...} # 字典: {chapter_number: ChapterOutline}
    }
    """
    
    def __init__(
        self,
        source: str,
        outlines: Optional[Dict[str, Any]] = None
    ):
        """
        初始化方式：
          - 如果只传了 source（字符串），且 outlines=None，视作文件路径 -> 从文件加载
          - 如果同时传 source（标识名称）和 outlines（完整字典），直接使用该字典
        """
        # 情况 A: 直接传入字典，绕过文件加载
        if outlines is not None:
            if not isinstance(outlines, dict):
                raise ValueError("当提供 outlines 时，必须是完整的字典格式")
            self.source = source
            self.outlines = outlines

        # 情况 B: 只传 source，视作文件路径
        else:
            if not os.path.isfile(source):
                raise FileNotFoundError(f"大纲文件 {source} 不存在")
            self.source = source
            with open(source, 'r', encoding='utf-8') as f:
                self.outlines = json.load(f)
                
    def get_novel_outline(self) -> NovelOutline:
        """获取完整的小说大纲对象"""
        novel_data = self.outlines.get("novel_outline")
        if not novel_data:
            raise ValueError("大纲数据中缺少 'novel_outline' 部分")
        return NovelOutline(**novel_data)
    
    def get_stage_outline(self, stage_name: str) -> StageOutline:
        """根据阶段名称获取细纲对象"""
        stage_data = self.outlines["stage_outlines"].get(stage_name)
        if not stage_data:
            raise ValueError(f"找不到阶段 '{stage_name}' 的细纲数据")
        return StageOutline(**stage_data)
    
    def get_chapter_outline(self, chapter_number: str) -> ChapterOutline:
        """根据章节编号获取章纲对象"""
        chapter_data = self.outlines["chapter_outlines"].get(chapter_number)
        if not chapter_data:
            raise ValueError(f"找不到章节 '{chapter_number}' 的章纲数据")
        return ChapterOutline(**chapter_data)
    
    def get_all_stage_names(self) -> List[str]:
        """获取所有可用的阶段名称列表"""
        return list(self.outlines["stage_outlines"].keys())

    def get_all_chapter_numbers(self) -> List[str]:
        """获取所有可用的章节编号列表"""
        return list(self.outlines["chapter_outlines"].keys())
    
    def to_json(self) -> str:
        """返回完整大纲数据的 JSON 文本表示"""
        return json.dumps(self.outlines, ensure_ascii=False, indent=2)
    
    @classmethod
    def create_new(
        cls, 
        novel_outline: NovelOutline,
        stage_outlines: Dict[str, StageOutline],
        chapter_outlines: Dict[str, ChapterOutline],
        source_name: str = "new_outline"
    ) -> "OutlineManager":
        """
        从对象创建新的大纲管理器
        
        参数:
            novel_outline: 小说大纲对象
            stage_outlines: 阶段细纲字典 {stage_name: StageOutline}
            chapter_outlines: 章节章纲字典 {chapter_number: ChapterOutline}
            source_name: 数据来源标识
        """
        # 转换为可序列化的字典格式
        outlines = {
            "novel_outline": novel_outline.model_dump(),
            "stage_outlines": {k: v.model_dump() for k, v in stage_outlines.items()},
            "chapter_outlines": {k: v.model_dump() for k, v in chapter_outlines.items()}
        }
        return cls(source_name, outlines=outlines)
    def get_novel_outline_json(self) -> str:
        """
        获取小说大纲的JSON字符串表示（使用model_dump()）
        
        返回:
            str: 小说大纲的JSON格式字符串
        """
        novel_outline = self.get_novel_outline()
        return json.dumps(novel_outline.model_dump(), ensure_ascii=False, indent=2)
    
    def get_stage_outline_json(self, stage_name: str) -> str:
        """
        获取指定阶段细纲的JSON字符串表示（使用model_dump()）
        
        参数:
            stage_name (str): 要获取的阶段名称
            
        返回:
            str: 阶段细纲的JSON格式字符串
            
        异常:
            ValueError: 如果找不到指定阶段
        """
        stage_outline = self.get_stage_outline(stage_name)
        return json.dumps(stage_outline.model_dump(), ensure_ascii=False, indent=2)
    