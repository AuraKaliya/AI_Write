# state_manager.py
import os, json, glob, re, time
from typing import Dict, Any, List, Optional
from .chapter_state import ChapterState
from .setting_extractor import SettingExtractor
from pydantic import BaseModel
class StateManager:
    def __init__(self, data_path: str = "./data"):
        self.data_path = data_path
        os.makedirs(self.data_path, exist_ok=True)

    def _find_latest_file(self, pattern: str, novel_id: Optional[str] = None) -> Optional[str]:
        """查找最新文件，支持小说ID过滤"""
        if novel_id:
            # 如果指定了小说ID，添加ID前缀到模式中
            pattern = f"{novel_id}_{pattern}"
        
        files = glob.glob(os.path.join(self.data_path, pattern))
        if not files:
            return None
        
        def get_numeric_part(filename):
            # 提取文件名中的章节编号（忽略小说ID部分）
            basename = os.path.basename(filename)
            if novel_id:
                # 移除小说ID前缀后再提取数字
                basename = basename.replace(f"{novel_id}_", "", 1)
            numbers = re.findall(r'\d+', basename)
            return int(numbers[0]) if numbers else 0
        
        return max(files, key=get_numeric_part)

    def load_latest_state(self, novel_id: Optional[str] = None) -> Optional[ChapterState]:
        """加载最新状态，支持小说ID过滤"""
        latest_file = self._find_latest_file("chapter_*_state.json", novel_id)
        if not latest_file:
            return None

        with open(latest_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
            return ChapterState(**data)

    def save_state(self, state: ChapterState, novel_id: Optional[str] = None):
        """保存状态，支持小说ID"""
        if novel_id:
            file_path = os.path.join(
                self.data_path, 
                f"{novel_id}_chapter_{state.chapter_index:03d}_state.json"
            )
        else:
            # 兼容旧格式
            file_path = os.path.join(
                self.data_path, 
                f"chapter_{state.chapter_index:03d}_state.json"
            )
        
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(state.model_dump_json(indent=2))

    def load_world_bible(self,key_words="" ,novel_id: Optional[str] = None) -> Dict[str, Any]:
        """加载世界设定，支持小说ID过滤"""
        latest_file = self._find_latest_file("world_bible_*.json", novel_id)
        if not latest_file:
            return {}

        with open(latest_file, 'r', encoding='utf-8') as f:
            setting_extractor = SettingExtractor(latest_file, json.load(f))
            world_setting = setting_extractor.get_setting(key_words)
            return world_setting.model_dump()

    def save_world_bible(self, world_bible: Dict[str, Any], novel_id: Optional[str] = None, version: int = 0):
        """保存世界设定，支持小说ID"""
        if novel_id:
            file_path = os.path.join(
                self.data_path,
                f"{novel_id}_world_bible_{version:02d}.json"
            )
        else:
            # 兼容旧格式
            file_path = os.path.join(
                self.data_path,
                f"world_bible_{version:02d}.json"
            )
        
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(world_bible, f, indent=2, ensure_ascii=False)
    
    def list_novel_states(self, novel_id: str) -> List[str]:
        """列出指定小说的所有状态文件"""
        pattern = f"{novel_id}_chapter_*_state.json"
        files = glob.glob(os.path.join(self.data_path, pattern))
        return sorted(files)
    
    def list_novels(self) -> List[str]:
        """列出所有小说ID"""
        pattern = "*_chapter_*_state.json"
        files = glob.glob(os.path.join(self.data_path, pattern))
        novel_ids = set()
        
        for file_path in files:
            filename = os.path.basename(file_path)
            # 提取小说ID（第一个下划线之前的部分）
            parts = filename.split('_')
            if len(parts) >= 3 and parts[1] == 'chapter':
                novel_ids.add(parts[0])
        
        return sorted(list(novel_ids))