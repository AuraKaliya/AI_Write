# main.py
from src.novel_generator import NovelGenerator
from src.llm_config_manager import LLMConfigManager
from src.llm_caller import LLMCaller
import os, json, time
from src.outline_manager import OutlineManager

def main():
    # 测试架构初始化
    print("=== 小说生成系统 - 高度模块化架构 ===")
    
    # 1. 测试配置管理器
    print("\n1. 测试配置管理器:")
    config = LLMConfigManager.get_config("deepseek_chat")
    print(f"   DeepSeek Chat配置: {config['provider']}, {config['model']}")
    print(f"   Base URL: {config['base_url']}")
    config_default = LLMConfigManager.get_config("")  # 测试默认
    print(f"   默认模型: {config_default['model']}")
    
    # 2. 测试组件初始化
    print("\n2. 测试组件初始化:")
    generator = NovelGenerator(chunk_size=100)
    print("   ✓ NovelGenerator 初始化成功")
    print("   ✓ StateManager 初始化成功")
    print("   ✓ MemoryManager 初始化成功 (分片存储+压缩)")
    
    # 测试不同分片大小
    small_chunk_generator = NovelGenerator(chunk_size=50)
    print("   ✓ NovelGenerator (小分片) 初始化成功")
    
    # 3. 测试会话管理
    print("\n3. 测试会话管理:")
    sessions = generator.memory_manager.list_sessions()
    print(f"   当前会话列表: {sessions}")
    
    # 4. 测试小说生成器传输结构
    print("\n4. 小说生成器传输结构:")
    outline_manager = OutlineManager("data/100_novel_outline_00.json")
    
    message = generator.generate_chapter(chapter_outline=json.dumps(outline_manager.get_chapter_outline("第1章").model_dump(), ensure_ascii=False, indent=2),novel_id=100)
    print(message)
    # 4. 显示使用示例
    # print("\n4. 使用示例:")
    # print("   # 生成章节 (带记忆)")
    # print("   generator.generate_chapter(chapter_plan, use_memory=True, recent_count=20)")
    # print("   # 对话聊天 (带压缩)")
    # print("   generator.chat('继续写作', use_compression=True, recent_count=15)")
    # print("   # 按范围加载记忆")
    # print("   generator.load_memory_by_range('session1', 1, 50, use_compression=True)")
    # print("   # 压缩记忆分片")
    # print("   generator.compress_memory_chunk('session1', 1)")
    # print("   # 批量压缩")
    # print("   generator.batch_compress_memory('session1', [1,2,3])")
    # print("   # 获取统计信息")
    # print("   generator.get_memory_stats('session1')")
    # print("   # 直接调用LLM")
    # print("   LLMCaller.call(messages, model_name='dsf5')")
    
    print("\n=== 架构测试完成 ===")
    print("所有组件已成功初始化，可以开始使用！")
    
    
    
    
    
    

if __name__ == '__main__':
    main()
