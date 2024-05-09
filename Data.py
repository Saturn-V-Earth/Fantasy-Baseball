import mlbstatsapi

import csv

mlb = mlbstatsapi.Mlb()

game_id = 661500

# Define the filename for the CSV file
csv_filename = "baseball_game_data.csv"

# Open the CSV file in write mode
with open(csv_filename, 'w', newline='') as csvfile:
    # Create a CSV writer object
    csv_writer = csv.writer(csvfile)
    
    # Write the header row
    csv_writer.writerow(['Inning', 'Batter_Avg', 'strike_percentage', 'At_Bat_Outcome'])
    
    for i in range(1000):
        playbyplay = mlb.get_game_play_by_play(game_id)

        try:
            all_plays = playbyplay.allplays
        except AttributeError:
            print("No plays found for game.")
            continue

        # Iterate over all plays
        for play in all_plays:
            # Extract inning number from the play
            inning_number = play.about.inning
            
            # Extract batter's name from the matchup attribute of the play
            batter_fullname = play.matchup.batter.fullname

            # Extract pitcher's name from the matchup attribute of the play
            pitcher_fullname = play.matchup.pitcher.fullname

            # Get player IDs for batter and pitcher
            try:
                batter_id = mlb.get_people_id(batter_fullname)[0]
            except IndexError:
                print(f"Batter {batter_fullname} not found. Skipped iteration")
                continue

            try:    
                pitcher_id = mlb.get_people_id(pitcher_fullname)[0]
            except IndexError:
                print(f"Pitcher {pitcher_fullname} not found. Skipped iteration")
                continue

            try:
                batter_stats = mlb.get_player_stats(batter_id, stats=['season'], groups=['hitting'], season=2023)
                season_stats = batter_stats['hitting']['season']
                for split in season_stats.splits:
                    batter_avg = '0' + split.stat.avg
            except KeyError:
                print(f"Batter {batter_fullname} not found. Skipped iteration")
                continue
            
            # Retrieve pitcher statistics to get strikeout to walk ratio
            try:
                pitcher_stats = mlb.get_player_stats(pitcher_id, stats=['season'], groups=['pitching'], season=2023)
                pitcher_k_bb_ratio = pitcher_stats['pitching']['season']
                for split in pitcher_k_bb_ratio.splits:
                    strike_percentage = '0' + split.stat.strikepercentage
            except KeyError:
                print(f"Pitcher {pitcher_fullname} not found. Skipped iteration")
                continue
            
            # Extract at-bat count from the count attribute of the play
            at_bat_count = f"{play.count.balls}-{play.count.strikes}"
            
            # Extract at-bat outcome from the result attribute of the play
            at_bat_outcome = play.result.event.lower()
            
            # Extract score at the time of play
            away_score = play.result.awayscore
            home_score = play.result.homescore
            
            # Categorize at-bat outcome
            if at_bat_outcome == 'strikeout':
                at_bat_outcome = 'strikeout'
            elif at_bat_outcome == 'walk':
                at_bat_outcome = 'walk'
            else:
                at_bat_outcome = 'hit'
            
            # Write the row to the CSV file
            csv_writer.writerow([inning_number, batter_avg, strike_percentage, at_bat_outcome])

        game_id += 2

print(f"Data has been saved to '{csv_filename}'")

