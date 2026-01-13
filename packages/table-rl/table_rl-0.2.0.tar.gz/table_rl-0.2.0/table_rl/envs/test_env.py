import gymnasium
import numpy as np

class BasicEnv(gymnasium.Env):

    def __init__(self, discount):

        self.observation_space = gymnasium.spaces.Discrete(3)
        self.action_space = gymnasium.spaces.Discrete(2)

        self.num_states = 3
        self.num_actions = 2
        self.T = np.zeros((self.num_states, self.num_actions, self.num_states), dtype=float)
        self.R = np.zeros((self.num_states, self.num_actions, self.num_states), dtype=float)
        left = 0
        right = 1
        self.T[0, right, 0] = 0.1
        self.T[0, right, 1] = 0.9
        self.T[0, left, 0] = 0.9
        self.T[0, left, 1] = 0.1

        self.T[1, right, 0] = 0.1
        self.T[1, right, 2] = 0.9
        self.T[1, left, 0] = 0.9
        self.T[1, left, 2] = 0.1

        self.T[2,:,2] = 1.0

        self.R[:,:,2] = 1.0
        self.R[2,:,2] = 0.0

        self.discount = discount

    def reset(self):
        self.current_state = 0
        return 0, {}

    def step(self, action):
        next_state = np.random.choice(3, p=self.T[self.current_state, action])
        reward = self.R[self.current_state, action, next_state]
        terminated = next_state == 2
        self.current_state = next_state
        return next_state, reward, terminated, False, {}
