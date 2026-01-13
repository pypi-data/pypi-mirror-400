from .expected_sarsa import ExpectedSarsa
import numpy as np

class QLearning(ExpectedSarsa):
    """Class that implements Q-Learning."""

    def update_q(self, obs, action, reward, terminated, next_obs):
        target = reward if terminated else reward + self.discount * np.max(self.q[next_obs])
        estimate = self.q[obs, action]
        step_size = self.step_size_schedule.step_size(obs, action)
        self.q[obs, action] = estimate + step_size * (target - estimate)
