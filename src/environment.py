import random
from typing import Tuple, Dict, Any

class GridWorldEnvironment:
    """
    A 2D navigation grid world where an agent learns to reach a goal
    while avoiding hazards, maximizing cumulative reward.
    """
    ACTIONS = {
        0: (-1, 0),  # Up
        1: (1, 0),   # Down
        2: (0, -1),  # Left
        3: (0, 1),   # Right
    }
    ACTION_NAMES = ["UP", "DOWN", "LEFT", "RIGHT"]

    def __init__(self, size: int = 6, num_hazards: int = 4):
        self.size = size
        self.num_hazards = num_hazards
        self.goal = (size - 1, size - 1)
        self.start = (0, 0)
        self.agent_pos = self.start
        self.step_count = 0
        self.max_steps = size * size * 2
        self.hazards = set()
        self._generate_hazards()

    def _generate_hazards(self):
        self.hazards.clear()
        possible_positions = [
            (r, c)
            for r in range(self.size)
            for c in range(self.size)
            if (r, c) != self.start and (r, c) != self.goal
        ]
        chosen = random.sample(possible_positions, min(self.num_hazards, len(possible_positions)))
        self.hazards = set(chosen)

    def reset(self) -> int:
        """Reset environment to starting state and return state index."""
        self.agent_pos = self.start
        self.step_count = 0
        return self._pos_to_state(self.agent_pos)

    def _pos_to_state(self, pos: Tuple[int, int]) -> int:
        return pos[0] * self.size + pos[1]

    def _state_to_pos(self, state: int) -> Tuple[int, int]:
        return divmod(state, self.size)

    @property
    def num_states(self) -> int:
        return self.size * self.size

    @property
    def num_actions(self) -> int:
        return len(self.ACTIONS)

    def step(self, action: int) -> Tuple[int, float, bool, Dict[str, Any]]:
        """
        Execute an action and return (next_state, reward, done, info).
        """
        self.step_count += 1
        dr, dc = self.ACTIONS[action]
        nr = max(0, min(self.size - 1, self.agent_pos[0] + dr))
        nc = max(0, min(self.size - 1, self.agent_pos[1] + dc))
        new_pos = (nr, nc)

        reward = -0.05  # Step penalty encourages shorter paths
        done = False
        info = {"reached_goal": False, "hit_hazard": False}

        if new_pos == self.goal:
            reward = 10.0
            done = True
            info["reached_goal"] = True
        elif new_pos in self.hazards:
            reward = -5.0
            done = True
            info["hit_hazard"] = True
        elif self.step_count >= self.max_steps:
            done = True
            reward = -1.0

        self.agent_pos = new_pos
        return self._pos_to_state(new_pos), reward, done, info

    def render(self):
        """ASCII visualization of the current grid state."""
        grid_repr = []
        for r in range(self.size):
            row = []
            for c in range(self.size):
                pos = (r, c)
                if pos == self.agent_pos:
                    row.append("A")
                elif pos == self.goal:
                    row.append("G")
                elif pos in self.hazards:
                    row.append("X")
                else:
                    row.append(".")
            grid_repr.append(" ".join(row))
        return "\n".join(grid_repr)
