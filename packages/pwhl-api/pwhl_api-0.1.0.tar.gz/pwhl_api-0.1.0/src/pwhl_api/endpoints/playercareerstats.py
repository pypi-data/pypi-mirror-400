from pwhl_api.endpoints.library.http import HTTPEndpointClient, HTTPEndpointResponse
# https://lscluster.hockeytech.com/feed/index.php?feed=statviewfeed&view=player&player_id=21&season_id=8&site_id=0&key=446521baf8c38984&client_code=pwhl&league_id=&lang=en&statsType=standard
class PlayerCareerStats(HTTPEndpointResponse):
    def __init__(self, player_id: str, season_id: str = None, statsType: str = "standard"):
        client = HTTPEndpointClient()
        self.endpoint = f"statviewfeed&view=player"
        self.params = {
            "player_id": player_id,
            "season_id": season_id,
            "key": "446521baf8c38984",
            "client_code": "pwhl",
            "site_id": 0,
            "league_id": 1,
            "statsType": statsType
        }
        self.response = client.get(self.endpoint, params = self.params)
    def get_data_frames(self):
        import pandas as pd
        player = self.get_raw_json()
        frames = {
            'playerStats': {
                'regularSeason': [],
                'playoffs': []
            },
            'gameByGame': [],
            'currentSeasonStats': None,
            'playerShots': []
            
        }
        for row in player['careerStats'][0]['sections'][0]['data']:
            frames['playerStats']['regularSeason'].append(row['row'])

        for row in player['careerStats'][0]['sections'][1]['data']:
            frames['playerStats']['playoffs'].append(row['row'])
        frames['playerStats']['regularSeason'] = pd.DataFrame(frames['playerStats']['regularSeason'])
        frames['playerStats']['playoffs'] = pd.DataFrame(frames['playerStats']['playoffs'])
        for row in player['gameByGame'][0]['sections'][0]['data']:
            curr_game = row['row']
            curr_game['game_id'] = row['prop']['game']['gameLink']
            frames['gameByGame'].append(curr_game)
        frames['gameByGame'] = pd.DataFrame(frames['gameByGame'])

        for shot in player['playerShots']:
            frames['playerShots'].append(shot)
        frames['playerShots'] = pd.DataFrame(frames['playerShots'])

        frames['currentSeasonStats'] = pd.DataFrame.from_dict(player['currentSeasonStats'][0]['sections'][0]['data'][0]['row'], orient='index').T
        return frames