import pytest
import numpy as np
import table_rl
import table_rl.dp.dp as dp
from table_rl.learners import QVLearning

class TestQVLearning:
    @pytest.fixture(autouse=True)
    def setUp(self):
        self.env = table_rl.envs.BasicEnv(discount=0.9)
        self.num_states = 3
        self.num_actions = 2 # L and R
        self.T = self.env.T
        self.R = self.env.R
        self.discount = 0.9
        self.policy = np.array([[0.3, 0.7],
                           [0.2, 0.8],
                           [0.4, 0.6]])


    def test_qv_learning_loop(self):
        explorer = table_rl.explorers.PolicyExecutor(self.policy)
        agent = QVLearning(self.T.shape[0],
                           self.T.shape[1],
                           table_rl.step_size_schedulers.ConstantStepSize(0.01),
                           table_rl.step_size_schedulers.ConstantStepSize(0.01),
                           explorer,
                           discount=self.discount,
                           initial_val=0.)
        observation, _ = self.env.reset()

        for _ in range(400000):
            action = agent.act(observation, True)
            observation, reward, terminated, truncated, _ = self.env.step(action)
            agent.observe(observation, reward, terminated, truncated, training_mode=True)
            if terminated or truncated:
                observation, _ = self.env.reset()

        expected_q_values = dp.policy_q_evaluation(self.policy, self.R, self.T, self.discount, 2500)
        expected_v_values = dp.policy_v_evaluation(self.policy, self.R, self.T, self.discount, 2500)
        np.testing.assert_almost_equal(expected_q_values, agent.q, decimal=2)
        np.testing.assert_almost_equal(expected_v_values, agent.v, decimal=2)


    def test_qv_learning_update(self):
        explorer = table_rl.explorers.GreedyExplorer(self.T.shape[1])
        
        agent = QVLearning(self.T.shape[0],
                           self.T.shape[1],
                           table_rl.step_size_schedulers.ConstantStepSize(0.1),
                           table_rl.step_size_schedulers.ConstantStepSize(0.1),
                           explorer,
                           discount=self.discount,
                           initial_val=0.)
        agent.q = np.array([[1,2], [3,4], [5,6]], dtype=float)
        agent.v = np.array([0, 1, 2], dtype=float)
        agent.current_obs = 0
        agent.action = 0
        mock_next_state = 1
        mock_reward = 2.0
        target = mock_reward + self.discount * agent.v[mock_next_state]
        expected_updated_action_value = 1 + 0.1 * (target  - 1)
        expected_updated_state_value = 0.1 * target
        expected_next_q = np.array([[expected_updated_action_value, 2], [3,4], [5,6]], dtype=float)
        expected_next_v = np.array([expected_updated_state_value, 1, 2], dtype=float)
        agent.observe(mock_next_state, mock_reward, False, False, training_mode=True)
        np.testing.assert_allclose(expected_next_q, agent.q)
        np.testing.assert_allclose(expected_next_v, agent.v)

    def test_qv_learning_update_termination(self):
        explorer = table_rl.explorers.GreedyExplorer(self.T.shape[1])
        agent = QVLearning(self.T.shape[0],
                           self.T.shape[1],
                           table_rl.step_size_schedulers.ConstantStepSize(0.1),
                           table_rl.step_size_schedulers.ConstantStepSize(0.1),
                           explorer,
                           discount=self.discount,
                           initial_val=0.)
        agent.q = np.array([[1,2], [3,4], [5,6]], dtype=float)
        agent.v = np.array([0, 1, 2], dtype=float)
        agent.current_obs = 0
        agent.action = 0
        mock_next_state = 1
        mock_reward = 2.0
        expected_updated_action_value = 1 + 0.1 * (mock_reward  - 1)
        expected_updated_state_value = 0.1 * mock_reward
        expected_next_q = np.array([[expected_updated_action_value, 2], [3,4], [5,6]], dtype=float)
        expected_next_v = np.array([expected_updated_state_value, 1, 2], dtype=float)
        agent.observe(mock_next_state, mock_reward, True, False, training_mode=True)
        np.testing.assert_allclose(expected_next_q, agent.q)
        np.testing.assert_allclose(expected_next_v, agent.v)


    def test_qv_learning_truncation(self):
        explorer = table_rl.explorers.GreedyExplorer(self.T.shape[1])
        agent = QVLearning(self.T.shape[0],
                           self.T.shape[1],
                           table_rl.step_size_schedulers.ConstantStepSize(0.1),
                           table_rl.step_size_schedulers.ConstantStepSize(0.1),
                           explorer,
                           discount=self.discount,
                           initial_val=0.)
        agent.current_obs = 0
        agent.action = 0
        agent.observe(1, 5, False, False, training_mode=True)
        assert agent.action is not None
        agent.observe(1, 5, False, True, training_mode=True)
        assert agent.action is None

