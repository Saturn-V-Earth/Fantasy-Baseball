import mlbstatsapi

mlb = mlb = mlbstatsapi.Mlb()

teamID = mlb.get_team_id('Philadelphia Phillies')[0]

roster = mlb.get_team_roster(teamID, roster_type=['fullRoster'], season=['2024'])


for players in roster:
    print('\n')
    print(players.fullname)
    print(players.id)
    player_id = mlb.get_people_id(players.fullname)[0]
    print(players.primaryposition.abbreviation)

    try: 
        batter_stats = mlb.get_player_stats(player_id, stats=['season'], groups=['hitting'], season=2023)
        season_stats = batter_stats['hitting']['season']
        for split in season_stats.splits:
            batter_avg = '0' + split.stat.avg
            break
    except KeyError:
        print(None)
    
    try:
        pitcher_stats = mlb.get_player_stats(player_id, stats=['season'], groups=['pitching'], season=2023)
        era = pitcher_stats['pitching']['season']
        for split in era.splits:
            era = split.stat.era
            break
    except KeyError:
        print(None)

    try:
        pitcher_stats = mlb.get_player_stats(player_id, stats=['season'], groups=['fielding'], season=2023)
        fielding = pitcher_stats['fielding']['season']
        for split in fielding.splits:
            fielding = split.stat.fielding
            if fielding != '1.000':
                fielding = '0' + split.stat.fielding
            break
    except KeyError:
        print(None)
        
"""

player_id = mlb.get_people_id("Alec Bohm")[0]
stats = ['season', 'career']  # You can specify other stat types here
groups = ['fielding']

params = {'season': 2023}  # Replace with the desired season

pitching_stats_dict = mlb.get_player_stats(player_id, stats, groups, **params)

pitching_stats = pitching_stats_dict['fielding']

for stat_type, stat_obj in pitching_stats.items():
    print(f"Stat Type: {stat_type}")
    for k, v in stat_obj.__dict__.items():
        print(f"{k}: {v}")
"""