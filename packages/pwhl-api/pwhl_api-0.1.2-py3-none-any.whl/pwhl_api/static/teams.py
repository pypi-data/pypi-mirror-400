def get_team(team_id: str | int) -> dict:
    import json
    import os
    dir_path = os.path.dirname(os.path.realpath(__file__))
    with open(f"{dir_path}/teams.json", "r") as f:
        teams = json.load(f)
    return next((team for team in teams if team["id"] == str(team_id)), None)

def get_teams() -> list[dict]:
    import json
    import os
    dir_path = os.path.dirname(os.path.realpath(__file__))
    with open(f"{dir_path}/teams.json", "r") as f:
        teams = json.load(f)
    return teams

def get_team_by_name(team_name: str) -> dict:
    import json
    import os
    dir_path = os.path.dirname(os.path.realpath(__file__))
    with open(f"{dir_path}/teams.json", "r") as f:
        teams = json.load(f)
    return next((team for team in teams if (team["name"].lower() == team_name.lower() or team["nickname"].lower() == team_name.lower())), None)