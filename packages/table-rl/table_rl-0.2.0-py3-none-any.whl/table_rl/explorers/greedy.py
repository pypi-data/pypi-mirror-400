import numpy as np
from table_rl import explorer
from .epsilon_greedy import epsilon_greedy_action_probs

class GreedyExplorer(explorer.Explorer):
    """Explorer that takes the greedy action always.

    Args:
      num_actions: number of actions
    """

    def __init__(self, num_actions):
        self.num_actions = num_actions

    def select_action(self, obs, action_values) -> int:
        action_probs = self.compute_action_probabilities(obs, action_values)
        action = np.random.choice(len(action_probs), p=action_probs)
        return action

    def compute_action_probabilities(self, obs, action_values=None):
        """Compute action probabilities.

        Args:
          obs: observation
          action_values: np.ndarray of action-values

        Returns:
          action_probs: a np.ndarray of action probabilities
        """
        action_probs = epsilon_greedy_action_probs(action_values, 0.0)
        return action_probs

    def observe(self, obs, reward, terminated, truncated, training_mode):
        """Select an action.

        Args:
          obs: next state/observation
          reward: reward received
          terminated: bool indicating environment termination
          truncated: bool indicating episode truncation
          training_mode: bool indicating whether the agent is training
        """
        pass