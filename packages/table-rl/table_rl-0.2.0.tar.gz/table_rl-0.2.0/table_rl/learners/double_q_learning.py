from table_rl import learner
import numpy as np

def select_a_greedy_action(action_values):
    best_action_indices = np.flatnonzero(action_values == np.max(action_values))
    action = np.random.choice(best_action_indices)
    return action

class DoubleQLearning(learner.Learner):
    """Class that implements Double Q-Learning."""

    def __init__(self,
                 num_states,
                 num_actions,
                 step_size_schedule_a,
                 step_size_schedule_b,
                 explorer,
                 discount=0.99,
                 initial_val=0.):
        self.explorer = explorer
        self.step_size_schedule_a = step_size_schedule_a
        self.step_size_schedule_b = step_size_schedule_b
        self.q1 = np.full((num_states, num_actions), initial_val, dtype=float)
        self.q2 = np.full((num_states, num_actions), initial_val, dtype=float)
        self.discount = discount

    def update_q(self, obs, action, reward, terminated, next_obs):
        update_q1 = np.random.random() < 0.5
        if update_q1:
            step_size = self.step_size_schedule_a.step_size(obs, action)
            target = reward if terminated else reward + self.discount * self.q2[next_obs,select_a_greedy_action(self.q1[next_obs])]
            estimate = self.q1[obs, action]
            self.q1[obs, action] = estimate + step_size * (target - estimate)
        else:
            step_size = self.step_size_schedule_b.step_size(obs, action)
            target = reward if terminated else reward + self.discount * self.q1[next_obs, select_a_greedy_action(self.q2[next_obs])]
            estimate = self.q2[obs, action]
            self.q2[obs, action] = estimate + step_size * (target - estimate)
    
    def act(self, obs: int, train: bool) -> int:
        """Returns an integer 
        """
        self.current_obs = obs
        q_values = (self.q1[obs] + self.q2[obs]) / 2
        action = self.explorer.select_action(obs, q_values) if train else select_a_greedy_action(q_values)
        self.last_action = action
        return action
        
    def observe(self, obs: int, reward: float, terminated: bool, truncated: bool, training_mode: bool) -> None:
        """Observe consequences of the last action and update estimates accordingly.

        Returns:
            None
        """
        self.update_q(self.current_obs, self.last_action, reward, terminated, obs)
        self.explorer.observe(obs, reward, terminated, truncated, training_mode)
        self.step_size_schedule_a.observe(obs, reward, terminated, truncated, training_mode)
        self.step_size_schedule_b.observe(obs, reward, terminated, truncated, training_mode)
        if terminated or truncated:
            self.current_obs = None
            self.last_action = None

