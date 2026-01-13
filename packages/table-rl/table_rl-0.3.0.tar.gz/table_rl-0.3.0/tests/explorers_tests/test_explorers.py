import pytest
import numpy as np
import math
import table_rl
import table_rl.dp.dp as dp

class TestEpsilonGreedyExplorers:

    def test_constant_epsilon_greedy(self):
        explorer = table_rl.explorers.ConstantEpsilonGreedy(0.1, 4)
        action_vals = np.array([1.0, 4.0, 4.0, 3.0])
        actions = [explorer.select_action(None, action_vals) for _ in range(500)]
        assert 1 in actions
        assert 2 in actions
        explorer = table_rl.explorers.ConstantEpsilonGreedy(0., 4)
        actions = [explorer.select_action(None, action_vals) for _ in range(500)]
        assert 0 not in actions, actions
        assert 3 not in actions
        action = explorer.select_action(None, np.array([1.0, 2.0, 4.0, 3.0]))
        assert action == 2

    def test_linear_decay_epsilon_greedy(self):
        explorer = table_rl.explorers.LinearDecayEpsilonGreedy(1.0, 0.1, 9, 4)
        expected_epsilons = [1.0, 0.9, 0.8, 0.7, 0.6, 0.5, 0.4, 0.3, 0.2, 0.1, 0.1]
        for expected_epsilon in expected_epsilons:
            actual_epsilon = explorer.epsilon
            assert math.isclose(expected_epsilon, actual_epsilon)
            explorer.observe(None, None, None, None, True)


    def test_pct_decay_epsilon_greedy(self):
        explorer = table_rl.explorers.PercentageDecayEpsilonGreedy(1.0, 0.2, 0.8, 4)
        expected_epsilons = [math.pow(0.8, 0), 0.8, 0.64,  math.pow(0.8,3),  math.pow(0.8,4),
                             math.pow(0.8,5),  math.pow(0.8,6),  math.pow(0.8,7), 0.2, 0.2]
        for expected_epsilon in expected_epsilons:
            actual_epsilon = explorer.epsilon
            assert math.isclose(actual_epsilon, expected_epsilon)
            explorer.observe(None, None, None, None, True)

    def test_not_training_mode(self):
        explorer = table_rl.explorers.PercentageDecayEpsilonGreedy(1.0, 0.2, 0.8, 4)
        for _ in range(100):
            explorer.observe(None, None, None, None, True)

class TestPolicyExecutor:

    def test_policy_executor(self):
        policy = np.array([[0.3, 0.7],
                           [0.2, 0.8],
                           [0.4, 0.6]])
        explorer = table_rl.explorers.PolicyExecutor(policy)
        actions = [explorer.select_action(0, None) for _ in range(500)]
        assert 0 in actions
        assert 1 in actions
        assert 2 not in actions
        policy = np.array([[0.0, 1.0],
                   [0.2, 0.8],
                   [0.4, 0.6]])
        explorer = table_rl.explorers.PolicyExecutor(policy)
        actions = [explorer.select_action(0, None) for _ in range(500)]
        assert all(action == 1 for action in actions)
      

