from copy import deepcopy

import numpy as np
import pytest

from edugrid.algorithms.dynamic_programming import (
    PolicyEvaluation,
    PolicyIteration,
    ValueIteration,
)
from edugrid.algorithms.policy import DeterministicPolicy, StochasticPolicy
from edugrid.envs.grids import Action, EduGridEnv


class TestPolicy:
    def test_create_det_policy(self):
        det_policy = DeterministicPolicy((5, 5), 4)
        assert det_policy.map.shape == (5, 5)
        assert det_policy.get_probs().shape == (5, 5, 4)

    def test_get_det_probs(self, det_policy: DeterministicPolicy):
        probs = det_policy.get_probs()
        expected_probs = np.array(
            [
                [[1, 0, 0, 0], [0, 1, 0, 0], [0, 0, 1, 0], [0, 0, 0, 1], [1, 0, 0, 0]],
                [[0, 0, 0, 1], [0, 0, 1, 0], [0, 1, 0, 0], [1, 0, 0, 0], [0, 1, 0, 0]],
                [[1, 0, 0, 0], [0, 1, 0, 0], [0, 0, 1, 0], [0, 0, 0, 1], [0, 0, 1, 0]],
                [[0, 0, 0, 1], [0, 0, 1, 0], [0, 1, 0, 0], [1, 0, 0, 0], [0, 0, 0, 1]],
                [[0, 1, 0, 0], [0, 0, 1, 0], [0, 0, 0, 1], [0, 1, 0, 0], [0, 1, 0, 0]],
            ]
        )
        assert np.array_equal(probs, expected_probs)

    def test_get_det_map(self, det_policy: DeterministicPolicy):
        expected = np.array(
            [
                [Action.RIGHT, Action.UP, Action.LEFT, Action.DOWN, Action.RIGHT],
                [Action.DOWN, Action.LEFT, Action.UP, Action.RIGHT, Action.UP],
                [Action.RIGHT, Action.UP, Action.LEFT, Action.DOWN, Action.LEFT],
                [Action.DOWN, Action.LEFT, Action.UP, Action.RIGHT, Action.DOWN],
                [Action.UP, Action.LEFT, Action.DOWN, Action.UP, Action.UP],
            ]
        )
        assert np.all(det_policy.map == expected)

    def test_set_det_map_1(self, det_policy: DeterministicPolicy):
        new_map = np.full((5, 5), Action.DOWN)
        det_policy.map = new_map
        assert np.all(det_policy.map == new_map)

    def test_set_det_map_2(self, det_policy: DeterministicPolicy):
        with pytest.raises(AssertionError):
            det_policy.map = 1

    def test_set_det_map_3(self, det_policy: DeterministicPolicy):
        with pytest.raises(AssertionError):
            det_policy.map = np.full((5, 5), 100)

    def test_set_det_map_4(self, det_policy: DeterministicPolicy):
        with pytest.raises(AssertionError):
            det_policy.map = np.full((5, 5), 1.5)

    def test_setitem_det_map_1(self, det_policy: DeterministicPolicy):
        det_policy.map[0, 0] = Action.DOWN
        expected = np.array(
            [
                [Action.DOWN, Action.UP, Action.LEFT, Action.DOWN, Action.RIGHT],
                [Action.DOWN, Action.LEFT, Action.UP, Action.RIGHT, Action.UP],
                [Action.RIGHT, Action.UP, Action.LEFT, Action.DOWN, Action.LEFT],
                [Action.DOWN, Action.LEFT, Action.UP, Action.RIGHT, Action.DOWN],
                [Action.UP, Action.LEFT, Action.DOWN, Action.UP, Action.UP],
            ]
        )
        assert np.all(det_policy.map == expected)

    def test_setitem_det_map_2(self, det_policy: DeterministicPolicy):
        with pytest.raises(ValueError):
            det_policy.map[0] = np.full((5, 5), 1)

    def test_setitem_det_map_3(self, det_policy: DeterministicPolicy):
        with pytest.raises(AssertionError):
            det_policy.map[0] = np.full((5,), 100)

    def test_create_stoch_policy(self):
        stoch_policy = StochasticPolicy((5, 5), 4)
        assert stoch_policy.probs.shape == (5, 5, 4)
        assert stoch_policy.get_probs().shape == (5, 5, 4)

    def test_get_stoch_probs(self, stoch_policy: StochasticPolicy):
        probs = stoch_policy.get_probs()
        assert np.array_equal(probs, np.ones((5, 5, 4)) / 4)

    def test_set_stoch_probs_1(self, stoch_policy: StochasticPolicy):
        new_probs = np.zeros((5, 5, 4))
        new_probs[:, :, 0] = 1.0
        stoch_policy.probs = new_probs
        assert np.allclose(stoch_policy.probs, new_probs)

    def test_set_stoch_probs_2(self, stoch_policy: StochasticPolicy):
        with pytest.raises(AssertionError):
            stoch_policy.probs = 1

    def test_set_stoch_probs_3(self, stoch_policy: StochasticPolicy):
        new_probs = np.zeros((5, 5, 4))
        new_probs[:, :, 0] = 2.0
        with pytest.raises(AssertionError):
            stoch_policy.probs = new_probs

    def test_setitem_stoch_probs_1(self, stoch_policy: StochasticPolicy):
        expected = np.ones((5, 5, 4)) / 4
        new_probs = np.array([1, 0, 0, 0])
        expected[:, :] = new_probs

        stoch_policy.probs[:, :] = new_probs
        assert np.allclose(stoch_policy.probs, expected)

    def test_setitem_stoch_probs_2(self, stoch_policy: StochasticPolicy):
        new_probs = np.zeros((5, 5, 4))
        new_probs[:, :, 0] = 1.0
        with pytest.raises(ValueError):
            stoch_policy.probs[0] = new_probs

    def test_setitem_stoch_probs_3(self, stoch_policy: StochasticPolicy):
        new_probs = np.array([2, 0, 0, 0])
        with pytest.raises(AssertionError):
            stoch_policy.probs[:, :] = new_probs

    def test_setitem_stoch_probs_4(self, stoch_policy: StochasticPolicy):
        expected = np.ones((5, 5, 4)) / 4
        stoch_policy.probs[:] = 0.25
        assert np.allclose(stoch_policy.probs, expected)


class TestPolicyEvaluation:
    def test_next_state_values(
        self,
        det_policy: DeterministicPolicy,
        simple_transitions: np.ndarray,
        simple_rewards: np.ndarray,
    ):
        # shape of 'values': (nrows, ncols)
        values = np.ones((5, 5))
        values[4, 4] = 0
        policy_probs = det_policy.get_probs()
        gamma = 0.9

        next_values = PolicyEvaluation.get_next_state_values(
            values, policy_probs, simple_transitions, simple_rewards, gamma
        )
        expected = -0.1 * np.ones((5, 5))
        expected[3, 4] = 10
        expected[4, 4] = 0

        assert np.allclose(next_values, expected)

    def test_next_action_values(
        self,
        det_policy: DeterministicPolicy,
        simple_transitions: np.ndarray,
        simple_rewards: np.ndarray,
    ):
        # shape of 'values': (nrows, ncols, num_actions)
        values = np.ones((5, 5, 4))
        values[4, 4, :] = 0
        policy_probs = det_policy.get_probs()
        gamma = 0.9

        next_values = PolicyEvaluation.get_next_action_values(
            values, policy_probs, simple_transitions, simple_rewards, gamma
        )
        expected = -0.1 * np.ones((5, 5, 4))
        expected[3, 4, Action.DOWN] = 10
        expected[4, 3, Action.RIGHT] = 10
        expected[4, 4, :] = 0

        assert np.allclose(next_values, expected)

    def test_evaluation_state_det(
        self, lecture_env: EduGridEnv, lecture_det_policy: DeterministicPolicy
    ):
        pe = PolicyEvaluation(lecture_env, mode="state")
        _, values = pe.evaluate(lecture_det_policy)
        assert values.shape == (4, 4)

        expected = np.array(
            [
                [-0, -1, -2, -3],
                [-1, -2, -3, -2],
                [-2, -3, -2, -1],
                [-3, -2, -1, -0],
            ]
        )
        assert np.allclose(values, expected)

    def test_evaluation_state_stoch(
        self, lecture_env: EduGridEnv, lecture_uniform_stoch_policy: StochasticPolicy
    ):
        pe = PolicyEvaluation(lecture_env, mode="state")
        _, values = pe.evaluate(lecture_uniform_stoch_policy)
        assert values.shape == (4, 4)

        expected = np.array(
            [
                [0, -14, -20, -22],
                [-14, -18, -20, -20],
                [-20, -20, -18, -14],
                [-22, -20, -14, 0],
            ]
        )
        assert np.allclose(values, expected)

    def test_evaluation_action_det(
        self, lecture_env: EduGridEnv, lecture_det_policy: DeterministicPolicy
    ):
        pe = PolicyEvaluation(lecture_env, mode="action")
        _, values = pe.evaluate(lecture_det_policy)
        assert values.shape == (4, 4, 4)

        expected = np.array(
            [
                [
                    [-0, -0, -0, -0],
                    [-3, -2, -1, -3],
                    [-4, -3, -2, -4],
                    [-4, -4, -3, -3],
                ],
                [
                    [-3, -1, -2, -3],
                    [-4, -2, -2, -4],
                    [-3, -3, -3, -3],
                    [-3, -4, -4, -2],
                ],
                [
                    [-4, -2, -3, -4],
                    [-3, -3, -3, -3],
                    [-2, -4, -4, -2],
                    [-2, -3, -3, -1],
                ],
                [
                    [-3, -3, -4, -4],
                    [-2, -4, -4, -3],
                    [-1, -3, -3, -2],
                    [-0, -0, -0, -0],
                ],
            ]
        )
        assert np.allclose(values, expected)

    def test_evaluation_action_stoch(
        self,
        lecture_env: EduGridEnv,
        lecture_uniform_stoch_policy: StochasticPolicy,
        lecture_action_values: np.ndarray,
    ):
        pe = PolicyEvaluation(lecture_env, mode="action")
        _, values = pe.evaluate(lecture_uniform_stoch_policy)
        assert values.shape == (4, 4, 4)

        assert np.allclose(values, lecture_action_values)

    def test_evaluation_iter_state_stoch(
        self, lecture_env: EduGridEnv, lecture_uniform_stoch_policy: StochasticPolicy
    ):
        pe = PolicyEvaluation(lecture_env, mode="state")
        iter = pe.iter(lecture_uniform_stoch_policy)

        # 1. iteration
        values = next(iter)
        assert values.shape == (4, 4)
        expected = -np.ones((4, 4))
        expected[0, 0] = 0
        expected[3, 3] = 0
        assert np.allclose(values, expected)

        # 2. iteration
        values = next(iter)
        assert values.shape == (4, 4)
        expected = np.array(
            [
                [0, -1.75, -2, -2],
                [-1.75, -2, -2, -2],
                [-2, -2, -2, -1.75],
                [-2, -2, -1.75, 0],
            ]
        )
        assert np.allclose(values, expected)

    def test_evaluation_iter_all_state_stoch(
        self, lecture_env: EduGridEnv, lecture_uniform_stoch_policy: StochasticPolicy
    ):
        pe = PolicyEvaluation(lecture_env, mode="state")

        for values in pe.iter(lecture_uniform_stoch_policy):
            pass

        expected = np.array(
            [
                [0, -14, -20, -22],
                [-14, -18, -20, -20],
                [-20, -20, -18, -14],
                [-22, -20, -14, 0],
            ]
        )
        assert np.allclose(values, expected)


class TestPolicyIteration:

    def test_evaluation_state_det(
        self, lecture_env: EduGridEnv, lecture_det_policy: DeterministicPolicy
    ):
        pi = PolicyIteration(lecture_env, mode="state", policy="deterministic")
        pi._policy = lecture_det_policy
        _, values = pi.evaluate_policy()
        assert values.shape == (4, 4)

        expected = np.array(
            [
                [-0, -1, -2, -3],
                [-1, -2, -3, -2],
                [-2, -3, -2, -1],
                [-3, -2, -1, -0],
            ]
        )
        assert np.allclose(values, expected)

    def test_evaluation_state_stoch(self, lecture_env: EduGridEnv):
        pi = PolicyIteration(lecture_env, mode="state", policy="stochastic")
        _, values = pi.evaluate_policy()
        assert values.shape == (4, 4)

        expected = np.array(
            [
                [0, -14, -20, -22],
                [-14, -18, -20, -20],
                [-20, -20, -18, -14],
                [-22, -20, -14, 0],
            ]
        )
        assert np.allclose(values, expected)

    def test_evaluation_action_det(
        self, lecture_env: EduGridEnv, lecture_det_policy: DeterministicPolicy
    ):
        pi = PolicyIteration(lecture_env, mode="action", policy="deterministic")
        pi._policy = lecture_det_policy
        _, values = pi.evaluate_policy()
        assert values.shape == (4, 4, 4)

        expected = np.array(
            [
                [
                    [-0, -0, -0, -0],
                    [-3, -2, -1, -3],
                    [-4, -3, -2, -4],
                    [-4, -4, -3, -3],
                ],
                [
                    [-3, -1, -2, -3],
                    [-4, -2, -2, -4],
                    [-3, -3, -3, -3],
                    [-3, -4, -4, -2],
                ],
                [
                    [-4, -2, -3, -4],
                    [-3, -3, -3, -3],
                    [-2, -4, -4, -2],
                    [-2, -3, -3, -1],
                ],
                [
                    [-3, -3, -4, -4],
                    [-2, -4, -4, -3],
                    [-1, -3, -3, -2],
                    [-0, -0, -0, -0],
                ],
            ]
        )
        assert np.allclose(values, expected)

    def test_evaluation_action_stoch(
        self, lecture_env: EduGridEnv, lecture_action_values: np.ndarray
    ):
        pi = PolicyIteration(lecture_env, mode="action", policy="stochastic")
        _, values = pi.evaluate_policy()
        assert values.shape == (4, 4, 4)

        assert np.allclose(values, lecture_action_values)

    def test_improvement_state_det(
        self, lecture_env: EduGridEnv, lecture_det_policy: DeterministicPolicy
    ):
        pi = PolicyIteration(lecture_env, mode="state", policy="deterministic")
        pi._values = np.array(
            [
                [0, -14, -20, -22],
                [-14, -18, -20, -20],
                [-20, -20, -18, -14],
                [-22, -20, -14, 0],
            ]
        )
        policy = pi.improve_policy()
        assert np.array_equal(policy._map, lecture_det_policy._map)

    def test_improvement_state_stoch(
        self, lecture_env: EduGridEnv, lecture_stoch_policy: StochasticPolicy
    ):
        pi = PolicyIteration(lecture_env, mode="state", policy="stochastic")
        pi._values = np.array(
            [
                [0, -14, -20, -22],
                [-14, -18, -20, -20],
                [-20, -20, -18, -14],
                [-22, -20, -14, 0],
            ]
        )
        policy = pi.improve_policy()
        expected = lecture_stoch_policy.get_probs()
        assert np.allclose(policy._probs, expected)

    def test_improvement_action_det(
        self,
        lecture_env: EduGridEnv,
        lecture_action_values: np.ndarray,
        lecture_det_policy: DeterministicPolicy,
    ):
        pi = PolicyIteration(lecture_env, mode="action", policy="deterministic")
        pi._values = lecture_action_values
        policy = pi.improve_policy()
        assert np.array_equal(policy._map, lecture_det_policy._map)

    def test_improvement_action_stoch(
        self,
        lecture_env: EduGridEnv,
        lecture_action_values: np.ndarray,
        lecture_stoch_policy: StochasticPolicy,
    ):
        pi = PolicyIteration(lecture_env, mode="action", policy="stochastic")
        pi._values = lecture_action_values
        policy = pi.improve_policy()
        expected = lecture_stoch_policy.get_probs()
        assert np.allclose(policy._probs, expected)

    def test_execution_state_det(
        self,
        lecture_env: EduGridEnv,
        lecture_det_policy: DeterministicPolicy,
        lecture_opt_state_values: np.ndarray,
    ):
        pi = PolicyIteration(lecture_env, mode="state", policy="deterministic")
        pi._policy = lecture_det_policy
        _, values, policy = pi.execute()

        assert values.shape == (4, 4)
        assert np.allclose(values, lecture_opt_state_values)
        assert np.array_equal(policy._map, lecture_det_policy._map)

    def test_execution_state_stoch(
        self,
        lecture_env: EduGridEnv,
        lecture_opt_stoch_policy: StochasticPolicy,
        lecture_opt_state_values: np.ndarray,
    ):
        pi = PolicyIteration(lecture_env, mode="state", policy="stochastic")
        _, values, policy = pi.execute()

        assert values.shape == (4, 4)
        assert np.allclose(values, lecture_opt_state_values)

        expected_probs = lecture_opt_stoch_policy.get_probs()
        assert np.allclose(policy._probs, expected_probs)

    def test_execution_action_det(
        self,
        lecture_env: EduGridEnv,
        lecture_det_policy: DeterministicPolicy,
        lecture_opt_action_values: np.ndarray,
        lecture_opt_det_policy: DeterministicPolicy,
    ):
        pi = PolicyIteration(lecture_env, mode="action", policy="deterministic")
        pi._policy = deepcopy(lecture_det_policy)
        _, values, policy = pi.execute()

        assert values.shape == (4, 4, 4)
        assert np.allclose(values, lecture_opt_action_values)
        assert np.array_equal(policy._map, lecture_opt_det_policy._map)

    def test_execution_action_stoch(
        self,
        lecture_env: EduGridEnv,
        lecture_opt_action_values: np.ndarray,
        lecture_opt_stoch_policy: StochasticPolicy,
    ):
        pi = PolicyIteration(lecture_env, mode="action", policy="stochastic")
        _, values, policy = pi.execute()

        assert values.shape == (4, 4, 4)
        assert np.allclose(values, lecture_opt_action_values)

        expected_probs = lecture_opt_stoch_policy.get_probs()
        assert np.allclose(policy._probs, expected_probs)

    def test_evaluation_iter_state_stoch(self, lecture_env: EduGridEnv):
        pi = PolicyIteration(lecture_env, mode="state", policy="stochastic")
        iter = pi.evaluation_iter()

        # 1. iteration
        values = next(iter)
        assert values.shape == (4, 4)
        expected = -np.ones((4, 4))
        expected[0, 0] = 0
        expected[3, 3] = 0
        assert np.allclose(values, expected)

        # 2. iteration
        values = next(iter)
        assert values.shape == (4, 4)
        expected = np.array(
            [
                [0, -1.75, -2, -2],
                [-1.75, -2, -2, -2],
                [-2, -2, -2, -1.75],
                [-2, -2, -1.75, 0],
            ]
        )
        assert np.allclose(values, expected)

    def test_evaluation_iter_all_state_stoch(self, lecture_env: EduGridEnv):
        pi = PolicyIteration(lecture_env, mode="state", policy="stochastic")

        for values in pi.evaluation_iter():
            pass

        expected = np.array(
            [
                [0, -14, -20, -22],
                [-14, -18, -20, -20],
                [-20, -20, -18, -14],
                [-22, -20, -14, 0],
            ]
        )
        assert np.allclose(values, expected)

    def test_execution_iter_all_state_stoch(
        self,
        lecture_env: EduGridEnv,
        lecture_opt_state_values: np.ndarray,
        lecture_opt_stoch_policy: StochasticPolicy,
    ):
        pi = PolicyIteration(lecture_env, mode="state", policy="stochastic")

        for _, values, policy in pi:
            pass

        assert values.shape == (4, 4)
        assert np.allclose(values, lecture_opt_state_values)

        expected_probs = lecture_opt_stoch_policy.get_probs()
        assert np.allclose(policy._probs, expected_probs)


class TestValueIteration:
    def test_next_state_values(
        self,
        simple_transitions: np.ndarray,
        simple_rewards: np.ndarray,
    ):
        # shape of 'values': (nrows, ncols)
        values = np.ones((5, 5))
        values[4, 4] = 0
        gamma = 0.9

        next_values = ValueIteration.get_next_state_values(
            values, simple_transitions, simple_rewards, gamma
        )
        expected = -0.1 * np.ones((5, 5))
        expected[3, 4] = 10
        expected[4, 3] = 10
        expected[4, 4] = 0
        assert np.allclose(next_values, expected)

    def test_next_action_values(
        self,
        simple_transitions: np.ndarray,
        simple_rewards: np.ndarray,
    ):
        # shape of 'values': (nrows, ncols, num_actions)
        values = np.ones((5, 5, 4))
        values[4, 4, :] = 0
        gamma = 0.9

        next_values = ValueIteration.get_next_action_values(
            values, simple_transitions, simple_rewards, gamma
        )
        expected = -0.1 * np.ones((5, 5, 4))
        expected[3, 4, Action.DOWN] = 10
        expected[4, 3, Action.RIGHT] = 10
        expected[4, 4, :] = 0
        assert np.allclose(next_values, expected)

    def test_execution_state(
        self, lecture_env: EduGridEnv, lecture_opt_state_values: np.ndarray
    ):
        vi = ValueIteration(lecture_env, mode="state")
        _, values = vi.execute()
        assert values.shape == (4, 4)
        assert np.allclose(values, lecture_opt_state_values)

    def test_execution_action(
        self, lecture_env: EduGridEnv, lecture_opt_action_values: np.ndarray
    ):
        vi = ValueIteration(lecture_env, mode="action")
        _, values = vi.execute()
        assert values.shape == (4, 4, 4)
        assert np.allclose(values, lecture_opt_action_values)

    def test_get_det_policy_from_state(
        self, lecture_env: EduGridEnv, lecture_opt_det_policy: DeterministicPolicy
    ):
        vi = ValueIteration(lecture_env, mode="state")
        _, values = vi.execute()
        policy = vi.get_policy(values, type="deterministic")
        assert np.array_equal(policy._map, lecture_opt_det_policy._map)

    def test_get_det_policy_from_action(
        self, lecture_env: EduGridEnv, lecture_opt_det_policy: DeterministicPolicy
    ):
        vi = ValueIteration(lecture_env, mode="action")
        _, values = vi.execute()
        policy = vi.get_policy(values, type="deterministic")
        assert np.array_equal(policy._map, lecture_opt_det_policy._map)

    def test_get_stoch_policy_from_state(
        self, lecture_env: EduGridEnv, lecture_opt_stoch_policy: StochasticPolicy
    ):
        vi = ValueIteration(lecture_env, mode="state")
        _, values = vi.execute()
        policy = vi.get_policy(values, type="stochastic")
        assert np.allclose(policy._probs, lecture_opt_stoch_policy.get_probs())

    def test_get_stoch_policy_from_action(
        self, lecture_env: EduGridEnv, lecture_opt_stoch_policy: StochasticPolicy
    ):
        vi = ValueIteration(lecture_env, mode="action")
        _, values = vi.execute()
        policy = vi.get_policy(values, type="stochastic")
        assert np.allclose(policy._probs, lecture_opt_stoch_policy.get_probs())

    def test_iter_state(self, lecture_env: EduGridEnv):
        vi = ValueIteration(lecture_env, mode="state")
        iterator = vi.iter()

        # 1. iteration
        values = next(iterator)
        assert values.shape == (4, 4)
        expected = -np.ones((4, 4))
        expected[0, 0] = 0
        expected[3, 3] = 0
        assert np.allclose(values, expected)

        # 2. iteration
        values = next(iterator)
        assert values.shape == (4, 4)
        expected = np.array(
            [
                [-0, -1, -2, -2],
                [-1, -2, -2, -2],
                [-2, -2, -2, -1],
                [-2, -2, -1, -0],
            ]
        )
        assert np.allclose(values, expected)

    def test_iter_action(self, lecture_env: EduGridEnv):
        vi = ValueIteration(lecture_env, mode="action")
        iterator = vi.iter()

        # 1. iteration
        values = next(iterator)
        assert values.shape == (4, 4, 4)
        expected = -np.ones((4, 4, 4))
        expected[0, 0, :] = 0
        expected[3, 3, :] = 0
        assert np.allclose(values, expected)

        # 2. iteration
        values = next(iterator)
        assert values.shape == (4, 4, 4)
        expected = -2 * np.ones((4, 4, 4))
        expected[0, 1, Action.LEFT] = -1
        expected[1, 0, Action.UP] = -1
        expected[2, 3, Action.DOWN] = -1
        expected[3, 2, Action.RIGHT] = -1
        expected[0, 0, :] = 0
        expected[3, 3, :] = 0
        assert np.allclose(values, expected)

    def test_iter_all_state(
        self, lecture_env: EduGridEnv, lecture_opt_state_values: np.ndarray
    ):
        vi = ValueIteration(lecture_env, mode="state")

        for values in vi.iter():
            pass

        assert values.shape == (4, 4)
        assert np.allclose(values, lecture_opt_state_values)

    def test_iter_all_action(
        self, lecture_env: EduGridEnv, lecture_opt_action_values: np.ndarray
    ):
        vi = ValueIteration(lecture_env, mode="action")

        for values in vi.iter():
            pass

        assert values.shape == (4, 4, 4)
        assert np.allclose(values, lecture_opt_action_values)
