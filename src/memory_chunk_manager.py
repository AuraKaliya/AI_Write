# memory_chunk_manager.py
import os
from typing import List

# === 记忆分片存储管理器 ===
class MemoryChunkManager:
    """分片存储管理器 - 处理消息的分片存储和索引"""
    
    def __init__(self, chunk_size: int = 100):
        self.chunk_size = chunk_size
    
    def get_chunk_index(self, message_number: int) -> int:
        """获取消息所属的分片索引"""
        return (message_number - 1) // self.chunk_size + 1
    
    def get_chunk_range(self, chunk_index: int) -> tuple:
        """获取分片的消息范围 (start, end)"""
        start = (chunk_index - 1) * self.chunk_size + 1
        end = chunk_index * self.chunk_size
        return start, end
    
    def get_chunk_filename(self, session_id: str, chunk_index: int) -> str:
        """生成分片文件名"""
        return f"{session_id}_chunk_{chunk_index:03d}.json"
    
    def calculate_required_chunks(self, start_msg: int, end_msg: int) -> List[int]:
        """计算需要读取的分片索引列表"""
        start_chunk = self.get_chunk_index(start_msg)
        end_chunk = self.get_chunk_index(end_msg)
        return list(range(start_chunk, end_chunk + 1))