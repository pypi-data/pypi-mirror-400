# OSRS Hiscores

Simple OSRS Hiscores client for Python.

---

## Installation

```bash
pip install osrs-hiscores-client
```


## Usage

```py
from osrs_hiscores.client import HiscoresClient
from osrs_hiscores.enums import PlayerType, Skill, Activity

rsn = "Lynx Titan"

client = HiscoresClient()

# PlayerType also has PlayerType.IRONMAN, PlayerType.HARDCORE_IRONMAN and PlayerType.ULTIMATE_IRONMAN
stats = client.get_player_stats(rsn, PlayerType.NORMAL)

# You can access specific skill using ID.
agility_skill = stats.get_skill_by_id(Skill.AGILITY)

if agility_skill is not None:
    print(f"Player {stats.rsn} has agility level of {agility_skill.level}, {agility_skill.experience} experience and rank {agility_skill.rank}.")
    # Player Lynx Titan has agility level of 99, 200000000 experience and rank 24.

# You can loop all skills.
for skill in stats.skills.values():
    print(f"Player {stats.rsn} has {skill.name} level of {skill.level}, {skill.experience} experience and rank {skill.rank}.")

# You can access specific activity using ID.
jad_activity = stats.get_activity_by_id(Activity.TZTOK_JAD)

if jad_activity is not None:
    print(f"Player {stats.rsn} has {jad_activity.score} Jad KC and rank {jad_activity.rank}.")
    # Player Lynx Titan has activity TzTok-Jad score of 186 and rank 375.

# You can also loop all activities.
for activity in stats.activities.values():
    print(f"Player {stats.rsn} has activity {activity.name} score of {activity.score} and rank {activity.rank}.")
```
