import pytest
import numpy as np
import table_rl
from table_rl.learners import QLearning

class TestQLearning:
    @pytest.fixture(autouse=True)
    def setUp(self):
        self.env = table_rl.envs.BasicEnv(discount=0.9)
        self.num_states = 3
        self.num_actions = 2 # L and R
        self.T = self.env.T
        self.R = self.env.R
        self.discount = 0.9


    def test_q_learning_loop(self):
        explorer = table_rl.explorers.ConstantEpsilonGreedy(0.1, self.T.shape[1])

        agent = QLearning(self.T.shape[0],
                          self.T.shape[1],
                          table_rl.step_size_schedulers.ConstantStepSize(0.02),
                          explorer,
                          discount=self.discount,
                          initial_val=0.)

        observation, info = self.env.reset()

        for _ in range(300000):
            action = agent.act(observation, True)
            observation, reward, terminated, truncated, info = self.env.step(action)
            agent.observe(observation, reward, terminated, truncated, training_mode=True)
            if terminated or truncated:
                observation, info = self.env.reset()

        hand_confirmed_opt = np.array([[0.79345359, 0.8708637 ], 
                                       [0.80539959, 0.97837773],
                                       [0.,         0.        ]])
        np.testing.assert_almost_equal(hand_confirmed_opt, agent.q, decimal=2)

    def test_q_learning_update(self):
        explorer = table_rl.explorers.ConstantEpsilonGreedy(0.1, self.T.shape[1])
        agent = QLearning(self.T.shape[0],
                          self.T.shape[1],
                          table_rl.step_size_schedulers.ConstantStepSize(0.1),
                          explorer,
                          discount=self.discount,
                          initial_val=0.)
        agent.q = np.array([[1,2], [3,4], [5,6]], dtype=float)
        agent.current_obs = 0
        agent.last_action = 0
        mock_next_state = 1
        mock_reward = 2.0
        expected_updated_q_value = 1 + 0.1 * (mock_reward + self.discount * 4  - 1)
        expected_next_q = np.array([[expected_updated_q_value, 2], [3,4], [5,6]], dtype=float)
        agent.observe(1, mock_reward, False, False, training_mode=True)
        np.testing.assert_allclose(expected_next_q, agent.q)

