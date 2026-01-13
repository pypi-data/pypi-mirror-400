import gymnasium
import numpy as np


class ControlGridworldEnv(gymnasium.Env):
    '''
        Implements a rectangular gridworld with a goal in the upper right hand corner.
        
        The agent starts in the bottom right hand corner and can move in four directions (up, down, left, right).
        The episode ends when the agent reaches the goal state at the top left hand corner.
        Each step incurs a reward of -1, and reaching the goal yields a reward of 1.
    '''
    def __init__(self, width=4, height=4, truncation_limit=None):
        assert width > 1 and height > 1, "Width and height must be at least 2."
        self.width = width # columns
        self.height = height # rows
        self.num_states = self.width * self.height # goal state is terminal
        self.truncation_limit = truncation_limit
        self.episode_steps = 0
        self.construct_transition()
        self.construct_reward()
        
    def construct_transition(self):
        self.T = np.zeros((self.num_states, 4, self.num_states))
        
        # Handle up
        for state in range(0, self.num_states - 1):
            next_state = state if state + self.width >= self.num_states else state + self.width
            self.T[state, 0, next_state] = 1.0

        # Handle down
        for state in range(0, self.num_states - 1):
            next_state = state if state - self.width < 0 else state - self.width
            self.T[state, 1, next_state] = 1.0

        # Handle left
        for state in range(0, self.num_states - 1):
            next_state = state if state % self.width == 0 else state - 1
            self.T[state, 2, next_state] = 1.0

        # Handle right
        for state in range(0, self.num_states - 1):
            next_state = state if state % self.width == self.width - 1 else state + 1
            self.T[state, 3, next_state] = 1.0

        # Assuming UDLR
        self.T[self.num_states - 1, :, self.num_states - 1] = 1.0 # terminal goal state
        for state in range(self.num_states):
            for action in range(4):
                assert np.sum(self.T[state, action]) == 1

    def construct_reward(self):
        self.R = np.full((self.num_states, 4, self.num_states), -1.0)
        self.R[:, :, self.num_states - 1] = 5.0 # reward for reaching goal state
        self.R[self.num_states - 1,:,:] = 0. # Transitions from goal state give nothing

    def step(self, action):
        next_state = np.random.choice(self.num_states, p=self.T[self.current_state, action])
        reward = self.R[self.current_state, action, next_state]
        self.current_state = next_state
        terminated = next_state == self.num_states - 1
        truncation = self.truncation_limit is not None and self.episode_steps >= self.truncation_limit
        self.episode_steps += 1
        return next_state, reward, terminated, truncation, {}

    def reset(self):
        obs = 0
        self.episode_steps = 0
        info = {}
        self.current_state = obs
        return obs, info
