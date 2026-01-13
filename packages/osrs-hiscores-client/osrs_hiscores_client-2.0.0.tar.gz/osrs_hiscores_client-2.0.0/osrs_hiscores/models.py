from dataclasses import dataclass, asdict, is_dataclass
from typing import Any
from .enums import Skill as SkillEnum, Activity as ActivityEnum


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

    @classmethod
    def dict_from_json(cls, json: dict) -> dict[int, "Skill"]:
        skills_json = json["skills"]

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
    def from_json(cls, json: dict) -> "Activity":
        id: int = json["id"]
        name: str = json["name"]
        rank: int = json["rank"]
        score: int = json["score"]

        return cls(id, name, rank, score)

    @classmethod
    def dict_from_json(cls, json: dict) -> dict[int, "Activity"]:
        activities_json = json["activities"]

        activities_dict: dict[int, Activity] = {}

        for activity in activities_json:
            activities_dict[activity["id"]] = Activity.from_json(activity)

        return activities_dict


@dataclass(frozen=True)
class PlayerStats(ToDictMixin):
    rsn: str
    skills: dict[int, Skill]
    activities: dict[int, Activity]

    @classmethod
    def from_json(cls, json: dict) -> "PlayerStats":
        """
        Creates PlayerStats from JSON data.

        :param json: JSON data as dictionary.
        :type json: dict
        :return: PlayerStats data class which contains skills.
        :rtype: PlayerStats
        """
        skills: dict[int, Skill] = Skill.dict_from_json(json)
        activities: dict[int, Activity] = Activity.dict_from_json(json)
        return cls(json["name"], skills, activities)

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
