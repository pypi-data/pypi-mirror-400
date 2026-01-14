from abc import ABC, abstractmethod

from gymnasium.error import DependencyNotInstalled

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from edugrid.envs.grids import EduGridEnv
    import pygame


class CellType:
    NORMAL = 0
    TARGET = 1
    SINK = 2
    WALL = 3
    CUSTOM = 4

    _STR_TO_TYPE = {"N": NORMAL, "T": TARGET, "S": SINK, "W": WALL, "C": CUSTOM}
    _TYPE_TO_STR = dict(zip(_STR_TO_TYPE.values(), _STR_TO_TYPE.keys()))

    @classmethod
    def to_str(cls, cell_type: int) -> str:
        _str = cls._TYPE_TO_STR.get(cell_type)
        if _str is None:
            raise ValueError(f"Unknown cell type: {cell_type}")
        return _str

    @classmethod
    def from_str(cls, string: str) -> int:
        _type = cls._STR_TO_TYPE.get(string)
        if _type is None:
            raise ValueError(f"'{string}' cannot be converted to a CellType")
        return _type


class Cell(ABC):
    """Abstract base class for custom cells.

    The methods are called in the following order:
    - `on_left`
    - `on_entered`
    - `on_step`
    """

    @abstractmethod
    def is_blocking(self) -> bool:
        """Indicates whether the cell is blocking, i.e., it is not reachable by the agent.

        Returns
        -------
        bool
            True if cell is blocking and False otherwise
        """
        pass

    def on_entered(self, env: "EduGridEnv", row: int, column: int) -> None:
        """Called if the agent has entered this custom cell.

        Parameters
        ----------
        env : EduGridEnv
            The environment
        row : int
            The row of this custom cell
        column : int
            The column of this custom cell
        """
        pass

    def on_left(self, env: "EduGridEnv", row: int, column: int) -> None:
        """Called if the agent has left this custom cell.

        Parameters
        ----------
        env : EduGridEnv
            The environment
        row : int
            The row of this custom cell
        column : int
            The column of this custom cell
        """
        pass

    def on_step(self, env: "EduGridEnv", row: int, column: int) -> None:
        """Called after each environment step.

        Parameters
        ----------
        env : EduGridEnv
            The environment
        row : int
            The row of this custom cell
        column : int
            The column of this custom cell
        """
        pass

    def render(
        self,
        canvas: "pygame.Surface",
        left_top_x: int,
        left_top_y: int,
        width: int,
        height: int,
    ) -> None:
        """Renders this custom cell.

        Parameters
        ----------
        canvas : pygame.Surface
            The canvas on which the cell is rendered
        left_top_x : int
            X coordinate of the left-top corner of the tile to be rendered
        left_top_y : int
            Y coordinate of the left-top corner of the tile to be rendered
        width : int
            Width of the tile to be rendered
        height : int
            Height of the tile to be rendered

        Raises
        ------
        DependencyNotInstalled
            If `pygame` is not installed.
        """
        try:
            import pygame
        except ImportError as e:
            raise DependencyNotInstalled(
                "pygame is not installed, run `pip install pygame`"
            ) from e

        color = (255, 0, 255)

        pygame.draw.rect(
            canvas,
            color,
            pygame.Rect(
                (left_top_x, left_top_y),
                (width, height),
            ),
        )


class Object(ABC):  # TODO
    @abstractmethod
    def is_blocking(self) -> bool:
        pass


class MovingTarget(Cell):  # TODO
    def __init__(self, initial_position: tuple[int, int]) -> None:
        super().__init__()
        self._position = initial_position
        self._last_position = None

    def is_blocking(self) -> bool:
        return False

    def on_step(self, env) -> None:
        # TODO change env._target_locations
        # TODO change env._cell_types
        # TODO change env._terminal_matrix
        # TODO change env._transition_matrix
        # TODO change env._reward_matrix
        pass

    def render(self) -> None:
        pass
