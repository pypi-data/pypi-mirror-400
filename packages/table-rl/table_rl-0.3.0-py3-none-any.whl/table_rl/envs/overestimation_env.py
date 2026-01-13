import gymnasium
import numpy as np
import table_rl


class OverestimationGridworld(gymnasium.Env):
    '''
        Implements the Gridworld MDP from Figure 2 of Hado van Hasselt's 2010 NIPS paper: Double Q-learning
    '''
    def __init__(self):
        self.observation_space = gymnasium.spaces.Discrete(10) # 9 states plus a terminal state
        self.action_space = gymnasium.spaces.Discrete(4)
        self.construct_transition()

        self.init_state_distribution = np.zeros(10)
        self.init_state_distribution[0] = 1.0
        self.terminal_state = 9
        self.goal_state = 8

        
    def construct_transition(self):
        T = np.zeros((self.observation_space.n, self.action_space.n, self.observation_space.n))
        UP = 0
        DOWN = 1
        LEFT = 2
        RIGHT = 3
        for state in range(3): # bottom row
            T[state, UP, state+3] = 1.0
            T[state, DOWN, state] = 1.0
        for state in range(3,6): # second row
            T[state, UP, state+3] = 1.0
            T[state, DOWN, state-3] = 1.0
        for state in range(6,8): # top row (excluding goal)
            T[state, UP, state] = 1.0
            T[state, DOWN, state-3] = 1.0
        for state in range(0,9,3): # left column
            T[state, LEFT, state] = 1.0
            T[state, RIGHT, state+1] = 1.0
        for state in range(1,9,3): # middle column
            T[state, LEFT, state-1] = 1.0
            T[state, RIGHT, state+1] = 1.0
        for state in range(2,7,3): # right column (excluding goal)
            T[state, LEFT, state-1] = 1.0
            T[state, RIGHT, state] = 1.0
        T[8,:,9] = 1.0 # goal always transitions to terminal
        T[9,:,9] = 1.0
        table_rl.dp.dp.check_valid_transition(T)
        self.T = T


    def step(self, action):
        next_state = np.random.choice(self.observation_space.n, p=self.T[self.current_state,action])
        if self.current_state == self.goal_state:
            reward = 5.0
            assert next_state == self.terminal_state
        else:
            reward = np.random.choice([-12., 10.])
        self.current_state = next_state
        terminated = next_state == self.terminal_state
        return next_state, reward, terminated, False, {}


    def reset(self):
        obs = np.random.choice(self.observation_space.n, p=self.init_state_distribution)
        info = {}
        self.current_state = obs
        return obs, info
