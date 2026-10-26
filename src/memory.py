import os
from typing import List, Dict, Any, Optional
from mem0 import Memory
from src.config import Config

class MemoryManager:
    """
    Manages long-term persistent memory for the AI agent using Mem0.
    Enables the agent to self-learn user preferences, facts, and past instructions.
    """

    def __init__(self, user_id: Optional[str] = None):
        self.user_id = user_id or Config.DEFAULT_USER_ID
        
        # Configure Mem0 with OpenAI as LLM & Embedder
        config = {
            "llm": {
                "provider": "openai",
                "config": {
                    "model": Config.MODEL_NAME,
                    "temperature": 0.2,
                }
            },
            "embedder": {
                "provider": "openai",
                "config": {
                    "model": "text-embedding-3-small"
                }
            }
        }
        
        # Initialize Mem0 client
        self.client = Memory.from_config(config)

    def add(self, messages: List[Dict[str, str]], user_id: Optional[str] = None) -> Any:
        """
        Extract and store relevant memories, facts, and preferences from messages.
        """
        uid = user_id or self.user_id
        return self.client.add(messages, user_id=uid)

    def search(self, query: str, user_id: Optional[str] = None, limit: int = 5) -> List[str]:
        """
        Retrieve relevant memories matching the user's latest query or context.
        """
        uid = user_id or self.user_id
        try:
            results = self.client.search(query=query, user_id=uid, limit=limit)
            memories = []
            if isinstance(results, dict) and "results" in results:
                items = results["results"]
            elif isinstance(results, list):
                items = results
            else:
                items = []

            for item in items:
                if isinstance(item, dict) and "memory" in item:
                    memories.append(item["memory"])
                elif isinstance(item, str):
                    memories.append(item)
            return memories
        except Exception as e:
            print(f"[!] Error searching memories: {e}")
            return []

    def get_all(self, user_id: Optional[str] = None) -> List[str]:
        """
        Get all memories currently stored for the specified user.
        """
        uid = user_id or self.user_id
        try:
            results = self.client.get_all(user_id=uid)
            memories = []
            if isinstance(results, dict) and "results" in results:
                items = results["results"]
            elif isinstance(results, list):
                items = results
            else:
                items = []

            for item in items:
                if isinstance(item, dict) and "memory" in item:
                    memories.append(item["memory"])
                elif isinstance(item, str):
                    memories.append(item)
            return memories
        except Exception as e:
            print(f"[!] Error retrieving all memories: {e}")
            return []

    def reset(self, user_id: Optional[str] = None):
        """
        Clear all memories for the user.
        """
        uid = user_id or self.user_id
        try:
            self.client.delete_all(user_id=uid)
            return True
        except Exception as e:
            print(f"[!] Error resetting memories: {e}")
            return False
