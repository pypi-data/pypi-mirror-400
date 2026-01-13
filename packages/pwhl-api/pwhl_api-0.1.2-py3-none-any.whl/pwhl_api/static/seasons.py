def get_season(season_name: str) -> str:
    import json
    import os
    dir_path = os.path.dirname(os.path.realpath(__file__))
    with open(f"{dir_path}/seasons.json", "r") as f:
        seasons = json.load(f)
    return seasons.get(season_name, None)

def get_season_by_id(season_id: str) -> str:
    import json
    import os
    dir_path = os.path.dirname(os.path.realpath(__file__))
    with open(f"{dir_path}/seasons.json", "r") as f:
        seasons = json.load(f)
    for name, id in seasons.items():
        if id == season_id:
            return name
    return None

def get_most_recent_season() -> str:
    import json
    import os
    dir_path = os.path.dirname(os.path.realpath(__file__))
    with open(f"{dir_path}/seasons.json", "r") as f:
        seasons = json.load(f)
    most_recent_season = max(seasons.values(), key=int)
    return most_recent_season