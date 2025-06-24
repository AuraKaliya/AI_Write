# llm_caller.py
from typing import List, Dict, Any, Optional
from .llm_config_manager import LLMConfigManager

class LLMCaller:
    @staticmethod
    def call(
        messages: List[Dict[str, str]],
        model_name: str = "deepseek_chat",
        memory: Optional[Any] = None,
        temperature: Optional[float] = None
    ) -> str:
        config = LLMConfigManager.get_config(model_name)
        
        if temperature is not None:
            config["temperature"] = temperature
            
        # 根据provider创建对应的LLM实例
        if config["provider"] == "openai":
            from langchain_openai import ChatOpenAI
            llm_params = {
                "model": config["model"],
                "api_key": config["api_key"],
                "temperature": config["temperature"]
            }
            if config["base_url"]:
                llm_params["base_url"] = config["base_url"]
            llm = ChatOpenAI(**llm_params)
        elif config["provider"] == "anthropic":
            from langchain_anthropic import ChatAnthropic
            llm = ChatAnthropic(
                model=config["model"],
                api_key=config["api_key"],
                temperature=config["temperature"]
            )
        elif config["provider"] == "google":
            from langchain_google_genai import ChatGoogleGenerativeAI
            llm = ChatGoogleGenerativeAI(
                model=config["model"],
                google_api_key=config["api_key"],
                temperature=config["temperature"]
            )
        else:
            raise ValueError(f"Unsupported provider: {config['provider']}")
        
        # 如果有记忆，使用对话链
        if memory:
            from langchain.chains import ConversationChain
            chain = ConversationChain(llm=llm, memory=memory, verbose=False)
            # 将messages转换为单个输入
            user_input = messages[-1]["content"] if messages else ""
            return chain.predict(input=user_input)
        else:
            # 直接调用LLM
            from langchain_core.messages import HumanMessage, SystemMessage
            lang_messages = []
            for msg in messages:
                if msg["role"] == "system":
                    lang_messages.append(SystemMessage(content=msg["content"]))
                else:
                    lang_messages.append(HumanMessage(content=msg["content"]))
            
            response = llm.invoke(lang_messages)
            return response.content