from pwhl_api.endpoints.library.http import HTTPEndpointClient, HTTPEndpointResponse
from pwhl_api.static import seasons

class PlayerLeagueLeaders(HTTPEndpointResponse):
    def __init__(self, season: str = None, team_id: str | int = 0):
        client = HTTPEndpointClient()
        self.endpoint = f"statviewfeed&view=leadersExtended"
        if season is not None and len(season) > 1:
            season = seasons.get_season(season)
        elif season is None:
            season = seasons.get_most_recent_season()
        else:
            season = str(season)

        self.params = {
            "season_id": season,
            "team_id": team_id,
            "key": "446521baf8c38984",
            "client_code": "pwhl",
            "site_id": 0,
            "league_id": 1,
            "playerTypes": "skaters,goalies",
            "skaterStatTypes": "points,goals,assists",
            "goalieStatTypes": "wins,save_percentage,goals_against_average",
            "activeOnly": 0
        }
        self.response = client.get(self.endpoint, params = self.params)
    
    def get_data_frames(self):
        import pandas as pd
        result = self.get_raw_json()
        leaders =  {
            "skaters": {},
            "goalies": {}
        }
        for category in result:
            for stat in result[category]:
                for player in result[category][stat]['results']:
                    if stat not in leaders[category]:
                        leaders[category][stat] = []
                    leaders[category][stat].append(player)
        for category in leaders:
            for stat in leaders[category]:
                df = pd.DataFrame(leaders[category][stat])
                leaders[category][stat] = df
        return leaders