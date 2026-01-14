from copy import deepcopy
from typing import Iterator, Literal

import numpy as np

from edugrid.algorithms.policy import DeterministicPolicy, Policy, StochasticPolicy
from edugrid.envs.grids import EduGridEnv


class PolicyEvaluation:
    """Policy evaluation."""

    def __init__(
        self,
        env: EduGridEnv,
        *,
        mode: Literal["state", "action"] = "state",
        gamma: float = 1.0,
        epsilon: float = 1e-5,
    ) -> None:
        """Initializes the policy evaluation.

        Parameters
        ----------
        env : EduGridEnv
            The environment
        mode : Literal["state", "action"], optional
            State values (V) are used if mode is "state" and action values (Q) if mode is "action". By default "state"
        gamma : float, optional
            Discount factor in [0, 1], by default 1.0
        epsilon : float, optional
            Evaluation is terminated if the value update difference is smaller than epsilon. By default 1e-5

        Raises
        ------
        ValueError
            If an invalid `mode` is specified.
        """
        self._env: EduGridEnv = env.unwrapped
        assert isinstance(self._env, EduGridEnv)

        if mode == "state":
            self._values_shape = (self._env._nrows, self._env._ncols)
        elif mode == "action":
            self._values_shape = (
                self._env._nrows,
                self._env._ncols,
                self._env._num_actions,
            )
        else:
            raise ValueError("invalid 'mode' specified")

        self._mode = mode
        self._gamma = gamma
        self._epsilon = epsilon

    @staticmethod
    def get_next_state_values(
        values: np.ndarray,
        policy_probs: np.ndarray,
        transition_probs: np.ndarray,
        rewards: np.ndarray,
        gamma: float,
    ) -> np.ndarray:
        """Returns the updated state values (V) with respect to previous state values and other parameters.

        Parameters
        ----------
        values : np.ndarray
            Old state values. Shape: (rows, columns)
        policy_probs : np.ndarray
            Policy probabilities of selecting actions given the states. Shape: (rows, columns, actions)
        transition_probs : np.ndarray
            Transition probabilites for reaching next states given previous states and actions. Shape: (rows, columns, actions, rows, columns)
        rewards : np.ndarray
            Rewards for all possible transitions (state, action, next_state). Shape: (rows, columns, actions, rows, columns)
        gamma : float
            Discount factor in [0, 1]

        Returns
        -------
        np.ndarray
            Updated state values (V). Shape: (rows, columns)
        """
        # shape of 'values' is (nrows, ncols)
        assert len(values.shape) == 2
        nrows, ncols = values.shape
        # shape of 'policy_probs' is (nrows, ncols, num_actions)
        assert len(policy_probs.shape) == 3
        num_actions = policy_probs.shape[2]
        assert policy_probs.shape == (nrows, ncols, num_actions)

        # shape of 'transition_probs' is (nrows, ncols, num_actions, nrows, ncols)
        assert transition_probs.shape == (nrows, ncols, num_actions, nrows, ncols)
        # shape of 'rewards' is (nrows, ncols, num_actions, nrows, ncols)
        assert rewards.shape == (nrows, ncols, num_actions, nrows, ncols)

        # shape of 'returns' is (nrows, ncols, num_actions)
        returns = np.sum(transition_probs * rewards, axis=(3, 4)) + gamma * np.sum(
            transition_probs * values, axis=(3, 4)
        )

        # shape of 'next_values' is (nrows, ncols)
        next_values = np.sum(policy_probs * returns, axis=2)
        return next_values

    @staticmethod
    def get_next_action_values(
        values: np.ndarray,
        policy_probs: np.ndarray,
        transition_probs: np.ndarray,
        rewards: np.ndarray,
        gamma: float,
    ) -> np.ndarray:
        """Returns the updated action values (Q) with respect to previous action values and other parameters.

        Parameters
        ----------
        values : np.ndarray
            Old action values. Shape: (rows, columns, actions)
        policy_probs : np.ndarray
            Policy probabilities of selecting actions given the states. Shape: (rows, columns, actions)
        transition_probs : np.ndarray
            Transition probabilites for reaching next states given previous states and actions. Shape: (rows, columns, actions, rows, columns)
        rewards : np.ndarray
            Rewards for all possible transitions (state, action, next_state). Shape: (rows, columns, actions, rows, columns)
        gamma : float
            Discount factor in [0, 1]

        Returns
        -------
        np.ndarray
            Updated action values (Q). Shape: (rows, columns, actions)
        """
        # shape of 'values' is (nrows, ncols, num_actions)
        assert len(values.shape) == 3
        nrows, ncols, num_actions = values.shape
        # shape of 'policy_probs' is (nrows, ncols, num_actions)
        assert policy_probs.shape == (nrows, ncols, num_actions)

        # shape of 'transition_probs' is (nrows, ncols, num_actions, nrows, ncols)
        assert transition_probs.shape == (nrows, ncols, num_actions, nrows, ncols)
        # shape of 'rewards' is (nrows, ncols, num_actions, nrows, ncols)
        assert rewards.shape == (nrows, ncols, num_actions, nrows, ncols)

        # shape of 'interim' is (nrows, ncols)
        interim = np.sum(policy_probs * values, axis=2)

        # shape of 'next_values' is (nrows, ncols, num_actions)
        next_values = np.sum(transition_probs * rewards, axis=(3, 4)) + gamma * np.sum(
            transition_probs * interim, axis=(3, 4)
        )
        return next_values

    def evaluate(
        self, policy: Policy, initial_values: np.ndarray | None = None
    ) -> tuple[int, np.ndarray]:
        """Evaluates the policy by updating the values until the update difference is smaller than an epsilon.

        Parameters
        ----------
        policy : Policy
            The policy to evaluate

        initial_values: np.ndarray | None, optional
            Initial values for the evaluation. If `None`, initial values are set to zero. By default None

        Returns
        -------
        tuple[int, np.ndarray]
            The tuple (number of iterations, new values)
        """
        assert isinstance(policy, Policy)

        delta = float("inf")
        iteration = 0

        if initial_values is not None:
            assert initial_values.shape == self._values_shape
            values = initial_values
        else:
            values = np.zeros(self._values_shape)

        kwargs = dict(
            values=values,
            policy_probs=policy.get_probs(),
            transition_probs=self._env._transition_matrix,
            rewards=self._env._reward_matrix,
            gamma=self._gamma,
        )

        while delta > self._epsilon:
            if self._mode == "state":
                next_values = PolicyEvaluation.get_next_state_values(**kwargs)
            elif self._mode == "action":
                next_values = PolicyEvaluation.get_next_action_values(**kwargs)

            delta = np.max(np.abs(next_values - values))

            # update the values
            values = next_values
            kwargs.update(values=next_values)
            iteration += 1

        return iteration, values

    def iter(
        self, policy: Policy, initial_values: np.ndarray | None = None
    ) -> "PolicyEvaluationIter":
        """Returns an iterator that executes the evaluation stepwise.

        Parameters
        ----------
        policy : Policy
            The policy to evaluate
        initial_values : np.ndarray | None, optional
            Initial values for the evaluation. If `None`, initial values are set to zero. By default None

        Returns
        -------
        PolicyEvaluationIter
            The iterator
        """
        return PolicyEvaluationIter(self, policy=policy, initial_values=initial_values)


class PolicyEvaluationIter(Iterator):
    """An iterator for the policy evaluation."""

    def __init__(
        self,
        policy_evaluation: PolicyEvaluation,
        policy: Policy,
        initial_values: np.ndarray | None = None,
    ):
        """Constructs an iterator for the policy evaluation.

        Parameters
        ----------
        policy_evaluation : PolicyEvaluation
            The context for the policy evaluation
        policy : Policy
            The policy to evaluate
        initial_values : np.ndarray | None, optional
            Initial values for the evaluation. If `None`, initial values are set to zero. By default None
        """
        assert isinstance(policy_evaluation, PolicyEvaluation)
        assert isinstance(policy, Policy)

        self._pe = policy_evaluation
        self._policy = policy

        if initial_values is not None:
            assert initial_values.shape == self._pe._values_shape
            self._values = initial_values
        else:
            self._values = np.zeros(self._pe._values_shape)

        self._kwargs = dict(
            values=self._values,
            policy_probs=self._policy.get_probs(),
            transition_probs=self._pe._env._transition_matrix,
            rewards=self._pe._env._reward_matrix,
            gamma=self._pe._gamma,
        )

    def __next__(self) -> np.ndarray:
        """Executes one update step of the policy evaluation.

        Returns
        -------
        np.ndarray
           The updated values

        Raises
        ------
        StopIteration
            If the evaluation has converged.
        """
        if self._pe._mode == "state":
            next_values = PolicyEvaluation.get_next_state_values(**self._kwargs)
        elif self._pe._mode == "action":
            next_values = PolicyEvaluation.get_next_action_values(**self._kwargs)

        if np.allclose(next_values, self._values, atol=self._pe._epsilon, rtol=0.0):
            raise StopIteration

        # update the values
        self._values = next_values
        self._kwargs.update(values=next_values)

        return next_values.copy()


class PolicyIteration:
    """The base class for policy iteration algorithms."""

    def __init__(
        self,
        env: EduGridEnv,
        *,
        mode: Literal["state", "action"] = "state",
        policy: Policy | Literal["deterministic", "stochastic"] = "deterministic",
        gamma: float = 1.0,
        epsilon: float = 1e-5,
    ) -> None:
        """Initialization for the policy iteration algorithm.

        Parameters
        ----------
        env : EduGridEnv
            The environment
        mode : Literal["state", "action"], optional
            State values (V) are used if mode is "state" and action values (Q) if mode is "action". By default "state"
        policy : Policy | Literal["deterministic", "stochastic"], optional
            Specifies the policy or whether a "deterministic" or "stochastic" default policy is used. By default "deterministic"
        gamma : float, optional
            Discount factor in [0, 1], by default 1.0
        epsilon : float, optional
            Evaluation is terminated if the value update difference is smaller than epsilon. By default 1e-5

        Raises
        ------
        ValueError
            If an invalid `mode` or `policy` is specified.
        """
        self._env: EduGridEnv = env.unwrapped
        self._mode = mode
        self._gamma = gamma

        self._eval = PolicyEvaluation(
            env=self._env,
            mode=self._mode,
            gamma=self._gamma,
            epsilon=epsilon,
        )
        self._values = np.zeros(self._eval._values_shape)
        self._old_policy_array = None

        if isinstance(policy, DeterministicPolicy):
            self._policy_str = "deterministic"
            self._policy = policy
        elif isinstance(policy, StochasticPolicy):
            self._policy_str = "stochastic"
            self._policy = policy
        elif policy == "deterministic":
            self._policy_str = policy
            self._policy = DeterministicPolicy.from_env(env)
        elif policy == "stochastic":
            self._policy_str = policy
            self._policy = StochasticPolicy.from_env(env, init_mode="uniform")
        else:
            raise ValueError("invalid 'policy' specified")

    @property
    def policy(self) -> Policy:
        """
        Returns
        -------
        Policy
            Copy of the current policy
        """
        return deepcopy(self._policy)

    @property
    def values(self) -> np.ndarray:
        """
        Returns
        -------
        np.ndarray
            Copy of the current values
        """
        return deepcopy(self._values)

    def evaluate_policy(
        self, return_values: bool = True
    ) -> tuple[int, np.ndarray] | int:
        """Evaluates the policy by updating the values until the update difference is smaller than an epsilon.

        Parameters
        ----------
        return_values : bool, optional
            Indicates whether the new values shall also be returned, by default True

        Returns
        -------
        tuple[int, np.ndarray] | int
            The tuple (number of iterations, new values) is returned if `return_values` is true, and only the number of iterations otherwise.
        """
        iteration, self._values = self._eval.evaluate(
            policy=self._policy, initial_values=self._values
        )

        if return_values:
            return iteration, self._values.copy()
        else:
            return iteration

    def evaluation_iter(
        self, reset_values: bool = False, reset_policy: bool = False
    ) -> PolicyEvaluationIter:
        """An iterator for the policy evaluation.

        Parameters
        ----------
        reset_values : bool, optional
            Indicates whether the values are initially reset to zero, by default False
        reset_policy : bool, optional
            Indicates whether the policy is initially reset, by default False

        Yields
        ------
        PolicyEvaluationIter
            Iterates over the evaluation steps
        """
        if reset_values:
            self._values = np.zeros_like(self._values)
        if reset_policy:
            self._policy.reset()

        return self._eval.iter(policy=self._policy, initial_values=self._values)

    def improve_policy(self, return_policy: bool = True) -> Policy | None:
        """Improves the policy given the current evaluation.

        Parameters
        ----------
        return_policy : bool, optional
            Indicates whether the improved policy is returned, by default True

        Returns
        -------
        Policy | None
            The improved policy if `return_policy` is true and `None` otherwise
        """
        if self._mode == "state":
            self._policy.update_with_state_values(
                values=self._values,
                transition_probs=self._env._transition_matrix,
                rewards=self._env._reward_matrix,
                gamma=self._gamma,
            )
        elif self._mode == "action":
            self._policy.update_with_action_values(self._values)

        if return_policy:
            return deepcopy(self._policy)

    def _execute_iteration(
        self, return_values: bool, return_policy: bool
    ) -> tuple[int, np.ndarray, Policy]:
        eval_result = self.evaluate_policy(return_values)

        if self._policy_str == "deterministic":
            self._old_policy_array = self._policy._map.copy()
        elif self._policy_str == "stochastic":
            self._old_policy_array = self._policy._probs.copy()

        impr_result = self.improve_policy(return_policy)

        if return_policy:
            return *eval_result, impr_result
        else:
            return eval_result

    def _is_execution_finished(self) -> bool:
        if self._old_policy_array is None:
            return False

        return (
            self._policy_str == "deterministic"
            and np.array_equal(self._policy._map, self._old_policy_array)
        ) or (
            self._policy_str == "stochastic"
            and np.all(np.isclose(self._policy._probs, self._old_policy_array))
        )

    def execute(self) -> tuple[int, np.ndarray, Policy]:
        """Executes the policy iteration by alternating between evaluation and improvement.

        Returns
        -------
        tuple[int, np.ndarray, Policy]
            The tuple (number of iterations, new values, new policy)
        """
        iterations = 0

        while True:
            if self._is_execution_finished():
                # Do one evaluation step so that the values are correct for the final policy
                self.evaluate_policy(return_values=False)
                return iterations, self._values.copy(), deepcopy(self._policy)

            iterations += 1
            self._execute_iteration(return_values=False, return_policy=False)

    def iter(self) -> Iterator:
        """Returns an iterator that executes the policy iteration stepwise.

        Returns
        -------
        Iterator
            The iterator
        """
        return self

    def __iter__(self) -> Iterator:
        """Returns an iterator that executes the policy iteration stepwise.

        Returns
        -------
        Iterator
            The iterator
        """
        return self

    def __next__(self) -> tuple[int, np.ndarray, Policy]:
        """Executes one step of the policy iteration.

        Returns
        -------
        tuple[int, np.ndarray, Policy]
            The tuple (number of iterations, new values, new policy)

        Raises
        ------
        StopIteration
            If the policy iteration has converged.
        """
        if self._is_execution_finished():
            # Do one evaluation step so that the values are correct for the final policy
            self.evaluate_policy(return_values=False)
            raise StopIteration

        result = self._execute_iteration(return_values=True, return_policy=True)
        return result


class ValueIteration:
    """The base class for value iteration algorithms."""

    def __init__(
        self,
        env: EduGridEnv,
        *,
        mode: Literal["state", "action"] = "state",
        gamma: float = 1.0,
        epsilon: float = 1e-5,
    ) -> None:
        """Initialization for the value iteration algorithm.

        Parameters
        ----------
        env : EduGridEnv
            The environment
        mode : Literal["state", "action"], optional
            State values (V) are used if mode is "state" and action values (Q) if mode is "action". By default "state"
        gamma : float, optional
            Discount factor in [0, 1], by default 1.0
        epsilon : float, optional
            Value iteration is terminated if the value update difference is smaller than epsilon. By default 1e-5

        Raises
        ------
        ValueError
            If an invalid `mode` is specified.
        """
        self._env: EduGridEnv = env.unwrapped
        self._mode = mode
        self._gamma = gamma
        self._epsilon = epsilon

        if mode == "state":
            self._values_shape = (self._env._nrows, self._env._ncols)
        elif mode == "action":
            self._values_shape = (
                self._env._nrows,
                self._env._ncols,
                self._env._num_actions,
            )
        else:
            raise ValueError("invalid 'mode' specified")

    @staticmethod
    def get_next_state_values(
        values: np.ndarray,
        transition_probs: np.ndarray,
        rewards: np.ndarray,
        gamma: float,
    ) -> np.ndarray:
        """Returns the updated state values (V) with respect to previous state values and other parameters.

        Parameters
        ----------
        values : np.ndarray
            Old state values. Shape: (rows, columns)
        transition_probs : np.ndarray
            Transition probabilites for reaching next states given previous states and actions. Shape: (rows, columns, actions, rows, columns)
        rewards : np.ndarray
            Rewards for all possible transitions (state, action, next_state). Shape: (rows, columns, actions, rows, columns)
        gamma : float
            Discount factor in [0, 1]

        Returns
        -------
        np.ndarray
            Updated state values (V). Shape: (rows, columns)
        """
        # shape of 'values' is (nrows, ncols)
        assert len(values.shape) == 2
        nrows, ncols = values.shape
        # shape of 'transition_probs' is (nrows, ncols, num_actions, nrows, ncols)
        assert len(transition_probs.shape) == 5
        num_actions = transition_probs.shape[2]
        assert transition_probs.shape == (nrows, ncols, num_actions, nrows, ncols)
        # shape of 'rewards' is (nrows, ncols, num_actions, nrows, ncols)
        assert rewards.shape == (nrows, ncols, num_actions, nrows, ncols)

        # shape of 'returns' is (nrows, ncols, num_actions)
        returns = np.sum(transition_probs * rewards, axis=(3, 4)) + gamma * np.sum(
            transition_probs * values, axis=(3, 4)
        )

        # shape of 'next_values' is (nrows, ncols)
        next_values = np.max(returns, axis=2)
        return next_values

    @staticmethod
    def get_next_action_values(
        values: np.ndarray,
        transition_probs: np.ndarray,
        rewards: np.ndarray,
        gamma: float,
    ) -> np.ndarray:
        """Returns the updated action values (Q) with respect to previous action values and other parameters.

        Parameters
        ----------
        values : np.ndarray
            Old action values. Shape: (rows, columns, actions)
        transition_probs : np.ndarray
            Transition probabilites for reaching next states given previous states and actions. Shape: (rows, columns, actions, rows, columns)
        rewards : np.ndarray
            Rewards for all possible transitions (state, action, next_state). Shape: (rows, columns, actions, rows, columns)
        gamma : float
            Discount factor in [0, 1]

        Returns
        -------
        np.ndarray
            Updated action values (Q). Shape: (rows, columns, actions)
        """
        # shape of 'values' is (nrows, ncols, num_actions)
        assert len(values.shape) == 3
        nrows, ncols, num_actions = values.shape
        # shape of 'transition_probs' is (nrows, ncols, num_actions, nrows, ncols)
        assert transition_probs.shape == (nrows, ncols, num_actions, nrows, ncols)
        # shape of 'rewards' is (nrows, ncols, num_actions, nrows, ncols)
        assert rewards.shape == (nrows, ncols, num_actions, nrows, ncols)

        # shape of 'interim' is (nrows, ncols)
        interim = np.max(values, axis=2)

        # shape of 'next_values' is (nrows, ncols, num_actions)
        next_values = np.sum(transition_probs * rewards, axis=(3, 4)) + gamma * np.sum(
            transition_probs * interim, axis=(3, 4)
        )
        return next_values

    def execute(
        self, initial_values: np.ndarray | None = None
    ) -> tuple[int, np.ndarray]:
        """Executes the value iteration.

        Parameters
        ----------
        initial_values : np.ndarray | None, optional
            Initial values for the value iteration. If `None`, initial values are set to zero. By default None

        Returns
        -------
        tuple[int, np.ndarray]
            The tuple (number of iterations, new values)
        """
        delta = float("inf")
        iteration = 0

        if initial_values is not None:
            assert initial_values.shape == self._values_shape
            values = initial_values
        else:
            values = np.zeros(self._values_shape)

        kwargs = dict(
            values=values,
            transition_probs=self._env._transition_matrix,
            rewards=self._env._reward_matrix,
            gamma=self._gamma,
        )

        while delta > self._epsilon:
            if self._mode == "state":
                next_values = self.get_next_state_values(**kwargs)
            elif self._mode == "action":
                next_values = self.get_next_action_values(**kwargs)

            delta = np.max(np.abs(next_values - values))

            # update the values
            values = next_values
            kwargs.update(values=next_values)
            iteration += 1

        return iteration, values.copy()

    def get_policy(
        self,
        values: np.ndarray,
        type: Literal["deterministic", "stochastic"] = "deterministic",
    ) -> Policy:
        """Returns an optimal policy for the given values.

        Parameters
        ----------
        values: np.ndarray
            The given values
        type : Literal["deterministic", "stochastic"], optional
            Specifies whether a "deterministic" or "stochastic" policy is returned, by default "deterministic"

        Returns
        -------
        Policy
            The optimal policy

        Raises
        ------
        ValueError
            If an invalid policy type is specified.
        """
        if type == "deterministic":
            policy = DeterministicPolicy.from_env(self._env)
        elif type == "stochastic":
            policy = StochasticPolicy.from_env(self._env, init_mode="uniform")
        else:
            raise ValueError("invalid policy type specified")

        if self._mode == "state":
            policy.update_with_state_values(
                values,
                self._env._transition_matrix,
                self._env._reward_matrix,
                self._gamma,
            )
        elif self._mode == "action":
            policy.update_with_action_values(values)

        return policy

    def iter(self, initial_values: np.ndarray | None = None) -> "ValueIterationIter":
        """Returns an iterator that executes the value iteration stepwise.

        Parameters
        ----------
        initial_values : np.ndarray | None, optional
            Initial values for the value iteration. If `None`, initial values are set to zero. By default None

        Returns
        -------
        ValueIterationIter
            The iterator
        """
        return ValueIterationIter(self, initial_values=initial_values)


class ValueIterationIter(Iterator):
    """An iterator for the value iteration."""

    def __init__(
        self, value_iteration: ValueIteration, initial_values: np.ndarray | None = None
    ):
        """Constructs an iterator for the value iteration.

        Parameters
        ----------
        value_iteration : ValueIteration
            The context for the value iteration
        initial_values : np.ndarray | None, optional
            Initial values for the value iteration. If `None`, initial values are set to zero. By default None
        """
        self._vi = value_iteration

        if initial_values is not None:
            assert initial_values.shape == self._vi._values_shape
            self._values = initial_values
        else:
            self._values = np.zeros(self._vi._values_shape)

        self._kwargs = dict(
            values=self._values,
            transition_probs=self._vi._env._transition_matrix,
            rewards=self._vi._env._reward_matrix,
            gamma=self._vi._gamma,
        )

    def __next__(self) -> np.ndarray:
        """Executes one step of the value iteration.

        Returns
        -------
        np.ndarray
            The updated values

        Raises
        ------
        StopIteration
            If the value iteration has converged.
        """

        if self._vi._mode == "state":
            next_values = ValueIteration.get_next_state_values(**self._kwargs)
        elif self._vi._mode == "action":
            next_values = ValueIteration.get_next_action_values(**self._kwargs)

        if np.allclose(next_values, self._values, atol=self._vi._epsilon, rtol=0.0):
            raise StopIteration

        # update the values
        self._values = next_values
        self._kwargs.update(values=next_values)

        return self._values.copy()

    def get_policy(
        self,
        type: Literal["deterministic", "stochastic"] = "deterministic",
    ) -> Policy:
        """Returns an optimal policy for the current values.

        Parameters
        ----------
        type : Literal["deterministic", "stochastic"], optional
            Specifies whether a "deterministic" or "stochastic" policy is returned, by default "deterministic"

        Returns
        -------
        Policy
            The optimal policy

        Raises
        ------
        ValueError
            If an invalid policy type is specified.
        """
        self._vi.get_policy(values=self._values, type=type)
