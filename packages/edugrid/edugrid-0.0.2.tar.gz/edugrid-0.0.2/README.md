[![pypi](https://img.shields.io/pypi/v/edugrid)](https://pypi.org/project/edugrid)
[![license](https://img.shields.io/github/license/philsteg/edugrid)](https://github.com/philsteg/edugrid)
[![tests](https://github.com/philsteg/edugrid/actions/workflows/python-app.yml/badge.svg)](https://github.com/philsteg/edugrid/actions/workflows/python-app.yml)

# EduGrid

> [!NOTE]
> EduGrid is intended for educational purposes and is hence not optimized for speed. If you don't need so much flexibility, have a look at the Gymmasium environments ["Minigrid"](https://minigrid.farama.org/index.html) and ["Frozen Lake"](https://gymnasium.farama.org/environments/toy_text/frozen_lake/).

EduGrid is a Gymnasium grid environment with focus on flexibility for educational purposes. The agent moves in a grid of cells and tries to reach target cells. Furthermore, dynamic programming algorithms are implemented and can iteratively be inspected.

## Features
- The following environment properties can be inspected and modified:
    - `transition_matrix` with shape `(rows, columns, actions, rows, columns)` specifying the probabilities for all "state-action-next_state" transitions
    - `reward_matrix` with shape `(rows, columns, actions, rows, columns)` specifying the rewards for all "state-action-next_state" transitions
    - `terminal_matrix` with shape `(rows, columns)` specifying whether states are terminal.
- Custom cells can be defined by implementing the abstract class `Cell` and overriding callbacks such as `on_left`, `on_entered`, `on_step`, `is_blocking`, and `render`.
- The dynamic programming algorithms "policy evaluation", "policy iteration" and "value iteration" are implemented in `edugrid.algorithms`. They can iteratively be executed and inspected.

## Installation
`pip install edugrid`

## Examples

### Environment creation and modification:

```python
import edugrid
import gymnasium as gym

env = gym.make(
        "philsteg/EduGrid-v0",
        size=(3, 3),
        agent_location=(0, 0),
        wall_locations=[(2, slice(None))],
        sink_locations=[(0, 1), (1, 0)],
        target_locations=[(0, 2)],
        slip_prob=0.5,
    )

# Modify the reward matrix
env.unwrapped.reward_matrix[:, :, :, 0, 0] = 5
```

### Algorithm: Value Iteration

```python
import edugrid
from edugrid.algorithms.dynamic_programming import ValueIteration
import gymnasium as gym

env = gym.make("philsteg/EduGrid-v0")

value_iteration = ValueIteration(env, mode="state", gamma=1.0)

for i, values in enumerate(value_iteration.iter()):
    # Inspect the values in each iteration
    ...

policy = value_iteration.get_policy(values, type="stochastic")
```

See the more sophisticated examples in `examples`.