import numpy as np
from table_rl import step_size_scheduler


class ConstantStepSize(step_size_scheduler.StepSizeScheduler):
    """Step-size scheduler that uses a constant step-size

    Args:
      step_size: float step_size
    """

    def __init__(self, step_size):
        self.constant_step_size = step_size

    def step_size(self, obs, action=None):
        return self.constant_step_size

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