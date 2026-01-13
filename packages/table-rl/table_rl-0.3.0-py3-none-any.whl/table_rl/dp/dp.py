import numpy as np

def policy_q_eval_update(Q, policy, R, T, discount):
    expected_v = np.sum(np.multiply(policy, Q), 1)
    delta = R + discount * np.broadcast_to(expected_v, R.shape)
    Q = np.sum(np.multiply(T, delta), 2)
    return Q

def policy_q_evaluation(policy, R, T, discount, iterations):
    num_states = T.shape[0]
    num_actions = T.shape[1]
    Q = np.zeros((num_states, num_actions))
    for i in range(iterations):
        Q = policy_q_eval_update(Q, policy, R, T, discount)
    return Q

def policy_v_eval_update(V, policy, R, T, discount):
    delta = R + discount * np.broadcast_to(V, R.shape)
    Q = np.sum(np.multiply(T, delta), 2)
    V = np.sum(np.multiply(policy, Q), 1)
    return V

def policy_v_evaluation(policy, R, T, discount, iterations):
    num_states = T.shape[0]
    num_actions = T.shape[1]
    V = np.zeros((num_states))
    for i in range(iterations):
        V = policy_v_eval_update(V, policy, R, T, discount)
    return V

def check_q_bellman_optimal(Q, R, T, discount, diff=1e-03):
    num_states, num_actions = Q.shape
    for state in range(num_states):
        for action in range(num_actions):
            expectation = 0
            for ns in range(num_states):
                expectation += T[state, action, ns] * (R[state, action, ns] + discount * np.max(Q[ns]))
            assert np.isclose(Q[state,action], expectation, atol=diff)


def check_v_bellman_optimal(V, R, T, discount, diff=1e-03):
    num_states, num_actions = V.shape[0], T.shape[1]
    for state in range(num_states):
        expectations = []
        for action in range(num_actions):
            expectation = 0
            for ns in range(num_states):
                expectation += T[state, action, ns] * (R[state, action, ns] + discount * V[ns])
            expectations.append(expectation)
        assert np.isclose(V[state], max(expectations), atol=diff)
    
def check_q_bellman_consistent(Q, policy, R, T, discount, diff=1e-03):
    num_states, num_actions = Q.shape
    for state in range(num_states):
        for action in range(num_actions):
            expectation = 0
            for ns in range(num_states):
                expected_v = 0
                for na in range(num_actions):
                    expected_v += policy[ns, na] * Q[ns, na]
                expectation += T[state, action, ns] * (R[state, action, ns] + discount * expected_v)
            assert np.isclose(Q[state,action], expectation, atol=diff)

def check_v_bellman_consistent(V, policy, R, T, discount, diff=1e-03):
    num_states, num_actions= V.shape[0], T.shape[1]
    for state in range(num_states):
        expectation = 0
        for action in range(num_actions):
            for ns in range(num_states):
                expectation += policy[state, action] * T[state, action, ns] * (R[state, action, ns] + discount * V[ns]) 
        assert np.isclose(V[state], expectation, atol=diff)

def q_bellman_optimality_update(Q, T, R, discount):
    delta = R + discount * np.broadcast_to(np.max(Q,1), R.shape)
    Q = np.sum(np.multiply(T, delta), 2)
    return Q

# Assume reward is of form R(s,a,s')
def q_value_iteration(num_states, num_actions, R, T, discount, iterations):
    Q = np.zeros((num_states, num_actions))
    for i in range(iterations):
        Q = q_bellman_optimality_update(Q, T, R, discount)
    return Q

def v_bellman_optimality_update(V, R, T, discount):
    delta = R + discount * np.broadcast_to(V, R.shape)
    Q = np.sum(np.multiply(T, delta), 2)
    V = np.max(Q, axis=1)
    return V

def value_iteration(num_states, num_actions, R, T, discount, iterations):
    V = np.zeros((num_states))
    for i in range(iterations):
        V = v_bellman_optimality_update(V, R, T, discount)
    return V
        
def loop_q_value_iteration(num_states, num_actions, R, T, discount, iterations):
    Q = np.zeros((num_states, num_actions))
    for _ in range(iterations):
        Q_prev = Q.copy()
        for s in range(num_states):
            for a in range(num_actions):
                expectation = 0.0
                for next_s in range(num_states):
                    expectation += T[s,a,next_s] * (R[s,a,next_s] + discount * np.max(Q_prev[next_s]))
                Q[s,a] = expectation
    return Q

def loop_value_iteration(num_states, num_actions, R, T, discount, iterations):
    V = np.zeros((num_states))
    for i in range(iterations):
        V_prev = V.copy()
        for s in range(num_states):
            Q_vals = np.zeros(num_actions)
            for a in range(num_actions):
                for next_s in range(num_states):
                    prob = T[s,a,next_s]
                    Q_vals[a] += prob * (R[s, a, next_s] + discount * V_prev[next_s])
            V[s] = np.max(Q_vals)
    return V

def assert_transition_shape(T):
    assert len(T.shape) == 3
    assert T.shape[0] == T.shape[2]

def check_valid_transition(T):
    assert_transition_shape(T)
    states = range(T.shape[0])
    actions = range(T.shape[1])
    for s in states:
        for a in actions:
            assert np.sum(T[s,a]) == 1.0

def compute_transition_under_pi(T, pi):
    assert_transition_shape(T)
    assert len(pi.shape) == 2
    assert pi.shape == T.shape[0:2]
    num_states = T.shape[0]

    pi_reshaped = np.reshape(pi, (pi.shape[0], pi.shape[1], 1))
    T_pi = np.sum(T * pi_reshaped, axis=1)
    return T_pi

def find_terminal_states(T):
    terminal_states = []
    for state in range(T.shape[0]):
        if np.allclose(T[state, :, state], np.full(T.shape[1], 1)):
            terminal_states.append(state)
    return terminal_states


def compute_on_policy_distribution(T, pi, start_state_dist=None):
    T_pi = compute_transition_under_pi(T, pi)
    # initial distribution shouldn't matter for steady state, set it to uniform
    if start_state_dist is None:
        initial_dist = np.full((1, T_pi.shape[0]), 1/T_pi.shape[0])
    else:
        initial_dist = start_state_dist
    T_pi_pow = np.linalg.matrix_power(T_pi, 1000)
    converge_dist = np.dot(initial_dist, T_pi_pow)
    T_converge_dist = np.dot(converge_dist, T_pi)
    while not np.allclose(converge_dist, T_converge_dist):
        T_pi_pow = np.dot(T_pi_pow, T_pi_pow)
        T_converge_dist = np.dot(converge_dist, T_pi_pow)
    return T_converge_dist


def compute_on_policy_sa_distribution(T, pi, start_state_dist=None):
    mu_computed = compute_on_policy_distribution(T, pi, start_state_dist)
    mu_broadcasted = np.broadcast_to(mu_computed, pi.T.shape)
    sa_mu = np.multiply(mu_broadcasted.T, pi)
    return sa_mu


def compute_successor_representation(T, pi, discount):
    assert 0 < discount < 1.
    assert T.shape == (pi.shape[0], pi.shape[1], pi.shape[0])
    T_pi = compute_transition_under_pi(T, pi)
    return np.linalg.inv(np.eye(pi.shape[0]) - discount * T_pi)


