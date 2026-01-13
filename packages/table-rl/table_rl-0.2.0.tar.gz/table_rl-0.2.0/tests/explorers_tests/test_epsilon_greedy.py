import numpy as np
from table_rl.explorers.epsilon_greedy import epsilon_greedy_action_probs


def test_epsilon_greedy_standard():
    q_values = np.array([0, 8, 5, 5])
    epsilon = 0.2
    expected_results = np.array([0.05, 0.85, 0.05, 0.05])
    actual_result = epsilon_greedy_action_probs(q_values, epsilon)
    assert np.allclose(expected_results, actual_result)

def test_epsilon_greedy_tiebreak():
    q_values = np.array([0, 5, 5., 4])
    epsilon = 0.2
    expected_results = np.array([0.05, 0.45, 0.45, 0.05])
    actual_result = epsilon_greedy_action_probs(q_values, epsilon)
    assert np.allclose(expected_results, actual_result)

def test_uniform_random():
    q_values = np.array([0, 1, 2., 3, 9])
    epsilon = 1.0
    expected_results = np.array([0.2, 0.2, 0.2, 0.2, 0.2])
    actual_result = epsilon_greedy_action_probs(q_values, epsilon)
    assert np.allclose(expected_results, actual_result)

def test_exploit():
    q_values = np.array([0, 5, 5., 4, 9])
    epsilon = 0.0
    expected_results = np.array([0., 0., 0., 0., 1.0])
    actual_result = epsilon_greedy_action_probs(q_values, epsilon)
    assert np.allclose(expected_results, actual_result)
