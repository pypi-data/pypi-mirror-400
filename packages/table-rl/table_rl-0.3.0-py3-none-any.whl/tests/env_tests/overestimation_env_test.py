import pytest
from table_rl.envs import OverestimationGridworld


UP = 0
DOWN = 1
LEFT = 2
RIGHT = 3


class TestOverestimationGridworld:
    @pytest.fixture(autouse=True)
    def setUp(self):
        self.env = OverestimationGridworld()
        self.num_states = 10
        self.num_actions = 4


    def test_trajectory(self):
        observation, info = self.env.reset()
        assert observation == 0
        observation, reward, terminated, truncated, info = self.env.step(UP)
        assert observation == 3
        assert reward in [-12., 10.]
        assert not truncated and not terminated
        observation, reward, terminated, truncated, info = self.env.step(UP)
        assert observation == 6
        assert reward in [-12., 10.]
        assert not truncated and not terminated
        observation, reward, terminated, truncated, info = self.env.step(UP) # bump into wall
        assert observation == 6
        assert reward in [-12., 10.]
        assert not truncated and not terminated
        observation, reward, terminated, truncated, info = self.env.step(RIGHT)
        assert observation == 7
        assert reward in [-12., 10.]
        assert not truncated and not terminated
        observation, reward, terminated, truncated, info = self.env.step(DOWN)
        assert observation == 4
        assert reward in [-12., 10.]
        assert not truncated and not terminated
        observation, reward, terminated, truncated, info = self.env.step(DOWN)
        assert observation == 1
        assert reward in [-12., 10.]
        assert not truncated and not terminated
        observation, reward, terminated, truncated, info = self.env.step(DOWN) # wall
        assert observation == 1
        assert reward in [-12., 10.]
        assert not truncated and not terminated
        observation, reward, terminated, truncated, info = self.env.step(RIGHT)
        assert observation == 2
        assert reward in [-12., 10.]
        assert not truncated and not terminated
        observation, reward, terminated, truncated, info = self.env.step(RIGHT) # wall
        assert observation == 2
        assert reward in [-12., 10.]
        assert not truncated and not terminated
        observation, reward, terminated, truncated, info = self.env.step(UP) # wall
        assert observation == 5
        assert reward in [-12., 10.]
        assert not truncated and not terminated
        observation, reward, terminated, truncated, info = self.env.step(UP) # wall
        assert observation == 8
        assert reward in [-12., 10.]
        assert not truncated and not terminated
        observation, reward, terminated, truncated, info = self.env.step(UP) # wall
        assert observation == 9
        assert reward == 5.0
        assert terminated and not truncated