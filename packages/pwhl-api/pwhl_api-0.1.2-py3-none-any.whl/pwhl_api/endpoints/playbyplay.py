from pwhl_api.endpoints.library.http import HTTPEndpointClient, HTTPEndpointResponse

class PlayByPlay(HTTPEndpointResponse):
    def __init__(self, game_id: str):
        client = HTTPEndpointClient()
        self.endpoint = f"statviewfeed&view=gameCenterPlayByPlay"
        self.params = {
            "game_id": game_id,
            "key": "446521baf8c38984",
            "client_code": "pwhl",
            "site_id": 0,
            "league_id": 1
        }
        self.response = client.get(self.endpoint, params = self.params)
    def get_data_frame(self):
        import pandas as pd
        events = self.get_raw_json()
        events_data = []
        for idx, event in enumerate(events):
            event_id = idx
            base = {
                'event_id': event_id,
                'event_type': event['event'],
                'period_id': event['details'].get('period', {}).get('id'),
                'time': event['details'].get('time'),
                'x_location': event['details'].get('xLocation'),
                'y_location': event['details'].get('yLocation'),
            }
            events_data.append(base)
        return pd.DataFrame(events_data)
    
    def get_data_frames(self):
        import pandas as pd
        events = self.get_raw_json()
        # Main events table
        events_data = []
        # Related tables
        shots_data = []
        goals_data = []
        assists_data = []
        penalties_data = []
        
        for idx, event in enumerate(events):
            event_id = idx
            base = {
                'event_id': event_id,
                'event_type': event['event'],
                'period_id': event['details'].get('period', {}).get('id'),
                'time': event['details'].get('time'),
                'x_location': event['details'].get('xLocation'),
                'y_location': event['details'].get('yLocation'),
            }
            events_data.append(base)
            
            if event['event'] in ['shot', 'blocked_shot']:
                shots_data.append({
                    'event_id': event_id,
                    'time': event['details'].get('time'),
                    'period_type': event['details'].get('period', {}).get('shortName') if event['details'].get('period').get('shortName') else event['details'].get('period').get('id'),
                    'shooter_id': event['details'].get('shooter', {}).get('id'),
                    'shooter_name': f"{event['details'].get('shooter', {}).get('firstName', '')} {event['details'].get('shooter', {}).get('lastName', '')}",
                    'goalie_id': event['details'].get('goalie', {}).get('id'),
                    'goalie_name': f"{event['details'].get('goalie', {}).get('firstName', '')} {event['details'].get('goalie', {}).get('lastName', '')}",
                    'is_goal': event['details'].get('isGoal'),
                    'shot_quality': event['details'].get('shotQuality'),
                    'shot_type': event['details'].get('shotType'),
                    'xLocation': event['details'].get('xLocation'),
                    'yLocation': event['details'].get('yLocation'),
                    'blocker_id': event['details'].get('blocker', {}).get('id') if event['event'] == 'blocked_shot' else None,
                    'blocker_name': f"{event['details'].get('blocker', {}).get('firstName', '')} {event['details'].get('blocker', {}).get('lastName', '')}" if event['event'] == 'blocked_shot' else None,
                })
            
            if event['event'] == 'goal':
                goals_data.append({
                    'event_id': event_id,
                    'scorer_id': event['details'].get('scoredBy', {}).get('id'),
                    'scorer_name': f"{event['details'].get('scoredBy', {}).get('firstName', '')} {event['details'].get('scoredBy', {}).get('lastName', '')}",
                    'time': event['details'].get('time'),
                    'period_type': event['details'].get('period', {}).get('shortName') if event['details'].get('period').get('shortName') else event['details'].get('period').get('id'),
                    'xLocation': event['details'].get('xLocation'),
                    'yLocation': event['details'].get('yLocation'),
                    'isPowerPlay': event['details'].get('properties', {}).get('isPowerPlay'),
                    'isShortHanded': event['details'].get('properties', {}).get('isShortHanded'),
                    'isEmptyNet': event['details'].get('properties', {}).get('isEmptyNet'),
                    'isPenaltyShot': event['details'].get('properties', {}).get('isPenaltyShot'),
                    'isInsuranceGoal': event['details'].get('properties', {}).get('isInsuranceGoal'),
                    'isGameWinningGoal': event['details'].get('properties', {}).get('isGameWinningGoal'),
                })
                for i, assist in enumerate(event['details'].get('assists', [])):
                    assists_data.append({
                        'event_id': event_id,
                        'assist_number': i + 1,
                        'player_id': assist['id'],
                        'player_name': f"{assist['firstName']} {assist['lastName']}",
                    })
            
            if event['event'] == 'penalty':
                penalties_data.append({
                    'event_id': event_id,
                    'minutes': event['details'].get('minutes'),
                    'description': event['details'].get('description'),
                    'player_id': event['details'].get('takenBy', {}).get('id'),
                })
        
        return {
            'events': pd.DataFrame(events_data),
            'shots': pd.DataFrame(shots_data),
            'goals': pd.DataFrame(goals_data),
            'assists': pd.DataFrame(assists_data),
            'penalties': pd.DataFrame(penalties_data),
        }