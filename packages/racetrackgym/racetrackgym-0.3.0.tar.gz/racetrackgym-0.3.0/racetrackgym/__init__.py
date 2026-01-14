from __future__ import annotations

from importlib.metadata import version

import os

__USE_LEGACY_GYM = int(os.environ.get("RACETRACK_USE_GYM", 0))

if __USE_LEGACY_GYM != 0:
    import gym
    from gym.envs.registration import register

else:
    import gymnasium as gym
    from gymnasium.envs.registration import register

__version__ = version(__name__)

try:
    import sys

    from farama_notifications import notifications

    if "racetrack" in notifications and __version__ in notifications["racetrack"]:
        print(notifications["racetrack"][__version__], file=sys.stderr)

except:  # nosec  # noqa: E722, S110
    pass


_RACETRACK_MAP_VERSION = "v0"


def register_racetrack_envs(force: bool = False):  # noqa: FBT001, FBT002
    RT_IDS = [  # noqa: N806
        "barto-small",
        "barto-big",
        "double-track",
        "hansen-bigger",
        "large-curves",
        "maze-small",
        "maze",
        "maze-and-shortcuts",
        "maze-extended",
        "shortcut-big",
        "river-deadend",
        "river-deadend-narrow",
        "empty-40x40",
        "empty-80x80",
    ]

    registry = gym.envs.registration.registry.all() if __USE_LEGACY_GYM else gym.registry
    if f"racetrack-maze-{_RACETRACK_MAP_VERSION}" in registry and not force:
        return

    for rt_id in RT_IDS:
        gym_id = f"racetrack-{rt_id.replace('-', '_')}"
        register(
            id=f"{gym_id}-{_RACETRACK_MAP_VERSION}",
            entry_point="racetrackgym.environment:RacetrackEnv",
            kwargs={"map_name": rt_id},
        )

        register(
            id=f"{gym_id}-cont-{_RACETRACK_MAP_VERSION}",
            entry_point="racetrackgym.environment:RacetrackEnv",
            kwargs={"map_name": rt_id, "continuous": True, "normalize_observation": True},
        )
