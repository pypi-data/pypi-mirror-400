import numpy as np

class SRLearner:
    """SRLearner class."""

    def __init__(self, num_states, learning_rate, discount=0.99):
        self.learning_rate = learning_rate
        self.sr = np.full((num_states, num_states), 0.)
        self.discount = discount

    def update(self, from_state, to_state):
        reward = np.zeros(self.sr.shape[0])
        reward[from_state] = 1.0
        td_error = reward + self.discount * self.sr[to_state] - self.sr[from_state]
        self.sr[from_state] = self.sr[from_state] + self.learning_rate * td_error