#!/usr/bin/env python3
"""
Self-Learning AI Agent
Main demonstration entry point.
"""

from src.environment import GridWorldEnvironment
from src.agent import SelfLearningAgent
from src.trainer import Trainer

def main():
    print("=" * 60)
    print("        SELF-LEARNING AI AGENT (REINFORCEMENT LEARNING)        ")
    print("=" * 60)

    # 1. Initialize environment (6x6 grid with 4 hazard zones)
    env = GridWorldEnvironment(size=6, num_hazards=4)
    print("\nInitial Environment Layout:")
    print("Legend: [A] Start/Agent  [G] Goal  [X] Hazard  [.] Open Tile")
    print("-" * 20)
    print(env.render())
    print("-" * 20)

    # 2. Instantiate self-learning agent
    agent = SelfLearningAgent(
        num_states=env.num_states,
        num_actions=env.num_actions,
        learning_rate=0.1,
        discount_factor=0.95,
        epsilon_start=1.0,
        epsilon_min=0.05,
        epsilon_decay=0.992,
        replay_capacity=2000,
    )

    # 3. Train agent across episodes
    trainer = Trainer(agent=agent, env=env)
    trainer.train(episodes=350, replay_batch_size=32)

    # 4. Evaluate optimal greedy policy
    trainer.evaluate(num_trials=5)

    print("\n[✓] Self-learning cycle complete!")

if __name__ == "__main__":
    main()
