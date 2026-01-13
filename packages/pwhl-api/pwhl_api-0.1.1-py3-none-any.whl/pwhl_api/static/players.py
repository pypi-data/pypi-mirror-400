def get_players():
    # last updated: 2026-01-05
    import json
    import os
    dir_path = os.path.dirname(os.path.realpath(__file__))
    with open(f"{dir_path}/players.json", "r") as f:
        players = json.load(f)
    return players    
def get_player(player_id: str | int) -> dict:
    # last updated: 2026-01-05
    import json
    import os
    dir_path = os.path.dirname(os.path.realpath(__file__))
    with open(f"{dir_path}/players.json", "r") as f:
        players = json.load(f)
    return next((player for player in players if player["player_id"] == str(player_id)), None)
def get_player_by_name(player_name: str) -> dict:
    # last updated: 2026-01-05
    import json
    import os
    dir_path = os.path.dirname(os.path.realpath(__file__))
    with open(f"{dir_path}/players.json", "r") as f:
        players = json.load(f)
    return next((player for player in players if player["name"].lower() == player_name.lower()), None)