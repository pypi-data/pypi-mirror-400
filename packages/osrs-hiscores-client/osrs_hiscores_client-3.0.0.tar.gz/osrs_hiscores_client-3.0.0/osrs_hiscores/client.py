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
        self, player_name: str, player_type: PlayerType = PlayerType.NORMAL
    ) -> PlayerStats:
        """
        Returns player's stats from hiscores API as PlayerStats dataclass.

        :param player_name: Player name (e.g. 'Zezima')
        :type player_name: str
        :param player_type: Player type (normal, ironman, hardcore ironman or ultimate ironman)
        :type player_type: PlayerType
        :return: PlayerStats dataclass which includes player's name, skills and activities.
        :rtype: PlayerStats
        """
        url: str = get_player_stats_url(player_name, player_type)
        response = self.session.get(url)
        response.raise_for_status()
        response_json = response.json()
        return PlayerStats.from_json(player_type, response_json)


def get_player_stats_url(player_name: str, player_type: PlayerType) -> str:
    """
    Returns final API URL for getting player stats according to player_type.

    :param player_name: Player name.
    :type player_name: str
    :param player_type: Player type (e.g. ironman, hardcore ironman etc.)
    :type player_type: PlayerType
    :return: API URL.
    :rtype: str
    """
    player_name_quoted: str = quote(player_name)

    match player_type:
        case PlayerType.NORMAL:
            player_mode = "hiscore_oldschool"
        case PlayerType.IRONMAN:
            player_mode = "hiscore_oldschool_ironman"
        case PlayerType.HARDCORE_IRONMAN:
            player_mode = "hiscore_oldschool_hardcore_ironman"
        case PlayerType.ULTIMATE_IRONMAN:
            player_mode = "hiscore_oldschool_ultimate"
        case PlayerType.DEADMAN_MODE:
            player_mode = "hiscore_oldschool_deadman"
        case PlayerType.SEASONAL:
            player_mode = "hiscore_oldschool_seasonal"
        case PlayerType.TOURNAMENT:
            player_mode = "hiscore_oldschool_tournament"
        case _:
            raise ValueError(f"Unsupported player type: {player_type}")

    return f"https://secure.runescape.com/m={player_mode}/index_lite.json?player={player_name_quoted}"
