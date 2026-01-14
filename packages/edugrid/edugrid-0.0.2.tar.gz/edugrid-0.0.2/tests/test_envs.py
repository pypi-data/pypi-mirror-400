import gymnasium as gym
import numpy as np
import pytest

from edugrid.envs.cells import CellType
from edugrid.envs.grids import Action, EduGridEnv


def test_create_env():
    env = gym.make("philsteg/EduGrid-v0")
    assert env


def test_create_env_from_map_str():
    map_string = """
        NNS
        NNN
        NNT  
    """
    env = EduGridEnv(map_str=map_string)
    assert env.cell_type_matrix.shape == (3, 3)
    assert env.cell_type_matrix[0, 2] == CellType.SINK
    assert env.cell_type_matrix[2, 2] == CellType.TARGET
    assert np.all(env.cell_type_matrix[0, (0, 1)] == CellType.NORMAL)
    assert np.all(env.cell_type_matrix[1, :] == CellType.NORMAL)
    assert np.all(env.cell_type_matrix[2, (0, 1)] == CellType.NORMAL)


def test_action_space(simple_env: EduGridEnv):
    assert isinstance(simple_env.action_space, gym.spaces.Discrete)
    assert simple_env.action_space.start == 0
    assert simple_env.action_space.n == 4


def test_observation_space(simple_env: EduGridEnv):
    assert isinstance(simple_env.observation_space, gym.spaces.Dict)
    agent_space = simple_env.observation_space["agent"]
    assert isinstance(agent_space, gym.spaces.MultiDiscrete)
    assert np.all(agent_space.start == 0)
    assert np.all(agent_space.nvec == 5)
    targets_space = simple_env.observation_space["targets"]
    assert isinstance(targets_space, gym.spaces.Tuple)
    assert len(targets_space) == 1
    assert np.all(targets_space[0].start == 0)
    assert np.all(targets_space[0].nvec == 5)


def test_terminal_matrix(simple_env: EduGridEnv):
    expected = np.zeros((5, 5), dtype="bool")
    expected[4, 4] = True
    assert np.array_equal(simple_env.terminal_matrix, expected)


def test_terminal_matrix_set_1(simple_env: EduGridEnv):
    new = np.zeros((5, 5), dtype="bool")
    simple_env.terminal_matrix = new
    assert np.array_equal(simple_env.terminal_matrix, new)


def test_terminal_matrix_set_2(simple_env: EduGridEnv):
    new = np.zeros((5,), dtype="bool")
    with pytest.raises(AssertionError):
        simple_env.terminal_matrix = new


def test_terminal_matrix_set_3(simple_env: EduGridEnv):
    new = np.ones((5, 5)) * 5
    with pytest.raises(AssertionError):
        simple_env.terminal_matrix = new


def test_terminal_matrix_setitem_1(simple_env: EduGridEnv):
    expected = np.ones((5, 5), dtype="bool")
    simple_env.terminal_matrix[:] = True
    assert np.array_equal(simple_env.terminal_matrix, expected)


def test_terminal_matrix_setitem_2(simple_env: EduGridEnv):
    with pytest.raises(ValueError):
        simple_env.terminal_matrix[0, 0] = np.ones((5, 5), dtype="bool")


def test_transition_matrix(simple_env: EduGridEnv, simple_transitions: np.ndarray):
    assert np.array_equal(simple_env._transition_matrix, simple_transitions)


def test_transition_matrix_get(simple_env: EduGridEnv, simple_transitions: np.ndarray):
    assert np.array_equal(simple_env.transition_matrix, simple_transitions)


def test_transition_matrix_getitem_1(simple_env: EduGridEnv):
    expected_probs = np.zeros((5, 5))
    expected_probs[0, 1] = 1.0
    assert np.array_equal(
        simple_env.transition_matrix[0, 0, Action.RIGHT], expected_probs
    )


def test_transition_matrix_getitem_2(simple_env: EduGridEnv):
    expected_probs = np.zeros((5, 5))
    expected_probs[0, 1] = 1.0
    assert np.array_equal(
        simple_env.transition_matrix.get(0, 0, Action.RIGHT), expected_probs
    )


def test_transition_matrix_getitem_3(simple_env: EduGridEnv):
    expected_probs = np.zeros((5, 5))
    expected_probs[0, 1] = 1.0
    assert np.array_equal(
        simple_env.transition_matrix.get((0, 0, Action.RIGHT)), expected_probs
    )


def test_transition_matrix_set_1(simple_env: EduGridEnv):
    with pytest.raises(AssertionError):
        simple_env.transition_matrix = 1


def test_transition_matrix_set_2(
    simple_env: EduGridEnv, simple_transitions: np.ndarray
):
    with pytest.raises(AssertionError):
        simple_env.transition_matrix = np.ones_like(simple_transitions)


def test_transition_matrix_set_3(
    simple_env: EduGridEnv, simple_transitions: np.ndarray
):
    simple_env.transition_matrix = simple_transitions
    assert np.array_equal(simple_env.transition_matrix.get(), simple_transitions)


def test_transition_matrix_setitem_1(simple_env: EduGridEnv):
    with pytest.raises(IndexError):
        simple_env.transition_matrix[0, 0, 0, 0, 0] = 0


def test_transition_matrix_setitem_2(simple_env: EduGridEnv):
    with pytest.raises(IndexError):
        simple_env.transition_matrix[0, 0, 0, 0] = np.zeros((5,))


def test_transition_matrix_setitem_3(simple_env: EduGridEnv):
    with pytest.raises(AssertionError):
        simple_env.transition_matrix[0, 0, 0] = np.zeros((5, 5))


def test_transition_matrix_setitem_4(simple_env: EduGridEnv):
    with pytest.raises(AssertionError):
        simple_env.transition_matrix[0, 0, 0] = np.zeros((5, 5, 4, 5, 5))


def test_transition_matrix_setitem_5(simple_env: EduGridEnv):
    with pytest.raises(IndexError):
        simple_env.transition_matrix[0, 0, Action.RIGHT, 0, 1] = 1


def test_transition_matrix_setitem_6(
    simple_env: EduGridEnv, simple_transitions: np.ndarray
):
    a = np.zeros((5, 5))
    a[4, 4] = 1.0
    simple_env.transition_matrix[0, 0, 0] = a
    simple_transitions[0, 0, 0] = a
    assert np.array_equal(simple_env._transition_matrix, simple_transitions)


def test_transition_matrix_setitem_7(
    simple_env: EduGridEnv, simple_transitions: np.ndarray
):
    expected = np.ones((5, 5, 4, 5, 5)) / 25
    simple_env.transition_matrix[:] = 1 / 25
    assert np.array_equal(simple_env._transition_matrix, expected)


def test_reward_matrix_set(simple_env: EduGridEnv, simple_rewards: np.ndarray):
    assert np.array_equal(simple_env._reward_matrix, simple_rewards)


def test_reward_matrix_get(simple_env: EduGridEnv, simple_rewards: np.ndarray):
    assert np.array_equal(simple_env.reward_matrix.get(), simple_rewards)


def test_reward_matrix_getitem_1(simple_env: EduGridEnv):
    expected = -np.ones((5, 5))
    expected[4, 4] = 10.0
    assert np.array_equal(simple_env.reward_matrix[0, 0, Action.RIGHT], expected)


def test_reward_matrix_getitem_2(simple_env: EduGridEnv):
    expected = -np.ones((5, 5))
    expected[4, 4] = 10.0
    assert np.array_equal(simple_env.reward_matrix.get(0, 0, Action.RIGHT), expected)


def test_reward_matrix_getitem_3(simple_env: EduGridEnv):
    expected = -np.ones((5, 5))
    expected[4, 4] = 10.0
    assert np.array_equal(simple_env.reward_matrix.get((0, 0, Action.RIGHT)), expected)


def test_reward_matrix_set_1(simple_env: EduGridEnv):
    with pytest.raises(AssertionError):
        simple_env.reward_matrix = 1


def test_reward_matrix_set_2(simple_env: EduGridEnv):
    with pytest.raises(AssertionError):
        simple_env.reward_matrix = np.ones((1, 1, 1))


def test_reward_matrix_set_3(simple_env: EduGridEnv, simple_rewards: np.ndarray):
    simple_env.reward_matrix = simple_rewards
    assert np.array_equal(simple_env._reward_matrix, simple_rewards)


def test_reward_matrix_setitem_1(simple_env: EduGridEnv, simple_rewards: np.ndarray):
    simple_rewards[0, 0, 0, 0, 0] = 0
    simple_env.reward_matrix[0, 0, 0, 0, 0] = 0
    assert np.array_equal(simple_env._reward_matrix, simple_rewards)


def test_reward_matrix_setitem_2(simple_env: EduGridEnv, simple_rewards: np.ndarray):
    simple_rewards[0, 0, 0, 0] = np.zeros((5,))
    simple_env.reward_matrix[0, 0, 0, 0] = np.zeros((5,))
    assert np.array_equal(simple_env._reward_matrix, simple_rewards)


def test_reward_matrix_setitem_3(simple_env: EduGridEnv, simple_rewards: np.ndarray):
    simple_rewards[0, 0, 0] = np.zeros((5, 5))
    simple_env.reward_matrix[0, 0, 0] = np.zeros((5, 5))
    assert np.array_equal(simple_env._reward_matrix, simple_rewards)


def test_reward_matrix_setitem_4(simple_env: EduGridEnv):
    with pytest.raises(ValueError):
        simple_env.reward_matrix[0, 0, Action.RIGHT, 0, 1] = np.ones((5, 5))


def test_reset_env(simple_env: EduGridEnv):
    obs, info = simple_env.reset()
    assert np.all(obs["agent"] == simple_env._initial_agent_location)
    assert (
        len(obs["targets"]) == 1
        and obs["targets"][0][0] == 4
        and obs["targets"][0][1] == 4
    )
    assert info["prob"] is None


def test_step_env_right(simple_env: EduGridEnv):
    initial_obs, _ = simple_env.reset()
    initial_row, initial_col = initial_obs["agent"]
    obs, reward, terminated, truncated, info = simple_env.step(Action.RIGHT)
    row, col = obs["agent"]
    assert row == 0 and col == 1
    assert (
        len(obs["targets"]) == 1
        and obs["targets"][0][0] == 4
        and obs["targets"][0][1] == 4
    )
    assert (
        reward
        == simple_env.reward_matrix[initial_row, initial_col, Action.RIGHT, row, col]
    )
    assert terminated == simple_env.terminal_matrix[row, col]
    assert truncated is False
    assert (
        info["prob"]
        == simple_env.transition_matrix[
            initial_row, initial_col, Action.RIGHT, row, col
        ]
    )


def test_step_env_up(simple_env: EduGridEnv):
    initial_obs, _ = simple_env.reset()
    initial_row, initial_col = initial_obs["agent"]
    obs, reward, terminated, truncated, info = simple_env.step(Action.UP)
    row, col = obs["agent"]
    assert obs["agent"][0] == 0 and obs["agent"][1] == 0
    assert (
        len(obs["targets"]) == 1
        and obs["targets"][0][0] == 4
        and obs["targets"][0][1] == 4
    )
    assert (
        reward
        == simple_env.reward_matrix[initial_row, initial_col, Action.UP, row, col]
    )
    assert terminated == simple_env.terminal_matrix[row, col]
    assert truncated is False
    assert (
        info["prob"]
        == simple_env.transition_matrix[initial_row, initial_col, Action.UP, row, col]
    )


def test_step_env_left(simple_env: EduGridEnv):
    initial_obs, _ = simple_env.reset()
    initial_row, initial_col = initial_obs["agent"]
    obs, reward, terminated, truncated, info = simple_env.step(Action.LEFT)
    row, col = obs["agent"]
    assert obs["agent"][0] == 0 and obs["agent"][1] == 0
    assert (
        len(obs["targets"]) == 1
        and obs["targets"][0][0] == 4
        and obs["targets"][0][1] == 4
    )
    assert (
        reward
        == simple_env.reward_matrix[initial_row, initial_col, Action.LEFT, row, col]
    )
    assert terminated == simple_env.terminal_matrix[row, col]
    assert truncated is False
    assert (
        info["prob"]
        == simple_env.transition_matrix[initial_row, initial_col, Action.LEFT, row, col]
    )


def test_step_env_down(simple_env: EduGridEnv):
    initial_obs, _ = simple_env.reset()
    initial_row, initial_col = initial_obs["agent"]
    obs, reward, terminated, truncated, info = simple_env.step(Action.DOWN)
    row, col = obs["agent"]
    assert row == 1 and col == 0
    assert (
        len(obs["targets"]) == 1
        and obs["targets"][0][0] == 4
        and obs["targets"][0][1] == 4
    )
    assert (
        reward
        == simple_env.reward_matrix[initial_row, initial_col, Action.DOWN, row, col]
    )
    assert terminated == simple_env.terminal_matrix[row, col]
    assert truncated is False
    assert (
        info["prob"]
        == simple_env.transition_matrix[initial_row, initial_col, Action.DOWN, row, col]
    )
