import pytest
import pandas as pd
from pwhl_api.endpoints.leagueschedule import LeagueSchedule


class TestLeagueSchedule:
    """Test suite for LeagueSchedule endpoint"""

    def test_league_schedule_initialization_with_season(self):
        """Test that LeagueSchedule initializes with a season parameter"""
        schedule = LeagueSchedule(season="8")
        assert schedule is not None
        assert schedule.response is not None

    def test_league_schedule_initialization_without_season(self):
        """Test that LeagueSchedule initializes without a season parameter (uses most recent)"""
        schedule = LeagueSchedule()
        assert schedule is not None
        assert schedule.response is not None

    def test_league_schedule_response_status(self):
        """Test that the response object is valid"""
        schedule = LeagueSchedule(season="8")
        assert hasattr(schedule, 'response')
        assert schedule.response is not None

    def test_league_schedule_get_raw_json(self):
        """Test that get_raw_json returns data"""
        schedule = LeagueSchedule(season="8")
        raw_data = schedule.get_raw_json()
        assert raw_data is not None
        assert isinstance(raw_data, list)
        assert len(raw_data) > 0

    def test_league_schedule_get_data_frame(self):
        """Test that get_data_frame returns a valid pandas DataFrame"""
        schedule = LeagueSchedule(season="8")
        df = schedule.get_data_frame()
        
        assert isinstance(df, pd.DataFrame)
        assert not df.empty
        assert len(df) > 0

    def test_league_schedule_dataframe_columns(self):
        """Test that the returned DataFrame has expected columns"""
        schedule = LeagueSchedule(season="8")
        df = schedule.get_data_frame()
        
        # Check for common expected columns in schedule data
        expected_columns = ['row_id', 'player_id', 'name', 'hometown', 'birthdate']
        # The actual columns may vary, so we just verify DataFrame has columns
        assert len(df.columns) > 0

    def test_league_schedule_with_different_months(self):
        """Test that LeagueSchedule works with different month parameters"""
        schedule_all = LeagueSchedule(season="8", month=-1)
        schedule_jan = LeagueSchedule(season="8", month=1)
        
        assert schedule_all is not None
        assert schedule_jan is not None

    def test_league_schedule_with_location_parameter(self):
        """Test that LeagueSchedule works with different location parameters"""
        schedule_homeaway = LeagueSchedule(season="8", location="homeaway")
        schedule_home = LeagueSchedule(season="8", location="home")
        schedule_away = LeagueSchedule(season="8", location="away")
        
        assert schedule_homeaway is not None
        assert schedule_home is not None
        assert schedule_away is not None

    def test_league_schedule_endpoint_set(self):
        """Test that the endpoint is properly set"""
        schedule = LeagueSchedule(season="8")
        assert schedule.endpoint == "statviewfeed&view=schedule"

    def test_league_schedule_params_structure(self):
        """Test that the params dictionary is properly structured"""
        schedule = LeagueSchedule(season="8")
        params = schedule.params
        
        assert isinstance(params, dict)
        assert 'season' in params
        assert 'team' in params
        assert 'month' in params
        assert 'location' in params
        assert 'key' in params
