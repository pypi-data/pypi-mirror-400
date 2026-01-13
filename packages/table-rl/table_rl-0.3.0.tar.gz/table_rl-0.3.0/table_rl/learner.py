from abc import ABCMeta, abstractmethod


class Learner(object, metaclass=ABCMeta):
    """Abstract learner class."""

    @abstractmethod
    def act(self, obs: int, train: bool) -> int:
        """Returns an integer 
        """
        raise NotImplementedError()

    @abstractmethod
    def observe(self, obs: int, reward: float, terminated: bool, truncated: bool, training_mode: bool) -> None:
        """Observe consequences of the last action.

        Returns:
            None
        """
        raise NotImplementedError()

