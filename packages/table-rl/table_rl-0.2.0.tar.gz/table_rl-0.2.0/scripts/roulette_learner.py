import table_rl
from pdb import set_trace

env = table_rl.envs.Roulette()
step_size = table_rl.step_size_schedulers.ConstantStepSize(0.01)
explorer = table_rl.explorers.ConstantEpsilonGreedy(0.05, 171)

agent = table_rl.learners.QLearning(env.observation_space.n,
                  env.action_space.n,
                  step_size,
                  explorer,
                  discount=0.99,
                  initial_val=0.)

# agent = table_rl.learners.DoubleQLearning(env.observation_space.n,
#                   env.action_space.n,
#                   step_size,
#                   step_size,
#                   explorer,
#                   discount=0.95,
#                   initial_val=0.)

observation, info = env.reset()
for _ in range(100000):
    action = agent.act(observation, True)
    observation, reward, terminated, truncated, info = env.step(action)
    agent.observe(observation, reward, terminated, truncated, training_mode=True)
    if terminated or truncated:
        observation, info = env.reset()

optimal_values = table_rl.dp.dp.value_iteration(env.T.shape[0], env.T.shape[1], env.R, env.T, 0.95, 10000)
set_trace()
# np.testing.assert_allclose(optimal_values, np.amax(agent.q, axis=1))
