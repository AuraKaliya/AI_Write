import os,time
from typing import Dict, Any, List, Optional

class MemoryIndexManager:
    """记忆索引管理器 - 处理会话索引和元数据"""
    
    def __init__(self, memory_path: str):
        self.memory_path = memory_path
        self.chunks_path = os.path.join(memory_path, "chunks")
        self.summaries_path = os.path.join(memory_path, "summaries")
        os.makedirs(self.chunks_path, exist_ok=True)
        os.makedirs(self.summaries_path, exist_ok=True)
    
    def load_session_index(self, session_id: str) -> Dict[str, Any]:
        """加载会话索引"""
        index_file = os.path.join(self.memory_path, f"{session_id}_index.json")
        if os.path.exists(index_file):
            with open(index_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        else:
            # 创建新索引
            return {
                "session_id": session_id,
                "total_messages": 0,
                "chunks": {},  # {chunk_index: {"start": 1, "end": 100, "count": 100}}
                "summaries": {},  # {chunk_index: {"file": "summary_001.json", "created_at": "..."}}
                "created_at": time.time(),
                "last_updated": time.time()
            }
    
    def save_session_index(self, session_id: str, index_data: Dict[str, Any]):
        """保存会话索引"""
        index_data["last_updated"] = time.time()
        index_file = os.path.join(self.memory_path, f"{session_id}_index.json")
        with open(index_file, 'w', encoding='utf-8') as f:
            json.dump(index_data, f, indent=2, ensure_ascii=False)
    
    def update_chunk_info(self, session_id: str, chunk_index: int, start: int, end: int, count: int):
        """更新分片信息"""
        index_data = self.load_session_index(session_id)
        index_data["chunks"][str(chunk_index)] = {
            "start": start,
            "end": end, 
            "count": count,
            "updated_at": time.time()
        }
        index_data["total_messages"] = max(index_data["total_messages"], end)
        self.save_session_index(session_id, index_data)
    
    def update_summary_info(self, session_id: str, chunk_index: int, summary_file: str):
        """更新摘要信息"""
        index_data = self.load_session_index(session_id)
        index_data["summaries"][str(chunk_index)] = {
            "file": summary_file,
            "created_at": time.time()
        }
        self.save_session_index(session_id, index_data)
    
    def get_chunk_info(self, session_id: str, chunk_index: int) -> Optional[Dict[str, Any]]:
        """获取分片信息"""
        index_data = self.load_session_index(session_id)
        return index_data["chunks"].get(str(chunk_index))
    
    def list_available_chunks(self, session_id: str) -> List[int]:
        """列出可用的分片索引"""
        index_data = self.load_session_index(session_id)
        return [int(k) for k in index_data["chunks"].keys()]