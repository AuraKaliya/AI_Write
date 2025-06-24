# llm_config_manager.py
import os
from typing import Dict, Any
from dotenv import load_dotenv

load_dotenv()

class LLMConfigManager:
    @staticmethod
    def get_config(model_name: str) -> Dict[str, Any]:
        configs = {
            "deepseek_chat": {
                "provider": "openai",
                "model": "deepseek-chat",
                "api_key": os.getenv("DEEPSEEK_API_KEY"),
                "base_url": "https://api.deepseek.com/v1",
                "temperature": 0.7
            },
            "deepseek_reasoner": {
                "provider": "openai",
                "model": "deepseek-reasoner", 
                "api_key": os.getenv("DEEPSEEK_API_KEY"),
                "base_url": "https://api.deepseek.com/v1",
                "temperature": 0.7
            },
                        "dsf5": {
                "provider": "openai",
                "model": "[稳定]gemini-2.5-pro-preview-06-05-c",
                "api_key": os.getenv("DSF5_API_KEY"),
                "base_url": "https://api.sikong.shop/v1",
                "temperature": 0.7
            },
            "openai_gpt4": {
                "provider": "openai",
                "model": "gpt-4",
                "api_key": os.getenv("OPENAI_API_KEY"),
                "base_url": None,
                "temperature": 0.7
            },
            "openai_gpt35": {
                "provider": "openai", 
                "model": "gpt-3.5-turbo",
                "api_key": os.getenv("OPENAI_API_KEY"),
                "base_url": None,
                "temperature": 0.7
            },
            "anthropic_claude": {
                "provider": "anthropic",
                "model": "claude-3-sonnet-20240229",
                "api_key": os.getenv("ANTHROPIC_API_KEY"),
                "base_url": None,
                "temperature": 0.7
            },
            "google_gemini": {
                "provider": "google",
                "model": "gemini-pro",
                "api_key": os.getenv("GOOGLE_API_KEY"),
                "base_url": None,
                "temperature": 0.7
            }
        }
        return configs.get(model_name, configs["deepseek_chat"])
