import numpy as np
import table_rl
import table_rl.dp.dp as dp


env = table_rl.envs.BasicGridworld()
policy = np.full((15, 4), 0.25)
value_function = dp.policy_v_evaluation(policy, env.R, env.T, 1.0, 10000)
correct_action_values = dp.policy_q_evaluation(policy, env.R, env.T, 0.99, 10000)

env = table_rl.envs.BasicGridworld()
step_size = table_rl.step_size_schedulers.ConstantStepSize(0.0005)
explorer = table_rl.explorers.policy_executor.PolicyExecutor(policy)

agent = table_rl.learners.ExpectedSarsa(15,
                  4,
                  step_size,
                  explorer,
                  discount=0.99,)

observation, info = env.reset()
for timestep in range(10_000_000):
    action = agent.act(observation, True)
    observation, reward, terminated, truncated, info = env.step(action)
    agent.observe(observation, reward, terminated, truncated, training_mode=True)
    if terminated or truncated:
        observation, info = env.reset()
    if timestep % 100000 == 0:
        print(f"Timestep: {timestep}")

np.testing.assert_allclose(correct_action_values, agent.q, rtol=0.02, atol=0.1)