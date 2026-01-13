from urllib.parse import quote
from requests import Session
from .models import PlayerStats
from .enums import PlayerType


class HiscoresClient:
    """
    Client for OSRS Hiscores API.
    """

    def __init__(self, session: Session | None = None):
        """
        Initializes the client.

        :param session: Optional requests Session, usually not needed.
        :type session: Session | None
        """
        self.session = session or Session()

    def get_player_stats(
        self, rsn: str, player_type: PlayerType = PlayerType.NORMAL
    ) -> PlayerStats:
        """
        Returns player's stats from hiscores API as PlayerStats dataclass.

        :param rsn: Player name (e.g. 'Zezima')
        :type rsn: str
        :param player_type: Player type (normal, ironman, hardcore ironman or ultimate ironman)
        :type player_type: PlayerType
        :return: PlayerStats dataclass which includes player's RSN and skills.
        :rtype: PlayerStats
        """
        url: str = get_player_stats_url(rsn, player_type)
        response = self.session.get(url)
        response.raise_for_status()
        response_json = response.json()
        return PlayerStats.from_json(response_json)


def get_player_stats_url(rsn: str, player_type: PlayerType) -> str:
    """
    Returns final API URL for getting player stats according to player_type.

    :param rsn: Player name.
    :type rsn: str
    :param player_type: Player type (e.g. ironman, hardcore ironman etc.)
    :type player_type: PlayerType
    :return: API URL.
    :rtype: str
    """
    rsn: str = quote(rsn)

    match player_type:
        case PlayerType.NORMAL:
            return f"https://secure.runescape.com/m=hiscore_oldschool/index_lite.json?player={rsn}"
        case PlayerType.IRONMAN:
            return f"https://secure.runescape.com/m=hiscore_oldschool_ironman/index_lite.json?player={rsn}"
        case PlayerType.HARDCORE_IRONMAN:
            return f"https://secure.runescape.com/m=hiscore_oldschool_hardcore_ironman/index_lite.json?player={rsn}"
        case PlayerType.ULTIMATE_IRONMAN:
            return f"https://secure.runescape.com/m=hiscore_oldschool_ultimate/index_lite.json?player={rsn}"
        case _:
            raise ValueError(f"Unsupported player type: {player_type}")
