import json
from osrs_hiscores.client import get_player_stats_url
from osrs_hiscores.enums import PlayerType, Skill as SkillEnum, Activity as ActivityEnum
from osrs_hiscores.models import (
    Skill,
    SkillsCollection,
    Activity,
    ActivitiesCollection,
    PlayerStats,
)

TEST_JSON_DATA = """
{
  "name": "Lynx Titan",
  "skills": [
    {
      "id": 0,
      "name": "Overall",
      "rank": 83183,
      "level": 2278,
      "xp": 4600000000
    },
    {
      "id": 1,
      "name": "Attack",
      "rank": 15,
      "level": 99,
      "xp": 200000000
    },
    {
      "id": 2,
      "name": "Defence",
      "rank": 28,
      "level": 99,
      "xp": 200000000
    },
    {
      "id": 3,
      "name": "Strength",
      "rank": 18,
      "level": 99,
      "xp": 200000000
    },
    {
      "id": 4,
      "name": "Hitpoints",
      "rank": 7,
      "level": 99,
      "xp": 200000000
    },
    {
      "id": 5,
      "name": "Ranged",
      "rank": 8,
      "level": 99,
      "xp": 200000000
    },
    {
      "id": 6,
      "name": "Prayer",
      "rank": 11,
      "level": 99,
      "xp": 200000000
    },
    {
      "id": 7,
      "name": "Magic",
      "rank": 29,
      "level": 99,
      "xp": 200000000
    },
    {
      "id": 8,
      "name": "Cooking",
      "rank": 150,
      "level": 99,
      "xp": 200000000
    },
    {
      "id": 9,
      "name": "Woodcutting",
      "rank": 15,
      "level": 99,
      "xp": 200000000
    },
    {
      "id": 10,
      "name": "Fletching",
      "rank": 12,
      "level": 99,
      "xp": 200000000
    },
    {
      "id": 11,
      "name": "Fishing",
      "rank": 9,
      "level": 99,
      "xp": 200000000
    },
    {
      "id": 12,
      "name": "Firemaking",
      "rank": 48,
      "level": 99,
      "xp": 200000000
    },
    {
      "id": 13,
      "name": "Crafting",
      "rank": 4,
      "level": 99,
      "xp": 200000000
    },
    {
      "id": 14,
      "name": "Smithing",
      "rank": 3,
      "level": 99,
      "xp": 200000000
    },
    {
      "id": 15,
      "name": "Mining",
      "rank": 23,
      "level": 99,
      "xp": 200000000
    },
    {
      "id": 16,
      "name": "Herblore",
      "rank": 5,
      "level": 99,
      "xp": 200000000
    },
    {
      "id": 17,
      "name": "Agility",
      "rank": 24,
      "level": 99,
      "xp": 200000000
    },
    {
      "id": 18,
      "name": "Thieving",
      "rank": 12,
      "level": 99,
      "xp": 200000000
    },
    {
      "id": 19,
      "name": "Slayer",
      "rank": 2,
      "level": 99,
      "xp": 200000000
    },
    {
      "id": 20,
      "name": "Farming",
      "rank": 19,
      "level": 99,
      "xp": 200000000
    },
    {
      "id": 21,
      "name": "Runecraft",
      "rank": 6,
      "level": 99,
      "xp": 200000000
    },
    {
      "id": 22,
      "name": "Hunter",
      "rank": 4,
      "level": 99,
      "xp": 200000000
    },
    {
      "id": 23,
      "name": "Construction",
      "rank": 4,
      "level": 99,
      "xp": 200000000
    },
    {
      "id": 24,
      "name": "Sailing",
      "rank": -1,
      "level": 1,
      "xp": 0
    }
  ],
  "activities": [
    {
      "id": 0,
      "name": "Grid Points",
      "rank": -1,
      "score": -1
    },
    {
      "id": 1,
      "name": "League Points",
      "rank": -1,
      "score": -1
    },
    {
      "id": 2,
      "name": "Deadman Points",
      "rank": -1,
      "score": -1
    },
    {
      "id": 3,
      "name": "Bounty Hunter - Hunter",
      "rank": -1,
      "score": -1
    },
    {
      "id": 4,
      "name": "Bounty Hunter - Rogue",
      "rank": -1,
      "score": -1
    },
    {
      "id": 5,
      "name": "Bounty Hunter (Legacy) - Hunter",
      "rank": -1,
      "score": -1
    },
    {
      "id": 6,
      "name": "Bounty Hunter (Legacy) - Rogue",
      "rank": -1,
      "score": -1
    },
    {
      "id": 7,
      "name": "Clue Scrolls (all)",
      "rank": 1060210,
      "score": 22
    },
    {
      "id": 8,
      "name": "Clue Scrolls (beginner)",
      "rank": -1,
      "score": -1
    },
    {
      "id": 9,
      "name": "Clue Scrolls (easy)",
      "rank": -1,
      "score": -1
    },
    {
      "id": 10,
      "name": "Clue Scrolls (medium)",
      "rank": -1,
      "score": -1
    },
    {
      "id": 11,
      "name": "Clue Scrolls (hard)",
      "rank": 643444,
      "score": 22
    },
    {
      "id": 12,
      "name": "Clue Scrolls (elite)",
      "rank": -1,
      "score": -1
    },
    {
      "id": 13,
      "name": "Clue Scrolls (master)",
      "rank": -1,
      "score": -1
    },
    {
      "id": 14,
      "name": "LMS - Rank",
      "rank": -1,
      "score": -1
    },
    {
      "id": 15,
      "name": "PvP Arena - Rank",
      "rank": -1,
      "score": -1
    },
    {
      "id": 16,
      "name": "Soul Wars Zeal",
      "rank": -1,
      "score": -1
    },
    {
      "id": 17,
      "name": "Rifts closed",
      "rank": -1,
      "score": -1
    },
    {
      "id": 18,
      "name": "Colosseum Glory",
      "rank": -1,
      "score": -1
    },
    {
      "id": 19,
      "name": "Collections Logged",
      "rank": -1,
      "score": -1
    },
    {
      "id": 20,
      "name": "Abyssal Sire",
      "rank": -1,
      "score": -1
    },
    {
      "id": 21,
      "name": "Alchemical Hydra",
      "rank": -1,
      "score": -1
    },
    {
      "id": 22,
      "name": "Amoxliatl",
      "rank": -1,
      "score": -1
    },
    {
      "id": 23,
      "name": "Araxxor",
      "rank": -1,
      "score": -1
    },
    {
      "id": 24,
      "name": "Artio",
      "rank": -1,
      "score": -1
    },
    {
      "id": 25,
      "name": "Barrows Chests",
      "rank": -1,
      "score": -1
    },
    {
      "id": 26,
      "name": "Bryophyta",
      "rank": -1,
      "score": -1
    },
    {
      "id": 27,
      "name": "Callisto",
      "rank": -1,
      "score": -1
    },
    {
      "id": 28,
      "name": "Calvar'ion",
      "rank": -1,
      "score": -1
    },
    {
      "id": 29,
      "name": "Cerberus",
      "rank": -1,
      "score": -1
    },
    {
      "id": 30,
      "name": "Chambers of Xeric",
      "rank": -1,
      "score": -1
    },
    {
      "id": 31,
      "name": "Chambers of Xeric: Challenge Mode",
      "rank": -1,
      "score": -1
    },
    {
      "id": 32,
      "name": "Chaos Elemental",
      "rank": -1,
      "score": -1
    },
    {
      "id": 33,
      "name": "Chaos Fanatic",
      "rank": -1,
      "score": -1
    },
    {
      "id": 34,
      "name": "Commander Zilyana",
      "rank": -1,
      "score": -1
    },
    {
      "id": 35,
      "name": "Corporeal Beast",
      "rank": -1,
      "score": -1
    },
    {
      "id": 36,
      "name": "Crazy Archaeologist",
      "rank": -1,
      "score": -1
    },
    {
      "id": 37,
      "name": "Dagannoth Prime",
      "rank": -1,
      "score": -1
    },
    {
      "id": 38,
      "name": "Dagannoth Rex",
      "rank": -1,
      "score": -1
    },
    {
      "id": 39,
      "name": "Dagannoth Supreme",
      "rank": -1,
      "score": -1
    },
    {
      "id": 40,
      "name": "Deranged Archaeologist",
      "rank": -1,
      "score": -1
    },
    {
      "id": 41,
      "name": "Doom of Mokhaiotl",
      "rank": -1,
      "score": -1
    },
    {
      "id": 42,
      "name": "Duke Sucellus",
      "rank": -1,
      "score": -1
    },
    {
      "id": 43,
      "name": "General Graardor",
      "rank": -1,
      "score": -1
    },
    {
      "id": 44,
      "name": "Giant Mole",
      "rank": -1,
      "score": -1
    },
    {
      "id": 45,
      "name": "Grotesque Guardians",
      "rank": -1,
      "score": -1
    },
    {
      "id": 46,
      "name": "Hespori",
      "rank": -1,
      "score": -1
    },
    {
      "id": 47,
      "name": "Kalphite Queen",
      "rank": -1,
      "score": -1
    },
    {
      "id": 48,
      "name": "King Black Dragon",
      "rank": -1,
      "score": -1
    },
    {
      "id": 49,
      "name": "Kraken",
      "rank": -1,
      "score": -1
    },
    {
      "id": 50,
      "name": "Kree'Arra",
      "rank": -1,
      "score": -1
    },
    {
      "id": 51,
      "name": "K'ril Tsutsaroth",
      "rank": -1,
      "score": -1
    },
    {
      "id": 52,
      "name": "Lunar Chests",
      "rank": -1,
      "score": -1
    },
    {
      "id": 53,
      "name": "Mimic",
      "rank": -1,
      "score": -1
    },
    {
      "id": 54,
      "name": "Nex",
      "rank": -1,
      "score": -1
    },
    {
      "id": 55,
      "name": "Nightmare",
      "rank": -1,
      "score": -1
    },
    {
      "id": 56,
      "name": "Phosani's Nightmare",
      "rank": -1,
      "score": -1
    },
    {
      "id": 57,
      "name": "Obor",
      "rank": -1,
      "score": -1
    },
    {
      "id": 58,
      "name": "Phantom Muspah",
      "rank": -1,
      "score": -1
    },
    {
      "id": 59,
      "name": "Sarachnis",
      "rank": -1,
      "score": -1
    },
    {
      "id": 60,
      "name": "Scorpia",
      "rank": -1,
      "score": -1
    },
    {
      "id": 61,
      "name": "Scurrius",
      "rank": -1,
      "score": -1
    },
    {
      "id": 62,
      "name": "Shellbane Gryphon",
      "rank": -1,
      "score": -1
    },
    {
      "id": 63,
      "name": "Skotizo",
      "rank": -1,
      "score": -1
    },
    {
      "id": 64,
      "name": "Sol Heredit",
      "rank": -1,
      "score": -1
    },
    {
      "id": 65,
      "name": "Spindel",
      "rank": -1,
      "score": -1
    },
    {
      "id": 66,
      "name": "Tempoross",
      "rank": -1,
      "score": -1
    },
    {
      "id": 67,
      "name": "The Gauntlet",
      "rank": -1,
      "score": -1
    },
    {
      "id": 68,
      "name": "The Corrupted Gauntlet",
      "rank": -1,
      "score": -1
    },
    {
      "id": 69,
      "name": "The Hueycoatl",
      "rank": -1,
      "score": -1
    },
    {
      "id": 70,
      "name": "The Leviathan",
      "rank": -1,
      "score": -1
    },
    {
      "id": 71,
      "name": "The Royal Titans",
      "rank": -1,
      "score": -1
    },
    {
      "id": 72,
      "name": "The Whisperer",
      "rank": -1,
      "score": -1
    },
    {
      "id": 73,
      "name": "Theatre of Blood",
      "rank": -1,
      "score": -1
    },
    {
      "id": 74,
      "name": "Theatre of Blood: Hard Mode",
      "rank": -1,
      "score": -1
    },
    {
      "id": 75,
      "name": "Thermonuclear Smoke Devil",
      "rank": -1,
      "score": -1
    },
    {
      "id": 76,
      "name": "Tombs of Amascut",
      "rank": -1,
      "score": -1
    },
    {
      "id": 77,
      "name": "Tombs of Amascut: Expert Mode",
      "rank": -1,
      "score": -1
    },
    {
      "id": 78,
      "name": "TzKal-Zuk",
      "rank": -1,
      "score": -1
    },
    {
      "id": 79,
      "name": "TzTok-Jad",
      "rank": 374,
      "score": 186
    },
    {
      "id": 80,
      "name": "Vardorvis",
      "rank": -1,
      "score": -1
    },
    {
      "id": 81,
      "name": "Venenatis",
      "rank": -1,
      "score": -1
    },
    {
      "id": 82,
      "name": "Vet'ion",
      "rank": -1,
      "score": -1
    },
    {
      "id": 83,
      "name": "Vorkath",
      "rank": -1,
      "score": -1
    },
    {
      "id": 84,
      "name": "Wintertodt",
      "rank": -1,
      "score": -1
    },
    {
      "id": 85,
      "name": "Yama",
      "rank": -1,
      "score": -1
    },
    {
      "id": 86,
      "name": "Zalcano",
      "rank": -1,
      "score": -1
    },
    {
      "id": 87,
      "name": "Zulrah",
      "rank": -1,
      "score": -1
    }
  ]
}
"""


def test_stats_url_selection():
    rsn = "Example RSN"

    normal_player_url = get_player_stats_url(rsn, PlayerType.NORMAL)
    ironman_player_url = get_player_stats_url(rsn, PlayerType.IRONMAN)
    hardcore_ironman_player_url = get_player_stats_url(rsn, PlayerType.HARDCORE_IRONMAN)
    ultimate_ironman_player_url = get_player_stats_url(rsn, PlayerType.ULTIMATE_IRONMAN)

    assert (
        normal_player_url
        == "https://secure.runescape.com/m=hiscore_oldschool/index_lite.json?player=Example%20RSN"
    )
    assert (
        ironman_player_url
        == "https://secure.runescape.com/m=hiscore_oldschool_ironman/index_lite.json?player=Example%20RSN"
    )
    assert (
        hardcore_ironman_player_url
        == "https://secure.runescape.com/m=hiscore_oldschool_hardcore_ironman/index_lite.json?player=Example%20RSN"
    )
    assert (
        ultimate_ironman_player_url
        == "https://secure.runescape.com/m=hiscore_oldschool_ultimate/index_lite.json?player=Example%20RSN"
    )


def test_skill_parsing():
    json_data = json.loads(TEST_JSON_DATA)

    attack_skill_json = json_data["skills"][SkillEnum.ATTACK.value]

    skill = Skill.from_json(attack_skill_json)

    assert skill.id == 1
    assert skill.name == "Attack"
    assert skill.rank == 15
    assert skill.level == 99
    assert skill.experience == 200000000


def test_skill_collection_parsing():
    json_data = json.loads(TEST_JSON_DATA)

    skills_collection = SkillsCollection.from_json(json_data)

    skills_collection_skills_dict = skills_collection.to_dict()

    assert len(skills_collection_skills_dict) == len(SkillEnum)
    assert len(skills_collection_skills_dict) == 25
    assert skills_collection.fishing.name == "Fishing"
    assert skills_collection.fishing.rank == 9

    for skill in skills_collection:
        skill_in_json = next(
            (item for item in json_data["skills"] if item["id"] == skill.id)
        )

        assert skill.id == skill_in_json["id"]
        assert skill.name == skill_in_json["name"]
        assert skill.rank == skill_in_json["rank"]
        assert skill.level == skill_in_json["level"]
        assert skill.experience == skill_in_json["xp"]


def test_activity_parsing():
    json_data = json.loads(TEST_JSON_DATA)

    clue_scrolls_all_activity_json = json_data["activities"][
        ActivityEnum.CLUE_SCROLLS_ALL.value
    ]

    activity = Activity.from_json(clue_scrolls_all_activity_json)

    assert activity.id == 7
    assert activity.name == "Clue Scrolls (all)"
    assert activity.rank == 1060210
    assert activity.score == 22


def test_activities_collection_parsing():
    json_data = json.loads(TEST_JSON_DATA)

    activities_collection = ActivitiesCollection.from_json(json_data)

    activities_collection_dict = activities_collection.to_dict()

    assert len(activities_collection_dict) == len(ActivityEnum)
    assert len(activities_collection_dict) == 88
    assert activities_collection.clue_scrolls_all.name == "Clue Scrolls (all)"
    assert activities_collection.clue_scrolls_all.rank == 1060210

    for activity in activities_collection:
        activity_in_json = next(
            (item for item in json_data["activities"] if item["id"] == activity.id)
        )

        assert activity.id == activity_in_json["id"]
        assert activity.name == activity_in_json["name"]
        assert activity.rank == activity_in_json["rank"]
        assert activity.score == activity_in_json["score"]


def test_player_stats_parsing():
    json_data = json.loads(TEST_JSON_DATA)

    player_stats = PlayerStats.from_json(json_data)

    assert player_stats.rsn == "Lynx Titan"
    assert len(player_stats.to_dict()["skills"]) == len(json_data["skills"])
    assert len(player_stats.to_dict()["activities"]) == len(json_data["activities"])
