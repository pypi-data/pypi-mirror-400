import pytest
import numpy as np
import math
import table_rl.dp.dp as dp
import table_rl

class TestDP:
    @pytest.fixture(autouse=True)
    def setUp(self):
        self.env = table_rl.envs.BasicEnv(discount=0.9)
        self.T = self.env.T
        self.R = self.env.R

        self.num_states = 3
        self.num_actions = 2 # L and R
    
        self.discount = 0.9

        self.policy = np.array([[0.3, 0.7],
                           [0.2, 0.8],
                           [0.4, 0.6]])

    def test_q_bellman_optimality_update(self):
        Q = np.array([[0.3, 0.4],
                      [0.5, 0.4],
                      [0.7, 0.8]])
        Q_update = dp.q_bellman_optimality_update(Q, self.T, self.R, self.discount)
        Q_true_update = np.array([[0.369, 0.441],
                      [0.496, 1.584],
                      [0.72, 0.72]])
        np.testing.assert_almost_equal(Q_true_update, Q_update)

    def test_q_value_iteration(self):
        opt_Q = dp.q_value_iteration(self.num_states,
                                          self.num_actions,
                                          self.R, self.T,
                                          self.discount, 1000)
        hand_confirmed_opt = np.array([[0.79345359, 0.8708637 ], 
                                       [0.80539959, 0.97837773],
                                       [0.,         0.        ]])
        np.testing.assert_almost_equal(hand_confirmed_opt, opt_Q, decimal=5)

    def test_v_bellman_optimality_update(self):
        V = np.array([0.1, 0.2, 0.3])
        V_update = dp.v_bellman_optimality_update(V, self.R, self.T, self.discount)
        V_true = np.array([0.171, 1.152, 0.27])
        np.testing.assert_almost_equal(V_true, V_update)

    def test_value_iteration(self):
        opt_V = dp.value_iteration(self.num_states,
                                        self.num_actions,
                                        self.R, self.T,
                                        self.discount, 1000)
        hand_confirmed_V = np.array([0.8708637, 0.97837773, 0.])
        np.testing.assert_almost_equal(hand_confirmed_V, opt_V, decimal=5)


    def test_q_eval_update(self):
        Q = np.array([[0.3, 0.4],
                      [0.5, 0.4],
                      [0.7, 0.8]])
        Q_true_update = np.array([[0.3375, 0.3735],
                      [0.4681, 1.5489],
                      [0.684, 0.684]])
        Q_updated = dp.policy_q_eval_update(Q, self.policy, self.R, self.T, self.discount)
        np.testing.assert_almost_equal(Q_true_update, Q_updated)


    def test_policy_q_evaluation(self):
        Q_pi_learned = dp.policy_q_evaluation(self.policy, self.R, self.T, self.discount, 400)
        hand_confirmed_Q = np.array([[0.72479142, 0.82079478 ], 
                              [0.7415119, 0.9712791],
                              [0.,         0.        ]])
        np.testing.assert_almost_equal(hand_confirmed_Q, Q_pi_learned, decimal=5)


    def test_v_eval_update(self):
        V = np.array([0.37, 0.42, 0.76])
        V_true = np.array([0.3627, 1.33274, 0.684])
        V_updated = dp.policy_v_eval_update(V, self.policy, self.R, self.T, self.discount)
        np.testing.assert_almost_equal(V_true, V_updated)

    def test_policy_v_evaluation(self):
        V_pi_learned = dp.policy_v_evaluation(self.policy, self.R, self.T, self.discount, 400)
        hand_confirmed_V = np.array([0.791993772, 0.92532566, 0.0])
        np.testing.assert_almost_equal(hand_confirmed_V, V_pi_learned, decimal=6)

    def test_q_bellman_consistent(self):
        Q_converged = np.array([[0.72479142, 0.82079478 ], 
                              [0.7415119, 0.9712791],
                              [0.,         0.        ]])
        dp.check_q_bellman_consistent(Q_converged, self.policy, self.R, self.T, self.discount, diff=1e-04)
        with pytest.raises(AssertionError):
            Q_converged[0,1] = 0.8
            dp.check_q_bellman_consistent(Q_converged,
                                               self.policy, self.R, self.T,
                                               self.discount, diff=1e-04)

    def test_v_bellman_consistent(self):
        V_converged = np.array([0.791993772, 0.92532566, 0.0])
        dp.check_v_bellman_consistent(V_converged, self.policy, self.R, self.T, self.discount, diff=1e-04)
        with pytest.raises(AssertionError):
            V_converged[1] = 0.9
            dp.check_v_bellman_consistent(V_converged, self.policy, 
                                               self.R, self.T, self.discount, diff=1e-02)

    def test_check_q_bellman_optimal(self):
        Q_converged = np.array([[0.79345359, 0.8708637 ], 
                                [0.80539959, 0.97837773],
                                [0.,         0.        ]])
        dp.check_q_bellman_optimal(Q_converged, self.R, self.T, self.discount, diff=1e-04)
        with pytest.raises(AssertionError):
            Q_converged[0,1] = 0.85
            dp.check_q_bellman_optimal(Q_converged, self.R, self.T,
                                               self.discount, diff=1e-04)


    def test_check_v_bellman_optimal(self):
        V_converged = np.array([0.8708637, 0.97837773, 0.])
        dp.check_v_bellman_optimal(V_converged, self.R, self.T, self.discount, diff=1e-04)
        with pytest.raises(AssertionError):
            V_converged[1] = 0.95
            dp.check_v_bellman_optimal(V_converged, self.R, self.T, self.discount, diff=1e-02)
    
    def test_transition_under_pi(self):
        pi = np.array([[0.1, 0.9], [0.2, 0.8], [0.3, 0.7]])

        T = np.zeros((3,2,3))
        T[0,0,0] = 0.9
        T[0,1,0] = 0.1
        T[0,0,1] = 0.1
        T[0,1,1] = 0.9

        T[1,0,0] = 0.9
        T[1,1,0] = 0.1
        T[1,0,2] = 0.1
        T[1,1,2] = 0.9

        T[2,0,1] = 0.9
        T[2,1,1] = 0.1
        T[2,0,2] = 0.1
        T[2,1,2] = 0.9

        T_pi_true = np.array([[0.18, 0.82, 0],
            [0.26, 0, 0.74],
            [0, 0.34, 0.66]])

        T_pi_computed = dp.compute_transition_under_pi(T, pi)
        assert np.allclose(T_pi_true, T_pi_computed)

    def test_compute_on_policy_distribution(self):
        pi = np.array([[0.1, 0.9], [0.2, 0.8], [0.3, 0.7]])

        T = np.zeros((3,2,3))
        T[0,0,0] = 0.9
        T[0,1,0] = 0.1
        T[0,0,1] = 0.1
        T[0,1,1] = 0.9

        T[1,0,0] = 0.9
        T[1,1,0] = 0.1
        T[1,0,2] = 0.1
        T[1,1,2] = 0.9

        T[2,0,1] = 0.9
        T[2,1,1] = 0.1
        T[2,0,2] = 0.1
        T[2,1,2] = 0.9


        mu_computed = dp.compute_on_policy_distribution(T, pi)
        # Equation 10.8 of S&B 
        for s_prime in range(3):
            val = np.array([[0., 0., 0.]])
            for s in range(3):
                val[0][s] = np.dot(T[s, :, s_prime], pi[s,:])
                # transition_under_pi[s, s_prime] = np.dot(T[s, :, s_prime], pi[s,:])
            assert math.isclose(mu_computed[0, s_prime], np.dot(mu_computed, val.transpose())[0][0])


    def test_compute_successor_representation(self):
        sr = dp.compute_successor_representation(self.T, self.policy, self.discount)
        policy_reshaped = np.reshape(self.policy, (self.policy.shape[0], self.policy.shape[1], 1))
        reward = np.sum(np.sum(self.T * policy_reshaped * self.R, axis=1),axis=1)
        sr_induced_vf = np.dot(sr, reward)
        hand_confirmed_V = np.array([0.791993772, 0.92532566, 0.0])
        np.testing.assert_allclose(sr_induced_vf, hand_confirmed_V, atol=1e-05)
