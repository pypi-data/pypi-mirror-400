import table_rl
import numpy as np

env = table_rl.envs.ControlGridworldEnv(width=3, height=3, truncation_limit=100)
step_size = table_rl.step_size_schedulers.ConstantStepSize(0.05)
explorer = table_rl.explorers.ConstantEpsilonGreedy(0.1, 4)

agent = table_rl.learners.QLearning(9,
                  4,
                  step_size,
                  explorer,
                  discount=0.9,
                  initial_val=0.)

observation, info = env.reset()
for _ in range(100_000):
    action = agent.act(observation, True)
    observation, reward, terminated, truncated, info = env.step(action)
    agent.observe(observation, reward, terminated, truncated, training_mode=True)
    if terminated or truncated:
        observation, info = env.reset()

optimal_values = table_rl.dp.dp.value_iteration(9, 4, env.R, env.T, 0.9, 10000)
np.testing.assert_allclose(optimal_values, np.amax(agent.q, axis=1))
