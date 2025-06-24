# memory_manager.py
import os, json, time, glob
from typing import Dict, Any, List, Optional
from .memory_chunk_manager import MemoryChunkManager
from .memory_compressor import MemoryCompressor
from .memory_index_manager import MemoryIndexManager


class MemoryManager:
    """增强的记忆管理器 - 支持分片存储、索引和压缩"""
    
    def __init__(self, memory_path: str = "./memory", chunk_size: int = 100):
        self.memory_path = memory_path
        self.chunk_size = chunk_size
        os.makedirs(self.memory_path, exist_ok=True)

        # 初始化子模块
        self.chunk_manager = MemoryChunkManager(chunk_size)
        self.compressor = MemoryCompressor()
        self.index_manager = MemoryIndexManager(memory_path)
    
    def save_message(self, session_id: str, message: Dict[str, Any]) -> int:
        """保存单条消息，返回消息编号"""
        # 加载会话索引
        index_data = self.index_manager.load_session_index(session_id)
        
        # 计算新消息编号
        message_number = index_data["total_messages"] + 1
        chunk_index = self.chunk_manager.get_chunk_index(message_number)
        
        # 加载或创建分片
        chunk_file = os.path.join(
            self.index_manager.chunks_path,
            self.chunk_manager.get_chunk_filename(session_id, chunk_index)
        )
        
        if os.path.exists(chunk_file):
            with open(chunk_file, 'r', encoding='utf-8') as f:
                chunk_data = json.load(f)
        else:
            chunk_data = {"messages": []}
        
        # 添加消息
        message_with_meta = {
            "number": message_number,
            "timestamp": time.time(),
            **message
        }
        chunk_data["messages"].append(message_with_meta)
        
        # 保存分片
        with open(chunk_file, 'w', encoding='utf-8') as f:
            json.dump(chunk_data, f, indent=2, ensure_ascii=False)
        
        # 更新索引
        start, end = self.chunk_manager.get_chunk_range(chunk_index)
        actual_end = min(end, message_number)
        self.index_manager.update_chunk_info(
            session_id, chunk_index, start, actual_end, len(chunk_data["messages"])
        )
        
        return message_number
    
    def load_messages_by_range(
        self,
        session_id: str,
        start_msg: int = 1,
        end_msg: Optional[int] = None,
        use_compression: bool = False,
        compression_model: str = "deepseek_chat",
        read_compressed: bool = False
    ) -> List[Dict[str, Any]]:
        """按范围加载消息
        
        Args:
            session_id: 会话ID
            start_msg: 开始消息编号
            end_msg: 结束消息编号
            use_compression: 是否实时压缩（读取时临时压缩）
            compression_model: 压缩使用的模型
            read_compressed: 是否读取已压缩的记忆（从summaries读取）
        """
        # 如果要读取已压缩的记忆
        if read_compressed:
            return self._load_compressed_summaries(session_id, start_msg, end_msg)
        
        # 获取会话总消息数
        index_data = self.index_manager.load_session_index(session_id)
        total_messages = index_data["total_messages"]
        
        if total_messages == 0:
            return []
        
        # 处理end_msg参数
        if end_msg is None:
            end_msg = total_messages
        end_msg = min(end_msg, total_messages)
        
        if start_msg > end_msg:
            return []
        
        # 计算需要的分片
        required_chunks = self.chunk_manager.calculate_required_chunks(start_msg, end_msg)
        
        all_messages = []
        for chunk_index in required_chunks:
            chunk_messages = self._load_chunk_messages(session_id, chunk_index, start_msg, end_msg)
            all_messages.extend(chunk_messages)
        
        # 可选实时压缩
        if use_compression and all_messages:
            compressed_summary = self.compressor.compress_messages(
                all_messages, compression_model
            )
            return [{
                "role": "system",
                "content": f"[实时压缩摘要] {compressed_summary}",
                "is_compressed": True,
                "compression_type": "realtime",
                "original_count": len(all_messages)
            }]
        
        return all_messages

    def _load_compressed_summaries(
        self,
        session_id: str,
        start_msg: int = 1,
        end_msg: Optional[int] = None
    ) -> List[Dict[str, Any]]:
        """加载已压缩的记忆摘要"""
        index_data = self.index_manager.load_session_index(session_id)
        summaries = index_data.get("summaries", {})
        
        if not summaries:
            return []
        
        # 计算需要的分片范围
        start_chunk = self.chunk_manager.get_chunk_index(start_msg)
        if end_msg:
            end_chunk = self.chunk_manager.get_chunk_index(end_msg)
        else:
            # 获取最大的chunk索引
            available_chunks = [int(k) for k in summaries.keys()]
            end_chunk = max(available_chunks) if available_chunks else start_chunk
        
        compressed_messages = []
        
        for chunk_index in range(start_chunk, end_chunk + 1):
            if str(chunk_index) in summaries:
                summary_info = summaries[str(chunk_index)]
                summary_file = summary_info["file"]
                summary_path = os.path.join(self.index_manager.summaries_path, summary_file)
                
                if os.path.exists(summary_path):
                    try:
                        with open(summary_path, 'r', encoding='utf-8') as f:
                            summary_data = json.load(f)
                        
                        compressed_messages.append({
                            "role": "system",
                            "content": f"[压缩记忆-分片{chunk_index}] {summary_data['compressed_summary']}",
                            "is_compressed": True,
                            "compression_type": "stored",
                            "chunk_index": chunk_index,
                            "original_count": summary_data.get("original_count", 0),
                            "compression_model": summary_data.get("compression_model", "unknown")
                        })
                    except Exception as e:
                        print(f"加载压缩摘要失败: {e}")
        
        return compressed_messages

    def load_recent_messages(
        self,
        session_id: str,
        count: int = 20,
        use_compression: bool = False,
        compression_model: str = "deepseek_chat",
        read_compressed: bool = False
    ) -> List[Dict[str, Any]]:
        """加载最近的N条消息
        
        Args:
            session_id: 会话ID
            count: 消息数量
            use_compression: 是否实时压缩
            compression_model: 压缩模型
            read_compressed: 是否读取已压缩的记忆
        """
        index_data = self.index_manager.load_session_index(session_id)
        total_messages = index_data["total_messages"]
        
        if total_messages == 0:
            return []
        
        start_msg = max(1, total_messages - count + 1)
        return self.load_messages_by_range(
            session_id, start_msg, total_messages, use_compression, compression_model, read_compressed
        )
    
    def compress_chunk(
        self,
        session_id: str,
        chunk_index: int,
        model_name: str = "deepseek_chat",
        compression_prompt: str = ""
    ) -> bool:
        """压缩指定分片"""
        try:
            # 加载分片消息
            chunk_messages = self._load_chunk_messages(session_id, chunk_index)
            if not chunk_messages:
                return False
            
            # 执行压缩
            compressed_summary = self.compressor.compress_messages(
                chunk_messages, model_name, compression_prompt
            )
            
            # 保存压缩结果
            summary_file = f"{session_id}_summary_{chunk_index:03d}.json"
            summary_path = os.path.join(self.index_manager.summaries_path, summary_file)
            
            summary_data = {
                "chunk_index": chunk_index,
                "original_count": len(chunk_messages),
                "compressed_summary": compressed_summary,
                "compression_model": model_name,
                "created_at": time.time()
            }
            
            with open(summary_path, 'w', encoding='utf-8') as f:
                json.dump(summary_data, f, indent=2, ensure_ascii=False)
            
            # 更新索引
            self.index_manager.update_summary_info(session_id, chunk_index, summary_file)
            
            return True
            
        except Exception as e:
            print(f"压缩分片失败: {e}")
            return False
    
    def batch_compress_chunks(
        self,
        session_id: str,
        chunk_indices: List[int],
        model_name: str = "deepseek_chat",
        compression_prompt: str = ""
    ) -> Dict[int, bool]:
        """批量压缩分片"""
        results = {}
        for chunk_index in chunk_indices:
            results[chunk_index] = self.compress_chunk(
                session_id, chunk_index, model_name, compression_prompt
            )
        return results
    
    def _load_chunk_messages(
        self,
        session_id: str,
        chunk_index: int,
        start_filter: Optional[int] = None,
        end_filter: Optional[int] = None
    ) -> List[Dict[str, Any]]:
        """加载分片中的消息"""
        chunk_file = os.path.join(
            self.index_manager.chunks_path,
            self.chunk_manager.get_chunk_filename(session_id, chunk_index)
        )
        
        if not os.path.exists(chunk_file):
            return []
        
        try:
            with open(chunk_file, 'r', encoding='utf-8') as f:
                chunk_data = json.load(f)
            
            messages = chunk_data.get("messages", [])
            
            # 应用范围过滤
            if start_filter is not None or end_filter is not None:
                filtered_messages = []
                for msg in messages:
                    msg_num = msg.get("number", 0)
                    if start_filter is not None and msg_num < start_filter:
                        continue
                    if end_filter is not None and msg_num > end_filter:
                        continue
                    filtered_messages.append(msg)
                return filtered_messages
            
            return messages
            
        except Exception as e:
            print(f"加载分片失败: {e}")
            return []
    
    def get_session_stats(self, session_id: str) -> Dict[str, Any]:
        """获取会话统计信息"""
        index_data = self.index_manager.load_session_index(session_id)
        available_chunks = self.index_manager.list_available_chunks(session_id)

        return {
            "session_id": session_id,
            "total_messages": index_data["total_messages"],
            "total_chunks": len(available_chunks),
            "compressed_chunks": len(index_data["summaries"]),
            "chunk_size": self.chunk_size,
            "created_at": index_data["created_at"],
            "last_updated": index_data["last_updated"]
        }
    
    def list_sessions(self) -> List[str]:
        """列出所有会话"""
        index_files = glob.glob(os.path.join(self.memory_path, "*_index.json"))
        sessions = []
        for file_path in index_files:
            filename = os.path.basename(file_path)
            session_id = filename.replace("_index.json", "")
            sessions.append(session_id)
        return sessions
