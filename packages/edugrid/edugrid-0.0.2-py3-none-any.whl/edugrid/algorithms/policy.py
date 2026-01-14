from abc import ABC, abstractmethod
from typing import Any, Literal

import numpy as np

from edugrid.envs.grids import EduGridEnv
from edugrid.utils import ArrayDescriptor, ArrayWrapper


class Policy(ABC):
    """Abstract base class for policies."""

    def __init__(self, states_shape: tuple[int, int], num_actions: int) -> None:
        """Initializes the policy.

        Parameters
        ----------
        states_shape : tuple[int, int]
            The tuple (number of rows, number of columns)
        num_actions : int
            The number of actions
        """
        self._nrows, self._ncols = states_shape
        self._num_actions = num_actions
        self._rng = np.random.default_rng()

    @abstractmethod
    def reset(self) -> None:
        """Resets the policy."""
        pass

    @abstractmethod
    def __call__(self, state: tuple[int, int]) -> int | np.ndarray:
        """Returns the action or action probabilities for a state.

        Parameters
        ----------
        state : tuple[int, int]
            The tuple (row, column)

        Returns
        -------
        int | np.ndarray
            Action or action probabilities
        """
        pass

    @abstractmethod
    def get_probs(self) -> np.ndarray:
        """Returns the action probabilities for all states.

        Returns
        -------
        np.ndarray
            The action probabilities
        """
        pass

    @abstractmethod
    def update_with_state_values(
        self,
        values: np.ndarray,
        transition_probs: np.ndarray,
        rewards: np.ndarray,
        gamma: float,
    ) -> None:
        """Updates the policy according to state values and other parameters.

        Parameters
        ----------
        values : np.ndarray
            The state values (V). Shape: (rows, columns)
        transition_probs : np.ndarray
            Transition probabilites for reaching next states given previous states and actions. Shape: (rows, columns, actions, rows, columns)
        rewards : np.ndarray
            Rewards for all possible transitions (state, action, next_state). Shape: (rows, columns, actions, rows, columns)
        gamma : float
            Discount factor in [0, 1]
        """
        pass

    def _assert_for_state_values(
        self,
        values: np.ndarray,
        transition_probs: np.ndarray,
        rewards: np.ndarray,
        gamma: float,
    ) -> None:
        # shape of 'values' is (nrows, ncols)
        assert values.shape == (self._nrows, self._ncols)
        # shape of 'transition_probs' is (nrows, ncols, num_actions, nrows, ncols)
        assert transition_probs.shape == (
            self._nrows,
            self._ncols,
            self._num_actions,
            self._nrows,
            self._ncols,
        )
        # shape of 'rewards' is (nrows, ncols, num_actions, nrows, ncols)
        assert rewards.shape == transition_probs.shape

    @abstractmethod
    def update_with_action_values(self, values: np.ndarray) -> None:
        """Updates the policy according to action values.

        Parameters
        ----------
        values : np.ndarray
            The action values (Q). Shape: (rows, columns, actions)
        """
        pass

    def _assert_for_action_values(self, values: np.ndarray) -> None:
        # shape of 'values' is (nrows, ncols, num_actions)
        assert values.shape == (self._nrows, self._ncols, self._num_actions)


class DeterministicPolicy(Policy):
    def __init__(self, states_shape: tuple[int, int], num_actions: int) -> None:
        super().__init__(states_shape, num_actions)
        self._map = self._rng.integers(0, num_actions, size=states_shape)
        self._map_wrapper = ArrayWrapper(
            self._map,
            val_set=self._validate_set_map,
            val_setitem=self._validate_setitem_map,
        )

    @classmethod
    def from_env(cls, env: EduGridEnv) -> "DeterministicPolicy":
        """Returns a deterministic policy suitable for the environment.

        Parameters
        ----------
        env : EduGridEnv
            The environment

        Returns
        -------
        DeterministicPolicy
            The deterministic policy
        """
        env: EduGridEnv = env.unwrapped
        return cls((env._nrows, env._ncols), env._num_actions)

    map = ArrayDescriptor()
    """Numpy array with shape `(rows, columns)` that specifies the actions for all states."""

    def reset(self) -> None:
        self._map = np.random.randint(
            0, self._num_actions, size=(self._nrows, self._ncols)
        )

    def __call__(self, state: tuple[int, int]) -> int:
        return self._map[state]

    def get_probs(self) -> np.ndarray:
        return self.argmax_to_probs(self._map, self._num_actions)

    def update_with_state_values(
        self,
        values: np.ndarray,
        transition_probs: np.ndarray,
        rewards: np.ndarray,
        gamma: float,
    ) -> None:
        self._assert_for_state_values(values, transition_probs, rewards, gamma)

        # shape of 'returns' is (nrows, ncols, num_actions)
        returns = np.sum(transition_probs * rewards, axis=(3, 4)) + gamma * np.sum(
            transition_probs * values, axis=(3, 4)
        )
        # greedy update (in-place)
        np.argmax(returns, axis=2, out=self._map)

    def update_with_action_values(self, values: np.ndarray) -> None:
        self._assert_for_action_values(values)

        # greedy update (in-place)
        np.argmax(values, axis=2, out=self._map)

    def __repr__(self) -> str:
        return f"DeterministicPolicy(map=\n{self._map}\n)"

    @staticmethod
    def argmax_to_probs(
        argmax: np.ndarray, num_actions: int, out: np.ndarray | None = None
    ) -> np.ndarray | None:
        """Converts argmax indices to probabilities.

        Parameters
        ----------
        argmax : np.ndarray
            Argmax indices with shape of (rows, columns)
        num_actions : int
            Number of actions
        out : np.ndarray | None, optional
            If provided, the result will be inserted into this array. Otherwise, the result is returned. By default None

        Returns
        -------
        np.ndarray | None
            The probabilities or `None` if `out` is provided

        Raises
        ------
        ValueError
            If `out` has not the expected shape.
        """
        offsets = np.arange(argmax.size) * num_actions
        ind = argmax.ravel() + offsets

        if out is None:
            probs = np.zeros((*argmax.shape, num_actions))
            np.put(probs, ind, 1.0)
            return probs
        else:
            expected_shape = (*argmax.shape, num_actions)
            if out.shape != expected_shape:
                raise ValueError(
                    f"'out' has shape {out.shape} but must have {expected_shape}"
                )
            out.fill(0.0)
            np.put(out, ind, 1.0)

    def _validate_set_map(self, values: np.ndarray) -> None:
        assert isinstance(values, np.ndarray), "'map' must be a numpy array"
        assert (
            values.shape == self._map.shape
        ), f"'map' has shape {values.shape} but should have {self._map.shape}"
        assert np.issubdtype(
            values.dtype, np.integer
        ), f"'dtype' of 'map' is {values.dtype} but must be integer"
        assert np.all(values >= 0) and np.all(
            values < self._num_actions
        ), f"All values of `map` must be actions, i.e., >=0 and <{self._num_actions}"

    def _validate_setitem_map(self, key: Any, value: np.ndarray) -> None:
        assert np.all(value >= 0) and np.all(
            value < self._num_actions
        ), f"All values of `map` must be actions, i.e., >=0 and <{self._num_actions}"


class StochasticPolicy(Policy):
    def __init__(
        self,
        states_shape: tuple[int, int],
        num_actions: int,
        init_mode: Literal["random", "uniform"] = "uniform",
    ) -> None:
        """Initializes the policy.

        Parameters
        ----------
        states_shape : tuple[int, int]
            The tuple (number of rows, number of columns)
        num_actions : int
            The number of actions
        init_mode : Literal["random", "uniform"], optional
            Indicates whether the probabilities are initialized as "random" or "uniform". By default "uniform"
        """
        super().__init__(states_shape, num_actions)
        self._init_mode = init_mode
        self._init_probs(init_mode)

    def _init_probs(self, init_mode: Literal["random", "uniform"]) -> None:
        if init_mode == "random":
            r = self._rng.random((self._nrows, self._ncols, self._num_actions))
            self._probs = r / np.sum(r, axis=2, keepdims=True)
        elif init_mode == "uniform":
            self._probs = (
                np.ones((self._nrows, self._ncols, self._num_actions))
                / self._num_actions
            )
        else:
            raise ValueError(f"'{init_mode}' is an invalid 'init_mode'")

        self._probs_wrapper = ArrayWrapper(
            self._probs,
            val_set=self._validate_set_probs,
            val_setitem=self._validate_setitem_probs,
        )

    @classmethod
    def from_env(
        cls, env: EduGridEnv, init_mode: Literal["random", "uniform"] = "uniform"
    ) -> "StochasticPolicy":
        """Returns a stochastic policy suitable for the environment.

        Parameters
        ----------
        env : EduGridEnv
            The environment
        init_mode : Literal["random", "uniform"], optional
            Indicates whether the probabilities are initialized as "random" or "uniform". By default "uniform"

        Returns
        -------
        StochasticPolicy
            The stochastic policy
        """
        env: EduGridEnv = env.unwrapped
        return cls((env._nrows, env._ncols), env._num_actions, init_mode)

    probs = ArrayDescriptor()
    """Numpy array with shape `(rows, columns, actions)` that specifies the probabilities of choosing actions given states."""

    def get_probs(self) -> np.ndarray:
        return self._probs.copy()

    def reset(self) -> None:
        self._init_probs(self._init_mode)

    def __call__(self, state: tuple[int, int]) -> int:
        return self._rng.choice(self._num_actions, p=self._probs[state])

    def update_with_state_values(
        self,
        values: np.ndarray,
        transition_probs: np.ndarray,
        rewards: np.ndarray,
        gamma: float,
    ) -> None:
        self._assert_for_state_values(values, transition_probs, rewards, gamma)

        # shape of 'returns' is (nrows, ncols, num_actions)
        returns = np.sum(
            np.multiply(transition_probs, rewards), axis=(3, 4)
        ) + gamma * np.sum(np.multiply(transition_probs, values), axis=(3, 4))
        max = np.max(returns, axis=2, keepdims=True)
        argmax_mask = np.isclose(returns, max)
        # greedy update (in-place)
        self.argmax_to_probs(argmax_mask, out=self._probs)

    def update_with_action_values(self, values: np.ndarray) -> None:
        self._assert_for_action_values(values)

        max = np.max(values, axis=2, keepdims=True)
        argmax_mask = np.isclose(values, max)
        # greedy update (in-place)
        self.argmax_to_probs(argmax_mask, out=self._probs)

    def __repr__(self) -> str:
        return f"StochasticPolicy(probs=\n{self._probs}\n)"

    @staticmethod
    def argmax_to_probs(
        argmax_mask: np.ndarray, out: np.ndarray | None = None
    ) -> np.ndarray | None:
        """Converts an argmax mask to probabilities.

        Parameters
        ----------
        argmax : np.ndarray
            Argmax mask with shape of (rows, columns, actions)
        out : np.ndarray | None, optional
            If provided, the result will be inserted into this array. Otherwise, the result is returned. By default None

        Returns
        -------
        np.ndarray | None
            The probabilities or `None` if `out` is provided

        Raises
        ------
        ValueError
            If `out` has not the expected shape.
        """
        num = np.count_nonzero(argmax_mask, axis=2, keepdims=True)
        p = 1.0 / num

        if out is None:
            probs = np.zeros_like(argmax_mask)
            np.copyto(probs, p, where=argmax_mask)
            return probs
        else:
            expected_shape = argmax_mask.shape
            if out.shape != expected_shape:
                raise ValueError(
                    f"'out' has shape {out.shape} but must have {expected_shape}"
                )
            out.fill(0.0)
            np.copyto(out, p, where=argmax_mask)

    def _validate_set_probs(self, values: np.ndarray) -> None:
        assert isinstance(values, np.ndarray), "'probs' must be a numpy array"
        assert (
            values.shape == self._probs.shape
        ), f"'probs' has shape {values.shape} but should have {self._probs.shape}"
        assert (
            values.dtype.kind == "f"
        ), f"'dtype' of 'probs' is {values.dtype} but must be floating-point"
        assert np.all(values >= 0) and np.all(
            values <= 1
        ), "All probabilities of 'probs' must be in [0, 1]"
        assert np.allclose(
            np.sum(values, axis=-1), 1.0
        ), "All probabilities of 'probs' must sum to 1"

    def _validate_setitem_probs(self, key: Any, value: np.ndarray) -> None:
        if isinstance(key, tuple) and len(key) > 2:
            raise IndexError(
                f"'len(key)' is {len(key)} but must be <= 2 since all probabilites for a state must be updated at once"
            )
        if not isinstance(value, np.ndarray) or len(value.shape) <= 1:
            value = np.broadcast_to(value, (self._num_actions,))

        assert np.all(value >= 0) and np.all(
            value <= 1
        ), "All probabilities must be in [0, 1]"
        assert np.allclose(
            np.sum(value, axis=-1), 1.0
        ), "All probabilities must sum to 1"
