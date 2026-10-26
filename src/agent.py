from typing import List, Dict, Optional
from openai import OpenAI
from src.config import Config
from src.memory import MemoryManager

class SelfLearningAIAgent:
    """
    Self-Learning AI Agent based on Dave Ebbelaar's architecture.
    Features:
    - Persistent long-term memory via Mem0
    - Dynamic contextual memory retrieval
    - Automatic learning from user interactions
    """

    def __init__(self, user_id: Optional[str] = None):
        self.user_id = user_id or Config.DEFAULT_USER_ID
        self.memory = MemoryManager(user_id=self.user_id)
        self.client = OpenAI(api_key=Config.OPENAI_API_KEY)
        self.model = Config.MODEL_NAME

        self.system_prompt_template = (
            "You are a helpful, self-learning AI assistant. "
            "You have access to persistent long-term memory about the user. "
            "Use the provided relevant memories to personalize your responses, remember user preferences, "
            "and continuously adapt without asking the user to repeat themselves.\n\n"
            "Relevant memories about the user:\n{memories}\n"
        )

    def chat(self, user_input: str) -> str:
        """
        Main interaction cycle:
        1. Retrieve relevant memories for the current prompt.
        2. Construct memory-augmented system prompt.
        3. Generate response with OpenAI.
        4. Save interaction turn to memory so the agent self-learns.
        """
        # 1. Search for relevant memories
        relevant_memories = self.memory.search(user_input, user_id=self.user_id)
        memories_str = (
            "\n".join(f"- {m}" for m in relevant_memories)
            if relevant_memories
            else "No previous memories found."
        )

        # 2. Build augmented system prompt
        system_prompt = self.system_prompt_template.format(memories=memories_str)

        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_input},
        ]

        # 3. Call LLM
        response = self.client.chat.completions.create(
            model=self.model,
            messages=messages,
            temperature=0.7,
        )
        assistant_reply = response.choices[0].message.content

        # 4. Self-Learning: Store new interaction in Mem0
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
