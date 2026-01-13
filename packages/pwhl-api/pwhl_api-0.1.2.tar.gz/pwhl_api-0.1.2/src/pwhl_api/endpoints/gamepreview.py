# https://lscluster.hockeytech.com/feed/index.php?feed=statviewfeed&view=gameCenterPreview&game_id=248&key=446521baf8c38984&client_code=pwhl&lang=en&league_id=
from pwhl_api.endpoints.library.http import HTTPEndpointClient, HTTPEndpointResponse

class GamePreview(HTTPEndpointResponse):
    def __init__(self, game_id: str):
        client = HTTPEndpointClient()
        self.endpoint = f"statviewfeed&view=gameCenterPreview"
        self.params = {
            "game_id": game_id,
            "key": "446521baf8c38984",
            "client_code": "pwhl",
            "site_id": 0,
            "league_id": 1
        }
        self.response = client.get(self.endpoint, params = self.params)