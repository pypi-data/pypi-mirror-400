import gymnasium
import numpy as np


class BasicGridworld(gymnasium.Env):
	'''
		Implements the gridworld from example 4.1 of the RL book by Sutton and Barto: http://incompleteideas.net/book/RLbook2020.pdf
	'''
	def __init__(self):
		self.construct_transition()
		self.construct_reward()
		
	def construct_transition(self):
		self.T = np.zeros((15, 4, 15))
		
		# Handle up
		for state in range(1,15):
			next_state = state if state - 4 < 0 else state - 4
			self.T[state, 0, next_state] = 1.0

		# Handle down
		for state in range(1,15):
			next_state = state if state + 4 >= 15 else state + 4
			if state == 11:
				next_state = 0
			self.T[state, 1, next_state] = 1.0

		# Handle left
		for state in range(1,15):
			next_state = state if state % 4 == 0 else state - 1
			self.T[state, 2, next_state] = 1.0

		# Handle right
		for state in range(1, 15):
			next_state = state if state % 4 == 3 else state + 1
			if state == 14:
				next_state = 0
			self.T[state, 3, next_state] = 1.0

		# Assuming UDLR
		self.T[0, :, 0] = 1.0 # terminal transitions
		for state in range(15):
			for action in range(4):
				assert np.sum(self.T[state, action]) == 1


	def construct_reward(self):
		self.R = np.full((15, 4, 15), -1.0)
		self.R[0,:,:] = 0

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
