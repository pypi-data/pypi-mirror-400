from pwhl_api.endpoints.library.http import HTTPEndpointClient, HTTPEndpointResponse
from pwhl_api.static import seasons

class LeagueSchedule(HTTPEndpointResponse):
    def __init__(self, season: str = None, month: str | int = -1, location: str = "homeaway"):
        client = HTTPEndpointClient()
        self.endpoint = f"statviewfeed&view=schedule"

        if season is not None and len(season) > 1:
            season = seasons.get_season(season)
        elif season is None:
            season = seasons.get_most_recent_season()
        else:
            season = str(season)
            

        self.params = {
            "team": -1,
            "season": season,
            "month": month,
            "location": location,
            "key": "446521baf8c38984",
            "client_code": "pwhl",
            "site_id": 0,
            "league_id": 1,
            "conference_id": -1,
            "division_id": -1,
            "lang": "en"
        }
        self.response = client.get(self.endpoint, params = self.params)
    def get_data_frame(self):
        import pandas as pd
        games = self.get_raw_json()
        games = games[0]['sections'][0]['data']
        df = pd.json_normalize(games[0], sep='_')
        for game in games[1:]:
            df_game = pd.json_normalize(game, sep='_')
            df = pd.concat([df, df_game], ignore_index=True)

        return df