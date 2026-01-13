# https://lscluster.hockeytech.com/feed/index.php?feed=statviewfeed&view=roster&team_id=1&season_id=8&key=446521baf8c38984&client_code=pwhl&site_id=0&league_id=1&lang=en
from pwhl_api.endpoints.library.http import HTTPEndpointClient, HTTPEndpointResponse
from pwhl_api.static import seasons

class TeamRoster(HTTPEndpointResponse):
    def __init__(self, team_id: str, season: str = None):
        client = HTTPEndpointClient()
        self.endpoint = f"statviewfeed&view=roster"
        if season is not None and len(season) > 1:
            season = seasons.get_season(season)
        elif season is None:
            season = seasons.get_most_recent_season()
        else:
            season = str(season)

        self.params = {
            "team_id": team_id,
            "season_id": season,
            "key": "446521baf8c38984",
            "client_code": "pwhl",
            "site_id": 0,
            "league_id": 1
        }
        self.response = client.get(self.endpoint, params = self.params)
    def get_data_frames(self):
        import pandas as pd
        frames = {}
        roster = self.get_raw_json()
        for section in roster['roster'][0]['sections']:
            players = []
            for player in section['data']:
                players.append(player['row'])
            frames[section['title']] = players
        for key, value in frames.items():
            df = pd.DataFrame(value)
            frames[key] = df
        return frames
        