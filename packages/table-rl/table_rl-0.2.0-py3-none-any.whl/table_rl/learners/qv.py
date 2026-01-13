from table_rl import learner
import numpy as np

class QVLearning(learner.Learner):
    """Class that implements QV-Learning."""

    def __init__(self,
                 num_states,
                 num_actions,
                 step_size_q_schedule,
                 step_size_v_schedule,
                 explorer,
                 discount=0.99,
                 initial_val=0.):
        self.explorer = explorer
        self.step_size_q_schedule = step_size_q_schedule
        self.step_size_v_schedule = step_size_v_schedule
        self.q = np.full((num_states, num_actions), initial_val, dtype=float)
        self.v = np.full((num_states), initial_val, dtype=float)
        self.discount = discount

    def _compute_target(self, reward, next_obs, terminated):
        target = reward if terminated else reward + self.discount * self.v[next_obs]
        return target

    def _update_q(self, obs, action, target, step_size):
        q_estimate = self.q[obs, action]
        self.q[obs, action] = q_estimate + step_size * (target - q_estimate)

    def _update_v(self, obs, target, step_size):
        v_estimate = self.v[obs]
        self.v[obs] = v_estimate + step_size * (target - v_estimate)

    def update(self, obs, action, reward, terminated, next_obs):
        step_size_q = self.step_size_q_schedule.step_size(obs, action)
        step_size_v = self.step_size_v_schedule.step_size(obs, 0)
        target = self._compute_target(reward, next_obs, terminated)
        self._update_q(obs, action, target, step_size_q)
        self._update_v(obs, target, step_size_v)
    
    def act(self, obs: int, train: bool) -> int:
        """Returns an integer 
        """
        self.current_obs = obs
        q_values = self.q[obs]
        action = self.explorer.select_action(obs, q_values) if train else np.argmax(q_values)
        self.action = action
        return action
        
    def observe(self, obs: int, reward: float, terminated: bool, truncated: bool, training_mode: bool) -> None:
        """Observe consequences of the last action and update estimates accordingly.

        Returns:
            None
        """
        self.update(self.current_obs, self.action, reward, terminated, obs)
        self.explorer.observe(obs, reward, terminated, truncated, training_mode)
        self.step_size_q_schedule.observe(obs, reward, terminated, truncated, training_mode)
        self.step_size_v_schedule.observe(obs, reward, terminated, truncated, training_mode)
        if terminated or truncated:
            self.current_obs = None
            self.action = None

