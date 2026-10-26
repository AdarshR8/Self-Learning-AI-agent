from typing import List, Dict, Optional
from src.config import Config
from src.memory import MemoryManager

class SelfLearningAIAgent:
    """
    Self-Learning AI Agent based on Dave Ebbelaar's tutorial architecture.
    Supports Google Gemini (free) and OpenAI with persistent Mem0 memory.
    """

    def __init__(self, user_id: Optional[str] = None):
        self.user_id = user_id or Config.DEFAULT_USER_ID
        self.provider = Config.get_active_provider()
        self.model = Config.MODEL_NAME
        self.memory = MemoryManager(user_id=self.user_id)

        if self.provider == "gemini":
            from google import genai
            self.gemini_client = genai.Client(api_key=Config.GEMINI_API_KEY)
        else:
            from openai import OpenAI
            self.openai_client = OpenAI(api_key=Config.OPENAI_API_KEY)

        self.system_prompt_template = (
            "You are a helpful, self-learning AI assistant. "
            "You have access to persistent long-term memory about the user. "
            "Use the provided relevant memories to personalize your responses, remember user preferences, "
            "and continuously adapt without asking the user to repeat themselves.\n\n"
            "Relevant memories about the user:\n{memories}\n"
        )

    def chat(self, user_input: str) -> str:
        """
        1. Retrieve relevant memories.
        2. Formulate memory-infused prompt.
        3. Generate response.
        4. Add interaction to memory for continuous self-learning.
        """
        # 1. Retrieve relevant memories
        relevant_memories = self.memory.search(user_input, user_id=self.user_id)
        memories_str = (
            "\n".join(f"- {m}" for m in relevant_memories)
            if relevant_memories
            else "No previous memories found."
        )

        # 2. Build augmented system prompt
        system_prompt = self.system_prompt_template.format(memories=memories_str)

        # 3. Call LLM
        if self.provider == "gemini":
            response = self.gemini_client.models.generate_content(
                model=self.model,
                contents=f"{system_prompt}\n\nUser: {user_input}",
            )
            assistant_reply = response.text
        else:
            messages = [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_input},
            ]
            response = self.openai_client.chat.completions.create(
                model=self.model,
                messages=messages,
                temperature=0.7,
            )
            assistant_reply = response.choices[0].message.content

        # 4. Store interaction in Mem0 for self-learning
        interaction = [
            {"role": "user", "content": user_input},
            {"role": "assistant", "content": assistant_reply},
        ]
        self.memory.add(interaction, user_id=self.user_id)

        return assistant_reply

    def get_known_memories(self) -> List[str]:
        """Return all memories the agent has learned about the user."""
        return self.memory.get_all(user_id=self.user_id)

    def reset_memory(self) -> bool:
        """Reset all learned memories."""
        return self.memory.reset(user_id=self.user_id)
