from abc import ABCMeta, abstractmethod


class StepSizeScheduler(object, metaclass=ABCMeta):
    """Abstract explorer."""

    @abstractmethod
    def step_size(self, obs, action=None) -> float:
        """Select a step-size.

        Args:
          obs: observation
          action: action
        """
        raise NotImplementedError()

    def observe(self, obs, reward, terminated, truncated, training_mode):
        """Select an action.

        Args:
          obs: next state/observation
          reward: reward received
          terminated: bool indicating environment termination
          truncated: bool indicating episode truncation
          training_mode: bool indicating whether the agent is training
        """
        raise NotImplementedError()
