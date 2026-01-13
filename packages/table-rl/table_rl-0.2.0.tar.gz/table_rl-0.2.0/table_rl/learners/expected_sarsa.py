from table_rl import learner
import numpy as np

class ExpectedSarsa(learner.Learner):
    """Class that implements Expected Sarsa."""

    def __init__(self,
                 num_states,
                 num_actions,
                 step_size_schedule,
                 explorer,
                 discount=0.99,
                 initial_val=0.):
        self.explorer = explorer
        self.step_size_schedule = step_size_schedule
        self.q = np.full((num_states, num_actions), initial_val, dtype=float)
        self.discount = discount

    def update_q(self, obs, action, reward, terminated, next_obs):
        next_action_probs = self.explorer.compute_action_probabilities(next_obs, self.q[next_obs])
        expected_next_q = np.sum(next_action_probs * self.q[next_obs])
        target = reward if terminated else reward + self.discount * expected_next_q
        estimate = self.q[obs, action]
        step_size = self.step_size_schedule.step_size(obs, action)
        self.q[obs, action] = estimate + step_size * (target - estimate)
    
    def act(self, obs: int, train: bool) -> int:
        """Returns an integer 
        """
        self.current_obs = obs
        q_values = self.q[obs]
        action = self.explorer.select_action(obs, q_values) if train else np.argmax(q_values)
        self.last_action = action
        return action
        
    def observe(self, obs: int, reward: float, terminated: bool, truncated: bool, training_mode: bool) -> None:
        """Observe consequences of the last action and update estimates accordingly.

        Returns:
            None
        """
        self.update_q(self.current_obs, self.last_action, reward, terminated, obs)
        self.explorer.observe(obs, reward, terminated, truncated, training_mode)
        self.step_size_schedule.observe(obs, reward, terminated, truncated, training_mode)
        if terminated or truncated:
            self.current_obs = None
            self.last_action = None

