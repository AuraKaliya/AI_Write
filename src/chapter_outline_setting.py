from pydantic import BaseModel
from typing import List, Dict, Any
import json
import os

#### 章纲相关类定义 ####

class ChapterPlot(BaseModel):
    """
    章节情节单元，描述章节中的关键情节
    """
    summary: str
    details: Dict[str, Any]
    
    
class ChapterScene(BaseModel):
    """
    章节场景定义，描述章节中的具体场景
    """
    scene_name: str
    scene_description: str
    scene_purpose: str
    characters: List[str]
    
class ChapterOutline(BaseModel):
    """
    章节大纲，描述单个章节的结构和内容
    """
    chapter_number: str
    chapter_name: str
    stage_name: str
    chapter_purpose: str
    scenes: List[ChapterScene]
    plots: List[ChapterPlot]
    

#### 细纲相关类定义 ####

class MainEvent(BaseModel):
    """
    主要事件定义，描述故事阶段中的关键事件
    """
    event_name: str
    main_character: List[str]
    event_effect: str
    event_summary: str   
    
    
class StageOutline(BaseModel):
    """
    故事阶段细纲，描述一个故事阶段的详细内容
    """
    stage_name: str
    stage_target:list[str]
    main_event: List[MainEvent]


#### 大纲相关类定义 ####

class StoryStage(BaseModel):
    """
    故事阶段定义，描述小说中的一个主要部分
    """
    stage_name: str
    stage_summary: str
    
class NovelOutline(BaseModel):
    """
    小说大纲，描述整部小说的顶层结构
    """
    novel_name: str  # 小说名
    core_story: str  # 故事梗概
    story_stage: List[StoryStage]  # 故事阶段
    protagonist: List[str]  # 主角
    tone:str #作品基调
