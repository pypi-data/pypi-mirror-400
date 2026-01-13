import numpy as np
from table_rl import explorer


class PolicyExecutor(explorer.Explorer):
    """Executes a specific policy

    Args:
      policy: 2D numpy array where policy[state,action] is the pi(a|s)
    """

    def __init__(self, policy):
        self.policy = policy

    def select_action(self, obs, action_values) -> int:
        action = np.random.choice(self.policy.shape[1], p=self.compute_action_probabilities(obs, action_values))
        return action

    def compute_action_probabilities(self, obs, action_values=None):
        """Compute action probabilities.

        Args:
          obs: observation
          action_values: np.ndarray of action-values

        Returns:
          action_probs: a np.ndarray of action probabilities
        """
        action_probs = self.policy[obs]
        return action_probs


    def observe(self, obs, reward, terminated, truncated, training_mode):
        """Select an action.

        Args:
          obs: next state/observation
          reward: reward received
          terminated: bool indicating environment termination
          truncated: bool indicating epsisode truncation
          training_mode: bool indicating whether the agent is training
        """
        pass
