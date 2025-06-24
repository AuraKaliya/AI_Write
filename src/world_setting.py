# world_setting.py
from pydantic import BaseModel
from typing import List, Dict, Any
import json
import os

class WorldPowerLevel(BaseModel):
    name: str   #等阶名
    level: int  #由小到大，连续
    details: str
    
class WorldPowerSystem(BaseModel):
    name: str   #力量体系（如魔法、信仰、灵力）
    details: str
    power_levels:List[WorldPowerLevel]


class BaseWorldSetting(BaseModel):
    name: str
    introduction: str
    power_system: List[WorldPowerSystem]
    tech_level: str


class WorldSetting(BaseModel):
    base_world_setting: BaseWorldSetting
    related_settings: Dict[str, str]


