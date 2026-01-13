import pytest
import numpy as np
import table_rl
from table_rl.learners import ExpectedSarsa

class TestExpectedSarsa:
    @pytest.fixture(autouse=True)
    def setUp(self):
        self.env = table_rl.envs.BasicEnv(discount=0.9)
        self.num_states = 3
        self.num_actions = 2 # L and R
        self.T = self.env.T
        self.R = self.env.R
        self.discount = 0.9


    def test_expected_sarsa_loop(self):
        policy = np.array([[0.2, 0.8],[0.3, 0.7],[0.9, 0.1]])
        explorer = table_rl.explorers.PolicyExecutor(policy)

        agent = ExpectedSarsa(self.T.shape[0],
                          self.T.shape[1],
                          table_rl.step_size_schedulers.ConstantStepSize(0.02),
                          explorer,
                          discount=self.discount,
                          initial_val=0.)

        observation, _ = self.env.reset()

        for _ in range(300000):
            action = agent.act(observation, True)
            observation, reward, terminated, truncated, _ = self.env.step(action)
            agent.observe(observation, reward, terminated, truncated, training_mode=True)
            if terminated or truncated:
                observation, _ = self.env.reset()

        ground_truth = table_rl.dp.policy_q_evaluation(policy, self.R, self.T, self.discount, 10000)
        np.testing.assert_almost_equal(ground_truth, agent.q, decimal=2)

    def test_expected_sarsa_update(self):
        policy = np.array([[0.2, 0.8],[0.3, 0.7],[0.9, 0.1]])
        explorer = table_rl.explorers.PolicyExecutor(policy)
        agent = ExpectedSarsa(self.T.shape[0],
                          self.T.shape[1],
                          table_rl.step_size_schedulers.ConstantStepSize(0.1),
                          explorer,
                          discount=self.discount,
                          initial_val=0.)
        agent.q = np.array([[1,2], [3, 4], [5,6]], dtype=float)
        agent.current_obs = 0
        agent.last_action = 0
        mock_next_state = 1
        mock_reward = 2.0
        target_q = 0.3 * 3 + 0.7 * 4
        expected_updated_q_value = 1 + 0.1 * (mock_reward + self.discount * target_q - 1)
        expected_next_q = np.array([[expected_updated_q_value, 2], [3,4], [5,6]], dtype=float)
        agent.observe(mock_next_state, mock_reward, False, False, training_mode=True)
        np.testing.assert_allclose(expected_next_q, agent.q)

