import pyxel
import mlbstatsapi
import pickle
import os

global mlb

mlb = mlbstatsapi.Mlb()

class GameState:
    MENU = 0
    TEAM_SELECTION = 1
    CREATE_ACCOUNT = 2
    PLAYER_TEAM_SCREEN = 3
    ROSTER_SCREEN = 4
    FRONT_OFFICE = 5
    LOAD_GAME = 6
    PLAY_GAME_SCREEN = 7
    GAME = 8
        
class Menu:
    def __init__(self):
        self.state = GameState.MENU
        pyxel.init(160, 130, title="Fantasy Baseball")
        self.options = ["New Game", "Load Game", "Quit"]
        self.selected = 0

    def update(self):
        if pyxel.btnp(pyxel.KEY_DOWN):
            self.selected = (self.selected + 1) % len(self.options)
        if pyxel.btnp(pyxel.KEY_UP):
            self.selected = (self.selected - 1) % len(self.options)
        if pyxel.btnp(pyxel.KEY_RETURN):
            selected_option = self.options[self.selected]
            if selected_option == "Quit":
                pyxel.quit()
            elif selected_option == "New Game":
                self.state = GameState.TEAM_SELECTION
            elif selected_option == "Load Game":
                self.state = GameState.LOAD_GAME

    def draw(self):
        pyxel.cls(12)
        pyxel.text(50, 40, "Fantasy Baseball", 1)
        for i, option in enumerate(self.options):
            y = 60 + i * 10
            if i == self.selected:
                pyxel.text(50, y, "> " + option, 0)
            else:
                pyxel.text(50, y, option, 7)

class TeamSelectionScreen:
    def __init__(self, mlb_teamsNL, mlb_teamsAL):
        self.mlb_teamsNL = mlb_teamsNL
        self.mlb_teamsAL = mlb_teamsAL
        self.teams = {
            "American League": self.mlb_teamsNL,
            "National League": self.mlb_teamsAL
        }
        self.selected_section = "American League"
        self.selected_team = 0

    def update(self):
        if pyxel.btnp(pyxel.KEY_DOWN):
            if self.selected_section == "American League":
                self.selected_team = (self.selected_team + 1) % len(self.teams["American League"])
            elif self.selected_section == "National League":
                self.selected_team = (self.selected_team + 1) % len(self.teams["National League"])
        elif pyxel.btnp(pyxel.KEY_UP):
            if self.selected_section == "American League":
                self.selected_team = (self.selected_team - 1) % len(self.teams["American League"])
            elif self.selected_section == "National League":
                self.selected_team = (self.selected_team - 1) % len(self.teams["National League"])
        elif pyxel.btnp(pyxel.KEY_LEFT):
            self.selected_section = "American League"
        elif pyxel.btnp(pyxel.KEY_RIGHT):
            self.selected_section = "National League"
        elif pyxel.btnp(pyxel.KEY_RETURN):
            selected_team = self.teams[self.selected_section][self.selected_team]
            teamID = mlb.get_team_id(selected_team)[0]
            print(f"Selected team: {selected_team}")
            return selected_team, teamID
        return None, None

    def draw(self):
        pyxel.cls(12)
        pyxel.text(60, 10, "NEW GAME", 1)
        pyxel.text(10, 20, "National League", 1 if self.selected_section == "National League" else 7)
        pyxel.text(85, 20, "American League", 1 if self.selected_section == "American League" else 7)

        section_teams = self.teams[self.selected_section]
        for i, team in enumerate(section_teams):
            y = 30 + i/2 * 12
            if i == self.selected_team:
                pyxel.text(10 if self.selected_section == "American League" else 10, y, "> " + team, 0)
            else:
                pyxel.text(10 if self.selected_section == "American League" else 10, y, team, 7)

class loadGame:
    def __init__(self):
        self.saved_games = self.get_saved_games()
        self.selected_index = 0
        self.loaded_data = None

    def get_saved_games(self):
        return [f for f in os.listdir() if f.endswith('_account.pkl')]
    
    def update(self):
        if pyxel.btnp(pyxel.KEY_UP):
            self.selected_index = (self.selected_index - 1) % len(self.saved_games)
        elif pyxel.btnp(pyxel.KEY_DOWN):
            self.selected_index = (self.selected_index + 1) % len(self.saved_games)
        elif pyxel.btnp(pyxel.KEY_RETURN):
            self.load_selected_game()

    def load_selected_game(self):
        selected_file = self.saved_games[self.selected_index]
        with open(selected_file, 'rb') as f:
            self.loaded_data = pickle.load(f)
        print(f"Loaded data from {selected_file}")
        self.teamID = self.loaded_data['teamID']
        self.selected_team = self.loaded_data['selected_team']
        self.coachFirstName = self.loaded_data['coachFirstName']
        self.coachLastName = self.loaded_data['coachLastName']
        self.CoachingCredits = self.loaded_data['CoachingCredits']
        self.state = GameState.FRONT_OFFICE
        return self.teamID, self.selected_team

    def draw(self):
        pyxel.cls(12)
        pyxel.text(10, 10, "Load Game Save", 1)
        for i, filename in enumerate(self.saved_games):
            y = 60 + i * 10
            if i == self.selected_index:
                pyxel.text(10, y, "> " + filename, 0)
            else:
                pyxel.text(10, y, filename, 7)

class CreateAccountScreen:
    def __init__(self, teamID, selected_team):
        self.teamID = teamID
        self.selected_team = selected_team
        self.coachFirstName = ""
        self.coachLastName = ""
        self.CoachingCredits = 10
        self.current_input = "first_name"  # Track which input field is active
        self.createdAccount = False  # Track if the account has been created

    def get_coachFirstName(self):
        return self.coachFirstName

    def get_coachLastName(self):
        return self.coachLastName
    
    def get_CoachingCredits(self):
        return self.CoachingCredits

    def update(self):
        # Switch between input fields using the Tab key
        if pyxel.btnp(pyxel.KEY_TAB):
            if self.current_input == "first_name":
                self.current_input = "last_name"
            else:
                self.current_input = "first_name"

        # Handle text input
        if self.current_input == "first_name":
            self.coachFirstName = self.handle_text_input(self.coachFirstName)
        else:
            self.coachLastName = self.handle_text_input(self.coachLastName)

        # Check if Enter key is pressed to create account
        if pyxel.btnp(pyxel.KEY_RETURN):
            self.create_account()

    def handle_text_input(self, text):
        # Handle character input
        for char in "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz":
            if pyxel.btnp(getattr(pyxel, f"KEY_{char.upper()}")):
                return text + char

        # Handle special keys
        if pyxel.btnp(pyxel.KEY_BACKSPACE):
            return text[:-1]
        if pyxel.btnp(pyxel.KEY_SPACE):
            return text + " "

        return text

    def draw(self):
        pyxel.cls(12)
        pyxel.text(10, 10, "Create Account", 1)
        pyxel.text(10, 30, f"First Name: {self.coachFirstName}", 7)
        pyxel.text(10, 50, f"Last Name: {self.coachLastName}", 7)

        # Draw a cursor at the end of the active input field
        if self.current_input == "first_name":
            pyxel.text(10 + len(self.coachFirstName) * 4, 30, "            _", 0)
        else:
            pyxel.text(10 + len(self.coachLastName) * 4, 50, "           _", 0)

        # Indicate if the account has been created
        if self.createdAccount:
            pyxel.text(10, 70, "Account Created!", pyxel.COLOR_GREEN)

    def create_account(self):
        # Logic to create an account
        if self.coachFirstName and self.coachLastName:
            self.createdAccount = True
            self.save_account()

    def save_account(self):
        account_data = {
            'teamID': self.teamID,
            'selected_team': self.selected_team,
            'coachFirstName': self.coachFirstName,
            'coachLastName': self.coachLastName,
            'CoachingCredits': self.CoachingCredits
        }

        filename = f"{self.coachFirstName}_{self.coachLastName}_account.pkl"
        with open(filename, 'wb') as f:
            pickle.dump(account_data, f)
        print(f"Account saved to {filename}")

    def run(self):
        pyxel.run(self.update, self.draw)

class PlayerTeamScreen:
    def __init__(self, selected_team, teamID, schedule):
        self.selected_team = selected_team
        self.teamID = teamID
        self.optionsPlayer = ["Play Game","Front Office", "Roster", "Hall of Fame", "Advance Week", "Options"]
        self.selectedPlayer = 0
        self.schedule = schedule
        self.current_round = 0

    def update(self):
        if pyxel.btnp(pyxel.KEY_DOWN):
            self.selectedPlayer = (self.selectedPlayer + 1) % len(self.optionsPlayer)
        if pyxel.btnp(pyxel.KEY_UP):
            self.selectedPlayer = (self.selectedPlayer - 1) % len(self.optionsPlayer)
        if pyxel.btnp(pyxel.KEY_RETURN):
            selected_option = self.optionsPlayer[self.selectedPlayer]
            if selected_option == "Advance Week":
                self.current_round += 1
                if self.current_round >= len(self.schedule):
                    self.current_round = len(self.schedule)
                self.state = GameState.PLAYER_TEAM_SCREEN

    def draw_schedule(self):
        pyxel.text(50, 90, "Season Schedule", 1)
        start_x = 5
        start_y = 100
        cell_width = 100
        cell_height = 70

        def draw_game(round_num, game, y):
            pyxel.text(start_x, y, f"Round {round_num + 1}", 1)
            home, away = game
            if home == 'BYE':
                hometeamName = home
            else:
                hometeamName = home.split()
                hometeamName = hometeamName[len(hometeamName) - 1]
            if away == 'BYE':
                awayteamName = away
            else:
                awayteamName = away.split()
                awayteamName = awayteamName[len(awayteamName) - 1]
            pyxel.text(start_x + 10, y + 10, f"{hometeamName} vs {awayteamName}", 7)

        y = start_y
        previous_game_found = False

        # Display the previous game
        for round_num in range(self.current_round - 1, -1, -1):
            for home, away in self.schedule[round_num]:
                if home == self.selected_team or away == self.selected_team:
                    draw_game(round_num, (home, away), y)
                    y += cell_height
                    previous_game_found = True
                    break
            if previous_game_found:
                break

        # Display the next game
        for round_num in range(self.current_round, len(self.schedule)):
            for home, away in self.schedule[round_num]:
                if home == self.selected_team or away == self.selected_team:
                    draw_game(round_num, (home, away), y)
                    return  # Exit after drawing the next game

    def draw(self):
        pyxel.cls(12)
        pyxel.text(15, 10, f"Your Team: {self.selected_team}", 1)
        self.draw_schedule()
        for i, option in enumerate(self.optionsPlayer):
            y = 30 + i * 10
            if i == self.selectedPlayer:
                pyxel.text(30, y, "> " + option, 0)
            else:
                pyxel.text(30, y, option, 7)

class FrontOffice:
    def __init__(self):
        self.stadium = 1
        self.training_facilities = 1
        self.rehab_facilities = 1
        self.increase_salary_cap = False
        self.free_agents = False
        self.staff_Hires = False
        self.coaches = []
        self.Verticaloptions = ['Upgrade Stadium', 'Upgrade Training Facilities', 'Upgrade Rehab Facilities']
        self.Horizontaloptions = ['Increase \n Salary Cap', 'Free \n Agents', 'Staff \n Hires']
        self.selectedVerticalOption = 0
        self.selectedHorizontalOption = 0
        self.axis = "vertical"  # Track the current axis (vertical or horizontal)

    def update(self):
        if pyxel.btnp(pyxel.KEY_TAB):
            self.axis = "horizontal" if self.axis == "vertical" else "vertical"

        if self.axis == "vertical":
            if pyxel.btnp(pyxel.KEY_DOWN):
                self.selectedVerticalOption = (self.selectedVerticalOption + 1) % len(self.Verticaloptions)
            elif pyxel.btnp(pyxel.KEY_UP):
                self.selectedVerticalOption = (self.selectedVerticalOption - 1) % len(self.Verticaloptions)
        elif self.axis == "horizontal":
            if pyxel.btnp(pyxel.KEY_RIGHT):
                self.selectedHorizontalOption = (self.selectedHorizontalOption + 1) % len(self.Horizontaloptions)
            elif pyxel.btnp(pyxel.KEY_LEFT):
                self.selectedHorizontalOption = (self.selectedHorizontalOption - 1) % len(self.Horizontaloptions)

        if pyxel.btnp(pyxel.KEY_RETURN):
            if self.axis == "vertical":
                selected_option = self.Verticaloptions[self.selectedVerticalOption]
                print(f"Selected vertical option: {selected_option}")
            elif self.axis == "horizontal":
                selected_option = self.Horizontaloptions[self.selectedHorizontalOption]
                print(f"Selected horizontal option: {selected_option}")

    def draw(self):
        pyxel.cls(12)
        pyxel.text(60, 10, "Front Office", 1)

        # Draw vertical options
        for i, option in enumerate(self.Verticaloptions):
            y = 25 + i * 10
            if self.axis == "vertical" and i == self.selectedVerticalOption:
                pyxel.text(15, y, "> " + option, 0)
            else:
                pyxel.text(15, y, option, 7)

        # Draw horizontal options
        for j, option in enumerate(self.Horizontaloptions):
            x = 15 + j * 50
            if self.axis == "horizontal" and j == self.selectedHorizontalOption:
                pyxel.text(x, 100, "> " + option, 0)
            else:
                pyxel.text(x, 100, option, 7)

class RosterScreen:
    def __init__(self, selected_team, teamID):
        self.selected_team = selected_team
        self.teamID = teamID
        self.players = []
        self.BA = []
        self.Fld = []
        self.star_ratings = []
        self.salaries = []
        self.roster = self.get_or_load_roster()
        self.salary_cap = 150000000
        self.current_player_index = 0

    def normalize_stat(self, stat, min_stat, max_stat, invert=False):
        if stat is None:
            return None
        normalized = (stat - min_stat) / (max_stat - min_stat)
        if invert:
            normalized = 1 - normalized
        return max(0, min(1, normalized))

    def stat_to_stars(self, normalized_score):
        if normalized_score is None:
            return None
        return round(normalized_score * 10) / 2

    def calculate_star_rating(self, ba=None, fa=None, era=None):
        # Determine if the player is primarily a batter or a pitcher
        if ba is not None and era is None:
            # Batter star rating
            ba_min, ba_max = 0.200, 0.300
            fa_min, fa_max = 0.950, 0.990

            normalized_ba = self.normalize_stat(ba, ba_min, ba_max)
            normalized_fa = self.normalize_stat(fa, fa_min, fa_max)

            print(f"Normalized BA: {normalized_ba}, FA: {normalized_fa}")

            ba_stars = self.stat_to_stars(normalized_ba)
            fa_stars = self.stat_to_stars(normalized_fa)

            print(f"Star Ratings - BA: {ba_stars}, FA: {fa_stars}")

            return ba_stars, fa_stars, None

        elif ba is None and era is not None:
            # Pitcher star rating
            fa_min, fa_max = 0.950, 0.990
            era_min, era_max = 2.00, 5.00

            normalized_fa = self.normalize_stat(fa, fa_min, fa_max)
            normalized_era = self.normalize_stat(era, era_min, era_max, invert=True)

            print(f"Normalized FA: {normalized_fa}, ERA: {normalized_era}")

            fa_stars = self.stat_to_stars(normalized_fa)
            era_stars = self.stat_to_stars(normalized_era)

            print(f"Star Ratings - FA: {fa_stars}, ERA: {era_stars}")

            return None, fa_stars, era_stars

        elif ba is not None and era is not None:
            # Player with all three stats
            ba_min, ba_max = 0.200, 0.300
            fa_min, fa_max = 0.950, 0.990
            era_min, era_max = 2.00, 5.00

            normalized_ba = self.normalize_stat(ba, ba_min, ba_max)
            normalized_fa = self.normalize_stat(fa, fa_min, fa_max)
            normalized_era = self.normalize_stat(era, era_min, era_max, invert=True)

            print(f"Normalized BA: {normalized_ba}, FA: {normalized_fa}, ERA: {normalized_era}")

            ba_stars = self.stat_to_stars(normalized_ba)
            fa_stars = self.stat_to_stars(normalized_fa)
            era_stars = self.stat_to_stars(normalized_era)

            print(f"Star Ratings - BA: {ba_stars}, FA: {fa_stars}, ERA: {era_stars}")

            return ba_stars, fa_stars, era_stars

        return None, None, None

    def calculate_salary(self, ba_stars, fa_stars, era_stars):
        base_salary = 500000  # Base salary in dollars
        star_bonus = 2000000  # Bonus per star in dollars

        total_stars = (ba_stars or 0) + (era_stars or 0)
        salary = base_salary + (total_stars * star_bonus)
        return salary

    def draw_salary_bar(self):
        self.total_salary = sum(self.salaries)
        filled_width = min(120, int((self.total_salary / self.salary_cap) * 120))
        pyxel.rectb(20, 110, 120, 10, 1)
        pyxel.rect(21, 111, filled_width, 8, 3)

    def update(self):
        if pyxel.btnp(pyxel.KEY_LEFT) and len(self.players) > 1:
            self.current_player_index = (self.current_player_index - 1) % len(self.players)
        elif pyxel.btnp(pyxel.KEY_RIGHT) and len(self.players) > 1:
            self.current_player_index = (self.current_player_index + 1) % len(self.players)

    def draw(self):
        pyxel.cls(12)
        pyxel.text(65, 10, "ROSTER", 1)
        self.draw_salary_bar()
        if self.players:
            player = self.players[self.current_player_index]
            batting_average = self.BA[self.current_player_index]
            fielding_average = self.Fld[self.current_player_index]
            ba_stars, fa_stars, era_stars = self.star_ratings[self.current_player_index]
            salary = self.salaries[self.current_player_index]

            pyxel.rect(20, 30, 120, 80, 1)  # Player card background
            pyxel.text(30, 100, f"SALARY CAP ${self.total_salary/ 1000000:.1f}M / 150M", 7)
            pyxel.text(30, 35, f"Player Name: {player['fullname']}", 7)
            pyxel.text(30, 45, f"Position: {player['position']}", 7)
            pyxel.text(30, 55, f"Batting: {batting_average} ({ba_stars} stars)" if ba_stars is not None else f"Batting: {batting_average}", 7)
            pyxel.text(30, 65, f"Pitching: {player['era']} ({era_stars} stars)" if era_stars is not None else f"Pitching: {player['era']}", 7)
            pyxel.text(30, 75, f"Fielding: {fielding_average} ({fa_stars} stars)" if fa_stars is not None else f"Fielding: {fielding_average}", 7)
            pyxel.text(30, 85, f"Salary: ${salary:,}", 7)
        else:
            pyxel.text(30, 30, "No players in roster", 7)
    
    def get_or_load_roster(self):
        teamID = self.teamID
        filename = f"team_{teamID}_roster.pkl"
        if os.path.exists(filename):
            with open(filename,"rb") as f:
                data = pickle.load(f)
            print("Loaded roster from file")
            self.players = data['players']
            self.BA = data['BA']
            self.Fld = data['Fld']
            self.star_ratings = data['star_ratings']
            self.salaries = data['salaries']
            return self.players, self.BA, self.Fld, self.star_ratings, self.salaries
        else:
            roster = mlb.get_team_roster(teamID, roster_type=['fullRoster'], season=['2024'])

            for player_info in roster:
                player_id = mlb.get_people_id(player_info.fullname)[0]
                position = player_info.primaryposition.abbreviation

                batter_avg = None
                try: 
                    batter_stats = mlb.get_player_stats(player_id, stats=['season'], groups=['hitting'], season=2023)
                    season_stats = batter_stats['hitting']['season']
                    for split in season_stats.splits:
                        batter_avg = float('0' + split.stat.avg)
                        break
                except KeyError:
                    pass
                
                era = None
                try:
                    pitcher_stats = mlb.get_player_stats(player_id, stats=['season'], groups=['pitching'], season=2023)
                    season_stats = pitcher_stats['pitching']['season']
                    for split in season_stats.splits:
                        era = float(split.stat.era)
                        break
                except KeyError:
                    pass

                fielding_avg = None
                try:
                    fielding_stats = mlb.get_player_stats(player_id, stats=['season'], groups=['fielding'], season=2023)
                    season_stats = fielding_stats['fielding']['season']
                    for split in season_stats.splits:
                        fielding_avg = float('0' + split.stat.fielding) if split.stat.fielding != '1.000' else 1.0
                        break
                except KeyError:
                    pass
                
                print(f"Player: {player_info.fullname}, BA: {batter_avg}, ERA: {era}, FA: {fielding_avg}")

                self.players.append({'fullname': player_info.fullname, 'era': era, 'position': position})
                self.BA.append(batter_avg)
                self.Fld.append(fielding_avg)

                ba_stars, fa_stars, era_stars = self.calculate_star_rating(batter_avg, fielding_avg, era)
                self.star_ratings.append((ba_stars, fa_stars, era_stars))

                salary = self.calculate_salary(ba_stars, fa_stars, era_stars)
                self.salaries.append(salary)

            with open(filename, "wb") as f:
                data = {
                    'players': self.players,
                    'BA': self.BA,
                    'Fld': self.Fld,
                    'star_ratings': self.star_ratings,
                    'salaries': self.salaries
                }
                pickle.dump(data, f)
            print("Saved roster to file")
            return self.players, self.BA, self.Fld, self.star_ratings, self.salaries
        
class Schedule:
    def __init__(self, mlb_teamsNL, mlb_teamsAL, selected_team):
        self.mlb_teamsNL = mlb_teamsNL
        self.mlb_teamsAL = mlb_teamsAL
        print(selected_team)
        if selected_team in self.mlb_teamsNL:
            self.teams = self.mlb_teamsNL
        elif selected_team in self.mlb_teamsAL:
            self.teams = self.mlb_teamsAL
        if len(self.teams) % 2:
            self.teams.append('BYE')  # If the number of teams is odd, add a dummy team "BYE"
        self.num_rounds = len(self.teams) - 1
        self.num_matches_per_round = len(self.teams) // 2
        self.schedule = []

    def generate_round_robin_schedule(self):
        teams = self.teams[:]
        for round in range(self.num_rounds):
            round_matches = []
            for match in range(self.num_matches_per_round):
                home = teams[match]
                away = teams[-(match + 1)]
                round_matches.append((home, away))
            teams.insert(1, teams.pop())  # Rotate teams to generate new pairs
            self.schedule.append(round_matches)

    def generate_home_away_schedule(self):
        if not self.schedule:
            self.generate_round_robin_schedule()
        home_away_schedule = []
        for round_matches in self.schedule:
            home_away_schedule.append(round_matches)
            home_away_schedule.append([(away, home) for home, away in round_matches])
        return home_away_schedule

    def get_Schedule(self):
        self.schedule = self.generate_home_away_schedule()
        return self.schedule
    
class PlayGameScreen:
    def __init__(self, selected_team, team_id):
        self.selected_team = selected_team
        self.team_id = team_id
        self.players = self.load_player_data()
        self.remaining_players = []
        self.current_player_index = 0
        self.mode = 'cycle'  # Modes: 'cycle' or 'play'
        pyxel.images[0].load(0, 0, "istockphoto-667849798-612x612 (3).jpg")
        
        # Define the coordinates for each position
        self.position_coords = {
            'P': (35, 87),
            'C': (55, 100),
            '1B': (100, 80),
            '2B': (80, 50),
            '3B': (20, 80),
            'SS': (50, 65),
            'LF': (10, 35),
            'CF': (55, 20),
            'RF': (85, 35),
            'DH': (95, 106)
        }

    def load_player_data(self):
        filename = f'team_{self.team_id:03d}_roster.pkl'
        with open(filename, 'rb') as f:
            data = pickle.load(f)
        return data['players']

    def update(self):   
        if self.mode == 'cycle':
            if pyxel.btnp(pyxel.KEY_LEFT) and len(self.remaining_players) > 1:
                self.current_player_index = (self.current_player_index - 1) % len(self.remaining_players)
            elif pyxel.btnp(pyxel.KEY_RIGHT) and len(self.remaining_players) > 1:
                self.current_player_index = (self.current_player_index + 1) % len(self.remaining_players)
            elif pyxel.btnp(pyxel.KEY_DOWN):
                self.mode = 'play'
        elif self.mode == 'play':
            if pyxel.btnp(pyxel.KEY_UP):
                self.mode = 'cycle'

    def draw(self):
        pyxel.cls(5)
        pyxel.blt(0, 0, 0, 0, 0, 160, 120)
        pyxel.text(60, 7,"PLAY GAME", 1)
        
        filled_positions = set()  # Reset filled positions

        # Iterate through the players and display their names and positions
        for player in self.players:
            position = player['position']
            if position in self.position_coords and position not in filled_positions:
                x, y = self.position_coords[position]
                text = f"{player['fullname']} \n{position}"
                pyxel.text(x, y, text, 0)
                filled_positions.add(position)
            else:
                self.remaining_players.append(player)

        # Display remaining players in cycle mode
        if self.mode == 'cycle' and self.remaining_players:
            pyxel.text(5, 110, "> Reserves", 7)
            player = self.remaining_players[self.current_player_index]
            position = player['position']
            text = f"< {player['fullname']} - {position} >"
            pyxel.text(5, 120, text, 7)

        # Display "Press Enter to Play" in play mode
        if self.mode == 'play':
            pyxel.text(5, 110, "> Play", 7)
            pyxel.text(10, 120, "Press Enter to Play", 7)

class SlidingBar:
    def __init__(self, x, y, width, height, direction='horizontal', min_value=0, max_value=100, gradient_colors=None):
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.direction = direction
        self.min_value = min_value
        self.max_value = max_value
        self.value = min_value
        self.moving_forward = True 
        self.horistopped = False
        self.vertstopped = False
        
        # Use provided gradient colors or default gradient colors
        if gradient_colors is None:
            self.gradient_colors = [7, 15, 10, 9, 8, 9, 10, 15, 7]
        else:
            self.gradient_colors = gradient_colors

    def update(self):
        if not self.horistopped:
            if self.direction == 'horizontal':
                if self.moving_forward:
                    self.value += 2
                    if self.value >= self.max_value:
                        self.moving_forward = False
                else:
                    self.value -= 2
                    if self.value <= self.min_value:
                        self.moving_forward = True
        if not self.vertstopped:
            if self.direction == 'vertical':
                if self.moving_forward:
                    self.value += 2
                    if self.value >= self.max_value:
                        self.moving_forward = False
                else:
                    self.value -= 2
                    if self.value <= self.min_value:
                        self.moving_forward = True

        # Stop the bar movement when the "A" button (assumed to be pyxel.KEY_A) is pressed
        if pyxel.btnp(pyxel.KEY_P):
            self.horistopped = True
        
        if pyxel.btnp(pyxel.KEY_A):
            self.vertstopped = True
        
    def draw_gradient_rect(self, x, y, width, height, colors, direction='horizontal'):
        num_colors = len(colors)
        for i in range(width if direction == 'horizontal' else height):
            color_index = i * (num_colors) // (width if direction == 'horizontal' else height)
            color = colors[color_index]
            if direction == 'horizontal':
                pyxel.line(x + i, y, x + i, y + height, color)
            else:
                pyxel.line(x, y + i, x + width, y + i, color)

    def draw(self):
        if self.direction == 'horizontal':
            self.draw_gradient_rect(self.x, self.y, self.width, self.height, self.gradient_colors, 'horizontal')
            slider_position = self.x + (self.value - self.min_value) * self.width // (self.max_value - self.min_value)
            pyxel.rect(slider_position - 2, self.y, 4, self.height, 1)
        elif self.direction == 'vertical':
            self.draw_gradient_rect(self.x, self.y, self.width, self.height, self.gradient_colors, 'vertical')
            slider_position = self.y + (self.value - self.min_value) * self.height // (self.max_value - self.min_value)
            pyxel.rect(self.x, slider_position - 2, self.width, 4, 1)

class Game:
    def __init__(self):
        self.init_game()
        pyxel.images[1].load(0, 0, "pixilart-sprite (2) (1).jpg")
        self.power_bar = SlidingBar(105, 5, 50, 10, direction='horizontal')
        self.angle_bar = SlidingBar(145, 20, 10, 50, direction='vertical')

    def init_game(self):
        self.inning = 1
        self.half_inning = 'top'
        self.outs = 0

    def update(self):
        self.power_bar.update()
        self.angle_bar.update()

    def draw(self):
        pyxel.cls(5)
        pyxel.blt(0, 0, 1, 0, 0, 160, 120)
        self.power_bar.draw()
        self.angle_bar.draw()

# Define MLB teams
mlb_teamsNL = [
    "Philadelphia Phillies", "New York Mets", "Atlanta Braves", "Miami Marlins", "Washington Nationals",
    "Milwaukee Brewers", "Chicago Cubs", "Cincinnati Reds", "Pittsburgh Pirates", "St. Louis Cardinals",
    "Los Angeles Dodgers", "Arizona Diamondbacks", "San Diego Padres", "San Francisco Giants", "Colorado Rockies"
]

mlb_teamsAL = [
    "Baltimore Orioles", "Tampa Bay Rays", "Toronto Blue Jays", "New York Yankees", "Boston Red Sox",
    "Minnesota Twins", "Detroit Tigers", "Cleveland Guardians", "Chicago White Sox", "Kansas City Royals",
    "Houston Astros", "Texas Rangers", "Seattle Mariners", "Los Angeles Angels", "Oakland Athletics"
]

# Game state manager class
class GameStateManager:
    def __init__(self):
        self.menu = Menu()
        self.team_selection_screen = TeamSelectionScreen(mlb_teamsNL, mlb_teamsAL)
        self.load_game = loadGame()
        self.roster_screen = None
        self.front_office = None
        self.play_game_screen = None
        self.game = None
        self.selected_team = None
        self.teamID = None
        self.create_account_screen = None
        self.schedule = None
        self.player_team_screen = None
        self.game = Game()

    def update(self):
        if self.menu.state == GameState.MENU:
            self.menu.update()
        elif self.menu.state == GameState.TEAM_SELECTION:
            self.update_team_selection()
        elif self.menu.state == GameState.LOAD_GAME:
            self.update_load_game()
        elif self.menu.state == GameState.CREATE_ACCOUNT:
            self.update_create_account()
        elif self.menu.state == GameState.PLAYER_TEAM_SCREEN:
            self.update_player_team_screen()
        elif self.menu.state == GameState.ROSTER_SCREEN:
            self.update_roster_screen()
        elif self.menu.state == GameState.FRONT_OFFICE:
            self.update_front_office()
        elif self.menu.state == GameState.PLAY_GAME_SCREEN:
            self.update_play_game_screen()
        elif self.menu.state == GameState.GAME:
            self.game.update()

    def draw(self):
        if self.menu.state == GameState.MENU:
            self.menu.draw()
        elif self.menu.state == GameState.TEAM_SELECTION:
            self.team_selection_screen.draw()
        elif self.menu.state == GameState.CREATE_ACCOUNT:
            self.create_account_screen.draw()
        elif self.menu.state == GameState.LOAD_GAME:
            self.load_game.draw()
        elif self.menu.state == GameState.PLAYER_TEAM_SCREEN:
            self.player_team_screen.draw()
        elif self.menu.state == GameState.ROSTER_SCREEN and self.roster_screen:
            self.roster_screen.draw()
        elif self.menu.state == GameState.FRONT_OFFICE and self.front_office:
            self.front_office.draw()
        elif self.menu.state == GameState.PLAY_GAME_SCREEN and self.play_game_screen:
            self.play_game_screen.draw()
        elif self.menu.state == GameState.GAME:
            self.game.draw()

    def update_team_selection(self):
        self.selected_team, self.teamID = self.team_selection_screen.update()
        if self.selected_team:
            self.create_account_screen = CreateAccountScreen(self.selected_team, self.teamID)
            self.menu.state = GameState.CREATE_ACCOUNT

    def update_load_game(self):
        self.load_game.update()
        if pyxel.btnp(pyxel.KEY_RETURN):
            self.selected_team, self.teamID = self.load_game.load_selected_game()
            schedule_ = Schedule(mlb_teamsNL, mlb_teamsAL, self.selected_team)
            self.schedule = schedule_.get_Schedule()
            self.player_team_screen = PlayerTeamScreen(self.selected_team, self.teamID, self.schedule)
            self.menu.state = GameState.PLAYER_TEAM_SCREEN

    def update_create_account(self):
        self.create_account_screen.update()
        if self.create_account_screen.createdAccount:
            schedule_ = Schedule(mlb_teamsNL, mlb_teamsAL, self.selected_team)
            self.schedule = schedule_.get_Schedule()
            self.player_team_screen = PlayerTeamScreen(self.selected_team, self.teamID, self.schedule)
            self.menu.state = GameState.PLAYER_TEAM_SCREEN

    def update_player_team_screen(self):
        self.player_team_screen.update()
        if pyxel.btnp(pyxel.KEY_RETURN):
            selected_option = self.player_team_screen.optionsPlayer[self.player_team_screen.selectedPlayer]
            if selected_option == "Front Office":
                self.front_office = FrontOffice()
                self.menu.state = GameState.FRONT_OFFICE
            elif selected_option == "Roster":
                self.selected_team, self.teamID = self.player_team_screen.selected_team, self.player_team_screen.teamID
                self.roster_screen = RosterScreen(self.selected_team, self.teamID)
                self.menu.state = GameState.ROSTER_SCREEN
            elif selected_option == "Play Game":
                self.selected_team, self.teamID = self.player_team_screen.selected_team, self.teamID
                self.play_game_screen = PlayGameScreen(self.selected_team, self.teamID)
                self.menu.state = GameState.PLAY_GAME_SCREEN


    def update_roster_screen(self):
        if self.roster_screen:
            self.roster_screen.update()
        if pyxel.btnp(pyxel.KEY_BACKSPACE):
            self.menu.state = GameState.PLAYER_TEAM_SCREEN

    def update_front_office(self):
        if self.front_office:
            self.front_office.update()
        if pyxel.btnp(pyxel.KEY_BACKSPACE):
            self.menu.state = GameState.PLAYER_TEAM_SCREEN

    def update_play_game_screen(self):
        if self.play_game_screen:
            self.play_game_screen.update()
        if pyxel.btnp(pyxel.KEY_BACKSPACE):
            self.menu.state = GameState.PLAYER_TEAM_SCREEN
        if pyxel.btnp(pyxel.KEY_RETURN):
            self.menu.state = GameState.GAME

game_state_manager = GameStateManager()

def update():
    game_state_manager.update()

def draw():
    game_state_manager.draw()

pyxel.run(update, draw)

