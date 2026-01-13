import pytest
import pandas as pd
from pwhl_api.endpoints.playbyplay import PlayByPlay


class TestPlayByPlay:
    """Test suite for PlayByPlay endpoint"""

    def test_playbyplay_initialization(self):
        """Test that PlayByPlay initializes with a game_id parameter"""
        pbp = PlayByPlay(game_id="215")
        assert pbp is not None
        assert pbp.response is not None

    def test_playbyplay_response_status(self):
        """Test that the response object is valid"""
        pbp = PlayByPlay(game_id="215")
        assert hasattr(pbp, 'response')
        assert pbp.response is not None

    def test_playbyplay_get_raw_json(self):
        """Test that get_raw_json returns data"""
        pbp = PlayByPlay(game_id="215")
        raw_data = pbp.get_raw_json()
        assert raw_data is not None
        assert isinstance(raw_data, list)
        assert len(raw_data) > 0

    def test_playbyplay_get_data_frame(self):
        """Test that get_data_frame returns a valid pandas DataFrame"""
        pbp = PlayByPlay(game_id="215")
        df = pbp.get_data_frame()
        
        assert isinstance(df, pd.DataFrame)
        assert not df.empty
        assert len(df) > 0

    def test_playbyplay_dataframe_columns(self):
        """Test that the returned DataFrame has expected columns"""
        pbp = PlayByPlay(game_id="215")
        df = pbp.get_data_frame()
        
        expected_columns = ['event_id', 'event_type', 'period_id', 'time', 'x_location', 'y_location']
        for col in expected_columns:
            assert col in df.columns

    def test_playbyplay_dataframe_data_types(self):
        """Test that the returned DataFrame has correct data types"""
        pbp = PlayByPlay(game_id="215")
        df = pbp.get_data_frame()
        
        assert df['event_id'].dtype == 'int64'
        assert isinstance(df['event_type'].iloc[0], str)

    def test_playbyplay_get_data_frames(self):
        """Test that get_data_frames returns a dictionary of DataFrames"""
        pbp = PlayByPlay(game_id="215")
        dfs = pbp.get_data_frames()
        
        assert isinstance(dfs, dict)
        assert 'events' in dfs
        assert 'shots' in dfs
        assert 'goals' in dfs
        assert 'assists' in dfs
        assert 'penalties' in dfs

    def test_playbyplay_get_data_frames_events(self):
        """Test that the events DataFrame is properly structured"""
        pbp = PlayByPlay(game_id="215")
        dfs = pbp.get_data_frames()
        
        events_df = dfs['events']
        assert isinstance(events_df, pd.DataFrame)
        assert not events_df.empty
        assert 'event_id' in events_df.columns
        assert 'event_type' in events_df.columns

    def test_playbyplay_get_data_frames_shots(self):
        """Test that the shots DataFrame is properly structured"""
        pbp = PlayByPlay(game_id="215")
        dfs = pbp.get_data_frames()
        
        shots_df = dfs['shots']
        assert isinstance(shots_df, pd.DataFrame)
        # Shots may or may not be empty
        if not shots_df.empty:
            assert 'event_id' in shots_df.columns
            assert 'shooter_id' in shots_df.columns
            assert 'shooter_name' in shots_df.columns

    def test_playbyplay_get_data_frames_goals(self):
        """Test that the goals DataFrame is properly structured"""
        pbp = PlayByPlay(game_id="215")
        dfs = pbp.get_data_frames()
        
        goals_df = dfs['goals']
        assert isinstance(goals_df, pd.DataFrame)
        # Goals may or may not be empty
        if not goals_df.empty:
            assert 'event_id' in goals_df.columns
            assert 'scorer_id' in goals_df.columns
            assert 'scorer_name' in goals_df.columns

    def test_playbyplay_get_data_frames_assists(self):
        """Test that the assists DataFrame is properly structured"""
        pbp = PlayByPlay(game_id="215")
        dfs = pbp.get_data_frames()
        
        assists_df = dfs['assists']
        assert isinstance(assists_df, pd.DataFrame)
        # Assists may or may not be empty
        if not assists_df.empty:
            assert 'event_id' in assists_df.columns
            assert 'assist_number' in assists_df.columns
            assert 'player_id' in assists_df.columns

    def test_playbyplay_get_data_frames_penalties(self):
        """Test that the penalties DataFrame is properly structured"""
        pbp = PlayByPlay(game_id="215")
        dfs = pbp.get_data_frames()
        
        penalties_df = dfs['penalties']
        assert isinstance(penalties_df, pd.DataFrame)
        # Penalties may or may not be empty
        if not penalties_df.empty:
            assert 'event_id' in penalties_df.columns
            assert 'minutes' in penalties_df.columns

    def test_playbyplay_endpoint_set(self):
        """Test that the endpoint is properly set"""
        pbp = PlayByPlay(game_id="215")
        assert pbp.endpoint == "statviewfeed&view=gameCenterPlayByPlay"

    def test_playbyplay_params_structure(self):
        """Test that the params dictionary is properly structured"""
        pbp = PlayByPlay(game_id="215")
        params = pbp.params
        
        assert isinstance(params, dict)
        assert 'game_id' in params
        assert 'key' in params
        assert 'client_code' in params
        assert params['game_id'] == "215"

    def test_playbyplay_with_different_game_id(self):
        """Test that PlayByPlay works with a different game_id"""
        pbp = PlayByPlay(game_id="248")
        dfs = pbp.get_data_frames()
        
        assert 'events' in dfs
        assert isinstance(dfs['events'], pd.DataFrame)

    def test_playbyplay_event_types_present(self):
        """Test that various event types are present in the data"""
        pbp = PlayByPlay(game_id="215")
        df = pbp.get_data_frame()
        
        # Check that we have event types
        event_types = df['event_type'].unique()
        assert len(event_types) > 0
