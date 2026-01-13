import pytest
import pandas as pd
from pwhl_api.endpoints.gamesummary import GameSummary


class TestGameSummary:
    """Test suite for GameSummary endpoint"""

    def test_gamesummary_initialization(self):
        """Test that GameSummary initializes with a game_id parameter"""
        gs = GameSummary(game_id="227")
        assert gs is not None
        assert gs.response is not None

    def test_gamesummary_response_status(self):
        """Test that the response object is valid"""
        gs = GameSummary(game_id="227")
        assert hasattr(gs, 'response')
        assert gs.response is not None

    def test_gamesummary_get_raw_json(self):
        """Test that get_raw_json returns data"""
        gs = GameSummary(game_id="227")
        raw_data = gs.get_raw_json()
        assert raw_data is not None
        assert isinstance(raw_data, dict)
        assert 'details' in raw_data

    def test_gamesummary_get_data_frames(self):
        """Test that get_data_frames returns a dictionary of DataFrames"""
        gs = GameSummary(game_id="227")
        dfs = gs.get_data_frames()
        
        assert isinstance(dfs, dict)
        assert 'details' in dfs
        assert 'homeTeam' in dfs
        assert 'visitingTeam' in dfs
        assert 'periods' in dfs
        assert 'mostValuablePlayers' in dfs
        assert 'penalties' in dfs

    def test_gamesummary_details_dataframe(self):
        """Test that the details DataFrame is properly structured"""
        gs = GameSummary(game_id="227")
        dfs = gs.get_data_frames()
        
        details = dfs['details']
        assert isinstance(details, pd.DataFrame)
        assert not details.empty

    def test_gamesummary_home_team_structure(self):
        """Test that homeTeam has the expected nested structure"""
        gs = GameSummary(game_id="227")
        dfs = gs.get_data_frames()
        
        home_team = dfs['homeTeam']
        assert isinstance(home_team, dict)
        assert 'TeamInfo' in home_team
        assert 'TeamStats' in home_team
        assert 'TeamRecord' in home_team
        assert 'SkaterStats' in home_team
        assert 'GoalieStats' in home_team

    def test_gamesummary_visiting_team_structure(self):
        """Test that visitingTeam has the expected nested structure"""
        gs = GameSummary(game_id="227")
        dfs = gs.get_data_frames()
        
        away_team = dfs['visitingTeam']
        assert isinstance(away_team, dict)
        assert 'TeamInfo' in away_team
        assert 'TeamStats' in away_team
        assert 'TeamRecord' in away_team
        assert 'SkaterStats' in away_team
        assert 'GoalieStats' in away_team

    def test_gamesummary_team_info_dataframe(self):
        """Test that TeamInfo DataFrames are properly structured"""
        gs = GameSummary(game_id="227")
        dfs = gs.get_data_frames()
        
        home_info = dfs['homeTeam']['TeamInfo']
        away_info = dfs['visitingTeam']['TeamInfo']
        
        assert isinstance(home_info, pd.DataFrame)
        assert isinstance(away_info, pd.DataFrame)
        assert not home_info.empty
        assert not away_info.empty

    def test_gamesummary_skater_stats_dataframe(self):
        """Test that SkaterStats DataFrames are properly structured"""
        gs = GameSummary(game_id="227")
        dfs = gs.get_data_frames()
        
        home_skaters = dfs['homeTeam']['SkaterStats']
        away_skaters = dfs['visitingTeam']['SkaterStats']
        
        assert isinstance(home_skaters, pd.DataFrame)
        assert isinstance(away_skaters, pd.DataFrame)
        # Skaters may be empty in some games
        if not home_skaters.empty:
            assert 'player_id' in home_skaters.columns
            assert 'name' in home_skaters.columns
            assert 'position' in home_skaters.columns

    def test_gamesummary_goalie_stats_dataframe(self):
        """Test that GoalieStats DataFrames are properly structured"""
        gs = GameSummary(game_id="227")
        dfs = gs.get_data_frames()
        
        home_goalies = dfs['homeTeam']['GoalieStats']
        away_goalies = dfs['visitingTeam']['GoalieStats']
        
        assert isinstance(home_goalies, pd.DataFrame)
        assert isinstance(away_goalies, pd.DataFrame)
        # Goalies may be empty in some games
        if not home_goalies.empty:
            assert 'player_id' in home_goalies.columns
            assert 'name' in home_goalies.columns
            assert 'position' in home_goalies.columns

    def test_gamesummary_team_record_dataframe(self):
        """Test that TeamRecord DataFrames are properly structured"""
        gs = GameSummary(game_id="227")
        dfs = gs.get_data_frames()
        
        home_record = dfs['homeTeam']['TeamRecord']
        away_record = dfs['visitingTeam']['TeamRecord']
        
        assert isinstance(home_record, pd.DataFrame)
        assert isinstance(away_record, pd.DataFrame)
        assert not home_record.empty
        assert not away_record.empty

    def test_gamesummary_team_stats_dataframe(self):
        """Test that TeamStats DataFrames are properly structured"""
        gs = GameSummary(game_id="227")
        dfs = gs.get_data_frames()
        
        home_stats = dfs['homeTeam']['TeamStats']
        away_stats = dfs['visitingTeam']['TeamStats']
        
        assert isinstance(home_stats, pd.DataFrame)
        assert isinstance(away_stats, pd.DataFrame)
        assert not home_stats.empty
        assert not away_stats.empty

    def test_gamesummary_periods_structure(self):
        """Test that periods has the expected nested structure"""
        gs = GameSummary(game_id="227")
        dfs = gs.get_data_frames()
        
        periods = dfs['periods']
        assert isinstance(periods, dict)
        assert 'goals' in periods
        assert 'shots' in periods

    def test_gamesummary_goals_by_period_dataframe(self):
        """Test that goals by period DataFrame is properly structured"""
        gs = GameSummary(game_id="227")
        dfs = gs.get_data_frames()
        
        goals = dfs['periods']['goals']
        assert isinstance(goals, pd.DataFrame)
        assert not goals.empty
        assert 'T' in goals.columns  # Total column

    def test_gamesummary_shots_by_period_dataframe(self):
        """Test that shots by period DataFrame is properly structured"""
        gs = GameSummary(game_id="227")
        dfs = gs.get_data_frames()
        
        shots = dfs['periods']['shots']
        assert isinstance(shots, pd.DataFrame)
        assert not shots.empty
        assert 'T' in shots.columns  # Total column

    def test_gamesummary_most_valuable_players_dataframe(self):
        """Test that mostValuablePlayers DataFrame is properly structured"""
        gs = GameSummary(game_id="227")
        dfs = gs.get_data_frames()
        
        mvps = dfs['mostValuablePlayers']
        assert isinstance(mvps, pd.DataFrame)
        # MVPs may be empty in some games
        if not mvps.empty:
            assert 'player_id' in mvps.columns
            assert 'name' in mvps.columns
            assert 'position' in mvps.columns

    def test_gamesummary_penalties_dataframe(self):
        """Test that penalties DataFrame is properly structured"""
        gs = GameSummary(game_id="227")
        dfs = gs.get_data_frames()
        
        penalties = dfs['penalties']
        assert isinstance(penalties, pd.DataFrame)
        # Penalties may be empty in some games
        if not penalties.empty:
            expected_columns = ['game_penalty_id', 'period_id', 'time', 'description', 
                              'against_team_id', 'against_team_abbreviation', 'minutes',
                              'taken_by_id', 'taken_by_name', 'is_power_play', 'is_bench']
            for col in expected_columns:
                assert col in penalties.columns

    def test_gamesummary_endpoint_set(self):
        """Test that the endpoint is properly set"""
        gs = GameSummary(game_id="227")
        assert gs.endpoint == "statviewfeed&view=gameSummary"

    def test_gamesummary_params_structure(self):
        """Test that the params dictionary is properly structured"""
        gs = GameSummary(game_id="227")
        params = gs.params
        
        assert isinstance(params, dict)
        assert 'game_id' in params
        assert 'key' in params
        assert 'client_code' in params
        assert params['game_id'] == "227"

    def test_gamesummary_with_different_game_id(self):
        """Test that GameSummary works with a different game_id"""
        gs = GameSummary(game_id="248")
        dfs = gs.get_data_frames()
        
        assert 'details' in dfs
        assert isinstance(dfs['details'], pd.DataFrame)

    def test_gamesummary_skater_stats_columns_ordered(self):
        """Test that SkaterStats columns are ordered with player info first"""
        gs = GameSummary(game_id="227")
        dfs = gs.get_data_frames()
        
        home_skaters = dfs['homeTeam']['SkaterStats']
        if not home_skaters.empty:
            cols = home_skaters.columns.tolist()
            # Check that player_id, name, position are first
            assert cols[0] == 'player_id'
            assert cols[1] == 'name'
            assert cols[2] == 'position'

    def test_gamesummary_goalie_stats_columns_ordered(self):
        """Test that GoalieStats columns are ordered with player info first"""
        gs = GameSummary(game_id="227")
        dfs = gs.get_data_frames()
        
        home_goalies = dfs['homeTeam']['GoalieStats']
        if not home_goalies.empty:
            cols = home_goalies.columns.tolist()
            # Check that player_id, name, position are first
            assert cols[0] == 'player_id'
            assert cols[1] == 'name'
            assert cols[2] == 'position'
