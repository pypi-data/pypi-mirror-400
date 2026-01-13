Getting started
===============

Installation
------------

Before using the ``SkillcornerClient``, you need to install it:

.. code-block:: bash

    pip install --upgrade skillcorner

Now you need to set up your Skillcorner credentials by adding the following variables to your environment:

* SKILLCORNER_USERNAME: Your username
* SKILLCORNER_PASSWORD: Your password

How to use it
-------------

You can instantiate the ``SkillcornerClient`` class like so:

.. code-block:: python

    from skillcorner.client import SkillcornerClient

    client = SkillcornerClient()

Alternative
-----------

If you don't want to set those environment variables you will need to provide your username and password at instantiation. We strongly recommend using environment variables or any other way to avoid having your password in your code.

.. code-block:: python

    import os
    from skillcorner.client import SkillcornerClient

    secret_password = os.getenv('MY_PASSWORD_ENV_VAR')
    client = SkillcornerClient(username='myusername', password=secret_password)

Examples
--------

Seasons
~~~~~~~

Get and print seasons data

.. code-block:: python

    seasons = client.get_seasons()
    pprint(seasons)

Competitions
~~~~~~~~~~~~

Get and print competition data for season 2023-2024 (season id 28)

.. code-block:: python

    competitions = client.get_competitions(params={'season': 28})
    pprint(competitions)

Save competition data to a file

.. code-block:: python

    client.save_competitions(filepath='competitions_23_24.json', params={'season': 28})

Competition editions
~~~~~~~~~~~~~~~~~~~~

Get all the Competition Editions

.. code-block:: python

    competition_editions = client.get_competition_editions()
    pprint(competition_editions)

Or we can save the result to a file

.. code-block:: python

    client.save_competition_editions(filepath='competition_editions.json')

Get and print competition editions for FRA Ligue 1 (competition id 3)

.. code-block:: python

    competition_editions = client.get_competition_competition_editions(competition_id=3)
    pprint(competition_editions)

Or we can save the result to a file

.. code-block:: python

    client.save_competition_competition_editions(competition_id=3, filepath='competition_editions_FRA_Ligue_1.json')

We can also filter on the season using the 'params' parameter and retrieve the competition editions for the 2023-2024 season (season id 28)

.. code-block:: python

    competition_editions = client.get_competition_editions(params={'season': 28})
    pprint(competition_editions)

Or we can save the result to a file

.. code-block:: python

    client.save_competition_editions(filepath='competition_editions_23_24.json', params={'season': 28})

Data Collections
~~~~~~~~~~~~~~~~

Get and print data collections (match ids 1023377, 1023378)

.. code-block:: python

    data_collections = client.get_data_collections(params={'match': [1023377, 1023378]})
    pprint(data_collections)

Or we can save the result to a file

.. code-block:: python

    client.save_data_collections(filepath='data_collections_1023377_1023378.json', params={'match': [1023377, 1023378]})

Get and print data collections (competition edition id 548)

.. code-block:: python

    data_collections = client.get_data_collections(params={'competition_edition': 548})
    pprint(data_collections)


Matches
~~~~~~~

Get and print matches for FRA Ligue 1 2023-2024 (competition edition id 548)

.. code-block:: python

    matches = client.get_matches(params={'competition_edition': 548})
    pprint(matches)

Save matches to a file

.. code-block:: python

    client.save_matches(filepath='matches_FRA_Ligue_1_2023_2024.json', params={'competition_edition': 548})

Match data
~~~~~~~~~~

Get and print match data for FRA Ligue 1 2023-2024 - Clermont Foot vs AS Monaco (match id 1023377)

.. code-block:: python

    match_id = 1023377
    match_data = client.get_match(match_id=match_id)
    pprint(match_data)

Save match data to a file

.. code-block:: python

    client.save_match(match_id=match_id, filepath=f'match_data_{match_id}.json')

Match Tracking Data
~~~~~~~~~~~~~~~~~~~

Get and print match tracking data (if you have access to the match tracking data API)

.. code-block:: python

    match_id = 1023377  # FRA Ligue 1 2023-2024 - Clermont Foot vs AS Monaco
    match_tracking_data = client.get_match_tracking_data(match_id=match_id, params={'data_version': 3})
    pprint(match_tracking_data[10000:11000])  # print only the tracking data for frames 10000 to 11000

Save match tracking data to a file

.. code-block:: python

    client.save_match_tracking_data(match_id=match_id, filepath=f'match_tracking_data_{match_id}.jsonl', params={'data_version': 3})

Physical Data
~~~~~~~~~~~~~

Get and print physical data for FRA Ligue 1 2023-2024 - OGC Nice (team id 70)

.. code-block:: python

    physical_data = client.get_physical(params={'season': 28, 'team': 70, 'data_version': 3})
    pprint(physical_data)

Save physical data to a file

.. code-block:: python

    client.save_physical(filepath='physical.json', params={'season': 28, 'team': 70, 'data_version': 3})

In Possession Data
~~~~~~~~~~~~~~~~~~

Get and print off-ball running data for FRA Ligue 1 2023-2024 (competition edition id 548)

.. code-block:: python

    off_ball_runs = client.get_in_possession_off_ball_runs(params={'competition_edition': 548})
    pprint(off_ball_runs)

Get and print passing data for FRA Ligue 1 2023-2024 (competition edition id 548)

.. code-block:: python

    passes = client.get_in_possession_passes(params={'competition_edition': 548})
    pprint(passes)

Get and print overcoming pressure run data for FRA Ligue 1 2023-2024 (competition edition id 548)

.. code-block:: python

    pressure_received = client.get_in_possession_on_ball_pressures(params={'competition_edition': 548})
    pprint(pressure_received)

Dynamic Events
~~~~~~~~~~~~~~

Get a bytes array containing off-ball run events for 2024-03-31 Manchester City Vs Arsenal match (match id 1463739)

.. code-block:: python

    import pandas as pd

    from io import BytesIO

    match_id = 1463739
    off_ball_run_events = client.get_dynamic_events_off_ball_runs(
        match_id=match_id, 
        params={'file_format':'csv', 'ignore_dynamic_events_check': False}
    )
    df_off_ball_run_events = pd.read_csv(BytesIO(off_ball_run_events))

Get a bytes array containing passing option events for 2024-03-31 Manchester City Vs Arsenal match (match id 1463739)

.. code-block:: python

    import pandas as pd

    from io import BytesIO

    match_id = 1463739
    passing_options_events = client.get_dynamic_events_passing_options(
        match_id=match_id, 
        params={'file_format':'csv', 'ignore_dynamic_events_check': False}
    )
    df_passing_options_events = pd.read_csv(BytesIO(passing_options_events))

Get a bytes array containing player possession events for 2024-03-31 Manchester City Vs Arsenal match (match id 1463739)

.. code-block:: python

    from io import BytesIO

    import pandas as pd

    match_id = 1463739
    player_possessions_events = client.get_dynamic_events_player_possessions(
        match_id=match_id, 
        params={'file_format':'csv', 'ignore_dynamic_events_check': False}
    )
    df_player_possessions_events = pd.read_csv(BytesIO(player_possessions_events))

Get a bytes array containing phases of play events for 2024-03-31 Manchester City Vs Arsenal match (match id 1463739)

.. code-block:: python

    from io import BytesIO

    import pandas as pd

    match_id = 1463739
    phases_of_play_events = client.get_dynamic_events_phases_of_play(
        match_id=match_id, 
        params={'file_format':'csv', 'ignore_dynamic_events_check': False}
    )
    df_phases_of_play_events = pd.read_csv(BytesIO(phases_of_play_events))

Get a bytes array containing on-ball engagements events for 2024-03-31 Manchester City Vs Arsenal match (match id 1463739)

.. code-block:: python

    from io import BytesIO

    import pandas as pd

    match_id = 1463739
    on_ball_engagement_events = client.get_dynamic_events_on_ball_engagements(
        match_id=match_id, 
        params={'file_format':'csv', 'ignore_dynamic_events_check': False}
    )
    df_on_ball_engagement_events = pd.read_csv(BytesIO(on_ball_engagement_events))

Get a bytes array containing combined off-ball run, passing option, player possession, phases of play and on-ball engagement events for 2024-03-31 Manchester City Vs Arsenal match (match id 1463739)

.. code-block:: python

    import pandas as pd

    from io import BytesIO

    match_id = 1463739
    combined_dynamic_events = client.get_dynamic_events(
        match_id=match_id, 
        params={'file_format':'csv', 'ignore_dynamic_events_check': False}
    )
    df_combined_dynamic_events = pd.read_csv(BytesIO(combined_dynamic_events))

Save an off-ball run events CSV file for 2024-03-31 Manchester City Vs Arsenal match (match id 1463739)

.. code-block:: python

    match_id = 1463739
    client.save_dynamic_events_off_ball_runs(
        match_id=match_id,
        filepath=f'{match_id}_off_ball_runs.csv',
        params={'file_format':'csv', 'ignore_dynamic_events_check': False}
    )

Save a passing option events CSV file for 2024-03-31 Manchester City Vs Arsenal match (match id 1463739)

.. code-block:: python

    match_id = 1463739
    client.save_dynamic_events_passing_options(
        match_id=match_id,
        filepath=f'{match_id}_off_ball_runs.csv',
        params={'file_format':'csv', 'ignore_dynamic_events_check': False}
    )


Save a player possession events CSV file for 2024-03-31 Manchester City Vs Arsenal match (match id 1463739)

.. code-block:: python

    match_id = 1463739
    client.save_dynamic_events_player_possessions(
        match_id=match_id,
        filepath=f'{match_id}_off_ball_runs.csv',
        params={'file_format':'csv', 'ignore_dynamic_events_check': False}
    )

Save a combined off-ball run, passing option and player possession events CSV file for 2024-03-31 Manchester City Vs Arsenal match (match id 1463739)

.. code-block:: python

    match_id = 1463739
    client.save_dynamic_events(
        match_id=match_id,
        filepath=f'{match_id}_off_ball_runs.csv',
        params={'file_format':'csv', 'ignore_dynamic_events_check': False}
    )

Save an off-ball run events Sportscode XML file for 2024-03-31 Manchester City Vs Arsenal match (match id 1463739)

.. code-block:: python

    match_id = 1463739
    client.save_dynamic_events_off_ball_runs(
        match_id=match_id,
        filepath=f'{match_id}_off_ball_runs.xml',
        params={'file_format':'sportscode-xml', 'ignore_dynamic_events_check': False}
    )

Save a passing option events Sportscode XML file for 2024-03-31 Manchester City Vs Arsenal match (match id 1463739)

.. code-block:: python

    match_id = 1463739
    client.save_dynamic_events_passing_options(
        match_id=match_id,
        filepath=f'{match_id}_off_ball_runs.xml',
        params={'file_format':'sportscode-xml', 'ignore_dynamic_events_check': False}
    )

Save a player possession events Sportscode XML file for 2024-03-31 Manchester City Vs Arsenal match (match id 1463739)

.. code-block:: python

    match_id = 1463739
    client.save_dynamic_events_player_possessions(
        match_id=match_id,
        filepath=f'{match_id}_off_ball_runs.xml',
        params={'file_format':'sportscode-xml', 'ignore_dynamic_events_check': False}
    )

Save a combined off-ball run, passing option and player possession events Sportscode XML file for 2024-03-31 Manchester City Vs Arsenal match (match id 1463739)

.. code-block:: python

    match_id = 1463739
    client.save_dynamic_events(
        match_id=match_id,
        filepath=f'{match_id}_off_ball_runs.xml',
        params={'file_format':'sportscode-xml', 'ignore_dynamic_events_check': False}
    )

Save an off-ball run events Focus JSON file for 2024-03-31 Manchester City Vs Arsenal match (match id 1463739)

.. code-block:: python

    match_id = 1463739
    client.save_dynamic_events_off_ball_runs(
        match_id=match_id,
        filepath=f'{match_id}_off_ball_runs.json',
        params={'file_format':'focus-json', 'ignore_dynamic_events_check': False}
    )

Save a passing option events Focus JSON file for 2024-03-31 Manchester City Vs Arsenal match (match id 1463739)

.. code-block:: python

    match_id = 1463739
    client.save_dynamic_events_passing_options(
        match_id=match_id,
        filepath=f'{match_id}_off_ball_runs.json',
        params={'file_format':'focus-json', 'ignore_dynamic_events_check': False}
    )

Save a player possession events Focus JSON file for 2024-03-31 Manchester City Vs Arsenal match (match id 1463739)

.. code-block:: python

    match_id = 1463739
    client.save_dynamic_events_player_possessions(
        match_id=match_id,
        filepath=f'{match_id}_off_ball_runs.json',
        params={'file_format':'focus-json', 'ignore_dynamic_events_check': False}
    )

Save a combined off-ball run, passing option and player possession Focus JSON file for 2024-03-31 Manchester City Vs Arsenal match (match id 1463739)

.. code-block:: python

    match_id = 1463739
    client.save_dynamic_events(
        match_id=match_id,
        filepath=f'{match_id}_off_ball_runs.json',
        params={'file_format':'focus-json', 'ignore_dynamic_events_check': False}
    )

Teams
~~~~~

Get and print teams for FRA Ligue 1 2023-2024 (competition edition id 548)

.. code-block:: python

    teams = client.get_teams(params={'competition_edition': 548})
    pprint(teams)

Save team data

.. code-block:: python

    client.save_teams(filepath='teams_FRA_Ligue_1_2023_2024.json', params={'competition_edition': 548})

Get and print team data for OGC Nice (team id 70)

.. code-block:: python

    team_id = 70
    team_data = client.get_team(team_id=team_id)
    pprint(team_data)

Save team data

.. code-block:: python

    client.save_team(team_id=team_id, filepath=f'team_{team_id}.json')

Players
~~~~~~~

Get and print players

.. code-block:: python

    players = client.get_players(params={'search': 'barcola'})
    pprint(players)

Get and print player data

.. code-block:: python

    player_id = 68485
    player_data = client.get_player(player_id=player_id)
    pprint(player_data)

Save player data

.. code-block:: python

    client.save_player(player_id=player_id, filepath=f'player_{player_id}.json')
