import argparse


class RacetrackParser(argparse.ArgumentParser):
    def __init__(self):
        super().__init__()

        racetrack = self.add_argument_group("racetrack")

        # RT args
        racetrack.add_argument(
            "map_name",
            type=str,
            help="the map to run the racetrack on",
        )

        # RT args
        racetrack.add_argument(
            "-s",
            "--seed",
            help="seed for the racetrack env",
            default=0,
            type=int,
        )
        racetrack.add_argument(
            "-sr",
            "--step_reward",
            "--step-reward",
            help="reward for each step",
            default=0,
            type=float,
        )
        racetrack.add_argument(
            "-g",
            "--gamma",
            help="discount factor, used for landmarking",
            default=0.99,
            type=float,
        )
        racetrack.add_argument(
            "-nr",
            "--negative_reward",
            "--negative-reward",
            help="reward for hitting a wall",
            default=-20,
            type=float,
        )
        racetrack.add_argument(
            "-pr",
            "--positive_reward",
            "--positive-reward",
            help="reward for reaching the goal",
            default=100,
            type=float,
        )

        # RT binaries
        racetrack.add_argument(
            "-n",
            "--noise",
            help="use noisy version of racetrack",
            action="store_true",
        )
        racetrack.add_argument(
            "-rs",
            "--random_start",
            "--random-start",
            help="start racetrack from anywhere",
            action="store_true",
        )
        racetrack.add_argument(
            "-rv",
            "--random_velocity",
            "--random-velocity",
            help="start racetrack with random velocity",
            action="store_true",
        )
        racetrack.add_argument(
            "-l",
            "--landmarking",
            help="use landmarking. Requires a potential file",
            action="store_true",
        )
        racetrack.add_argument(
            "-sww",
            "--surround_with_walls",
            "--surround-with-walls",
            help="sorround map with walls",
            action="store_true",
        )
        racetrack.add_argument(
            "-ct",
            "--continuous",
            help="use continiuous version of rt",
            action="store_true",
        )
        racetrack.add_argument(
            "-pss",
            "--penalize_standing_still",
            "--penalize-standing-still",
            help="give 1/10 of nr if the agent decides to stand still",
            action="store_true",
        )
        racetrack.add_argument(
            "-ntoc",
            "--no-terminate-on-crash",
            "---no-terminate_on_crash",
            action="store_true",
        )
        racetrack.add_argument(
            "-nrsp",
            "--no_reset_stored_path",
            "--no-reset-stored-path",
            help="reset the stored path when resetting the environment",
            action="store_true",
        )

        racetrack.add_argument(
            "-prs",
            "--penalize_revisiting_states",
            "--penalize-revisiting-states",
            help="give 1/10 of nr if the agent decides to revisit an already visited state",
            action="store_true",
        )

        # RT options
        racetrack.add_argument(
            "-np",
            "--noise_probability",
            "--noise-probability",
            help="noise probability",
            default=0.1,
            type=float,
        )
        racetrack.add_argument(
            "-mrv",
            "--maximal_random_velocity",
            "--maximal-random-velocity",
            help="maximal probability used for rv",
            default=5,
            type=int,
        )
        racetrack.add_argument(
            "-wgl",
            "--width_goal_line",
            "--width-goal-line",
            help="with of the goal line. Only applicable when spawning new lines",
            default=3,
            type=int,
        )
