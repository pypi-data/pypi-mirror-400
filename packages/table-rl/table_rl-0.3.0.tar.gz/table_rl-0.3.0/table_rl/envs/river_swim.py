import gymnasium
import numpy as np
import table_rl

class RiverSwimEnv(gymnasium.Env):
    '''
        Implements the RiverSwim MDP from Strehl and Littman's 2008 paper:
        ``An analysis of model-based Interval Estimation for Markov Decision Processes''
    '''
    def __init__(self):
        self.observation_space = gymnasium.spaces.Discrete(6)
        self.action_space = gymnasium.spaces.Discrete(2)

        self.construct_transition()
        self.construct_reward()
        self.init_state_distribution = np.array([0, 0.5, 0.5, 0, 0, 0])

        
    def construct_transition(self):
        T = np.zeros((self.observation_space.n, self.action_space.n, self.observation_space.n))
        for state in range(5):
            T[state, 1, state+1] = 0.3
        for state in range(1,6):
            T[state, 0, state - 1] = 1.0
        for state in range(1,5):
            T[state, 1, state-1] = 0.1
            T[state, 1, state] = 0.6
        T[5, 1, 4] = 0.7
        for state in range(1,5):
            T[state, 1, state]
        T[0, 0, 0] = 1.0
        T[0, 1, 0] = 0.7
        T[5, 1, 5] = 0.3
        table_rl.dp.dp.check_valid_transition(T)
        self.T = T


    def construct_reward(self):
        R = np.zeros((self.observation_space.n, self.action_space.n, self.observation_space.n))
        R[0, 0, 0] = 5
        R[5, 1, 5] = 10000
        self.R = R

    def step(self, action):
        next_state = np.random.choice(15, p=self.T[self.current_state,action])
        reward = self.R[self.current_state, action, next_state]
        self.current_state = next_state
        terminated = next_state == 0
        return next_state, reward, terminated, False, {}

    def reset(self):
        obs = np.random.randint(1, 15)
        info = {}
        self.current_state = obs
        return obs, info
