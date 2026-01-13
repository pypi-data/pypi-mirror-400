from dataclasses import dataclass, fields, asdict
from typing import Iterator
from .enums import Skill as SkillEnum, Activity as ActivityEnum


class Base:
    """
    Base class for models.
    """

    def to_dict(self):
        """
        Returns the dataclass as a dictionary.
        """
        return asdict(self)


@dataclass(frozen=True)
class Skill(Base):
    """
    Represents player's skill.
    """

    id: int
    name: str
    rank: int
    level: int
    experience: int

    @classmethod
    def from_json(cls, json: dict) -> "Skill":
        """
        Creates Skill from JSON data.

        :param json: JSON data as dictionary.
        :type json: dict
        :return: Skill data class which contains skill data.
        :rtype: Skill
        """
        id: int = json["id"]
        name: str = json["name"]
        rank: int = json["rank"]
        level: int = json["level"]
        experience: int = json["xp"]

        return cls(id, name, rank, level, experience)


@dataclass(frozen=True)
class SkillsCollection(Base):
    """
    Represents a collection of skills.
    """

    overall: Skill
    attack: Skill
    defence: Skill
    strength: Skill
    hitpoints: Skill
    ranged: Skill
    prayer: Skill
    magic: Skill
    cooking: Skill
    woodcutting: Skill
    fletching: Skill
    fishing: Skill
    firemaking: Skill
    crafting: Skill
    smithing: Skill
    mining: Skill
    herblore: Skill
    agility: Skill
    thieving: Skill
    slayer: Skill
    farming: Skill
    runecraft: Skill
    hunter: Skill
    construction: Skill
    sailing: Skill

    def __iter__(self) -> Iterator[Skill]:
        for field in fields(self):
            yield getattr(self, field.name)

    @classmethod
    def from_json(cls, json: dict) -> "SkillsCollection":
        """
        Creates SkillsCollection from JSON data.

        :param json: JSON data as dictionary.
        :type json: dict
        :return: SkillsCollection data class which contains all skills and their data.
        :rtype: SkillsCollection
        """
        skills_json = json["skills"]

        skills_dict: dict[str, Skill] = {}

        for skill_enum in SkillEnum:
            skill_json: dict = skills_json[skill_enum.value]
            skills_dict[skill_enum.name.lower()] = Skill.from_json(skill_json)

        return SkillsCollection(**skills_dict)


@dataclass(frozen=True)
class Activity(Base):
    """
    Represents activity, for example Barrows kill count.
    """

    id: int
    name: str
    rank: int
    score: int

    @classmethod
    def from_json(cls, json: dict) -> "Activity":
        id: int = json["id"]
        name: str = json["name"]
        rank: int = json["rank"]
        score: int = json["score"]

        return cls(id, name, rank, score)

@dataclass(frozen=True)
class ActivitiesCollection(Base):
    """
    Represents a collection of activities.
    """

    grid_points: Activity
    league_points: Activity
    deadman_points: Activity

    bounty_hunter_hunter: Activity
    bounty_hunter_rogue: Activity
    bounty_hunter_legacy_hunter: Activity
    bounty_hunter_legacy_rogue: Activity

    clue_scrolls_all: Activity
    clue_scrolls_beginner: Activity
    clue_scrolls_easy: Activity
    clue_scrolls_medium: Activity
    clue_scrolls_hard: Activity
    clue_scrolls_elite: Activity
    clue_scrolls_master: Activity

    last_man_standing_rank: Activity
    pvp_arena_rank: Activity
    soul_wars_zeal: Activity
    rifts_closed: Activity
    colosseum_glory: Activity
    collections_logged: Activity

    abyssal_sire: Activity
    alchemical_hydra: Activity
    amoxliatl: Activity
    araxxor: Activity
    artio: Activity

    barrows_chests: Activity
    bryophyta: Activity

    callisto: Activity
    calvarion: Activity
    cerberus: Activity
    chambers_of_xeric: Activity
    chambers_of_xeric_challenge_mode: Activity
    chaos_elemental: Activity
    chaos_fanatic: Activity
    commander_zilyana: Activity
    corporeal_beast: Activity
    crazy_archaeologist: Activity

    dagannoth_prime: Activity
    dagannoth_rex: Activity
    dagannoth_supreme: Activity
    deranged_archaeologist: Activity
    doom_of_mokhaiotl: Activity
    duke_sucellus: Activity

    general_graardor: Activity
    giant_mole: Activity
    grotesque_guardians: Activity

    hespori: Activity

    kalphite_queen: Activity
    king_black_dragon: Activity
    kraken: Activity
    kree_arra: Activity
    kril_tsutsaroth: Activity

    lunar_chests: Activity

    mimic: Activity

    nex: Activity
    nightmare: Activity
    phosanis_nightmare: Activity

    obor: Activity
    phantom_muspah: Activity

    sarachnis: Activity
    scorpia: Activity
    scurrius: Activity
    shellbane_gryphon: Activity
    skotizo: Activity
    sol_heredit: Activity
    spindel: Activity

    tempoross: Activity
    the_gauntlet: Activity
    the_corrupted_gauntlet: Activity
    the_hueycoatl: Activity
    the_leviathan: Activity
    the_royal_titans: Activity
    the_whisperer: Activity
    theatre_of_blood: Activity
    theatre_of_blood_hard_mode: Activity
    thermonuclear_smoke_devil: Activity
    tombs_of_amascut: Activity
    tombs_of_amascut_expert_mode: Activity
    tzkal_zuk: Activity
    tztok_jad: Activity

    vardorvis: Activity
    venenatis: Activity
    vetion: Activity
    vorkath: Activity

    wintertodt: Activity
    yama: Activity
    zalcano: Activity
    zulrah: Activity

    def __iter__(self) -> Iterator[Skill]:
        for field in fields(self):
            yield getattr(self, field.name)

    @classmethod
    def from_json(cls, json: dict) -> "ActivitiesCollection":
        """
        Creates ActivitiesCollection from JSON data.

        :param json: JSON data as dictionary.
        :type json: dict
        :return: ActivitiesCollection data class which contains all activities and their data.
        :rtype: ActivitiesCollection
        """
        activities_json = json["activities"]

        activities_dict: dict[str, Activity] = {}

        for activity_enum in ActivityEnum:
            activity_json: dict = activities_json[activity_enum.value]
            activities_dict[activity_enum.name.lower()] = Activity.from_json(
                activity_json
            )

        return ActivitiesCollection(**activities_dict)


@dataclass(frozen=True)
class PlayerStats(Base):
    rsn: str
    skills: SkillsCollection
    activities: ActivitiesCollection

    @classmethod
    def from_json(cls, json: dict) -> "PlayerStats":
        """
        Creates PlayerStats from JSON data.

        :param json: JSON data as dictionary.
        :type json: dict
        :return: PlayerStats data class which contains skills.
        :rtype: PlayerStats
        """
        skills: SkillsCollection = SkillsCollection.from_json(json)
        activities: ActivitiesCollection = ActivitiesCollection.from_json(json)
        return cls(json["name"], skills, activities)
