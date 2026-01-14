from edugrid.algorithms.policy import Policy
from edugrid.envs.grids import Action

import numpy as np
import matplotlib.pyplot as plt


def visualize_grid(
    ax: plt.Axes, shape: tuple[int, ...], terminal: np.ndarray | None = None
) -> None:
    """Visualizes the environment as a grid.

    Parameters
    ----------
    ax : plt.Axes
        The axes of the figure
    shape : tuple[int, ...]
        Tuple with `shape[0]` as number of rows and `shape[1]` as number of columns
    terminal : np.ndarray | None, optional
        Matrix of shape `shape[:2]` that specifies whether states are terminal. If provided, the terminal states are plotted as gray cells. By default None
    """
    rows = shape[0]
    cols = shape[1]

    for i in range(rows + 1):
        ax.hlines(i, 0, cols, colors="black")

    for i in range(cols + 1):
        ax.vlines(i, 0, rows, colors="black")

    if terminal is not None:
        assert terminal.shape == (rows, cols)
        for (row, col), t in np.ndenumerate(terminal):
            if t:
                ax.add_patch(plt.Rectangle((col, rows - row), 1, -1, color="gray"))


def visualize_state_values(ax: plt.Axes, values: np.ndarray) -> None:
    """Visualizes the state values (V).

    Parameters
    ----------
    ax : plt.Axes
        The axes of the figure
    values : np.ndarray
        The state values (V)
    """
    ax.set_axis_off()

    visualize_grid(ax, values.shape)

    items = values.round(2)
    total_rows = items.shape[0]

    for (row, col), value in np.ndenumerate(items):
        ax.annotate(
            value,
            (0.5 + col, total_rows - 0.5 - row),
            horizontalalignment="center",
            verticalalignment="center",
            fontsize="xx-large",
        )


def visualize_policy(
    ax: plt.Axes, policy: Policy, terminal: np.ndarray | None = None
) -> None:
    """Visualizes the policy.

    Parameters
    ----------
    ax : plt.Axes
        The axes of the figure
    policy : Policy
        The policy
    terminal : np.ndarray | None, optional
        Matrix of shape `policy[:2]` that specifies whether states are terminal. If provided, the terminal states are plotted as gray cells. By default None

    Raises
    ------
    ValueError
        If the policy specifies an invalid action.
    """
    ax.set_axis_off()
    probs = policy.get_probs()

    visualize_grid(ax, probs.shape, terminal)

    arrow_length = 0.4
    total_rows = probs.shape[0]

    for (row, col, action), value in np.ndenumerate(probs):
        if value > 0:
            if action == Action.RIGHT:
                xytext = (0.5 + col + arrow_length, total_rows - 0.5 - row)
            elif action == Action.UP:
                xytext = (0.5 + col, total_rows - 0.5 - row + arrow_length)
            elif action == Action.LEFT:
                xytext = (0.5 + col - arrow_length, total_rows - 0.5 - row)
            elif action == Action.DOWN:
                xytext = (0.5 + col, total_rows - 0.5 - row - arrow_length)
            else:
                raise ValueError("Invalid action")

            ax.annotate(
                None,
                xy=(0.5 + col, total_rows - 0.5 - row),
                xytext=xytext,
                arrowprops=dict(
                    arrowstyle="<|-", lw=2, mutation_scale=20, color="black"
                ),
            )
