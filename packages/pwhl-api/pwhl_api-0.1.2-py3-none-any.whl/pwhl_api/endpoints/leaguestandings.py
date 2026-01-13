from pwhl_api.endpoints.library.http import HTTPEndpointClient, HTTPEndpointResponse
from pwhl_api.static import seasons

class LeagueStandings(HTTPEndpointResponse):
    def __init__(self, season: str = None, context: str = "overall", special_teams: str = "false", sort: str = "points"):
        client = HTTPEndpointClient()
        self.endpoint = f"statviewfeed&view=teams"
        if season is not None and len(season) > 1:
            season = seasons.get_season(season)
        elif season is None:
            season = seasons.get_most_recent_season()
        else:
            season = str(season)
        # context : overall, home, visiting
        # sort: points, power_play_pct, penalty_kill_pct, ot_wins, penalty_minutes 
        self.params = {
            "groupTeamsBy": "division",
            "context": context,
            "season": season,
            "key": "446521baf8c38984",
            "special": special_teams,
            "client_code": "pwhl",
            "site_id": 0,
            "league_id": 1,
            "conference_id": -1,
            "division_id": -1,
            "sort": sort,
            "lang": "en"
        }
        self.response = client.get(self.endpoint, params = self.params)
    def get_data_frame(self):
        import pandas as pd
        teams = self.get_raw_json()
        teams = teams[0]['sections'][0]['data']
        df = pd.json_normalize(teams[0], sep='_')
        for team in teams[1:]:
            df_team = pd.json_normalize(team, sep='_')
            df = pd.concat([df, df_team], ignore_index=True)
        
        return df