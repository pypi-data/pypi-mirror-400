from __future__ import annotations

from enum import Enum, IntEnum, IntFlag, auto
from typing import Optional

__all__ = (
    "Achievement",
    "ServerGamemode",
    "Difficulty",
    "AddonStatus",
    "AddonType",
)


class Achievement(IntEnum):
    CHRISTOFFEL_COLUMBUS = auto()
    STRIKE = auto()
    ARCH_ENEMY = auto()
    MARATHONER = auto()
    SKID_ROW = auto()
    GOLD_DRIVER = auto()
    POWERUP_LOVE = auto()
    UNSTOPPABLE = auto()
    BANANA_LOVER = auto()
    ITS_SECRET = auto()
    MOSQUITO_HUNTER = auto()
    BEYOND_LUCK = auto()

    def __str__(self) -> Optional[str]:

        lookup: dict[Achievement, str] = {
            Achievement.CHRISTOFFEL_COLUMBUS: "Christoffel Columbus",
            Achievement.STRIKE: "Strike!",
            Achievement.ARCH_ENEMY: "Arch Enemy",
            Achievement.MARATHONER: "Marathoner",
            Achievement.SKID_ROW: "Skid Row",
            Achievement.GOLD_DRIVER: "Gold Driver",
            Achievement.POWERUP_LOVE: "Powerup Love",
            Achievement.UNSTOPPABLE: "Unstoppable",
            Achievement.BANANA_LOVER: "Banana Lover",
            Achievement.ITS_SECRET: "It's Secret",
            Achievement.MOSQUITO_HUNTER: "Mosquito Hunter",
            Achievement.BEYOND_LUCK: "Beyond Luck",
        }

        return lookup.get(self, self.name)


class ServerGamemode(IntEnum):
    NORMAL_RACE_GRAND_PRIX = 0
    TIME_TRIAL_GRAND_PRIX = 1
    NORMAL_RACE = 3
    TIME_TRIAL = 4
    SOCCER = 6
    FREE_FOR_ALL = 7
    CAPTURE_THE_FLAG = 8

    def __str__(self) -> Optional[str]:
        lookup: dict[ServerGamemode, str] = {
            ServerGamemode.NORMAL_RACE: "Normal Race",
            ServerGamemode.TIME_TRIAL: "Time Trial",
            ServerGamemode.SOCCER: "Soccer",
            ServerGamemode.FREE_FOR_ALL: "Free For All",
            ServerGamemode.SOCCER: "Soccer",
            ServerGamemode.NORMAL_RACE_GRAND_PRIX: "Normal Race (Grand Prix)",
            ServerGamemode.TIME_TRIAL_GRAND_PRIX: "Time Trial (Grand Prix)",
        }

        return lookup.get(self, self.name)


class Difficulty(IntEnum):
    NOVICE = 0
    INTERMEDIATE = 1
    EXPERT = 2
    SUPERTUX = 3
    PLACEHOLDER = 4

    def __str__(self):
        lookup: dict[Difficulty, str] = {
            Difficulty.NOVICE: "Novice",
            Difficulty.INTERMEDIATE: "Intermediate",
            Difficulty.EXPERT: "Expert",
            Difficulty.SUPERTUX: "SuperTux",
        }

        return lookup.get(self, self.name)


class AddonStatus(IntFlag):
    APPROVED = auto()
    ALPHA = auto()
    BETA = auto()
    RC = auto()
    INVISIBLE = auto()
    RESERVED2 = auto()
    DFSG = auto()
    FEATURED = auto()
    LATEST = auto()
    TEX_NOT_POWER_OF_2 = auto()


class AddonType(Enum):
    KART = "kart"
    TRACK = "track"
    ARENA = "arena"
