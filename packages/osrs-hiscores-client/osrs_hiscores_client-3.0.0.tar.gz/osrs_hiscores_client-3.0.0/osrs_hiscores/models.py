from dataclasses import dataclass, asdict, is_dataclass
from typing import Any
from .enums import Skill as SkillEnum, Activity as ActivityEnum, PlayerType


class ToDictMixin:
    """
    Provides to_dict method to dataclass.
    """

    def to_dict(self) -> dict[str, Any]:
        """
        Returns the dataclass as a dictionary.
        """
        if not is_dataclass(self):
            return {}
        return asdict(self)


@dataclass(frozen=True)
class Skill(ToDictMixin):
    """
    Represents player's skill.
    """

    id: int
    name: str
    rank: int
    level: int
    experience: int

    @classmethod
    def from_json(cls, data: dict) -> "Skill":
        """
        Creates Skill from JSON data.

        :param data: JSON data as dictionary.
        :type data: dict
        :return: Skill data class which contains skill data.
        :rtype: Skill
        """
        id: int = data["id"]
        name: str = data["name"]
        rank: int = data["rank"]
        level: int = data["level"]
        experience: int = data["xp"]

        return cls(id, name, rank, level, experience)

    @classmethod
    def skills_from_json(cls, data: dict) -> dict[int, "Skill"]:
        skills_json = data["skills"]

        skills_dict: dict[int, Skill] = {}

        for skill in skills_json:
            skills_dict[skill["id"]] = Skill.from_json(skill)

        return skills_dict


@dataclass(frozen=True)
class Activity(ToDictMixin):
    """
    Represents activity, for example Barrows kill count.
    """

    id: int
    name: str
    rank: int
    score: int

    @classmethod
    def from_json(cls, data: dict) -> "Activity":
        id: int = data["id"]
        name: str = data["name"]
        rank: int = data["rank"]
        score: int = data["score"]

        return cls(id, name, rank, score)

    @classmethod
    def activities_from_json(cls, data: dict) -> dict[int, "Activity"]:
        activities_json = data["activities"]

        activities_dict: dict[int, Activity] = {}

        for activity in activities_json:
            activities_dict[activity["id"]] = Activity.from_json(activity)

        return activities_dict


@dataclass(frozen=True)
class PlayerStats(ToDictMixin):
    name: str
    type: PlayerType
    skills: dict[int, Skill]
    activities: dict[int, Activity]

    @classmethod
    def from_json(cls, type: PlayerType, data: dict) -> "PlayerStats":
        """
        Creates PlayerStats from JSON data.

        :param data: JSON data as dictionary.
        :type data: dict
        :return: PlayerStats data class which contains skills.
        :rtype: PlayerStats
        """
        skills: dict[int, Skill] = Skill.skills_from_json(data)
        activities: dict[int, Activity] = Activity.activities_from_json(data)
        return cls(data["name"], type, skills, activities)

    def get_skill_by_id(self, skill_id: SkillEnum | int) -> Skill | None:
        """
        Returns Skill by ID.
        """
        if isinstance(skill_id, SkillEnum):
            skill_id = skill_id.value
        return self.skills.get(skill_id)

    def get_activity_by_id(self, activity_id: ActivityEnum | int) -> Activity | None:
        """
        Returns Activity by ID.
        """
        if isinstance(activity_id, ActivityEnum):
            activity_id = activity_id.value
        return self.activities.get(activity_id)
