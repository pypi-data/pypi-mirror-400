from copy import deepcopy
from typing import Any, Iterable, Optional, Union

import gymnasium as gym
from gymnasium.error import DependencyNotInstalled
import numpy as np

from edugrid.envs.cells import Cell, CellType
from edugrid.utils import ArrayDescriptor, ArrayWrapper


class Action:
    RIGHT = 0
    UP = 1
    LEFT = 2
    DOWN = 3


class EduGridEnv(gym.Env[np.ndarray, Union[int, np.ndarray]]):
    """
    ## Description

    The EduGrid environment represents a grid of cells with different types such as walls, sinks and targets.
    The agent tries to reach target cells while avoiding getting terminated in sinks.

    In contrast to other grid environments, properties of individual cells can be adjusted by simply modifying environment properties
    such as `transition_matrix`, `reward_matrix` and `terminal_matrix`.
    Furthermore, custom cells that can change their behavior after each environment step can be added.

    ## Action Space

    The action is an `int` or `ndarray` with shape `(1,)` which can take values `{0, 3}` indicating which direction the agent moves to.
    The values are also specified in the class `Action`:
    - 0: right
    - 1: up
    - 2: left
    - 3: down

    ## Observation Space

    The observation is a dictionary with the key `"agent"` for the agent's location and the key `"targets"` for the tuple of target locations.
    Each location is encoded as an element of a `MultiDiscrete([number_of_rows, number_of_columns])`.
    Hence, the observation space is a `Dict["agent": MultiDiscrete, "targets": Tuple[MultiDiscrete, ...]]`.

    ## Starting State

    The default starting state is `(0, 0)` but it can be changed with the parameter `agent_location`.

    ## Rewards

    The default rewards are as follows:
    - Reach normal cell: -1.0
    - Reach sink: -5
    - Reach target: 10

    The rewards can be changed with the parameters `normal_reward`, `sink_reward`, `target_reward` or afterwards by modifying the property `reward_matrix`.
    The `reward_matrix` has the shape `(rows, columns, actions, rows, columns) and specifies the reward for all combination of states, actions and next states.

    ## Episode End

    The episode ends if the following happens:

    - Termination: The agent reaches a sink or a target.
    - Truncation: After `max_episode_steps` specified either by the constructor parameter or by a time_limit wrapper.

    ## Information

    `step()` and `reset()` return a dict with the following keys:
    - "prob": The probability of the transition or `None` if no transition occurred yet.
    """

    _agent_location: np.ndarray
    _target_locations: tuple[np.ndarray]

    metadata = {"render_modes": ["human", "rgb_array"], "render_fps": 4}

    _config_5x5_v0 = dict(
        size=(5, 5),
        agent_location=(0, 0),
        target_locations=[(4, 4)],
        normal_reward=-1,
        sink_reward=-5,
        target_reward=10,
    )

    configs = {"config_5x5_v0": _config_5x5_v0}

    def __init__(
        self,
        config: str | None = None,
        *,
        render_mode: str | None = None,
        size: tuple[int, int] | None = None,
        map_str: str | None = None,
        agent_location: tuple[int, int] | None = None,
        wall_locations: Iterable[tuple[int | slice, int | slice]] | None = None,
        sink_locations: Iterable[tuple[int | slice, int | slice]] | None = None,
        target_locations: Iterable[tuple[int, int]] | None = None,
        custom_cells: dict[tuple[int, int], Cell] | None = None,
        slip_prob: float = 0.0,
        normal_reward: float | None = None,
        sink_reward: float | None = None,
        target_reward: float | None = None,
        max_episode_steps: int | None = None,
        **kwargs,
    ):
        """Creates a EduGridEnv.

        Parameters
        ----------
        config : str | None, optional
            Name of a predefined config that is available in the class variable `configs`. By default None, which means that the base config "config_5x5_v0" is used.
            The predefined config can be overriden by specifying parameters for this constructor.
        render_mode : str | None, optional
            Render mode that is available in the class variable `metadata["render_modes"]`, by default None
        size : tuple[int, int] | None, optional
            (number_of_rows, number_of_columns) for the grid size, by default None.
        map_str : str | None, optional
            A string representation of the map layout, by default None.
            Number of lines represent the number of rows, and the number of letters in a line the number of columns, respectively.
            Each letter represents the cell type: "N" -> NORMAL, "T" -> TARGET, "S" -> SINK, "W" -> WALL, "C" -> CUSTOM
            Example of 3x3 grid with a sink at (0, 2) and a target at (2, 2):
            '''NNS
               NNN
               NNT'''
        agent_location : tuple[int, int] | None, optional
            Initial agent location as `(row, column)`-tuple, by default None
        wall_locations : Iterable[tuple[int  |  slice, int  |  slice]] | None, optional
            Iterable of wall locations as `(row, column)`-tuples, by default None. Slices can also be used as indices.
        sink_locations : Iterable[tuple[int, int]] | None, optional
            Iterable of sink locations as `(row, column)`-tuples, by default None
        target_locations : Iterable[tuple[int, int]] | None, optional
            Iterable of target locations as `(row, column)`-tuples, by default None
        custom_cells : dict[tuple[int, int], Cell] | None, optional
            Dictionary of custom cells with `(row, columns)`-tuple keys indicating the locations, by default None
        slip_prob : float, optional
            Probability of slipping during a transition, by default 0.0. The probility of reaching the desired cell is `1 - slip_prob` and each probability for the two neighbor cells is `slip_prob / 2`.
        normal_reward : float | None, optional
            Reward for reaching a normal cell, by default None
        sink_reward : float | None, optional
            Reward for reaching a sink cell, by default None
        target_reward : float | None, optional
            Reward for reaching a target cell, by default None
        max_episode_steps : int | None, optional
            Maximum steps after which an episode is truncated, by default None

        Raises
        ------
        ValueError
            If a specified location is invalid.
        """
        # We have 4 actions, corresponding to "right", "up", "left", "down", "right"
        self._num_actions = 4
        self._action_space = gym.spaces.Discrete(self._num_actions)

        self._action_to_direction = {
            Action.RIGHT: np.array([0, 1]),
            Action.UP: np.array([-1, 0]),
            Action.LEFT: np.array([0, -1]),
            Action.DOWN: np.array([1, 0]),
        }

        self._slip_prob = slip_prob
        self._custom_cells: dict[tuple[int, int], Cell] = (
            custom_cells if custom_cells is not None else {}
        )

        self._init_map(
            config=config,
            size=size,
            map_str=map_str,
            wall_locations=wall_locations,
            sink_locations=sink_locations,
            target_locations=target_locations,
            slip_prob=slip_prob,
            normal_reward=normal_reward,
            sink_reward=sink_reward,
            target_reward=target_reward,
            extra_params=kwargs,
        )
        self._num_targets = len(self._target_locations)

        if agent_location is not None:
            if not self._state_space.contains(agent_location):
                raise ValueError(
                    f"The 'agent_location' {agent_location} is invalid for the state space with size {size}"
                )
            self._initial_agent_location = np.asarray(agent_location, dtype=int)
        else:
            self._initial_agent_location = np.asarray((0, 0), dtype=int)

        self._agent_location = None
        self._last_state = None
        self._last_action = None
        self._episode_step = 0
        self._max_episode_steps = max_episode_steps

        self._pix_square_size = 100  # The size of a single grid square in pixels

        # Observations are dictionaries with the agent's and the targets' locations.
        # Each location is encoded as an element of MultiDiscrete([rows, columns]).
        self._observation_space = gym.spaces.Dict(
            {
                "agent": gym.spaces.MultiDiscrete([self._nrows, self._ncols]),
                "targets": gym.spaces.Tuple(
                    [
                        gym.spaces.MultiDiscrete([self._nrows, self._ncols])
                        for _ in range(self._num_targets)
                    ]
                ),
            }
        )

        assert render_mode is None or render_mode in self.metadata["render_modes"]
        self.render_mode = render_mode

        """
        If human-rendering is used, `self.window` will be a reference
        to the window that we draw to. `self.clock` will be a clock that is used
        to ensure that the environment is rendered at the correct framerate in
        human-mode. They will remain `None` until human-mode is used for the
        first time.
        """
        self.window = None
        self.clock = None

    @staticmethod
    def _map_from_str(string: str) -> tuple[np.ndarray, list[tuple[int, int]]]:
        string = string.strip()
        lines = string.splitlines()
        nrows = len(lines)
        ncols = len(lines[0].strip())

        cell_types = np.zeros((nrows, ncols), dtype=np.int8)
        target_locations = []

        for i in range(nrows):
            line = lines[i].strip()
            for j in range(ncols):
                type = CellType.from_str(line[j])
                cell_types[i, j] = type
                if type is CellType.TARGET:
                    target_locations.append((i, j))

        return cell_types, target_locations

    def _init_map(
        self,
        config: str | None,
        size: tuple[int, int] | None,
        map_str: str | None,
        wall_locations: Iterable[tuple[int | slice, int | slice]] | None,
        sink_locations: Iterable[tuple[int, int]] | None,
        target_locations: Iterable[tuple[int, int]] | None,
        slip_prob: float,
        normal_reward: float | None,
        sink_reward: float | None,
        target_reward: float | None,
        extra_params: dict | None,
    ) -> None:
        config_params = self.configs.get(config, {})
        config_params = dict(self._config_5x5_v0, **config_params)

        ### size

        if size is not None:
            assert len(size) == 2
            self._nrows, self._ncols = size

        ### cell types
        targets_in_map = []
        use_cell_types_from_config = False

        if "cell_types" in extra_params:
            self._cell_types = extra_params["cell_types"]
            assert isinstance(
                self._cell_types, np.ndarray
            ), f"'cell_types' must be a numpy array but is {type(self._cell_types)}"
            assert (
                self._cell_types.ndim == 2
            ), f"'cell_types' must have 2 dimensions but has {self._cell_types.ndim}"
            if size is None:
                self._nrows, self._ncols = self._cell_types.shape
            else:
                assert self._cell_types.shape == (
                    self._nrows,
                    self._ncols,
                ), f"'cell_types' has shape {self._cell_types.shape} but should have {(self._nrows, self._ncols)}"
            assert (
                np.issubdtype(self._cell_types.dtype, np.integer)
                and np.all(self._cell_types >= CellType.NORMAL)
                and np.all(self._cell_types <= CellType.CUSTOM)
            ), "'cell_types' must contain integers according to the enum CellType"
        elif map_str is not None:
            self._cell_types, targets_in_map = self._map_from_str(map_str)
            if size is None:
                self._nrows, self._ncols = self._cell_types.shape
            else:
                assert self._cell_types.shape == (
                    self._nrows,
                    self._ncols,
                ), f"'cell_types' has shape {self._cell_types.shape} but should have {(self._nrows, self._ncols)}"
        else:
            if size is None:
                self._nrows, self._ncols = config_params["size"]
                use_cell_types_from_config = True
            self._cell_types = np.full(
                (self._nrows, self._ncols), CellType.NORMAL, dtype=np.int8
            )

        self._state_space = gym.spaces.MultiDiscrete([self._nrows, self._ncols])

        # wall locations
        if wall_locations is None and use_cell_types_from_config:
            wall_locations = config_params.get("wall_locations")
        if wall_locations is not None:
            for row, col in wall_locations:
                try:
                    self._cell_types[row, col] = CellType.WALL
                except IndexError:
                    raise ValueError(
                        f"The 'wall_location' {(row, col)} is invalid for the state space with size {size}"
                    )

        # sink locations
        if sink_locations is None and use_cell_types_from_config:
            sink_locations = config_params.get("sink_locations")
        if sink_locations is not None:
            for row, col in sink_locations:
                try:
                    self._cell_types[row, col] = CellType.SINK
                except IndexError:
                    raise ValueError(
                        f"The 'sink_location' {(row, col)} is invalid for the state space with size {size}"
                    )

        # target locations
        if target_locations is None and use_cell_types_from_config:
            target_locations = config_params.get("target_locations")
        if target_locations is not None:
            for row, col in target_locations:
                assert type(row) is int and type(col) is int
                if not self._state_space.contains((row, col)):
                    raise ValueError(
                        f"The 'target_location' {(row, col)} is invalid for the state space with size {size}"
                    )
                if self._cell_types[row, col] is not CellType.TARGET:
                    targets_in_map.append((row, col))
                    self._cell_types[row, col] = CellType.TARGET

        self._target_locations = tuple(
            np.asarray(target, dtype=int) for target in targets_in_map
        )

        # custom cells
        for s, cell in self._custom_cells.items():
            self._cell_types[s[0], s[1]] = CellType.CUSTOM

        ### terminal matrix
        terminal_matrix_shape = (self._nrows, self._ncols)
        extra_terminal = "terminal_matrix" in extra_params
        if extra_terminal:
            self._terminal_matrix = extra_params["terminal_matrix"]
            assert isinstance(
                self._terminal_matrix, np.ndarray
            ), "'terminal_matrix' must be a numpy array"
            assert (
                self._terminal_matrix.shape == terminal_matrix_shape
            ), f"'terminal_matrix' has shape {self._terminal_matrix.shape} but should have {terminal_matrix_shape}"
            assert np.all(
                self._terminal_matrix[self._cell_types == CellType.TARGET]
            ), "'terminal_matrix' must be true for all target cells"
            assert np.all(
                self._terminal_matrix[self._cell_types == CellType.SINK]
            ), "'terminal_matrix' must be true for all sink cells"
        else:
            self._init_terminal_matrix(terminal_matrix_shape)

        self._terminal_matrix_wrapper = ArrayWrapper(
            self._terminal_matrix,
            val_set=self._validate_set_terminal_matrix,
            val_setitem=None,
        )

        ### transition matrix
        transition_matrix_shape = (
            self._nrows,
            self._ncols,
            self._num_actions,
            self._nrows,
            self._ncols,
        )
        extra_transition = "transition_matrix" in extra_params
        if extra_transition:
            self._transition_matrix = extra_params["transition_matrix"]
            assert isinstance(
                self._transition_matrix, np.ndarray
            ), "'transition_matrix' must be a numpy array"
            assert (
                self._transition_matrix.shape == transition_matrix_shape
            ), f"'transition_matrix' has shape {self._transition_matrix.shape} but should have {transition_matrix_shape}"
            assert (
                self._transition_matrix.dtype.kind == "f"
            ), f"'dtype' of 'transition_matrix' is {self._transition_matrix.dtype} but must be floating-point"
            assert np.all(self._transition_matrix >= 0) and np.all(
                self._transition_matrix <= 1
            ), "All probabilities of the 'transition_matrix' must be in [0, 1]"
            assert np.allclose(
                np.sum(self._transition_matrix, axis=(-2, -1)), 1.0
            ), "All probabilities of the 'transition_matrix' must sum to 1"
            assert np.all(
                self._transition_matrix[:, :, :, self._cell_types == CellType.WALL] == 0
            ), "All probabilities of the 'transition_matrix' must be zero for transitions into walls"
        else:
            assert (
                slip_prob >= 0 and slip_prob <= 1
            ), f"The 'slip_prob' is {slip_prob} but must be in [0,1]"
            self._init_transition_matrix(transition_matrix_shape, slip_prob)

        self._transition_matrix_wrapper = ArrayWrapper(
            self._transition_matrix,
            val_set=self._validate_set_transition_matrix,
            val_setitem=self._validate_setitem_transition_matrix,
        )

        ### reward matrix
        reward_matrix_shape = (
            self._nrows,
            self._ncols,
            self._num_actions,
            self._nrows,
            self._ncols,
        )
        extra_reward = "reward_matrix" in extra_params
        if extra_reward:
            self._reward_matrix = extra_params["reward_matrix"]
            assert isinstance(
                self._reward_matrix, np.ndarray
            ), "'reward_matrix' must be a numpy array"
            assert (
                self._reward_matrix.shape == reward_matrix_shape
            ), f"'reward_matrix' has shape {self._reward_matrix.shape} but should have {reward_matrix_shape}"
        else:
            if normal_reward is None:
                normal_reward = config_params["normal_reward"]
            if sink_reward is None:
                sink_reward = config_params["sink_reward"]
            if target_reward is None:
                target_reward = config_params["target_reward"]

            self._init_reward_matrix(
                reward_matrix_shape, normal_reward, sink_reward, target_reward
            )

        self._reward_matrix_wrapper = ArrayWrapper(
            self._reward_matrix,
            val_set=self._validate_set_reward_matrix,
            val_setitem=None,
        )

    def _init_terminal_matrix(self, shape: tuple[int, int]) -> None:
        self._terminal_matrix = np.full(shape, False)
        for row in range(self._nrows):
            for col in range(self._ncols):
                self._terminal_matrix[row, col] = (
                    self._cell_types[row, col] == CellType.SINK
                    or self._cell_types[row, col] == CellType.TARGET
                )

    def _init_transition_matrix(
        self, shape: tuple[int, int, int, int, int], slip_prob: float
    ) -> None:
        self._transition_matrix = np.zeros(shape)
        for row in range(self._nrows):
            for col in range(self._ncols):
                if self._terminal_matrix[row, col]:
                    # if the cell is terminal, the agent stays in this cell
                    self._transition_matrix[row, col, Action.RIGHT, row, col] = 1.0
                    self._transition_matrix[row, col, Action.UP, row, col] = 1.0
                    self._transition_matrix[row, col, Action.LEFT, row, col] = 1.0
                    self._transition_matrix[row, col, Action.DOWN, row, col] = 1.0
                    continue

                if self._is_blocking(row, col):
                    # the agent cannot be at a blocking cell, so all transition probabilities
                    # are zero starting from this blocking cell
                    continue

                # previous row
                prev_row = row - 1
                prev_row = (
                    prev_row
                    if prev_row >= 0 and not self._is_blocking(prev_row, col)
                    else row
                )
                # previous column
                prev_col = col - 1
                prev_col = (
                    prev_col
                    if prev_col >= 0 and not self._is_blocking(row, prev_col)
                    else col
                )
                # next row
                next_row = row + 1
                next_row = (
                    next_row
                    if next_row < self._nrows and not self._is_blocking(next_row, col)
                    else row
                )
                # next column
                next_col = col + 1
                next_col = (
                    next_col
                    if next_col < self._ncols and not self._is_blocking(row, next_col)
                    else col
                )

                # action right
                self._transition_matrix[row, col, Action.RIGHT, row, next_col] = (
                    1.0 - slip_prob
                )
                self._transition_matrix[row, col, Action.RIGHT, prev_row, col] += (
                    slip_prob / 2.0
                )
                self._transition_matrix[row, col, Action.RIGHT, next_row, col] += (
                    slip_prob / 2.0
                )

                # action up
                self._transition_matrix[row, col, Action.UP, prev_row, col] = (
                    1.0 - slip_prob
                )
                self._transition_matrix[row, col, Action.UP, row, prev_col] += (
                    slip_prob / 2.0
                )
                self._transition_matrix[row, col, Action.UP, row, next_col] += (
                    slip_prob / 2.0
                )

                # action left
                self._transition_matrix[row, col, Action.LEFT, row, prev_col] = (
                    1.0 - slip_prob
                )
                self._transition_matrix[row, col, Action.LEFT, prev_row, col] += (
                    slip_prob / 2.0
                )
                self._transition_matrix[row, col, Action.LEFT, next_row, col] += (
                    slip_prob / 2.0
                )

                # action down
                self._transition_matrix[row, col, Action.DOWN, next_row, col] = (
                    1.0 - slip_prob
                )
                self._transition_matrix[row, col, Action.DOWN, row, prev_col] += (
                    slip_prob / 2.0
                )
                self._transition_matrix[row, col, Action.DOWN, row, next_col] += (
                    slip_prob / 2.0
                )

    def _is_blocking(self, row: int, col: int) -> bool:
        cell_type = self._cell_types[row, col]
        if cell_type == CellType.WALL:
            return True
        if cell_type == CellType.CUSTOM:
            cell = self._custom_cells[(row, col)]
            return cell.is_blocking()
        return False

    def _init_reward_matrix(
        self,
        shape: tuple[int, int, int, int, int],
        normal_reward: float,
        sink_reward: float,
        target_reward: float,
    ) -> None:
        self._reward_matrix = np.full(shape, normal_reward, dtype=np.float64)

        for row in range(self._nrows):
            for col in range(self._ncols):
                cell_is_sink = self._cell_types[row, col] == CellType.SINK
                cell_is_target = self._cell_types[row, col] == CellType.TARGET

                if cell_is_sink:
                    self._reward_matrix[:, :, :, row, col] = sink_reward * np.ones(
                        (self._nrows, self._ncols, self._num_actions)
                    )
                elif cell_is_target:
                    self._reward_matrix[:, :, :, row, col] = target_reward * np.ones(
                        (self._nrows, self._ncols, self._num_actions)
                    )

                if cell_is_sink or cell_is_target:
                    self._reward_matrix[row, col] = np.zeros(
                        (self._num_actions, self._nrows, self._ncols)
                    )

    @property
    def state_space(self) -> gym.spaces.MultiDiscrete:
        return self._state_space

    @property
    def action_space(self) -> gym.spaces.Discrete:
        return self._action_space

    @property
    def observation_space(self) -> gym.spaces.Dict:
        return self._observation_space

    @property
    def cell_type_matrix(self) -> np.ndarray:
        """Copy of the numpy array with shape `(rows, columns)` containing the cell types. See the class `CellType` for the possible values."""
        return self._cell_types.copy()

    terminal_matrix = ArrayDescriptor()
    """Boolean numpy array with shape `(rows, columns)` indicating whether a cell is terminal."""

    transition_matrix = ArrayDescriptor()
    """Numpy array with shape `(rows, columns, actions, rows, columns)` that specifies the probability for all possible transitions `(state, action, next_state)`."""

    reward_matrix = ArrayDescriptor()
    """Numpy array with shape `(rows, columns, actions, rows, columns)` that specifies the reward for all possible transitions `(state, action, next_state)`."""

    def _validate_set_terminal_matrix(self, values: np.ndarray) -> None:
        assert isinstance(values, np.ndarray), "'terminal_matrix' must be a numpy array"
        assert (
            values.shape == self._terminal_matrix.shape
        ), f"'terminal_matrix' has shape {values.shape} but should have {self._terminal_matrix.shape}"
        assert (
            values.dtype.kind == "b"
        ), f"'dtype' of 'terminal_matrix' is {values.dtype} but must be boolean"

    def _validate_set_transition_matrix(self, values: np.ndarray) -> None:
        assert isinstance(
            values, np.ndarray
        ), "'transition_matrix' must be a numpy array"
        assert (
            values.shape == self._transition_matrix.shape
        ), f"'transition_matrix' has shape {values.shape} but should have {self._transition_matrix.shape}"
        assert (
            values.dtype.kind == "f"
        ), f"'dtype' of 'transition_matrix' is {values.dtype} but must be floating-point"
        assert np.all(values >= 0) and np.all(
            values <= 1
        ), "All probabilities of the 'transition_matrix' must be in [0, 1]"
        assert np.allclose(
            np.sum(values, axis=(-2, -1)), 1.0
        ), "All probabilities of the 'transition_matrix' must sum to 1"
        assert np.all(
            values[:, :, :, self._cell_types == CellType.WALL] == 0
        ), "All probabilities of the 'transition_matrix' must be zero for transitions into walls"

    def _validate_setitem_transition_matrix(self, key: Any, value: np.ndarray) -> None:
        if isinstance(key, tuple) and len(key) > 3:
            raise IndexError(
                f"'len(key)' is {len(key)} but must be <= 3 since all probabilites for a state-action pair must be updated at once"
            )
        if not isinstance(value, np.ndarray) or len(value.shape) <= 2:
            value = np.broadcast_to(value, (self._nrows, self._ncols))

        assert np.all(value >= 0) and np.all(
            value <= 1
        ), "All probabilities must be in [0, 1]"
        assert np.allclose(
            np.sum(value, axis=(-2, -1)), 1.0
        ), "All probabilities must sum to 1"
        assert np.all(
            value[..., self._cell_types == CellType.WALL] == 0
        ), "All probabilities must be zero for transitions into walls"

    def _validate_set_reward_matrix(self, values: np.ndarray) -> None:
        assert isinstance(values, np.ndarray), "'reward_matrix' must be a numpy array"
        assert (
            values.shape == self._reward_matrix.shape
        ), f"'reward_matrix' must have shape {self._reward_matrix.shape} but argument has shape {values.shape}"

    def _get_obs(self) -> dict[str, np.ndarray]:
        return {
            "agent": self._agent_location.copy(),
            "targets": deepcopy(self._target_locations),
        }

    def _get_next_state(self, s0: np.ndarray, a: Action) -> np.ndarray:
        s0 = tuple(s0)  # assumes s0 is a 1-d array
        p = self._transition_matrix[s0[0], s0[1], a].ravel()
        s1_index = self.np_random.choice(self._nrows * self._ncols, p=p)
        s1_row = s1_index // self._ncols
        s1_col = s1_index % self._ncols

        if cell := self._custom_cells.get(s0):
            cell.on_left(self, s0[0], s0[1])

        if cell := self._custom_cells.get((s1_row, s1_col)):
            cell.on_entered(self, s1_row, s1_col)

        for s, cell in self._custom_cells.items():
            cell.on_step(self, s[0], s[1])

        return np.asarray((s1_row, s1_col), dtype=int)

    def _get_reward(self, s0: np.ndarray, a: Action, s1: np.ndarray) -> float:
        return self._reward_matrix[s0[0], s0[1], a, s1[0], s1[1]].item()

    def _is_terminated(self) -> bool:
        return self._terminal_matrix[
            self._agent_location[0], self._agent_location[1]
        ].item()

    def _get_info(self) -> dict[str, Any]:
        if self._last_state is None:
            prob = None
        else:
            s0_row, s0_col = self._last_state[0], self._last_state[1]
            s1_row, s1_col = self._agent_location[0], self._agent_location[1]
            prob = self._transition_matrix[
                s0_row, s0_col, self._last_action, s1_row, s1_col
            ].copy()
        return {"prob": prob}

    def reset(self, seed=None, options=None) -> tuple[dict, dict]:
        # We need the following line to seed self.np_random
        super().reset(seed=seed)

        self._episode_step = 0
        self._agent_location = self._initial_agent_location.copy()
        self._last_state = None
        self._last_action = None

        # Choose the agent's location uniformly at random
        # self._agent_location = self.np_random.integers(0, self.size, size=2, dtype=int)

        # We will sample the target's location randomly until it does not coincide with the agent's location
        # self._target_location = self._agent_location
        # while np.array_equal(self._target_location, self._agent_location):
        #     self._target_location = self.np_random.integers(
        #         0, self.size, size=2, dtype=int
        #     )

        obs = self._get_obs()
        info = self._get_info()

        if self.render_mode == "human":
            self.render()

        return obs, info

    def step(self, action: Action | np.ndarray) -> tuple[dict, float, bool, bool, dict]:
        assert self._action_space.contains(
            action
        ), f"{action!r} ({type(action)}) invalid"
        assert self._agent_location is not None, "Call reset before using step method."

        action = action if isinstance(action, int) else action.item()

        self._last_state = self._agent_location
        self._last_action = action
        self._agent_location = self._get_next_state(self._last_state, action)
        obs = self._get_obs()
        reward = self._get_reward(self._last_state, action, self._agent_location)
        terminated = self._is_terminated()
        self._episode_step += 1
        truncated = (
            self._episode_step >= self._max_episode_steps
            if self._max_episode_steps is not None
            else False
        )
        info = self._get_info()

        if self.render_mode == "human":
            self.render()

        return obs, reward, terminated, truncated, info

    def render(self) -> Optional[np.ndarray]:
        if self.render_mode is None:
            gym.logger.warn(
                "You are calling render method without specifying any render mode. "
                "You can specify the render_mode at initialization, "
                'e.g. gym.make("...", render_mode="rgb_array")'
            )
            return

        try:
            import pygame
        except ImportError as e:
            raise DependencyNotInstalled(
                "pygame is not installed, run `pip install pygame`"
            ) from e

        if self.render_mode == "human":
            if self.window is None:
                pygame.init()
                pygame.display.init()
                self.window = pygame.display.set_mode(
                    (
                        self._pix_square_size * self._ncols,
                        self._pix_square_size * self._nrows,
                    )
                )
            if self.clock is None:
                self.clock = pygame.time.Clock()

        canvas = pygame.Surface(
            (self._pix_square_size * self._ncols, self._pix_square_size * self._nrows)
        )
        canvas.fill((255, 255, 255))

        # First we draw the cell types
        for row in range(self._nrows):
            for col in range(self._ncols):
                color = None
                cell_type = self._cell_types[row, col]

                left_top = (self._pix_square_size * col, self._pix_square_size * row)
                width, height = self._pix_square_size, self._pix_square_size

                if cell_type == CellType.WALL:
                    color = (255, 255, 0)
                elif cell_type == CellType.SINK:
                    color = (255, 0, 0)
                elif cell_type == CellType.CUSTOM:
                    custom_cell = self._custom_cells[row, col]
                    custom_cell.render(canvas, *left_top, width, height)

                if color is not None:
                    pygame.draw.rect(
                        canvas,
                        color,
                        pygame.Rect(left_top, (width, height)),
                    )

        # Now we draw the targets
        for target_loc in self._target_locations:
            pygame.draw.rect(
                canvas,
                (0, 255, 0),
                pygame.Rect(
                    self._pix_square_size * target_loc[::-1],
                    (self._pix_square_size, self._pix_square_size),
                ),
            )
        # Now we draw the agent
        if self._agent_location is not None:
            pygame.draw.circle(
                canvas,
                (0, 0, 255),
                (self._agent_location[::-1] + 0.5) * self._pix_square_size,
                self._pix_square_size / 3,
            )

        # Finally, add some gridlines
        for row in range(self._nrows + 1):
            pygame.draw.line(
                canvas,
                0,
                (0, self._pix_square_size * row),
                (self._pix_square_size * self._ncols, self._pix_square_size * row),
                width=3,
            )

        for col in range(self._ncols + 1):
            pygame.draw.line(
                canvas,
                0,
                (self._pix_square_size * col, 0),
                (self._pix_square_size * col, self._pix_square_size * self._nrows),
                width=3,
            )

        if self.render_mode == "human":
            # The following line copies our drawings from `canvas` to the visible window
            self.window.blit(canvas, canvas.get_rect())
            pygame.event.pump()
            pygame.display.update()

            # We need to ensure that human-rendering occurs at the predefined framerate.
            # The following line will automatically add a delay to keep the framerate stable.
            self.clock.tick(self.metadata["render_fps"])
        elif self.render_mode == "rgb_array":
            return np.transpose(
                np.array(pygame.surfarray.pixels3d(canvas)), axes=(1, 0, 2)
            )

    def close(self) -> None:
        if self.window is not None:
            pygame.display.quit()  # noqa: F821
            pygame.quit()  # noqa: F821
