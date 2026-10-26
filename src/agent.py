import json
import random
from collections import deque
from typing import Dict, List, Tuple

class SelfLearningAgent:
    """
    A reinforcement learning agent that self-learns optimal behavior
    through exploration, temporal-difference updates, and experience memory.
    """

    def __init__(
        self,
        num_states: int,
        num_actions: int,
        learning_rate: float = 0.1,
        discount_factor: float = 0.95,
        epsilon_start: float = 1.0,
        epsilon_min: float = 0.05,
        epsilon_decay: float = 0.995,
        replay_capacity: int = 1000,
    ):
        self.num_states = num_states
        self.num_actions = num_actions
        self.lr = learning_rate
        self.gamma = discount_factor
        self.epsilon = epsilon_start
        self.epsilon_min = epsilon_min
        self.epsilon_decay = epsilon_decay

        # Q-table: state -> [action_values]
        self.q_table: Dict[int, List[float]] = {
            s: [0.0] * num_actions for s in range(num_states)
        }

        # Experience Replay Memory: buffer of (s, a, r, s', done)
        self.memory = deque(maxlen=replay_capacity)

    def select_action(self, state: int, training: bool = True) -> int:
        """Epsilon-greedy action selection."""
        if training and random.random() < self.epsilon:
            return random.randint(0, self.num_actions - 1)

        q_values = self.q_table.get(state, [0.0] * self.num_actions)
        max_q = max(q_values)
        best_actions = [a for a, q in enumerate(q_values) if q == max_q]
        return random.choice(best_actions)

    def record_experience(
        self, state: int, action: int, reward: float, next_state: int, done: bool
    ):
        """Store interaction into memory for offline replay learning."""
        self.memory.append((state, action, reward, next_state, done))

    def learn_step(
        self, state: int, action: int, reward: float, next_state: int, done: bool
    ):
        """Online Bellman equation update."""
        current_q = self.q_table[state][action]
        if done:
            target_q = reward
        else:
            best_future_q = max(self.q_table[next_state])
            target_q = reward + self.gamma * best_future_q

        # TD update
        self.q_table[state][action] += self.lr * (target_q - current_q)

    def replay_learn(self, batch_size: int = 32):
        """Learn from a random sample of past experiences (experience replay)."""
        if len(self.memory) < batch_size:
            return

        batch = random.sample(self.memory, batch_size)
        for s, a, r, ns, d in batch:
            self.learn_step(s, a, r, ns, d)

    def decay_exploration(self):
        """Decay epsilon to transition from exploration to exploitation."""
        self.epsilon = max(self.epsilon_min, self.epsilon * self.epsilon_decay)

    def save_model(self, file_path: str):
        """Save Q-table and agent configuration to JSON."""
        data = {
            "num_states": self.num_states,
            "num_actions": self.num_actions,
            "epsilon": self.epsilon,
            "q_table": self.q_table,
        }
        with open(file_path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2)

    def load_model(self, file_path: str):
        """Load learned Q-table from JSON."""
        with open(file_path, "r", encoding="utf-8") as f:
            data = json.load(f)
        self.epsilon = data.get("epsilon", self.epsilon_min)
        # Convert string keys back to integers
        self.q_table = {int(k): v for k, v in data["q_table"].items()}
