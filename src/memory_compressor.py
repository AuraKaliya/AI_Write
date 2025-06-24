import os, json, time, glob
from typing import Dict, Any, List, Optional

class MemoryCompressor:
    """记忆压缩器 - 独立的压缩模块"""
    
    def __init__(self):
        pass
    
    def compress_messages(
        self, 
        messages: List[Dict[str, Any]], 
        model_name: str = "deepseek_chat",
        compression_prompt: str = ""
    ) -> str:
        """压缩消息列表为摘要文本"""
        if not messages:
            return ""
        
        # 构建压缩提示词
        if not compression_prompt:
            compression_prompt = """请将以下对话历史压缩为简洁的摘要，保留关键信息和上下文：

对话历史：
{history}

请返回压缩后的摘要："""
        
        # 格式化历史记录
        history_text = self._format_messages_for_compression(messages)
        
        # 调用LLM进行压缩
        compress_messages = [
            {"role": "user", "content": compression_prompt.format(history=history_text)}
        ]
        
        try:
            compressed_summary = LLMCaller.call(compress_messages, model_name)
            return compressed_summary
        except Exception as e:
            print(f"压缩失败: {e}")
            return self._fallback_compression(messages)
    
    def _format_messages_for_compression(self, messages: List[Dict[str, Any]]) -> str:
        """格式化消息用于压缩"""
        formatted = []
        for i, msg in enumerate(messages, 1):
            role = msg.get('role', 'unknown')
            content = msg.get('content', '')
            formatted.append(f"{i}. [{role}]: {content}")
        return "\n".join(formatted)
    
    def _fallback_compression(self, messages: List[Dict[str, Any]]) -> str:
        """压缩失败时的降级方案"""
        if not messages:
            return ""
        
        # 简单的截取压缩
        total_chars = sum(len(msg.get('content', '')) for msg in messages)
        summary = f"包含{len(messages)}条消息，总计约{total_chars}字符的对话记录。"
        
        # 添加最后几条消息的简要信息
        if len(messages) > 0:
            last_msg = messages[-1]
            summary += f" 最后消息: [{last_msg.get('role', 'unknown')}] {last_msg.get('content', '')[:50]}..."
        
        return summary
