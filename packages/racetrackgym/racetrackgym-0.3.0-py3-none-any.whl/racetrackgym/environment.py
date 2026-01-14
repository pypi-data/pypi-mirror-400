#!python3
from __future__ import annotations

import contextlib
import copy
import math
import os
from collections import OrderedDict
from contextlib import redirect_stdout
from pathlib import Path
from typing import TYPE_CHECKING, Any, ClassVar

import numpy as np

import racetrackgym.graphic as g
from racetrackgym import parser, register_racetrack_envs
from racetrackgym.argument_parser import RacetrackParser
from racetrackgym.logger import RTLogger

_USE_LEGACY_GYM = int(os.environ.get("RACETRACK_USE_GYM", 0))

if _USE_LEGACY_GYM != 0:
    import gym
    from gym import spaces
    from gym.utils.env_checker import check_env

else:
    import gymnasium as gym
    from gymnasium import spaces
    from gymnasium.utils.env_checker import check_env


if TYPE_CHECKING:
    from argparse import Namespace

    from numpy.typing import NDArray


def _round(x):
    return int(np.floor(x + 0.5))


def _discretize_position(pos):
    """used for cont. rt. rounds the continuous position to the neareast discrete one. (Each coordinate is round for itself.)

    Args:
        pos ((float, float)): current cont. position.

    Returns:
        ((int,int)): discrete position
    """
    discrete_x = _round(pos[0])
    discrete_y = _round(pos[1])

    return (discrete_x, discrete_y)


class Map:
    """Class representing a racetrack map."""

    def random_line(self, width):
        """method to randomly create a line of the given width within the empty tiles.

        Args:
            width ([int]): width of the line to create

        Returns:
            array [(int, int)]: returns the positions of the line
        """
        while True:
            x = self.rng.integers(0, self.height)
            y = self.rng.integers(0, self.width)

            if self.wall(x, y):
                continue

            vertical = bool(self.rng.integers(2))
            signum = self.rng.choice([-1, 1])

            if vertical:
                ys = [y + i * signum for i in range(width)]
                positions = [(x, new_y) for new_y in ys]

            else:
                xs = [x + i * signum for i in range(width)]
                positions = [(new_x, y) for new_x in xs]

            valid = True
            for pos in positions:
                if self.terminal(pos[0], pos[1]):
                    valid = False

            if not valid:
                continue
            return positions

    def spawn_lines(self, width_goal_line):
        """randomly sets a new goal line of the given width. Reinitializes the distances.

        Args:
            width_goal_line ([type]): width of the goal line to spawn.
        """
        self.height, self.width, self.map = parser.parse_file(
            self.map_path,
            replace_goals=True,
            surround_with_walls=self.surround_with_walls,
        )

        #         self.starters = []
        self.goals = []

        #         first = self.random_line()
        second = self.random_line(width_goal_line)

        #         self.starters = first
        #         for x,y in self.starters:
        #             self.map[x] = self.map[x][:y] + 's' + self.map[x][y+1:]

        self.goals = second
        for x, y in self.goals:
            self.map[x] = self.map[x][:y] + "g" + self.map[x][y + 1 :]

        self.init_distances()

    def init_distances(self):
        """computes and stores the distances from every position to the current goal line and all the wall tiles."""
        distances = np.zeros((self.height, self.width)).tolist()

        for x in range(self.height):
            for y in range(self.width):
                if self.terminal(x, y):
                    all_d = np.zeros(11).tolist()
                else:
                    d = self.calculate_wall_distances(x, y)
                    dg = self.calculate_goal_distances(x, y)
                    all_d = d + dg
                distances[x][y] = all_d
        self.distances = distances

    def calculate_continuous_distances(self, x, y):
        """calculates the distances from the given continuous to the current goal line and all the wall tiles."""
        if self.terminal(x, y):
            all_d = np.zeros(11).tolist()
        else:
            d = self.calculate_continuous_wall_distances(x, y)
            dg = self.calculate_goal_distances(x, y)
            all_d = d + dg
        return all_d

    def __init__(self, map_name, surround_with_walls, rng):
        """creates a map instance. Parses the map file with the provided name. If surround_with_walls is set, addionall wall tiles around the map are created.

        Args:
            map_name ([string]): name of the map file
            surround_with_walls (bool): flag to surround the map with addional wall tiles.

        """
        self.rng = rng
        self.surround_with_walls = surround_with_walls
        self.map_name = map_name

        if not self.map_name.endswith(".track"):
            self.map_name += ".track"

        found_map_file = False
        possible_paths = [
            Path("./maps/"),
            Path(__file__).parent.joinpath("maps"),
        ]
        extended_possible_paths = []
        for path in possible_paths:
            try:
                for name in path.iterdir():
                    current_extended_path = path.joinpath(name)
                    if Path(current_extended_path).is_dir():
                        extended_possible_paths.append(current_extended_path)
            except FileNotFoundError:
                # only one of the two above locations exists, so ignore is some possible dirs don't exist
                pass

        for path in possible_paths + extended_possible_paths:
            self.map_path = path.joinpath(self.map_name)
            if Path(self.map_path).exists():
                found_map_file = True
                break

        if not found_map_file:
            RTLogger.get_logger().error(
                f"Specified map file does not exist or at least couldn't be found: {self.map_name}",
            )

        self.height, self.width, self.map = parser.parse_file(
            self.map_path,
            surround_with_walls=self.surround_with_walls,
        )

        self.starters = []
        self.goals = []
        self.spawnable_positions = []
        for i, row in enumerate(self.map):
            for j, sign in enumerate(row):
                if sign == "s":
                    self.starters.append((i, j))
                    self.spawnable_positions.append((i, j))
                if sign == "g":
                    self.goals.append((i, j))
                if sign == ".":
                    self.spawnable_positions.append((i, j))

        self.dict = {
            0: (-1, -1),
            1: (0, -1),
            2: (1, -1),
            3: (-1, 0),
            4: (0, 0),
            5: (1, 0),
            6: (-1, 1),
            7: (0, 1),
            8: (1, 1),
        }

        self.init_distances()
        #         create distance and goal-distance features

    def calculate_goal_distances(self, x, y):
        """Compute the goal distances for the given position.

        Args:
            x (int): x-value of position
            y (int): y-value of position

        Returns:
            [(int, int, int)]: triple of dx, dy and sum of absolute values of the two former.
        """
        pos = np.array((x, y))

        dx = self.height + 1
        dy = self.width + 1
        d_m = dx + dy
        for goal in self.goals:
            g = np.array(goal)
            d = g - pos
            m = np.abs(d[0]) + np.abs(d[1])
            if m < d_m:
                dx = d[0]
                dy = d[1]
                d_m = m
        return [dx, dy, d_m]

    def calculate_wall_distances(self, x, y):
        """calculates the wall distances for the given position.

        Args:
            x (int): x-value of position
            y (int): y-value of position

        Returns:
            array [int]: returns the eight wall-distance values
        """

        pos = np.array((x, y))
        res = np.zeros(8)

        x_directions = [-1, 0, 1, -1, 1, -1, 0, 1]
        y_directions = [-1, -1, -1, 0, 0, 1, 1, 1]

        for i, (dx, dy) in enumerate(zip(x_directions, y_directions, strict=True)):
            direction = np.array((dx, dy))
            distance = 1
            while True:
                checking_coordinate = pos + distance * direction
                if self.wall(checking_coordinate[0], checking_coordinate[1]):
                    res[i] = distance
                    break
                distance += 1

        return res.tolist()

    def calculate_continuous_wall_distances(self, x, y):
        """calculates the wall distances for the given continuous position via a simple ray marching.

        Args:
            x (float): x-value of position
            y (float): y-value of position

        Returns:
            array [float]: returns the eight wall-distance values
        """
        cell_x, cell_y = _discretize_position((x, y))  # Starting cell

        x_directions = [-1, 0, 1, -1, 1, -1, 0, 1]
        y_directions = [-1, -1, -1, 0, 0, 1, 1, 1]

        res = []

        for dx, dy in zip(x_directions, y_directions, strict=True):
            curr_cell_x, curr_cell_y = cell_x, cell_y

            # Calculate 'time' distance in x and y directions
            t_max_x = (curr_cell_x - x) * dx + 0.5 if dx != 0 else float("inf")
            t_max_y = (curr_cell_y - y) * dy + 0.5 if dy != 0 else float("inf")

            t = 0.0  # time to nearest posible border
            while True:
                if t_max_x < t_max_y:
                    t = t_max_x
                    curr_cell_x += dx
                    t_max_x += dx

                elif t_max_x > t_max_y:
                    t = t_max_y
                    curr_cell_y += dy
                    t_max_y += dy

                else:  # if centered on a cell, we move exactly diagonally
                    t = t_max_x
                    curr_cell_x += dx
                    curr_cell_y += dy

                if self.wall(curr_cell_x, curr_cell_y):
                    res.append(t * math.hypot(dx, dy))  # Euclidean distance
                    break

        return res

    def terminal(self, x, y):
        """whether the given position is a terminal one, i.e., wall, goal, or outside of the map.

        Args:
            x (int): x-value of position
            y (int): y-value of position

        Returns:
            (bool): true if terminal, false else.
        """
        disc_pos = _discretize_position((x, y))
        disc_x, disc_y = disc_pos[0], disc_pos[1]
        if (
            x < 0 or y < 0 or x >= self.height or y >= self.width or (disc_pos in self.goals)
        ):  # this is not the whole truth!
            return True
        return self.map[disc_x][disc_y] == "x"

    def wall(self, x, y):
        """whether the given position is a wall one.

        Args:
            x (int): x-value of position
            y (int): y-value of position

        Returns:
            (bool): true if wall, false else.
        """
        if x < 0 or y < 0 or x >= self.height or y >= self.width:
            return True
        return self.map[x][y] == "x"

    def __eq__(self, other):
        if other is None:
            return False

        return other.map_name == self.map_name


class Environment:
    """class representing the racetrack game."""

    graphical_state: NDArray | None

    def __init__(
        self,
        rt_args: Namespace,
        clone_call: bool = False,
    ):
        """initializes an object of the class with the given arguments.

        Args:
            rt_args (Namespace): contains all the rt arguments to use. see argument_parser.py
            clone_call (bool, optional): if set to true, most steps of the init will be skipped because the env will be cloned anyway. Defaults to False.
        """
        self.rt_args = rt_args
        self.dtype = np.float32 if self.rt_args.continuous else np.int32

        self.noisy = rt_args.noise
        self.random_start = rt_args.random_start
        self.random_velocity = rt_args.random_velocity
        self.landmarking = rt_args.landmarking
        self.gamma = rt_args.gamma

        # initialise environment rng
        self.rng = np.random.default_rng(rt_args.seed)
        self.graphical_state = None

        self.terminate_on_crash = not rt_args.no_terminate_on_crash
        self.reset_stored_path = not rt_args.no_reset_stored_path

        if not clone_call:
            self.surround_with_walls = rt_args.surround_with_walls
            self.map = Map(rt_args.map_name, self.surround_with_walls, self.rng)

            if self.random_start:
                x = self.rng.integers(low=0, high=self.map.height)
                y = self.rng.integers(low=0, high=self.map.width)
                while self.map.terminal(x, y):
                    x = self.rng.integers(low=0, high=self.map.height)
                    y = self.rng.integers(low=0, high=self.map.width)
                self.position = np.array([x, y], dtype=self.dtype)
            else:
                self.position = np.array(self.rng.choice(self.map.starters), dtype=self.dtype)

            if self.random_velocity:
                vx = self.rng.integers(0, rt_args.maximal_random_velocity)
                vy = self.rng.integers(0, rt_args.maximal_random_velocity)
            else:
                vx = 0
                vy = 0
            self.velocity = np.array((vx, vy), dtype=self.dtype)

            self.done = False

            self.path = [self.position]

            if self.landmarking:
                self.potentials = self.read_potential_map()

    def spawn_lines(self):
        """spawns a new, randomly placed goal line."""
        self.map.spawn_lines(self.rt_args.width_goal_line)

    def read_potential_map(self):
        """reads the potentials from a potential file that corresponds to the given map file. Useful for reward shaping.


        Returns:
            array (int): two-dimensional array containing the potentials.
        """
        other_name = self.map.map_path[:-5] + "potentials"
        with Path(other_name).open("r+") as f:
            potential_array = np.zeros((self.map.height, self.map.width))

            for j, line in enumerate(f):
                for i, sign in enumerate(line.split()):
                    if not self.map.wall(j, i):
                        # TODO: 2x is an experiment, remove this
                        potential_array[j][i] = 2 * int(sign)

        return potential_array

    def __eq__(self, other):
        """checks equality of this and the other instance of the rt game

        Args:
            other (Racetrack): other instance of rt game.

        Returns:
            bool: True, if position and velocity are equal. False otherwise.
        """
        if other is None:
            return False
        return (
            (self.position == other.position).all()
            and (self.velocity == other.velocity).all()
            and self.map == other.map
        )

    def clone(self, deep_map=False, deep_rng=False):
        """creates a clone of the current instance.

        Args:
            deep (bool, optional): Whether to make a deep clone (also cloning the map and the rng) or just using the references. Defaults to False.

        Returns:
            [type]: [description]
        """
        oe = Environment(
            rt_args=self.rt_args,
            clone_call=True,
        )
        if deep_map:
            oe.map = copy.deepcopy(self.map)
        else:
            oe.map = self.map
        if deep_rng:
            oe.rng = copy.copy(self.rng)
        else:
            oe.rng = self.rng

        oe.position = copy.copy(self.position)
        oe.velocity = copy.copy(self.velocity)
        oe.path = copy.copy(self.path)
        oe.done = copy.copy(self.done)

        if self.landmarking:
            oe.potentials = copy.copy(self.potentials)

        return oe

    def calculate_intermediates(self, x, y, dx, dy):  # dx, dy continuous
        """provides all intermediates when steering with velocity dx dy starting in x y

        Args:
            x (int): x-value of position
            y (int): y-value of position
            dx (int): x-value of velocity
            dy (int): y-value of velocity

        Returns:
            [type]: [description]
        """
        # trivial case:
        if dx == 0 and dy == 0:
            return [(_round(x), _round(y))]

        if dx == 0:
            m = np.sign(dy)
            rounded_x = _round(x)
            return [(rounded_x, _round(y + i * m)) for i in range(int(np.abs(dy)) + 1)]

        if dy == 0:
            m = np.sign(dx)
            rounded_y = _round(y)
            return [(_round(x + i * m), rounded_y) for i in range(int(np.abs(dx)) + 1)]

        # if self.rt_args.continuous:
        abs_max = max(abs(dx), abs(dy))
        m_x = dx / abs_max
        m_y = dy / abs_max
        return [(_round(x + i * m_x), _round(y + i * m_y)) for i in range(int(abs_max) + 1)]

    def show(
        self,
        hide_positions=False,
        graphical=False,
        show_landmarks=False,
        additional_return=False,
        hide_start_line=False,
    ):
        """method to show the current state of the rt game.

        Args:
            hide_positions (bool, optional): hide positions, show map only. Defaults to False.
            graphical (bool, optional): use graphical representation intead of string one. Defaults to False.
            show_landmarks (bool, optional): visualize the landmarks. Defaults to False.
            additional_return (bool, optional): additionally to showing the picture, return it. May be used to save the graphical representation. Defaults to False.
            hide_start_line (bool, optional): hide start line. Defaults to False.

        Returns:
            img: potentially the image
        """
        if graphical:
            map_repr = g.create_map(
                self,
                show_path=(not hide_positions),
                show_landmarks=show_landmarks,
                hide_start_line=hide_start_line,
            )

        else:
            map_repr = [list(line) for line in self.map.map]

            if not hide_positions:
                for i, position in enumerate(self.path):
                    RTLogger.get_logger().debug(
                        "env.show, iteration %i with position %s",
                        i,
                        str(position),
                    )
                    x, y = _discretize_position(position)
                    if not (x < 0 or y < 0 or x >= self.map.height or y >= self.map.width):
                        map_repr[x][y] = str(i % 10)

            for line in map_repr:
                print("".join(line))

        if additional_return:  # Why even take this arg and not always return?
            return map_repr
        return None

    def reward(self, old_position, action):
        """reward function. Depends on the arguments set by rt_args in the init step.

        Args:
            old_position ((int, int))): old position
            action (int): the choosen action

        Returns:
            [int]: computed reward function.
        """
        res = self.rt_args.step_reward

        intermediates = self.calculate_intermediates(
            old_position[0],
            old_position[1],
            self.velocity[0],
            self.velocity[1],
        )

        if _discretize_position(self.position) not in intermediates:
            intermediates.append(_discretize_position(self.position))

        for intermediate in intermediates:
            if intermediate in self.map.goals:
                RTLogger.get_logger().debug("Reached goal, position: %s", str(intermediate))
                self.done = True
                self.reached_goal = True
                res = self.rt_args.positive_reward
                break
            if self.map.wall(intermediate[0], intermediate[1]):
                RTLogger.get_logger().debug("Crashed, position: %s", str(intermediate))
                self.done = True
                res = self.rt_args.negative_reward
                break

        discrete_pos = _discretize_position(self.position)
        self.positions_path.append(discrete_pos)
        if self.rt_args.continuous:
            if (
                self.rt_args.penalize_standing_still
                and abs(res - self.rt_args.step_reward) < 1e-6
                and np.allclose(self.position, old_position, atol=1e-3)
                and np.linalg.norm(self.velocity) < 1e-3
                and np.linalg.norm(action) < 1e-3
            ):
                res += self.rt_args.negative_reward / 10

            if (
                self.rt_args.penalize_revisiting_states
                and not np.allclose(action, [0.0, 0.0], atol=1e-3)
                and self.positions_path.count(discrete_pos) > 1
            ):
                res += self.rt_args.negative_reward / 10

        else:
            if (
                self.rt_args.penalize_standing_still
                and res == self.rt_args.step_reward
                and (self.position == old_position).all()
                and (self.velocity == 0).all()
                and (action == 0).all()
            ):
                res += self.rt_args.negative_reward / 10

            if (
                self.rt_args.penalize_revisiting_states
                and not (action == 0).all()
                and self.positions_path.count(discrete_pos) > 1
            ):
                res += self.rt_args.negative_reward / 10

        # For all terminal states (win and lose!) the potential must be zero to preserve the optimal policy
        if self.landmarking:
            if res != self.rt_args.step_reward:
                potential_to = 0
            else:
                new_pos = intermediates[-1]
                potential_to = self.potentials[new_pos[0]][new_pos[1]]
            potential_from = self.potentials[old_position[0]][old_position[1]]

            F = self.gamma * potential_to - potential_from

            res += F

        return res

    def light_step(self, action):
        """perform a light step, i.e., clone the environment, perform the action, return the clone.

        Args:
            action (int or float): action to apply in the clone
            clone_rng (bool, optional): see Environment.clone

        Returns:
            (Environment): other instance of this class
        """
        other_env = self.clone()
        res = other_env.step(action)
        return other_env, res

    def step(self, action):
        """Center piece of this class. Performs the given action in the racetrack game.
        Action is either int or float, depending on the game variant.

        Args:
            action (int or float): action to apply

        Returns:
            (int, array [int], bool): reward, state reached, termination flag.
        """
        if self.done:
            print("Already done, step has no further effect")
            return self.rt_args.step_reward, (self.position, self.velocity), self.done

        if self.rt_args.continuous:
            x_action = action[0]
            y_action = action[1]
            assert -1 <= x_action <= 1 and -1 <= y_action <= 1, "both ct actions must be in [-1,1]"
        else:
            action = np.array(self.map.dict[action])

        # NOISE!
        if self.noisy:
            self.last_noisy = self.rng.random() < self.rt_args.noise_probability
            if self.last_noisy:
                # 4 is the number of action doing nothing
                action = 4
                action = np.array(self.map.dict[action])

        self.velocity = self.velocity + action
        old_position = self.position.copy()
        self.position = self.position + self.velocity

        if not self.terminate_on_crash:
            # Eliminates crashes. This way the agent just stands still instead of crashing
            intermediates = self.calculate_intermediates(
                self.position[0],
                self.position[1],
                self.velocity[0],
                self.velocity[1],
            )

            for intermediate in intermediates:
                if self.map.wall(intermediate[0], intermediate[1]):
                    self.velocity = np.array([0, 0])
                    self.position = old_position
                    break

        # call reward function
        reward = self.reward(old_position=old_position, action=action)

        if not self.done:  # Do not store crashed position
            self.path.append(self.position)

        # actually, the state is defined through pos and velocity and the distances are only features
        # for reasons of simpler implementation, the features here are returned together with the state
        state = self.get_state()
        return reward, state, self.done

    def reset(self):
        """reset the rt game. Must be used before starting a new training episode.

        Returns:
            array [int]: initial state.
        """
        self.positions_path = []
        if self.random_start:
            x = self.rng.integers(0, self.map.height)
            y = self.rng.integers(0, self.map.width)
            while self.map.terminal(x, y):
                x = self.rng.integers(0, self.map.height)
                y = self.rng.integers(0, self.map.width)
            self.position = np.array([x, y], dtype=self.dtype)
        else:
            self.position = np.array(self.rng.choice(self.map.starters), dtype=self.dtype)

        if self.random_velocity:
            vx = self.rng.integers(0, self.rt_args.maximal_random_velocity)
            vy = self.rng.integers(0, self.rt_args.maximal_random_velocity)
        else:
            vx = 0
            vy = 0
        self.velocity = np.array((vx, vy), dtype=self.dtype)

        self.last_noisy = False
        self.reached_goal = False
        self.done = False

        if self.reset_stored_path:
            self.path = [self.position]

        return self.get_state()

    def reset_to_state(self, pos, velo=None):
        """resets the game and sets the position (and possibly velocity) to the given values.
        If no velocity is given, it is chosen acording to the current game mode.

        Args:
            pos ((int,int)) or ((float, float)): position to reset the rt game to.
            velo ((int,int) or ((float, float)), optional): velocity to reset the rt game to. Defaults to None.
        """
        self.reset()

        self.position = np.array(pos, dtype=self.dtype)

        if velo is not None:
            self.velocity = np.array(velo, dtype=self.dtype)

        if self.reset_stored_path:
            self.path = [self.position]

    def calculate_children(self):
        """calculate all possible sucessor states

        Returns:
            array [int, array[int]]: array containing the applied action and the resulting successor.
        """
        res = []
        for action in range(9):
            acc = self.map.dict[action]
            vel = self.velocity + acc
            pos = self.position - vel
            res.append((action, list(pos) + list(vel) + self.map.distances[pos[0]][pos[1]]))

        return res

    def get_graphical_state(self, state=None, *, show_velocity: bool = False):
        """get state represented by an greyscale image

        Returns:
            two dimensional array [int]: array containing the greyscale values
        """
        val = 1 / 4 if show_velocity else 1 / 3

        if self.graphical_state is None:
            self.graphical_state = np.zeros((self.map.height, self.map.width))
            for i, row in enumerate(self.map.map):
                for j, sign in enumerate(row):
                    # there is absolutely no difference between a starting state and a normal state
                    # during a race -> thus we handle it equally
                    if sign in (".", "s"):
                        self.graphical_state[i][j] = 0
                        continue
                    if sign == "x":
                        self.graphical_state[i][j] = 1 - val
                        continue
                    if sign == "g":
                        self.graphical_state[i][j] = 1
                        continue
                    print("could not identify ", sign)

        if state is None:
            x, y = self.position
            vx, vy = self.velocity
        else:
            x, y, vx, vy = state[:4]

        res = np.copy(self.graphical_state)

        # HACK: We store the numpy array with the first call.
        # Thus, we cannot reuse it later if show_velocity changes
        res[(res != 0) & (res != 1)] = 1 - val

        res[y][x] = val  # position
        if show_velocity:
            res[vy][vx] = 2 - val

        return [res, self.velocity]

    def get_state(self):
        """value-based representation of the current state.

        Returns:
            array[int or float]: current state.
        """
        x, y = self.position
        if not self.done:
            if self.rt_args.continuous:
                distance = self.map.calculate_continuous_distances(x, y)
                return list(self.position) + list(self.velocity) + distance
            return list(self.position) + list(self.velocity) + self.map.distances[x][y]
        return list(self.position) + list(self.velocity) + [0] * 11

    def applicable_actions(self):
        """returns list of applicable actions.
        Actually, this is a kind of lazy method, as for the rt game, this is (nearly) always the same.
        Still, is is neede by some algorithms.

        Returns:
            array [int]: list of applicable actions.
        """
        if not self.done:
            return list(range(9))
        return []

    def get_state_rep(self, pos, velo=None):
        """
        Given a position (x,y) and a velocity (optional (x,y))

        Returns:
            array[int or float]: state representation with given position and velocity (or (0,0)
                                 if not specified)
        """
        if velo is None:
            velo = (0, 0)

        x, y = pos
        if self.rt_args.continuous:
            distance = self.map.calculate_continuous_distances(x, y)
            return list(pos) + list(velo) + distance
        return list(pos) + list(velo) + self.map.distances[x][y]


class RacetrackEnv(gym.Env):
    metadata: ClassVar[dict[str, Any]] = {"render_modes": ["human"]}

    def __init__(
        self,
        map_name: str,
        rt_args: Namespace | str,
        render_mode: str = "human",
        *,
        continuous: bool = False,
        normalize_observation: bool = False,
    ):
        if isinstance(rt_args, str):
            rt_parser = RacetrackParser()
            split_stripped = [a.strip("\"'") for a in rt_args.split()]
            rt_args = rt_parser.parse_args([map_name, *split_stripped])
        else:
            rt_args.map_name = map_name

        if rt_args.continuous:
            from racetrackgym import _RACETRACK_MAP_VERSION  # noqa: PLC0415

            raise ValueError(
                f"Use the continuous version instead of passing --continuous:"
                f" racetrack-{map_name}-cont-{_RACETRACK_MAP_VERSION}",
            )

        super().__init__()

        rt_args.continuous = continuous
        self.continuous = rt_args.continuous
        self.normalize_observation = normalize_observation
        if self.normalize_observation and not self.continuous:
            RTLogger.get_logger().warn(
                "Normalizing observations in discrete environment setting. Please check whether this is intended!",
            )
        self.racetrack_env = Environment(rt_args)

        # Action space is the same as applicable actions in any state
        if self.continuous:
            self.action_space = spaces.Box(low=-1, high=1, shape=(2,), dtype=np.float32)
        else:
            self.action_space = spaces.Discrete(len(self.racetrack_env.applicable_actions()))

        # Observation space is composite
        rt_map = self.map

        self.rt_width = rt_map.width
        self.rt_height = rt_map.height
        self.max_distance = np.max(rt_map.distances)

        self.max_velocity = max(self.rt_width, self.rt_height)  # We could split these apart I guess
        if self.continuous or self.normalize_observation:
            if normalize_observation:
                self.observation_space = spaces.Dict(
                    {
                        "position": spaces.Box(
                            low=np.array([-1, -1]),
                            high=np.array([1, 1]),
                            dtype=np.float32,
                        ),
                        "velocity": spaces.Box(
                            low=-1,
                            high=1,
                            shape=(2,),
                            dtype=np.float32,
                        ),
                        "distances": spaces.Box(
                            low=-1,
                            high=1,
                            shape=(11,),
                            dtype=np.float32,
                        ),
                    },
                )
            else:
                self.observation_space = spaces.Dict(
                    {
                        "position": spaces.Box(
                            low=np.array([0, 0]),
                            high=np.array([self.rt_height, self.rt_width]),
                            dtype=np.float32,
                        ),
                        "velocity": spaces.Box(
                            low=-self.max_velocity,
                            high=self.max_velocity,
                            shape=(2,),
                            dtype=np.float32,
                        ),
                        "distances": spaces.Box(
                            low=-self.max_distance,
                            high=self.max_distance,
                            shape=(11,),
                            dtype=np.float32,
                        ),
                    },
                )
        else:
            self.observation_space = spaces.Dict(
                {
                    "position": spaces.Box(
                        low=np.array([0, 0], dtype=np.int32),
                        high=np.array([self.rt_height, self.rt_width], dtype=np.int32),
                        dtype=np.int32,
                    ),
                    "velocity": spaces.Box(
                        low=-self.max_velocity,
                        high=self.max_velocity,
                        shape=(2,),
                        dtype=np.int32,
                    ),  # Because these can be negative, we need to use Box
                    "distances": spaces.Box(
                        low=-self.max_distance,
                        high=self.max_distance,
                        shape=(11,),
                        dtype=np.int32,
                    ),  # Because these can be negative, we need to use Box
                },
            )

    def gen_obs(self):
        state = self.racetrack_env.get_state()

        return (self._state_to_dict(state), {"experienced_noise": self.racetrack_env.last_noisy})

    def _state_to_dict(self, state) -> OrderedDict:
        # HACK! Make sure the new observation are in bounds. We can either do something like this
        # or adjust the position bounds in the observation space.
        # I guess this should be fine as long as we are surrounded by walls... ?
        def clamp_pos_to_valid(state):
            return (
                min(max(0, state[0]), self.rt_height - 1),
                min(max(0, state[1]), self.rt_width - 1),
            )

        res = OrderedDict(
            position=np.array(
                [*clamp_pos_to_valid(state)],
                dtype=self.dtype,
            ),
            velocity=np.array(
                state[2:4],
                dtype=self.dtype,
            ),
            distances=np.array(
                state[4:],
                dtype=self.dtype,
            ),
        )
        if self.normalize_observation:
            res["distances"] = (res["distances"] / self.max_distance).astype(self.dtype)
            res["position"][0] = (2 * (res["position"][0] / self.rt_height) - 1).astype(self.dtype)
            res["position"][1] = (2 * (res["position"][1] / self.rt_width) - 1).astype(self.dtype)
            res["velocity"] = (res["velocity"] / self.max_velocity).astype(self.dtype)

        return res

    def step(self, action):
        reward, state, terminated = self.racetrack_env.step(action)

        if _USE_LEGACY_GYM:
            return self._state_to_dict(state), reward, terminated, {}

        return (
            self._state_to_dict(state),
            reward,
            terminated,
            False,  # No internal truncation, use gym.TimeLimit
            {
                "experienced_noise": self.racetrack_env.last_noisy,
                "is_success": self.racetrack_env.reached_goal,
            },
        )

    def reset_to_state(
        self,
        state,
        seed=None,
        options=None,
        *args,
        **kwargs,
    ):
        if not _USE_LEGACY_GYM and seed is not None:
            super().reset(seed=seed, options=options)
            self.racetrack_env.rng = self.np_random

        self.racetrack_env.reset_to_state(state["position"], state["velocity"])

        state_dict = self._state_to_dict(self.racetrack_env.get_state())

        if _USE_LEGACY_GYM:
            return state_dict
        return (
            state_dict,
            {"experienced_noise": False},  # Started here, no reason to have exp. noise here
        )

    def reset(self, seed=None, options=None):
        if not _USE_LEGACY_GYM and seed is not None:
            super().reset(seed=seed, options=options)
            self.racetrack_env.rng = self.np_random

        state = self.racetrack_env.reset()
        state_dict = self._state_to_dict(state)

        if _USE_LEGACY_GYM:
            return state_dict
        return (
            self._state_to_dict(state),
            {"experienced_noise": False},
        )

    def render(
        self,
        *args,
        emojify: bool = True,
        shielded_action_mask=None,
        **kwargs,
    ):
        """
        Render the current state of the environment.

        Args:
            emojify: Whether to print the environment in a more human readable format, with emojis.
            shielded_action_mask: List of actions mask, defining the shielded actions. See below.
            *args: Arguments to pass to the show method of the environment.
            **kwargs: Keyword arguments to pass to the show

        shielded_action_mask is expected to be a length 9 list, with the i'th element representing the i'th action,
        where an entry of np.inf means that the action is shielded, otherwise it is not.
        """

        # Suppress the print of the underlying rt environment
        kwargs["additional_return"] = True
        with Path(os.devnull).open("w") as devnull, redirect_stdout(devnull):
            str_rep = self.racetrack_env.show(*args, **kwargs)

        to_print = str_rep.copy()

        # Draw in future position. This is nice to see for the non-pretty print as well
        future_pos = self.position + self.velocity
        with contextlib.suppress(Exception):
            if (
                not np.all(self.velocity == 0)
                and 0 < future_pos[0] < self.height
                and 0 < future_pos[1] < self.width
            ):
                to_print[future_pos[0]][future_pos[1]] = "⧖"

        # If shield should be drawn compute the values
        if shielded_action_mask is not None:
            if len(shielded_action_mask) != 0:
                raise ValueError("Shield mask must have length 9.")

            if emojify:
                shield_pos = [
                    self.map.dict[i] for i, s in enumerate(shielded_action_mask) if np.isinf(s)
                ]
                shield_on_map = [s + self.position for s in shield_pos]
                for s in shield_on_map:
                    with contextlib.suppress(Exception):
                        to_print[s[0]][s[1]] = (
                            "🟨" if np.any(np.array(s) != self.position) else to_print[s[0]][s[1]]
                        )

        # Convert to string and draw in emojis if requested
        to_print = "\n".join(["".join(line) for line in to_print])
        if emojify:
            to_print = (
                to_print.replace("1", "1️⃣")
                .replace("2", "2️⃣")
                .replace("3", "3️⃣")
                .replace("4", "4️⃣")
                .replace("5", "5️⃣")
                .replace("6", "6️⃣")
                .replace("7", "7️⃣")
                .replace("8", "8️⃣")
                .replace("9", "9️⃣")
                .replace("0", "0️⃣")
                .replace("x", "⬛")
                .replace("s", "🟩")
                .replace("g", "🟥")
                .replace(".", "⬜")
                .replace("⧖", "🟦")
            )

        print(to_print)
        return str_rep

    def close(self):
        pass

    def get_distances(self, x, y):
        if self.racetrack_env.rt_args.continuous:
            return self.racetrack_env.map.calculate_continuous_distances(x, y)
        return self.distances[x][y]

    @property
    def starters(self):
        return self.racetrack_env.map.starters

    @property
    def path(self):
        return self.racetrack_env.path

    @property
    def width(self):
        return self.racetrack_env.map.width

    @property
    def height(self):
        return self.racetrack_env.map.height

    @property
    def position(self):
        return self.racetrack_env.position

    @position.setter
    def position(self, value):
        self.racetrack_env.position = value

    @property
    def velocity(self):
        return self.racetrack_env.velocity

    @property
    def map(self):
        return self.racetrack_env.map

    @property
    def distances(self):
        return self.racetrack_env.map.distances

    @property
    def rt_args(self):
        return self.racetrack_env.rt_args

    @property
    def dtype(self):
        return self.racetrack_env.dtype


if __name__ == "__main__":
    register_racetrack_envs()

    env = gym.make(
        "racetrack-empty_40x40-v0",
        max_episode_steps=100,
        render_mode="human",
        rt_args="-sww -n -np 0.25",
    )
    check_env(env.unwrapped)

    obs, _ = env.reset(seed=1)
    env.render()

    print(env.observation_space)
    print(env.action_space)
    print(env.action_space.sample())

    n_steps = 20
    for step in range(n_steps):
        print(f"Step {step + 1}")
        print(f"state: {obs}")
        act = input(f"Next action {'[x,y]' if env.get_wrapper_attr('continuous') else '(0-9)'}: ")
        parsed_act = eval(act) if env.get_wrapper_attr("continuous") else int(act)
        obs, reward, terminated, truncated, info = env.step(parsed_act)
        done = terminated or truncated
        print(f"{obs=}\t{reward=}\t{done=}")
        env.render()
        if done:
            print(f"Terminal state reached! {reward=}")
            break
