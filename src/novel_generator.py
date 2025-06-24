# novel_generator.py
import os, json, time
from typing import List, Dict, Any, Optional
from .state_manager import StateManager
from .memory_manager import MemoryManager
from .llm_caller import LLMCaller
from .chapter_state import ChapterState

# === 小说生成器 ===
class NovelGenerator:
    def __init__(self, chunk_size: int = 100):
        self.state_manager = StateManager()
        self.memory_manager = MemoryManager(chunk_size=chunk_size)

    def generate_chapter(
        self,
        chapter_outline: str,
        model_name: str = "deepseek_chat",
        system_prompt: str = "",
        use_memory: bool = False,
        session_id: str = "default",
        use_state: bool = True,
        use_world_bible: bool = True,
        update_state: bool = False,
        recent_count: int = 20,
        use_compression: bool = False,
        compression_model: str = "deepseek_chat",
        read_compressed: bool = False,
        novel_id: Optional[str] = None
    ) -> str:
        messages = []
        
        # 添加系统提示
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        
        # 加载历史记录
        if use_memory and recent_count > 0:
            history_messages = self.memory_manager.load_recent_messages(
                session_id=session_id,
                count=recent_count,
                use_compression=use_compression,
                compression_model=compression_model,
                read_compressed=read_compressed
            )
            messages.extend(history_messages)
        
        # 构建用户输入 - 使用更自然的提示词表达
        user_content = f"请根据下面的章节细纲进行小说内容创作：\n\n{chapter_outline}"
        
        if use_state:
            state = self.state_manager.load_latest_state(novel_id)
            if state:
                user_content += f"\n\n当前状态：{state.model_dump_json(indent=2)}"
        
        if use_world_bible:
            world_bible = self.state_manager.load_world_bible(novel_id)
            if world_bible:
                user_content += f"\n\n世界设定：{json.dumps(world_bible, ensure_ascii=False, indent=2)}"
        
        user_message = {"role": "user", "content": user_content}
        messages.append(user_message)
        
        # 保存用户消息到记忆
        if use_memory:
            self.memory_manager.save_message(session_id, user_message)
        
        # 调用LLM
        response = LLMCaller.call(messages, model_name)
        
        # 保存AI回复到记忆
        if use_memory:
            ai_message = {"role": "assistant", "content": response}
            self.memory_manager.save_message(session_id, ai_message)
            
            # 如果启用压缩，自动压缩最新的分片
            if use_compression:
                try:
                    # 获取当前会话的统计信息
                    stats = self.memory_manager.get_session_stats(session_id)
                    total_chunks = stats.get("total_chunks", 0)
                    
                    # 压缩最新的分片（如果存在且未压缩）
                    if total_chunks > 0:
                        index_data = self.memory_manager.index_manager.load_session_index(session_id)
                        compressed_chunks = len(index_data.get("summaries", {}))
                        
                        # 如果有未压缩的分片，压缩最新的一个
                        if total_chunks > compressed_chunks:
                            latest_chunk = total_chunks
                            success = self.memory_manager.compress_chunk(
                                session_id=session_id,
                                chunk_index=latest_chunk,
                                model_name=compression_model
                            )
                            if success:
                                print(f"自动压缩分片 {latest_chunk} 成功")
                            else:
                                print(f"自动压缩分片 {latest_chunk} 失败")
                except Exception as e:
                    print(f"自动压缩失败: {e}")
        
        # 保存章节内容 - 尝试从细纲中提取章节索引
        chapter_index = self._extract_chapter_index(chapter_outline)
        if chapter_index is not None:
            self._save_chapter(response, chapter_index, novel_id)
        
        # 状态更新 - 如果启用状态更新且使用了状态
        if update_state and use_state:
            current_state = self.state_manager.load_latest_state(novel_id)
            if current_state:
                print(f"正在更新状态...")
                try:
                    # 读取状态更新规则
                    update_rules_file = os.path.join("./prompts", "update_state_rules.txt")
                    update_system_prompt = ""
                    if os.path.exists(update_rules_file):
                        with open(update_rules_file, 'r', encoding='utf-8') as f:
                            update_system_prompt = f.read().strip()
                    
                    # 调用状态更新
                    new_state = self.update_state(
                        chapter_content=response,
                        current_state=current_state,
                        model_name=model_name,
                        novel_id=novel_id,
                        system_prompt=update_system_prompt
                    )
                    print(f"状态更新完成，新状态已保存")
                except Exception as e:
                    print(f"状态更新失败: {e}")
        
        return response

    def update_state(
        self,
        chapter_content: str,
        current_state: ChapterState,
        model_name: str = "deepseek_chat",
        novel_id: Optional[str] = None,
        system_prompt: str = """
你是一个精确的数据分析助手。你的任务是比较一个旧的JSON状态和一段新的小说章节内容，然后生成一个更新后的JSON对象。
**规则:**
1.  **以旧JSON为基础**: 完全基于我提供的旧JSON状态进行修改。
2.  **从新章节提取变化**: 阅读新的小说章节，找出所有导致状态变化的事件，例如：主角等级、属性提升；获得或失去了新物品；学会了新技能或功法；人际关系发生变化；解锁了新的任务或目标。
3.  **更新数值与描述**: 精确地更新JSON文件中的数值和描述文字。例如，"level"字段要根据小说内容合理提升。
4.  **添加新条目**: 如果有新物品或新人物关系，就在对应的数组中添加新的对象。
5.  **更新剧情总结**: 修改 `current_plot_summary` 字段，简要概括本章发生的核心事件。
6.  **严格遵守格式**: 你的输出必须严格遵循下面提供的JSON格式，不包含任何解释性文字或代码块标记。
"""
    ) -> ChapterState:
        messages = []

        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})

        user_content = f"""
---
### **旧的状态JSON**：{current_state.model_dump_json(indent=2)}
---

### **本章小说内容**：{chapter_content}

---
请根据以上信息，生成更新后的JSON对象：
"""
        messages.append({"role": "user", "content": user_content})
        
        response = LLMCaller.call(messages, model_name)
        
        try:
            # 提取JSON
            import re
            json_match = re.search(r'\{.*\}', response, re.DOTALL)
            if json_match:
                state_data = json.loads(json_match.group())
                new_state = ChapterState(**state_data)
                self.state_manager.save_state(new_state, novel_id)
                return new_state
        except Exception as e:
            print(f"状态更新失败: {e}")
        
        return current_state

    def chat(
        self,
        user_input: str,
        model_name: str = "deepseek_chat",
        system_prompt: str = "",
        session_id: str = "default",
        use_memory: bool = True,
        recent_count: int = 20,
        use_compression: bool = False,
        compression_model: str = "deepseek_chat",
        save_conversation: bool = True
    ) -> str:
        messages = []
        
        # 添加系统提示
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        
        # 加载历史记录
        if use_memory and recent_count > 0:
            history_messages = self.memory_manager.load_recent_messages(
                session_id=session_id,
                count=recent_count,
                use_compression=use_compression,
                compression_model=compression_model
            )
            messages.extend(history_messages)
        
        # 添加当前用户输入
        user_message = {"role": "user", "content": user_input}
        messages.append(user_message)
        
        # 保存用户消息
        if save_conversation:
            self.memory_manager.save_message(session_id, user_message)
        
        # 调用LLM
        response = LLMCaller.call(messages, model_name)
        
        # 保存AI回复
        if save_conversation:
            ai_message = {"role": "assistant", "content": response}
            self.memory_manager.save_message(session_id, ai_message)
        
        return response


    
    def load_memory_by_range(
        self,
        session_id: str,
        start_msg: int = 1,
        end_msg: Optional[int] = None,
        use_compression: bool = False,
        compression_model: str = "deepseek_chat"
    ) -> List[Dict[str, Any]]:
        """按范围加载记忆"""
        return self.memory_manager.load_messages_by_range(
            session_id=session_id,
            start_msg=start_msg,
            end_msg=end_msg,
            use_compression=use_compression,
            compression_model=compression_model
        )
    
    def compress_memory_chunk(
        self,
        session_id: str,
        chunk_index: int,
        model_name: str = "deepseek_chat",
        compression_prompt: str = ""
    ) -> bool:
        """压缩指定的记忆分片"""
        return self.memory_manager.compress_chunk(
            session_id=session_id,
            chunk_index=chunk_index,
            model_name=model_name,
            compression_prompt=compression_prompt
        )
    
    def batch_compress_memory(
        self,
        session_id: str,
        chunk_indices: List[int],
        model_name: str = "deepseek_chat",
        compression_prompt: str = ""
    ) -> Dict[int, bool]:
        """批量压缩记忆分片"""
        return self.memory_manager.batch_compress_chunks(
            session_id=session_id,
            chunk_indices=chunk_indices,
            model_name=model_name,
            compression_prompt=compression_prompt
        )
    
    def get_memory_stats(self, session_id: str) -> Dict[str, Any]:
        """获取记忆统计信息"""
        return self.memory_manager.get_session_stats(session_id)

    def _extract_chapter_index(self, chapter_outline: str) -> Optional[int]:
        """从章节细纲中提取章节索引"""
        import re
        
        # 尝试匹配各种章节索引格式
        patterns = [
            r'第(\d+)章',  # 第1章、第10章
            r'chapter[_\s]*(\d+)',  # chapter_1, chapter 1
            r'章节[_\s]*(\d+)',  # 章节_1, 章节 1
            r'【第(\d+)章',  # 【第1章
        ]
        
        for pattern in patterns:
            match = re.search(pattern, chapter_outline, re.IGNORECASE)
            if match:
                try:
                    return int(match.group(1))
                except ValueError:
                    continue
        
        # 如果没有找到，返回None
        return None

    def generate_multiple_versions(
        self,
        chapter_outline: str,
        num_versions: int = 3,
        model_name: str = "deepseek_chat",
        system_prompt: str = "",
        novel_id: Optional[str] = None
    ) -> List[str]:
        """生成多个版本的章节"""
        versions = []
        
        for i in range(num_versions):
            print(f"正在生成第 {i+1} 个版本...")
            version = self.generate_chapter(
                chapter_outline=chapter_outline,
                model_name=model_name,
                system_prompt=system_prompt,
                use_memory=False,  # 多版本生成时不使用记忆
                novel_id=novel_id
            )
            versions.append(version)
        
        # 保存所有版本
        chapter_index = self._extract_chapter_index(chapter_outline)
        if chapter_index is not None:
            self._save_versions(versions, chapter_index, novel_id)
        
        return versions

    def _save_chapter(self, content: str, chapter_index: int, novel_id: Optional[str] = None):
        os.makedirs("./xiaoshuo", exist_ok=True)
        if novel_id:
            file_path = f"./xiaoshuo/{novel_id}_chapter_{chapter_index:03d}.txt"
        else:
            # 兼容旧格式
            file_path = f"./xiaoshuo/chapter_{chapter_index:03d}.txt"
        
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)

    def _save_versions(self, versions: List[str], chapter_index: int, novel_id: Optional[str] = None):
        os.makedirs("./versions", exist_ok=True)
        if novel_id:
            file_path = f"./versions/{novel_id}_chapter_{chapter_index}_versions.json"
        else:
            # 兼容旧格式
            file_path = f"./versions/chapter_{chapter_index}_versions.json"
        
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump({
                "novel_id": novel_id,
                "chapter_index": chapter_index,
                "versions": versions,
                "created_at": time.time()
            }, f, indent=2, ensure_ascii=False)
