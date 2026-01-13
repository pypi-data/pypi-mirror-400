from pwhl_api.endpoints.library.http import HTTPEndpointClient, HTTPEndpointResponse
from pwhl_api.static import seasons

class PlayerSkaterStats(HTTPEndpointResponse):
    def __init__(self, season: str = None, team: str | int = "all", position: str = "skaters", rookies: int = 0, statsType: str = "standard", limit: int = 500):
        client = HTTPEndpointClient()
        self.endpoint = f"statviewfeed&view=players"
        if season is not None and len(season) > 1:
            season = seasons.get_season(season)
        elif season is None:
            season = seasons.get_most_recent_season()
        else:
            season = str(season)

        if isinstance(team, int):
            team = str(team)

        # position: skaters | forwards | defenders
        # rookies: 0 | 1

        self.params = {
            "season": season,
            "team": team,
            "key": "446521baf8c38984",
            "client_code": "pwhl",
            "site_id": 0,
            "league_id": 1,
            "position": position,
            "rookies": rookies,
            "statsType": statsType,
            "rosterstatus": "undefined",
            "activeOnly": 0,
            "limit": limit
        }
        self.response = client.get(self.endpoint, params = self.params)
    def get_data_frame(self):
        import pandas as pd
        rows = self.get_raw_json()
        players = []
        for row in rows[0]['sections'][0]['data']:
            players.append(row['row'])
        players_df = pd.DataFrame(players)
        return players_df