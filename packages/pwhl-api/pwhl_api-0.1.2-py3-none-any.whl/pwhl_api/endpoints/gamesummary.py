# https://lscluster.hockeytech.com/feed/index.php?feed=statviewfeed&view=gameCenterPreview&game_id=248&key=446521baf8c38984&client_code=pwhl&lang=en&league_id=
from pwhl_api.endpoints.library.http import HTTPEndpointClient, HTTPEndpointResponse

class GameSummary(HTTPEndpointResponse):
    def __init__(self, game_id: str):
        client = HTTPEndpointClient()
        self.endpoint = f"statviewfeed&view=gameSummary"
        self.params = {
            "game_id": game_id,
            "key": "446521baf8c38984",
            "client_code": "pwhl",
            "site_id": 0,
            "league_id": 1
        }
        self.response = client.get(self.endpoint, params = self.params)
    def get_data_frames(self) -> dict:
        """Returns the game summary data as a dictionary of DataFrames."""
        import pandas as pd
        summary = self.get_raw_json()
        home = summary['homeTeam']['info']
        away = summary['visitingTeam']['info']
        frames = {
            'details': pd.DataFrame.from_dict(summary['details'], orient='index').T,
            'penalties': None,
            'homeTeam': {
                'TeamInfo': pd.DataFrame.from_dict(summary['homeTeam']['info'], orient='index').T,
                'TeamStats': pd.DataFrame.from_dict(summary['homeTeam']['stats'], orient='index').T,
                'SkaterStats': None,
                'GoalieStats': None,
                'TeamRecord': pd.DataFrame.from_dict(summary['homeTeam']['seasonStats']['teamRecord'], orient='index').T,  
            },
            'visitingTeam': {
                'TeamInfo': pd.DataFrame.from_dict(summary['visitingTeam']['info'], orient='index').T,
                'TeamStats': pd.DataFrame.from_dict(summary['visitingTeam']['stats'], orient='index').T,
                'SkaterStats': None,
                'GoalieStats': None,
                'TeamRecord': pd.DataFrame.from_dict(summary['visitingTeam']['seasonStats']['teamRecord'], orient='index').T,  
            },
            'periods': {
                'goals': None,
                'shots': None,
            },
            'mostValuablePlayers': None
        }
        for skater in summary['homeTeam']['skaters']:
            if frames['homeTeam']['SkaterStats'] is None:
                frames['homeTeam']['SkaterStats'] = []
            curr = skater['stats']
            curr['name'] = skater['info']['firstName'] + ' ' + skater['info']['lastName']
            curr['player_id'] = skater['info']['id']
            curr['position'] = skater['info']['position']
            frames['homeTeam']['SkaterStats'].append(curr)
        frames['homeTeam']['SkaterStats'] = pd.DataFrame(frames['homeTeam']['SkaterStats'])
        # reorder columns to have player_id, name, position first
        if not frames['homeTeam']['SkaterStats'].empty:
            cols = frames['homeTeam']['SkaterStats'].columns.tolist()
            cols.insert(0, cols.pop(cols.index('position')))
            cols.insert(0, cols.pop(cols.index('name')))
            cols.insert(0, cols.pop(cols.index('player_id')))
            frames['homeTeam']['SkaterStats'] = frames['homeTeam']['SkaterStats'][cols]

        for skater in summary['visitingTeam']['skaters']:
            if frames['visitingTeam']['SkaterStats'] is None:
                frames['visitingTeam']['SkaterStats'] = []
            curr = skater['stats']
            curr['name'] = skater['info']['firstName'] + ' ' + skater['info']['lastName']
            curr['player_id'] = skater['info']['id']
            curr['position'] = skater['info']['position']
            frames['visitingTeam']['SkaterStats'].append(curr)
        frames['visitingTeam']['SkaterStats'] = pd.DataFrame(frames['visitingTeam']['SkaterStats'])
        
        if not frames['visitingTeam']['SkaterStats'].empty:
            cols = frames['visitingTeam']['SkaterStats'].columns.tolist()
            cols.insert(0, cols.pop(cols.index('position')))
            cols.insert(0, cols.pop(cols.index('name')))
            cols.insert(0, cols.pop(cols.index('player_id')))
            frames['visitingTeam']['SkaterStats'] = frames['visitingTeam']['SkaterStats'][cols]

        for goalie in summary['homeTeam']['goalies']:
            if frames['homeTeam']['GoalieStats'] is None:
                frames['homeTeam']['GoalieStats'] = []
            curr = goalie['stats']
            curr['name'] = goalie['info']['firstName'] + ' ' + goalie['info']['lastName']
            curr['player_id'] = goalie['info']['id']
            curr['position'] = goalie['info']['position']
            frames['homeTeam']['GoalieStats'].append(curr)
        frames['homeTeam']['GoalieStats'] = pd.DataFrame(frames['homeTeam']['GoalieStats'])
        
        # reorder columns to have player_id, name, position first
        if not frames['homeTeam']['GoalieStats'].empty:
            cols = frames['homeTeam']['GoalieStats'].columns.tolist()
            cols.insert(0, cols.pop(cols.index('position')))
            cols.insert(0, cols.pop(cols.index('name')))
            cols.insert(0, cols.pop(cols.index('player_id')))
            frames['homeTeam']['GoalieStats'] = frames['homeTeam']['GoalieStats'][cols]

        for goalie in summary['visitingTeam']['goalies']:
            if frames['visitingTeam']['GoalieStats'] is None:
                frames['visitingTeam']['GoalieStats'] = []
            curr = goalie['stats']
            curr['name'] = goalie['info']['firstName'] + ' ' + goalie['info']['lastName']
            curr['player_id'] = goalie['info']['id']
            curr['position'] = goalie['info']['position']
            frames['visitingTeam']['GoalieStats'].append(curr)
        frames['visitingTeam']['GoalieStats'] = pd.DataFrame(frames['visitingTeam']['GoalieStats'])
        
        if not frames['visitingTeam']['GoalieStats'].empty:
            cols = frames['visitingTeam']['GoalieStats'].columns.tolist()
            cols.insert(0, cols.pop(cols.index('position')))
            cols.insert(0, cols.pop(cols.index('name')))
            cols.insert(0, cols.pop(cols.index('player_id')))
            frames['visitingTeam']['GoalieStats'] = frames['visitingTeam']['GoalieStats'][cols]

        for player in summary['mostValuablePlayers']:
            if frames['mostValuablePlayers'] is None:
                frames['mostValuablePlayers'] = []
            curr = player['player']['stats']
            curr['name'] = player['player']['info']['firstName'] + ' ' + player['player']['info']['lastName']
            curr['player_id'] = player['player']['info']['id']
            curr['position'] = player['player']['info']['position']
            frames['mostValuablePlayers'].append(curr)
        
        frames['mostValuablePlayers'] = pd.DataFrame(frames['mostValuablePlayers'])
        # reorder columns to have player_id, name, position first
        if not frames['mostValuablePlayers'].empty:
            cols = frames['mostValuablePlayers'].columns.tolist()
            cols.insert(0, cols.pop(cols.index('position')))
            cols.insert(0, cols.pop(cols.index('name')))
            cols.insert(0, cols.pop(cols.index('player_id')))
            frames['mostValuablePlayers'] = frames['mostValuablePlayers'][cols]

        # for periods, create dataframe that is indexed by team, and has columns for each period, with each value correspond to number of goals scored in that period
        home = summary['homeTeam']['info']
        away = summary['visitingTeam']['info']

        # for periods, create dataframe that is indexed by team, and has columns for each period, with each value correspond to number of goals scored in that period
        periods_df = pd.DataFrame(columns=[period['info']['shortName'] for period in summary['periods']]) 
        shots_df = pd.DataFrame(columns=[period['info']['shortName'] for period in summary['periods']]) 
        for period in summary['periods']:
            # each period has a 'goals' list, with each goal having a 'team' dict
            if home['abbreviation'] not in periods_df.index:
                periods_df.loc[home['abbreviation']] = [0] * len(summary['periods'])
                shots_df.loc[home['abbreviation']] = [0] * len(summary['periods'])
            if away['abbreviation'] not in periods_df.index:
                periods_df.loc[away['abbreviation']] = [0] * len(summary['periods'])
                shots_df.loc[away['abbreviation']] = [0] * len(summary['periods'])
            # goals
            periods_df.at[home['abbreviation'], period['info']['shortName']] = (int)(period['stats']['homeGoals'])
            periods_df.at[away['abbreviation'], period['info']['shortName']] = (int)(period['stats']['visitingGoals'])
            # shots
            shots_df.at[home['abbreviation'], period['info']['shortName']] = (int)(period['stats']['homeShots'])
            shots_df.at[away['abbreviation'], period['info']['shortName']] = (int)(period['stats']['visitingShots'])
        if summary['hasShootout']:
            periods_df['SO'] = 0
            periods_df.at[summary['shootoutDetails']['winningTeam']['abbreviation'], 'SO'] = 1
        periods_df = periods_df.fillna(0).astype(int)
        periods_df['T'] = periods_df.sum(axis=1)
        shots_df = shots_df.fillna(0).astype(int)
        shots_df['T'] = shots_df.sum(axis=1)
        frames['periods']['goals'] = periods_df
        frames['periods']['shots'] = shots_df

        penalties = []
        for period in summary['periods']:
            for penalty in period['penalties']:
                penalties.append([penalty['game_penalty_id'], penalty['period']['id'], penalty['time'], penalty['description'], penalty['againstTeam']['id'], penalty['againstTeam']['abbreviation'], penalty['minutes'], penalty['takenBy']['id'], penalty['takenBy']['firstName'] + " " + penalty['takenBy']['lastName'], penalty['isPowerPlay'], penalty['isBench']])

        penalties_df = pd.DataFrame(penalties, columns=['game_penalty_id', 'period_id', 'time', 'description', 'against_team_id', 'against_team_abbreviation', 'minutes', 'taken_by_id', 'taken_by_name', 'is_power_play', 'is_bench'])
        frames['penalties'] = penalties_df
        return frames