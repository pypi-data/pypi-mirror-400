SkillcornerClient
=================

.. autoclass:: skillcorner.client.SkillcornerClient
   :members:
   :show-inheritance:

.. py:function:: get_competition_competition_editions(self, competition_id: str, raise_for_status: bool = True, **kwargs)

    Retrieve response from /api/competitions/{competition_id}/editions GET request.
    To learn more about it go to: https://skillcorner.com/api/docs/#/competitions/competitions_editions_list.


.. py:function:: get_competition_editions(self, raise_for_status: bool = True, **kwargs) -> Any

    Retrieve response from /api/competition_editions GET request.
    To learn more about it go to: https://skillcorner.com/api/docs/#/competition_editions_list.

.. py:function:: get_competition_rounds(self, competition_id: str, raise_for_status: bool = True,  **kwargs) -> Any

    Retrieve response from /api/competitions/{competition_id}/rounds GET request.
    To learn more about it go to: https://skillcorner.com/api/docs/#/competitions/competitions_rounds_list.

.. py:function:: get_competitions(self, raise_for_status: bool = True, **kwargs) -> Any

    Retrieve response from /api/competitions GET request.
    To learn more about it go to: https://skillcorner.com/api/docs/#/competitions/competitions_list.

.. py:function:: get_data_collections(self, raise_for_status: bool = True, **kwargs) -> Any

    Retrieve response from /api/data_collections GET request.
    To learn more about it go to: https://skillcorner.com/api/docs/#/data_collections/data_collections_list.

.. py:function:: get_dynamic_events(self, match_id: str, raise_for_status: bool = True, **kwargs) -> Any

    Retrieve response from /api/match/{match_id}/dynamic_events GET request.
    To learn more about it go to: https://skillcorner.com/api/docs/#/match/match_dynamic_events_list.

.. py:function:: get_dynamic_events_off_ball_runs(self, match_id: str, raise_for_status: bool = True, **kwargs) -> Any

    Retrieve response from /api/match/{match_id}/dynamic_events/off_ball_runs GET request.
    To learn more about it go to: https://skillcorner.com/api/docs/#/match/match_dynamic_events_off_ball_runs_list.

.. py:function:: get_dynamic_events_on_ball_engagements(self, match_id: str, raise_for_status: bool = True, **kwargs) -> Any

    Retrieve response from /api/match/{match_id}/dynamic_events/on_ball_engagements/ GET request.
    To learn more about it go to: https://skillcorner.com/api/docs/#/match/match_dynamic_events_on_ball_engagement_list.

.. py:function:: get_dynamic_events_passing_options(self, match_id: str, raise_for_status: bool = True, **kwargs) -> Any

    Retrieve response from /api/match/{match_id}/dynamic_events/passing_options GET request.
    To learn more about it go to: https://skillcorner.com/api/docs/#/match/match_dynamic_events_passing_options_list.

.. py:function:: get_dynamic_events_phases_of_play(self, match_id: str, raise_for_status: bool = True, **kwargs) -> Any

    Retrieve response from /api/match/{match_id}/dynamic_events/phases_of_play/ GET request.
    To learn more about it go to: https://skillcorner.com/api/docs/#/match/match_dynamic_events_phases_of_play_list.

.. py:function:: get_dynamic_events_player_possessions(self, match_id: str, raise_for_status: bool = True, **kwargs) -> Any

    Retrieve response from /api/match/{match_id}/dynamic_events/player_possessions GET request.
    To learn more about it go to: https://skillcorner.com/api/docs/#/match/match_dynamic_events_player_possessions_list.

.. py:function:: get_in_possession_off_ball_runs(self, raise_for_status: bool = True, **kwargs) -> Any

    Retrieve response from /api/in_possession/off_ball_runs GET request.
    To learn more about it go to: https://skillcorner.com/api/docs/#/in_possession/in_possession_off_ball_runs_list.

.. py:function:: get_in_possession_on_ball_pressures(self, raise_for_status: bool = True, **kwargs) -> Any

    Retrieve response from /api/in_possession/on_ball_pressures GET request.
    To learn more about it go to: https://skillcorner.com/api/docs/#/in_possession/in_possession_on_ball_pressures_list.

.. py:function:: get_in_possession_passes(self, raise_for_status: bool = True, **kwargs) -> Any

    Retrieve response from /api/in_possession/passes GET request.
    To learn more about it go to: https://skillcorner.com/api/docs/#/in_possession/in_possession_passes_list.

.. py:function:: get_match(self, match_id: str, raise_for_status: bool = True, **kwargs) -> Any

    Retrieve response from /api/match/{match_id} GET request.
    To learn more about it go to: https://skillcorner.com/api/docs/#/match/match_read.

.. py:function:: get_match_data_collection(self, match_id: str, raise_for_status: bool = True, **kwargs) -> Any

    Retrieve response from /api/match/{match_id}/data_collection GET request.
    To learn more about it go to: https://skillcorner.com/api/docs/#/match/match_data_collection_read.

.. py:function:: get_match_instructions(self, match_id: str, raise_for_status: bool = True, **kwargs) -> Any

    Match instructions

.. py:function:: get_match_tracking_data(self, match_id: str, raise_for_status: bool = True, **kwargs) -> Any

    Retrieve response from /api/match/{match_id}/tracking GET request.
    To learn more about it go to: https://skillcorner.com/api/docs/#/match/match_tracking_list.

.. py:function:: get_matches(self, raise_for_status: bool = True, **kwargs) -> Any

    Retrieve response from /api/matches GET request.
    To learn more about it go to: https://skillcorner.com/api/docs/#/matches/matches_list.

.. py:function:: get_physical(self, raise_for_status: bool = True, **kwargs) -> Any

    Retrieve response from /api/physical GET request.
    To learn more about it go to: https://skillcorner.com/api/docs/#/physical/physical_list.

.. py:function:: get_player(self, player_id: str, raise_for_status: bool = True, **kwargs) -> Any

    Retrieve response from /api/players/{player_id} GET request.
    To learn more about it go to: https://skillcorner.com/api/docs/#/players/players_read.

.. py:function:: get_players(self, raise_for_status: bool = True, **kwargs) -> Any

    Retrieve response from /api/players GET request.
    To learn more about it go to: https://skillcorner.com/api/docs/#/players/players_list.

.. py:function:: get_seasons(self, raise_for_status: bool = True, **kwargs) -> Any

    Retrieve response from /api/seasons GET request.
    To learn more about it go to: https://skillcorner.com/api/docs/#/seasons/seasons_list.

.. py:function:: get_team(self, team_id: str, raise_for_status: bool = True, **kwargs) -> Any

    Retrieve response from /api/teams/{team_id} GET request.
    To learn more about it go to: https://skillcorner.com/api/docs/#/teams/teams_read.

.. py:function:: get_teams(self, raise_for_status: bool = True, **kwargs) -> Any

    Retrieve response from /api/teams GET request.
    To learn more about it go to: https://skillcorner.com/api/docs/#/teams/teams_list.

.. py:function:: save_competition_competition_editions(self, competition_id: str, filepath: str, raise_for_status: bool = True, **kwargs) -> None

    Retrieve response from /api/competitions/{competition_id}/editions GET request.
    To learn more about it go to: https://skillcorner.com/api/docs/#/competitions/competitions_editions_list.

 .. py:function:: save_competition_editions(self, filepath: str, raise_for_status: bool = True, **kwargs) -> None

    Retrieve response from /api/competition_editions GET request.
    To learn more about it go to: https://skillcorner.com/api/docs/#/competition_editions_list.

.. py:function:: save_competition_rounds(self, competition_id: str, filepath: str, raise_for_status: bool = True, **kwargs) -> None

    Retrieve response from /api/competitions/{competition_id}/rounds GET request.
    To learn more about it go to: https://skillcorner.com/api/docs/#/competitions/competitions_rounds_list.

.. py:function:: save_competitions(self, filepath: str, raise_for_status: bool = True, **kwargs) -> None

    Retrieve response from /api/competitions GET request.
    To learn more about it go to: https://skillcorner.com/api/docs/#/competitions/competitions_list.

.. py:function:: save_dynamic_events(self, match_id: str, filepath: str, raise_for_status: bool = True, **kwargs) -> None

    Retrieve response from /api/match/{match_id}/dynamic_events GET request.
    To learn more about it go to: https://skillcorner.com/api/docs/#/match/match_dynamic_events_list.

.. py:function:: save_dynamic_events_off_ball_runs(self, match_id: str, filepath: str, raise_for_status: bool = True, **kwargs) -> None

    Retrieve response from /api/match/{match_id}/dynamic_events/off_ball_runs GET request.
    To learn more about it go to: https://skillcorner.com/api/docs/#/match/match_dynamic_events_off_ball_runs_list.

.. py:function:: save_dynamic_events_on_ball_engagements(self, match_id: str, filepath: str, raise_for_status: bool = True, **kwargs) -> None

    Retrieve response from /api/match/{match_id}/dynamic_events/on_ball_engagements/ GET request.
    To learn more about it go to: https://skillcorner.com/api/docs/#/match/match_dynamic_events_on_ball_engagement_list.

.. py:function:: save_dynamic_events_passing_options(self, match_id: str, filepath: str, raise_for_status: bool = True, **kwargs) -> None

    Retrieve response from /api/match/{match_id}/dynamic_events/passing_options GET request.
    To learn more about it go to: https://skillcorner.com/api/docs/#/match/match_dynamic_events_passing_options_list.

.. py:function:: save_dynamic_events_phases_of_play(self, match_id: str, filepath: str, raise_for_status: bool = True, **kwargs) -> None

    Retrieve response from /api/match/{match_id}/dynamic_events/phases_of_play/ GET request.
    To learn more about it go to: https://skillcorner.com/api/docs/#/match/match_dynamic_events_phases_of_play_list.

.. py:function:: save_dynamic_events_player_possessions(self, match_id: str, filepath: str, raise_for_status: bool = True, **kwargs) -> None

    Retrieve response from /api/match/{match_id}/dynamic_events/player_possessions GET request.
    To learn more about it go to: https://skillcorner.com/api/docs/#/match/match_dynamic_events_player_possessions_list.

.. py:function:: save_in_possession_off_ball_runs(self, filepath: str, raise_for_status: bool = True, **kwargs) -> None

    Retrieve response from /api/in_possession/off_ball_runs GET request.
    To learn more about it go to: https://skillcorner.com/api/docs/#/in_possession/in_possession_off_ball_runs_list.

.. py:function:: save_in_possession_on_ball_pressures(self, filepath: str, raise_for_status: bool = True, **kwargs) -> None

    Retrieve response from /api/in_possession/on_ball_pressures GET request.
    To learn more about it go to: https://skillcorner.com/api/docs/#/in_possession/in_possession_on_ball_pressures_list.

.. py:function:: save_in_possession_passes(self, filepath: str, raise_for_status: bool = True, **kwargs) -> None

    Retrieve response from /api/in_possession/passes GET request.
    To learn more about it go to: https://skillcorner.com/api/docs/#/in_possession/in_possession_passes_list.

.. py:function:: save_match(self, match_id: str, filepath: str, raise_for_status: bool = True, **kwargs) -> None

    Retrieve response from /api/match/{match_id} GET request.
    To learn more about it go to: https://skillcorner.com/api/docs/#/match/match_read.

.. py:function:: save_match_data_collection(self, match_id: str, filepath: str, raise_for_status: bool = True, **kwargs) -> None

    Retrieve response from /api/match/{match_id}/data_collection GET request.
    To learn more about it go to: https://skillcorner.com/api/docs/#/match/match_data_collection_read.

.. py:function:: save_match_instructions(self, match_id: str, filepath: str, raise_for_status: bool = True, **kwargs) -> None

    Match instructions

.. py:function:: save_match_tracking_data(self, match_id: str, filepath: str, raise_for_status: bool = True, **kwargs) -> None

    Retrieve response from /api/match/{match_id}/tracking GET request.
    To learn more about it go to: https://skillcorner.com/api/docs/#/match/match_tracking_list.

.. py:function:: save_matches(self, filepath: str, raise_for_status: bool = True, **kwargs) -> None

    Retrieve response from /api/matches GET request.
    To learn more about it go to: https://skillcorner.com/api/docs/#/matches/matches_list.

.. py:function:: save_physical(self, filepath: str, raise_for_status: bool = True, **kwargs) -> None

    Retrieve response from /api/physical GET request.
    To learn more about it go to: https://skillcorner.com/api/docs/#/physical/physical_list.

.. py:function:: save_player(self, player_id: str, filepath: str, raise_for_status: bool = True, **kwargs) -> None

    Retrieve response from /api/players/{player_id} GET request.
    To learn more about it go to: https://skillcorner.com/api/docs/#/players/players_read.

.. py:function:: save_players(self, filepath: str, raise_for_status: bool = True, **kwargs) -> None

    Retrieve response from /api/players GET request.
    To learn more about it go to: https://skillcorner.com/api/docs/#/players/players_list.

.. py:function:: save_seasons(self, filepath: str, raise_for_status: bool = True, **kwargs) -> None

    Retrieve response from /api/seasons GET request.
    To learn more about it go to: https://skillcorner.com/api/docs/#/seasons/seasons_list.

.. py:function:: save_team(self, team_id: str, filepath: str, raise_for_status: bool = True, **kwargs) -> None

    Retrieve response from /api/teams/{team_id} GET request.
    To learn more about it go to: https://skillcorner.com/api/docs/#/teams/teams_read.

.. py:function:: save_teams(self, filepath: str, raise_for_status: bool = True, **kwargs) -> None

    Retrieve response from /api/teams GET request.
    To learn more about it go to: https://skillcorner.com/api/docs/#/teams/teams_list.
