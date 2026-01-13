import pytest
import pandas as pd
from pwhl_api.endpoints.leaguestandings import LeagueStandings


class TestLeagueStandings:
    """Test suite for LeagueStandings endpoint"""

    def test_league_standings_initialization_with_season(self):
        """Test that LeagueStandings initializes with a season parameter"""
        standings = LeagueStandings(season="8")
        assert standings is not None
        assert standings.response is not None

    def test_league_standings_initialization_without_season(self):
        """Test that LeagueStandings initializes without a season parameter (uses most recent)"""
        standings = LeagueStandings()
        assert standings is not None
        assert standings.response is not None

    def test_league_standings_response_status(self):
        """Test that the response object is valid"""
        standings = LeagueStandings(season="8")
        assert hasattr(standings, 'response')
        assert standings.response is not None

    def test_league_standings_get_raw_json(self):
        """Test that get_raw_json returns data"""
        standings = LeagueStandings(season="8")
        raw_data = standings.get_raw_json()
        assert raw_data is not None
        assert isinstance(raw_data, list)
        assert len(raw_data) > 0

    def test_league_standings_get_data_frame(self):
        """Test that get_data_frame returns a valid pandas DataFrame"""
        standings = LeagueStandings(season="8")
        df = standings.get_data_frame()
        
        assert isinstance(df, pd.DataFrame)
        assert not df.empty
        assert len(df) > 0

    def test_league_standings_dataframe_has_columns(self):
        """Test that the returned DataFrame has columns"""
        standings = LeagueStandings(season="8")
        df = standings.get_data_frame()
        
        assert len(df.columns) > 0

    def test_league_standings_with_context_overall(self):
        """Test that LeagueStandings works with context='overall'"""
        standings = LeagueStandings(season="8", context="overall")
        df = standings.get_data_frame()
        
        assert df is not None
        assert not df.empty

    def test_league_standings_with_context_home(self):
        """Test that LeagueStandings works with context='home'"""
        standings = LeagueStandings(season="8", context="home")
        df = standings.get_data_frame()
        
        assert df is not None
        assert not df.empty

    def test_league_standings_with_context_visiting(self):
        """Test that LeagueStandings works with context='visiting'"""
        standings = LeagueStandings(season="8", context="visiting")
        df = standings.get_data_frame()
        
        assert df is not None
        assert not df.empty

    def test_league_standings_with_special_teams_true(self):
        """Test that LeagueStandings works with special_teams='true'"""
        standings = LeagueStandings(season="8", special_teams="true")
        df = standings.get_data_frame()
        
        assert df is not None
        assert not df.empty

    def test_league_standings_with_special_teams_false(self):
        """Test that LeagueStandings works with special_teams='false'"""
        standings = LeagueStandings(season="8", special_teams="false")
        df = standings.get_data_frame()
        
        assert df is not None
        assert not df.empty

    def test_league_standings_with_sort_points(self):
        """Test that LeagueStandings works with sort='points'"""
        standings = LeagueStandings(season="8", sort="points")
        df = standings.get_data_frame()
        
        assert df is not None
        assert not df.empty

    def test_league_standings_with_sort_power_play_pct(self):
        """Test that LeagueStandings works with sort='power_play_pct'"""
        standings = LeagueStandings(season="8", sort="power_play_pct")
        df = standings.get_data_frame()
        
        assert df is not None
        assert not df.empty

    def test_league_standings_with_sort_penalty_kill_pct(self):
        """Test that LeagueStandings works with sort='penalty_kill_pct'"""
        standings = LeagueStandings(season="8", sort="penalty_kill_pct")
        df = standings.get_data_frame()
        
        assert df is not None
        assert not df.empty

    def test_league_standings_endpoint_set(self):
        """Test that the endpoint is properly set"""
        standings = LeagueStandings(season="8")
        assert standings.endpoint == "statviewfeed&view=teams"

    def test_league_standings_params_structure(self):
        """Test that the params dictionary is properly structured"""
        standings = LeagueStandings(season="8")
        params = standings.params
        
        assert isinstance(params, dict)
        assert 'season' in params
        assert 'context' in params
        assert 'sort' in params
        assert 'special' in params
        assert 'key' in params

    def test_league_standings_with_multiple_parameters(self):
        """Test that LeagueStandings works with multiple parameters"""
        standings = LeagueStandings(
            season="8",
            context="overall",
            special_teams="true",
            sort="power_play_pct"
        )
        df = standings.get_data_frame()
        
        assert df is not None
        assert not df.empty
