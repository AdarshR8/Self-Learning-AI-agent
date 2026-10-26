import os
from typing import Dict, List, Any
from src.agent import SelfLearningAgent
from src.environment import GridWorldEnvironment

class Trainer:
    """
    Coordinates training episodes, evaluation metrics, and learning curves.
    """

    def __init__(self, agent: SelfLearningAgent, env: GridWorldEnvironment):
        self.agent = agent
        self.env = env
        self.history: Dict[str, List[Any]] = {
            "episode_rewards": [],
            "success_rates": [],
            "steps_per_episode": [],
            "epsilon": [],
        }

    def train(
        self,
        episodes: int = 400,
        replay_batch_size: int = 32,
        checkpoint_dir: str = "checkpoints",
    ) -> Dict[str, List[Any]]:
        """Run the reinforcement self-learning loop."""
        os.makedirs(checkpoint_dir, exist_ok=True)
        recent_successes = []

        print(f"[*] Starting self-learning training for {episodes} episodes...")
        for ep in range(1, episodes + 1):
            state = self.env.reset()
            total_reward = 0.0
            steps = 0
            done = False
            reached_goal = False

            while not done:
                action = self.agent.select_action(state, training=True)
                next_state, reward, done, info = self.env.step(action)

                # Store and learn
                self.agent.record_experience(state, action, reward, next_state, done)
                self.agent.learn_step(state, action, reward, next_state, done)
                self.agent.replay_learn(batch_size=replay_batch_size)

                total_reward += reward
                steps += 1
                state = next_state
                if info.get("reached_goal"):
                    reached_goal = True

            self.agent.decay_exploration()

            # Track metrics
            recent_successes.append(1 if reached_goal else 0)
            if len(recent_successes) > 50:
                recent_successes.pop(0)

            success_rate = (sum(recent_successes) / len(recent_successes)) * 100
            self.history["episode_rewards"].append(total_reward)
            self.history["steps_per_episode"].append(steps)
            self.history["success_rates"].append(success_rate)
            self.history["epsilon"].append(self.agent.epsilon)

            if ep % 50 == 0 or ep == episodes:
                avg_reward = sum(self.history["episode_rewards"][-50:]) / len(
                    self.history["episode_rewards"][-50:]
                )
                print(
                    f"Episode {ep:4d}/{episodes} | "
                    f"Avg Reward (last 50): {avg_reward:6.2f} | "
                    f"Success Rate: {success_rate:5.1f}% | "
                    f"Epsilon: {self.agent.epsilon:.3f}"
                )

        # Save final checkpoint
        final_model_path = os.path.join(checkpoint_dir, "agent_model.json")
        self.agent.save_model(final_model_path)
        print(f"[✓] Model checkpoint saved to: {final_model_path}")
        return self.history

    def evaluate(self, num_trials: int = 5) -> None:
        """Evaluate the learned policy greedily without random exploration."""
        print("\n--- Evaluating Learned Agent Policy ---")
        success_count = 0
        for trial in range(1, num_trials + 1):
            state = self.env.reset()
            done = False
            steps = 0
            path = [self.env._state_to_pos(state)]

            while not done:
                action = self.agent.select_action(state, training=False)
                state, reward, done, info = self.env.step(action)
                path.append(self.env._state_to_pos(state))
                steps += 1

            result = "SUCCESS (Goal Reached)" if info.get("reached_goal") else "FAILED"
            if info.get("reached_goal"):
                success_count += 1
            print(f"Trial {trial}: {result} in {steps} steps. Path: {path}")

        print(f"Evaluation Score: {success_count}/{num_trials} successes.")
