import pyxel
import mlbstatsapi
import pickle
import os
import time

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
    POST_GAME = 9
        
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

        self.stadium = self.loaded_data['stadium']
        self.training_facilitys = self.loaded_data['training_facilitys']
        self.rehab_facilitys = self.loaded_data['rehab_facilitys']

        self.state = GameState.FRONT_OFFICE
        return self.teamID, self.selected_team, self.CoachingCredits, self.stadium, self.training_facilitys, self.rehab_facilitys, self.coachFirstName, self.coachLastName

    def draw(self):
        pyxel.cls(12)
        pyxel.text(10, 10, "Load Game Save", 1)
        for i, filename in enumerate(self.saved_games):
            y = 60 + i * 10
            if i == self.selected_index:
                filename = filename[:-12]
                filename = filename.translate({ord("_"): " "})
                pyxel.text(10, y, "> " + filename, 0)
            else:
                filename = filename[:-12]
                filename = filename.translate({ord("_"): " "})
                pyxel.text(10, y, filename, 7)

class CreateAccountScreen:
    def __init__(self, teamID, selected_team):
        self.teamID = teamID
        self.selected_team = selected_team
        self.coachFirstName = ""
        self.coachLastName = ""
        self.CoachingCredits = 10

        self.stadium = 1
        self.training_facilitys = 1
        self.rehab_facilitys = 1

        self.current_input = "first_name"  # Track which input field is active
        self.createdAccount = False  # Track if the account has been created

    def get_coachFirstName(self):
        return self.coachFirstName

    def get_coachLastName(self):
        return self.coachLastName
    
    def get_CoachingCredits(self):
        return self.CoachingCredits
    

    def get_stadium(self):
        return self.stadium
    
    def get_training_facilitys(self):
        return self.training_facilitys
    
    def get_rehab_facilitys(self):
        return self.rehab_facilitys
    

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
            'CoachingCredits': self.CoachingCredits,
            'stadium': self.stadium,
            'training_facilitys': self.training_facilitys,
            'rehab_facilitys': self.rehab_facilitys
        }

        filename = f"{self.coachFirstName}_{self.coachLastName}_account.pkl"
        with open(filename, 'wb') as f:
            pickle.dump(account_data, f)
        print(f"Account saved to {filename}")

    def run(self):
        pyxel.run(self.update, self.draw)


class PlayerTeamScreen:
    def __init__(self, selected_team, teamID, schedule, coachingCredits):
        self.selected_team = selected_team
        self.teamID = teamID
        self.optionsPlayer = ["Play Game", "Front Office", "Roster", "Hall of Fame", "Advance Week", "Options"]
        self.CoachingCredits = coachingCredits
        self.selectedPlayer = 0
        self.schedule = schedule
        self.current_round = 0
        self.home = None
        self.away = None

    def update(self):
        if pyxel.btnp(pyxel.KEY_DOWN):
            self.selectedPlayer = (self.selectedPlayer + 1) % len(self.optionsPlayer)
        if pyxel.btnp(pyxel.KEY_UP):
            self.selectedPlayer = (self.selectedPlayer - 1) % len(self.optionsPlayer)

        if pyxel.btnp(pyxel.KEY_RETURN):
            selected_option = self.optionsPlayer[self.selectedPlayer]

            # Handle the "Advance Week" option
            if selected_option == "Advance Week":
                self.current_round += 1
                if self.current_round >= len(self.schedule):
                    self.current_round = len(self.schedule) - 1  # Ensure current_round stays valid

                # Check if the upcoming game involves a "BYE"
                next_round_games = self.schedule[self.current_round]
                for home, away in next_round_games:
                    if self.selected_team == home and away == 'BYE' or self.selected_team == away and home == 'BYE':
                        # If the opponent is BYE, display a message and prevent playing
                        self.current_round += 1  # Automatically skip this "BYE" week
                        if self.current_round >= len(self.schedule):
                            self.current_round = len(self.schedule) - 1  # Prevent out-of-bounds error
                        pyxel.text(10, 10, "Opponent is BYE. Advancing to next valid game.", 8)
                        return  # Skip further actions for this week

                # Proceed to the PlayGameScreen, passing the required parameters
                self.play_game_screen = PlayGameScreen(
                    mlb_teamsNL,        # Add mlb_teamsNL as the first argument
                    mlb_teamsAL,        # Add mlb_teamsAL as the second argument
                    self.selected_team,  # Third argument
                    self.teamID,        # Fourth argument (team_id)
                    week=self.current_round  # Fifth argument (week)
                )
                self.state = GameState.PLAY_GAME_SCREEN

    def draw_schedule(self):
        pyxel.text(50, 90, "Season Schedule", 1)
        start_x = 5
        start_y = 100
        cell_width = 100
        cell_height = 70

        def draw_game(round_num, game, y):
            pyxel.text(start_x, y, f"Round {round_num + 1}", 1)
            self.home, self.away = game

            # Check if either home or away team is 'BYE'
            if self.home == 'BYE':
                hometeamName = self.home
            else:
                hometeamName = self.home.split()[-1]  # Get the last part of the home team name

            if self.away == 'BYE':
                awayteamName = self.away
            else:
                awayteamName = self.away.split()[-1]  # Get the last part of the away team name

            # Prevent playing against a "BYE"
            if self.selected_team == self.home and self.away == 'BYE':
                pyxel.text(start_x + 10, y + 10, f"{hometeamName} vs BYE - No game this week", 8)
            elif self.selected_team == self.away and self.home == 'BYE':
                pyxel.text(start_x + 10, y + 10, f"{awayteamName} vs BYE - No game this week", 8)
            else:
                # Display the match if it's a valid game (not against BYE)
                pyxel.text(start_x + 10, y + 10, f"{hometeamName} vs {awayteamName}", 7)

        y = start_y
        previous_game_found = False

        # Display the previous game
        for round_num in range(self.current_round - 1, -1, -1):
            for self.home, self.away in self.schedule[round_num]:
                if self.home == self.selected_team or self.away == self.selected_team:
                    draw_game(round_num, (self.home, self.away), y)
                    y += cell_height
                    previous_game_found = True
                    break
            if previous_game_found:
                break

        # Display the next game
        for round_num in range(self.current_round, len(self.schedule)):
            for self.home, self.away in self.schedule[round_num]:
                if self.home == self.selected_team or self.away == self.selected_team:
                    draw_game(round_num, (self.home, self.away), y)
                    return self.away, self.home  # Return the current game

        # If no valid game is found, return None for both teams
        return None, None

    def draw(self):
        pyxel.cls(12)
        pyxel.text(15, 10, f"Your Team: {self.selected_team}", 1)
        pyxel.text(15, 20, f"Coaching Credits: {self.CoachingCredits}", 1)
        self.draw_schedule()
        for i, option in enumerate(self.optionsPlayer):
            y = 30 + i * 10
            if i == self.selectedPlayer:
                pyxel.text(30, y, "> " + option, 0)
            else:
                pyxel.text(30, y, option, 7)

class FrontOffice:
    def __init__(self, coachingCredits, stadium, training_facilities, rehab_facilities, coachFirstName, coachLastName):
        self.coachFirstName = coachFirstName
        self.coachLastName = coachLastName
        self.CoachingCredits = coachingCredits
        self.stadium = stadium
        self.training_facilitys = training_facilities
        self.rehab_facilitys = rehab_facilities
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
                # Spend coaching credit to upgrade
                if self.CoachingCredits > 0:
                    selected_option = self.Verticaloptions[self.selectedVerticalOption]
                    if selected_option == "Upgrade Stadium" and self.stadium < 10:
                        self.stadium += 1
                        self.CoachingCredits -= 1
                    elif selected_option == "Upgrade Training Facilities" and self.training_facilitys < 10:
                        self.training_facilitys += 1
                        self.CoachingCredits -= 1
                    elif selected_option == "Upgrade Rehab Facilities" and self.rehab_facilitys < 10:
                        self.rehab_facilitys += 1
                        self.CoachingCredits -= 1
                    self.save_account()
                else:
                    print("Not enough coaching credits!")

            elif self.axis == "horizontal":
                selected_option = self.Horizontaloptions[self.selectedHorizontalOption]
                print(f"Selected horizontal option: {selected_option}")

    def save_account(self):
        filename = f"{self.coachFirstName}_{self.coachLastName}_account.pkl"
        
        # Check if file exists and load existing data
        if os.path.exists(filename):
            with open(filename, 'rb') as f:
                account_data = pickle.load(f)
        else:
            # If no file exists, create a new dictionary
            account_data = {}

        # Update the relevant fields in the loaded account data
        account_data['CoachingCredits'] = self.CoachingCredits
        account_data['stadium'] = self.stadium
        account_data['training_facilitys'] = self.training_facilitys
        account_data['rehab_facilitys'] = self.rehab_facilitys

        # Write updated data back to the file
        with open(filename, 'wb') as f:
            pickle.dump(account_data, f)
        print(f"Account saved to {filename}")
        
    @staticmethod
    def draw_progress_bar(x, y, current_level, total_bars=10):
        for i in range(total_bars):
            if i < current_level:
                pyxel.rect(x + i * 12, y, 10, 5, 10)  # Filled bar (yellow)
            else:
                pyxel.rect(x + i * 12, y, 10, 5, 5)  # Unfilled bar (grey)

    def draw(self):
        pyxel.cls(12)
        pyxel.text(60, 10, "Front Office", 1)
        pyxel.text(15, 120, f"Coaching Credits: {self.CoachingCredits}", 1)

        # Draw vertical options and bars
        for i, option in enumerate(self.Verticaloptions):
            y = 25 + i * 20
            if self.axis == "vertical" and i == self.selectedVerticalOption:
                pyxel.text(15, y, "> " + option, 0)
            else:
                pyxel.text(15, y, option, 7)

            # Draw the progress bars
            if option == "Upgrade Stadium":
                FrontOffice.draw_progress_bar(15, y + 10, self.stadium)
            elif option == "Upgrade Training Facilities":
                FrontOffice.draw_progress_bar(15, y + 10, self.training_facilitys)
            elif option == "Upgrade Rehab Facilities":
                FrontOffice.draw_progress_bar(15, y + 10, self.rehab_facilitys)

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
        
class Schedule():
    def __init__(self, mlb_teamsNL, mlb_teamsAL, selected_team, current_round):
        self.mlb_teamsNL = mlb_teamsNL
        self.mlb_teamsAL = mlb_teamsAL
        self.selected_team = selected_team
        self.week = current_round
        
        # Determine if the selected team is from NL or AL
        if selected_team in self.mlb_teamsNL:
            self.teams = self.mlb_teamsNL
        elif selected_team in self.mlb_teamsAL:
            self.teams = self.mlb_teamsAL
        
        # Add a dummy "BYE" if the number of teams is odd
        if len(self.teams) % 2:
            self.teams.append('BYE')

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
    
    def get_opponent_for_week(self):
        """Gets the opponent for the selected team in the given week."""
        if self.week >= len(self.schedule):
            return None  # Invalid week

        for home, away in self.schedule[self.week]:
            if home == self.selected_team:
                return away
            if away == self.selected_team:
                return home

        return None  # Opponent not found

    def get_schedule(self):
        self.schedule = self.generate_home_away_schedule()
        return self.schedule

class PlayGameScreen(Schedule):
    def __init__(self, mlb_teamsNL, mlb_teamsAL, selected_team, team_id, week):
        # Initialize the parent class (Schedule)
        super().__init__(mlb_teamsNL, mlb_teamsAL, selected_team, week)
        pyxel.images[0].load(0, 0, "istockphoto-667849798-612x612 (3).jpg")
        
        self.team_id = team_id
        self.week = week
        self.schedule = self.get_schedule()  # Generate and retrieve the schedule

        # Get the opponent for the current week
        self.opponent_team = self.get_opponent_for_week()
        if self.opponent_team:
            self.opponent_team_id = self.get_team_id_from_name(self.opponent_team)
        else:
            self.opponent_team_id = None
        
        self.players = self.load_player_data(self.team_id)
        self.batting_order = []  # 9 players excluding the pitcher
        self.bench = []  # Remaining non-pitcher players
        self.pitcher = None  # Store pitcher separately
        self.current_player_index = 0
        self.remaining_players = []
        self.mode = 'cycle'  # Modes: 'cycle', 'play', 'Batting Order', 'Other Team'

        # Load the opponent for the given week
        self.opponent_players = self.load_player_data(self.opponent_team_id) if self.opponent_team_id else []
        self.opponent_batting_order = []  # 9 players excluding the pitcher
        self.opponent_bench = []  # Remaining non-pitcher players

        # Define position coordinates
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

        self.assign_positions()  # Assign players to field and bench


    def load_opponent_team(self):
        # Access the schedule for the current week (round)
        current_round = self.schedule[self.week]

        # Iterate through the matches in the current round to find the opponent
        for home_team, away_team in current_round:
            if self.selected_team == home_team:
                # If the user's team is the home team, the opponent is the away team
                opponent = away_team
                break
            elif self.selected_team == away_team:
                # If the user's team is the away team, the opponent is the home team
                opponent = home_team
                break
        else:
            # If no match is found (for example, if it's a BYE), opponent is None
            opponent = None

        return opponent

    def get_team_id_from_name(self, team_name):
        """Mock function to retrieve the team ID based on the team name."""
        print(team_name)
        return mlb.get_team_id(team_name)[0]

    def load_player_data(self, team_id):
        filename = f'team_{team_id:03d}_roster.pkl'
        with open(filename, 'rb') as f:
            data = pickle.load(f)
        return data['players']

    def assign_positions(self):
        filled_positions = set()

        for player in self.players:
            position = player['position']
            if position == 'P':
                self.pitcher = player  # Assign the pitcher
            elif len(self.batting_order) < 9:
                self.batting_order.append(player)
                filled_positions.add(position)
            else:
                self.bench.append(player)

        for player in self.opponent_players:
            position = player['position']
            if position == 'P':
                self.opponent_pitcher = player  # Assign the pitcher
            elif len(self.opponent_batting_order) < 9:
                self.opponent_batting_order.append(player)
                filled_positions.add(position)
            else:
                self.opponent_bench.append(player)

    def update(self):
        if self.mode == 'cycle':
            if pyxel.btnp(pyxel.KEY_LEFT) and len(self.remaining_players) > 1:
                self.current_player_index = (self.current_player_index - 1) % len(self.remaining_players)
            elif pyxel.btnp(pyxel.KEY_RIGHT) and len(self.remaining_players) > 1:
                self.current_player_index = (self.current_player_index + 1) % len(self.remaining_players)
            elif pyxel.btnp(pyxel.KEY_DOWN):
                self.mode = 'play'
            elif pyxel.btnp(pyxel.KEY_B):
                self.mode = 'Batting Order'
            elif pyxel.btnp(pyxel.KEY_D):
                self.mode = 'Other Team'
        elif self.mode == 'play':
            if pyxel.btnp(pyxel.KEY_UP):
                self.mode = 'cycle'
        elif self.mode == 'Batting Order':
            if pyxel.btnp(pyxel.KEY_B):
                self.mode = 'cycle'
        elif self.mode == 'Oppenent Batting Order':
            if pyxel.btnp(pyxel.KEY_B):
                self.mode = 'Other Team'
        elif self.mode == 'Other Team':
            if pyxel.btnp(pyxel.KEY_B):
                self.mode = 'Oppenent Batting Order'
            if pyxel.btnp(pyxel.KEY_A):
                self.mode = 'cycle'

    def draw(self):
        pyxel.cls(5)
        pyxel.blt(0, 0, 0, 0, 0, 160, 120)
        pyxel.text(60, 7, "PLAY GAME", 1)

        filled_positions = set()  # Reset filled positions
        
        if self.mode =='play':
            x, y = 40, 50
            pyxel.text(x, y, f"{self.selected_team} \n \n         vs.         \n \n{self.opponent_team}", 0)
            pyxel.text(5, 110, "> Play", 7)

        # Display the players from the selected team
        if self.mode == 'cycle':
            for player in self.players:
                position = player['position']
                if position in self.position_coords and position not in filled_positions:
                    x, y = self.position_coords[position]
                    text = f"{player['fullname']} \n{position}"
                    pyxel.text(x, y, text, 0)
                    filled_positions.add(position)
                else:
                    self.remaining_players.append(player)

        # Display the opponent team (if not a BYE week)
        if self.mode == 'Other Team':
            pyxel.text(5, 120, f"> Opponent Team: {self.opponent_team}", 7)
            for player in self.opponent_players:
                position = player['position']
                if position in self.position_coords and position not in filled_positions:
                    x, y = self.position_coords[position]
                    text = f"{player['fullname']} \n{position}"
                    pyxel.text(x, y, text, 0)
                    filled_positions.add(position)

        # Batting order mode
        if self.mode == 'Batting Order':
            y = 20
            no_in_batting = 1
            pyxel.text(10, 10, 'Batting Order', 7)
            for player in self.batting_order:
                position = player['position']
                text = f"{no_in_batting}. {player['fullname']} - {position}"
                pyxel.text(20, y, text, 0)
                y += 10
                no_in_batting += 1
        
        if self.mode == 'Oppenent Batting Order':
            pyxel.text(5, 120, f"> Opponent Team: {self.opponent_team}", 7)
            y = 20
            no_in_batting = 1
            pyxel.text(10, 10, 'Batting Order', 7)
            for player in self.opponent_batting_order:
                position = player['position']
                text = f"{no_in_batting}. {player['fullname']} - {position}"
                pyxel.text(20, y, text, 0)
                y += 10
                no_in_batting += 1

        # Display remaining players in cycle mode
        if self.remaining_players and (self.mode == 'cycle' or self.mode == 'Batting Order'):
            pyxel.text(5, 110, "> Reserves", 7)
            player = self.remaining_players[self.current_player_index]
            position = player['position']
            text = f"\n{player['fullname']} ({position})"
            pyxel.text(10, 110, text, 7)


class DeckShuffler:
    def __init__(self, deck=None):
        # Initialize the random seed based on the current time in milliseconds
        self.seed = int(time.time() * 1000)
        # If a custom deck is provided, use it; otherwise, create a default deck
        self.deck = deck if deck is not None else self.create_default_deck()

    def custom_random_number(self, min_value, max_value):
        # Update the seed using a linear congruential generator (LCG) formula
        self.seed = (self.seed * 1103515245 + 12345) & 0x7FFFFFFF
        # Generate a random number within the given range [min_value, max_value]
        random_value = self.seed % (max_value - min_value + 1)
        return min_value + random_value

    def riffle_shuffle(self):
        # If the deck has 1 or fewer cards, return it as-is (nothing to shuffle)
        if len(self.deck) <= 1:
            return self.deck

        # Split the deck at a random point
        split_point = self.custom_random_number(1, len(self.deck) - 1)
        left_half = self.deck[:split_point]
        right_half = self.deck[split_point:]

        shuffled_deck = []

        # Simulate the riffle shuffle by interleaving the two halves
        while left_half or right_half:
            if left_half and right_half:
                # Randomly choose to take from the left or right half
                if self.custom_random_number(0, 1) == 0:
                    shuffled_deck.append(left_half.pop(0))
                else:
                    shuffled_deck.append(right_half.pop(0))
            elif left_half:
                # If only the left half remains, add the remaining cards to the shuffled deck
                shuffled_deck.append(left_half.pop(0))
            elif right_half:
                # If only the right half remains, add the remaining cards to the shuffled deck
                shuffled_deck.append(right_half.pop(0))

        # Update the deck with the shuffled deck
        self.deck = shuffled_deck
        return self.deck

    def overhand_shuffle(self):
        shuffled_deck = []
        while self.deck:
            # Randomly determine how many cards to take from the top of the deck (1 to 5)
            num_cards = self.custom_random_number(1, min(5, len(self.deck)))
            # Move the selected cards to the front of the shuffled deck
            shuffled_deck = self.deck[:num_cards] + shuffled_deck
            # Remove the selected cards from the original deck
            self.deck = self.deck[num_cards:]
        # Update the deck with the shuffled deck
        self.deck = shuffled_deck
        return self.deck

    def smoosh_shuffle(self):
        # Randomly swap each card in the deck with another card
        for i in range(len(self.deck)):
            j = self.custom_random_number(0, len(self.deck) - 1)
            self.deck[i], self.deck[j] = self.deck[j], self.deck[i]
        return self.deck

    def mega_shuffle(self):
        # List of shuffle methods to apply
        self.deck = self.create_default_deck()
        shuffle_funcs = [self.riffle_shuffle, self.overhand_shuffle, self.smoosh_shuffle]
        for _ in range(3):  # Repeat the shuffling process three times
            # Randomly shuffle the list of shuffle functions and apply them in that order
            for shuffle in sorted(shuffle_funcs, key=lambda _: self.custom_random_number(0, 2)):
                shuffle()
        return self.deck

    def create_default_deck(self):
        # Create a default deck with predefined cards
        deck = []
        deck.extend(["ball"] * 10)
        deck.extend(["strike"] * 10)
        deck.extend(["fly_out"] * 2)
        deck.extend(["foul_ball"] * 2)
        deck.extend(["out_double_play_first"] * 1)
        deck.extend(["out_double_play_second"] * 1)
        deck.extend(["foul_out"] * 1)
        deck.extend(["hit_by_pitcher"] * 1)
        deck.extend(["stolen_base"] * 1)
        deck.extend(["balk"] * 1)
        deck.extend(["home_run"] * 1)
        deck.extend(["triple"] * 1)
        deck.extend(["double"] * 2)
        deck.extend(["single"] * 2)
        # Set the deck to the newly created deck
        self.deck = deck
        return self.deck

    def get_deck(self):
        # Return the current state of the deck
        return self.deck

    def shuffle_and_get_deck(self):
        # Shuffle the deck using mega_shuffle and return the shuffled deck
        return self.mega_shuffle()

class Game:
    def __init__(self, batting_order, opponent_batting_order, bench):
        # Initialize game state variables
        pyxel.images[0].load(0, 0, "istockphoto-667849798-612x612 (3).jpg")
        self.batting_order = batting_order
        self.opponent_batting_order = opponent_batting_order
        self.bench = bench
        self.current_card = None
        self.inning = 1
        self.outs = 0
        self.home_score = 0
        self.away_score = 0
        self.current_batter_index = 0
        self.field = [None, None, None]  # Represents bases (first, second, third)
        self.difficulty = 'easy'
        self.batter_turn_started = False  # Flag to indicate if the batter's turn has started
        self.strike = 0
        self.ball = 0
 
        # Initialize the deck using the DeckShuffler class
        self.deck_shuffler = DeckShuffler()
        self.new_deck()

        # Define the coordinates for displaying scores and other information
        self.score_coords = {
            'home': (10, 5),
            'away': (120, 5),
            'inning': (60, 5),
            'outs': (10, 35),
            'card': (90, 15),  # Coordinates for the card display
            'strike_ball': (10, 15),  # Coordinates for strikes and balls display
            'ball': (10, 25),
            'batter': (10, 110)  # Coordinates for the current batter display
        }

    def new_deck(self):
        # Shuffle and assign a new deck
        self.deck = self.deck_shuffler.shuffle_and_get_deck()

    def start_inning(self):
        # Start a new inning by resetting outs and incrementing the inning count
        self.inning += 1
        self.outs = 0
        self.field = [None, None, None]  # Clear the bases for a new inning

    def batter_turn(self):
        self.batter_turn_started = True

        if self.strike == 0 and self.ball == 0:
            # Initialize strike and ball counters for the new batter
            self.strike = 0
            self.ball = 0

        # Draw a card for the current batter's turn
        self.current_card = self.draw_card()
        
        # Handle the card action
        if self.current_card == "strike":
            self.handle_strike()
        elif self.current_card == "foul_ball" and self.strike < 2:  # Foul ball is strike unless it's the third strike
            self.handle_strike()
        elif self.current_card == "ball":
            self.handle_ball()
        elif self.current_card == "single":
            self.advance_runners(1, hit=False)
            self.next_batter()
        elif self.current_card == "double":
            self.advance_runners(2, hit=True)
            self.next_batter()
        elif self.current_card == "triple":
            self.advance_runners(3, hit=True)
            self.next_batter()
        elif self.current_card == "home_run":
            self.advance_runners(4, hit=True)
            self.next_batter()
        elif self.current_card == "hit_by_pitcher":
            self.advance_runners(1, hit=False)
            self.next_batter()
            """
        elif self.current_card == "stolen_base":
            self.advance_runners(1)
            self.next_batter()
            """
        elif self.current_card == "balk":
            self.advance_runners(1, hit=False)
        elif self.current_card == "fly_out":
            self.handle_out()
        elif self.current_card == "foul_out":
            self.handle_out()
        elif self.current_card == "out_double_play_first":
            self.out_at_first()
            self.out_at_second()
        elif self.current_card == "out_double_play_second":
            self.out_at_second()
            self.out_at_third()
        
    def next_batter(self):
        self.current_batter_index = (self.current_batter_index + 1) % 9
        self.strike = 0
        self.ball = 0
        self.new_deck()

    def handle_strike(self):
        # Handle the logic when a strike is drawn
        self.strike += 1
        if self.strike == 3:
            self.handle_out()

    def handle_ball(self):
        # Handle the logic when a ball is drawn
        self.ball += 1
        if self.ball >= 4:
            self.advance_runners(1, hit=False)
            self.next_batter()

    def handle_out(self):
        # Handle the logic when an out is drawn
        self.outs += 1
        if self.outs >= 3:
            self.end_inning()
        else:
            self.next_batter()

    def advance_runners(self, bases, hit):
        # Advance the runners on the field based on the number of bases moved
        if bases == 4:  # Home run, clear the bases
            for i in range(3):
                if self.field[i] is not None:
                    self.score_run()
                    self.field[i] = None
            self.score_run()  # Score for the batter
            self.next_batter()
        else:
            if hit:
                # Move runners on the bases forward for hits (single, double, triple)
                for i in reversed(range(3)):
                    if self.field[i] is not None:
                        if i + bases >= 3:
                            self.score_run()
                            self.field[i] = None
                        else:
                            self.field[i + bases] = self.field[i]
                            self.field[i] = None
                # Place the batter on the appropriate base
                if bases < 4:
                    self.field[bases - 1] = "batter"
                self.next_batter()
            else:
                # Move runners on the bases for walks or hit-by-pitch
                if self.field[2] is not None:
                    self.score_run()
                    self.field[2] = None
                if self.field[1] is not None:
                    self.field[2] = self.field[1]
                    self.field[1] = None
                if self.field[0] is not None:
                    self.field[1] = self.field[0]
                    self.field[0] = None
                self.field[0] = "batter"
                self.next_batter()

    def out_at_first(self):
        if self.field[0] is not None:
            self.field[0] = None
            self.handle_out()

    def out_at_second(self):
        if self.field[1] is not None:        
            self.field[1] = None
            self.handle_out()

    def out_at_third(self):
        if self.field[2] is not None:
            self.field[2] = None
            self.handle_out()

    def score_run(self):
        # Increase the score for the current team
        if self.inning % 2 == 1:
            self.home_score += 1
        else:
            self.away_score += 1

    def end_inning(self):
        self.start_inning()

    def draw_card(self):
        # Draw the next card from the deck
        if not self.deck:
            self.new_deck()  # Re-shuffle if the deck is empty
        return self.deck.pop(0)
    
    def get_base_coords(self, base):
        # Return the coordinates for a base position
        coords = {
            "1B": (100, 80),
            "2B": (80, 50),
            "3B": (20, 80)
        }
        return coords.get(base, (0, 0))

    def end_game(self):
        # Handle end-of-game logic, such as declaring the winner
        pyxel.quit()

    def draw(self):
        # Clear the screen and draw the background and game elements
        pyxel.cls(5)
        pyxel.blt(0, 0, 0, 0, 0, 160, 120)  # Draw the background image
        
        # Draw the inning, outs, and scores
        pyxel.text(self.score_coords['home'][0], self.score_coords['home'][1], f"Home: {self.home_score}", 7)
        pyxel.text(self.score_coords['away'][0], self.score_coords['away'][1], f"Away: {self.away_score}", 7)
        pyxel.text(self.score_coords['inning'][0], self.score_coords['inning'][1], f"Inning: {self.inning}", 7)
        pyxel.text(self.score_coords['outs'][0], self.score_coords['outs'][1], f"Outs: {self.outs}", 7)
        pyxel.text(30, 120, "Press SPACE to draw a card", 7)
        
        # Display strikes and balls
        pyxel.text(self.score_coords['strike_ball'][0], self.score_coords['strike_ball'][1], f"Strikes: {self.strike}", 7)
        pyxel.text(self.score_coords['ball'][0], self.score_coords['ball'][1], f"Balls: {self.ball}", 7)
        
        # Display bases
        positions = ["1B", "2B", "3B"]
        for i, pos in enumerate(positions):
            if self.field[i] == "batter":
                x, y = self.get_base_coords(pos)
                pyxel.text(x, y, "Batter", 8)
        
        # Display the current card
        if self.current_card:
            pyxel.text(self.score_coords['card'][0], self.score_coords['card'][1], f"Card: {self.current_card}", 7)

        # Display the current batter
        if self.inning % 2 == 1:
            current_batter = str({self.batting_order[self.current_batter_index]['fullname']})
            current_batter = current_batter.translate({ord("'"): None})
            current_batter = current_batter.translate({ord("{"): None})
            current_batter = current_batter.translate({ord("}"): None})
        else:
            current_batter = str({self.opponent_batting_order[self.current_batter_index]['fullname']})
            current_batter = current_batter.translate({ord("'"): None})
            current_batter = current_batter.translate({ord("{"): None})
            current_batter = current_batter.translate({ord("}"): None})
        pyxel.text(self.score_coords['batter'][0], self.score_coords['batter'][1], f"Batter: {current_batter}", 7)

class PostGameScreen:
    def __init__(self, home_score, away_score, batting_order, opponent_batting_order):
        self.home_score = home_score
        self.away_score = away_score
        self.batting_order = batting_order
        self.opponent_batting_order = opponent_batting_order
        self.winner = "Home" if home_score > away_score else "Away" if away_score > home_score else "Tie"

        # Define coordinates for displaying the post-game information
        self.score_coords = {
            'result': (60, 30),
            'home': (10, 60),
            'away': (120, 60),
            'winner': (60, 90)
        }

    def draw(self):
        # Clear the screen for the post-game view
        pyxel.cls(0)

        # Display the final scores
        pyxel.text(self.score_coords['home'][0], self.score_coords['home'][1], f"Home: {self.home_score}", 7)
        pyxel.text(self.score_coords['away'][0], self.score_coords['away'][1], f"Away: {self.away_score}", 7)

        # Display the winner
        pyxel.text(self.score_coords['winner'][0], self.score_coords['winner'][1], f"Winner: {self.winner}", 7)

        # Optionally display some player statistics
        pyxel.text(10, 120, "Press R to restart or Q to quit", 7)
        
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
        self.game = None
        self.post_game_screen = None

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
            self.update_game()
        elif self.menu.state == GameState.POST_GAME:
            self.update_post_game()

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
        elif self.menu.state == GameState.GAME and self.game:
            self.game.draw()
        elif self.menu.state == GameState.POST_GAME and self.post_game_screen:
            self.post_game_screen.draw()

    def update_team_selection(self):
        self.selected_team, self.teamID = self.team_selection_screen.update()
        if self.selected_team:
            self.create_account_screen = CreateAccountScreen(self.selected_team, self.teamID)
            self.menu.state = GameState.CREATE_ACCOUNT

    def update_load_game(self):
        self.load_game.update()
        if pyxel.btnp(pyxel.KEY_RETURN):
            self.selected_team, self.teamID, self.CoachingCredits, self.stadium, self.training_facilitys, self.rehab_facilitys, self.coachFirstName, self.coachLastName = self.load_game.load_selected_game()

            # Check if player_team_screen is initialized
            if self.player_team_screen is not None:
                current_round = self.player_team_screen.current_round
            else:
                current_round = 0  # Default to 0 or some appropriate fallback

            schedule_ = Schedule(mlb_teamsNL, mlb_teamsAL, self.selected_team, current_round)
            self.schedule = schedule_.get_schedule()
            self.player_team_screen = PlayerTeamScreen(self.selected_team, self.teamID, self.schedule, self.CoachingCredits)
            self.menu.state = GameState.PLAYER_TEAM_SCREEN

    def update_create_account(self):
        self.create_account_screen.update()
        if self.create_account_screen.createdAccount:
            # Check if player_team_screen is initialized

            if self.player_team_screen is not None:
                current_round = self.player_team_screen.current_round
            else:
                current_round = 0  # Default to 0 or some appropriate fallback

            schedule_ = Schedule(mlb_teamsNL, mlb_teamsAL, self.selected_team, current_round)
            self.schedule = schedule_.get_schedule()
            self.player_team_screen = PlayerTeamScreen(self.selected_team, self.teamID, self.schedule, self.CoachingCredits)
            self.menu.state = GameState.PLAYER_TEAM_SCREEN

    def update_player_team_screen(self):
        self.player_team_screen.update()

        if pyxel.btnp(pyxel.KEY_RETURN):
            selected_option = self.player_team_screen.optionsPlayer[self.player_team_screen.selectedPlayer]
            

            if selected_option == "Front Office":
                self.selected_team, self.teamID, self.CoachingCredits, self.stadium, self.training_facilitys, self.rehab_facilitys, self.coachFirstName, self.coachLastName = self.load_game.load_selected_game()

                self.front_office = FrontOffice(self.CoachingCredits, self.stadium, self.training_facilitys, self.rehab_facilitys, self.coachFirstName, self.coachLastName)
                self.menu.state = GameState.FRONT_OFFICE

            elif selected_option == "Roster":
                self.selected_team, self.teamID = self.player_team_screen.selected_team, self.teamID
                self.roster_screen = RosterScreen(self.selected_team, self.teamID)
                self.menu.state = GameState.ROSTER_SCREEN

            elif selected_option == "Play Game":
                # Fetch the current game from the schedule
                away_team, home_team = self.player_team_screen.draw_schedule()
                current_round = self.player_team_screen.current_round
                
                self.play_game_screen = PlayGameScreen(
                    mlb_teamsNL,        # First argument
                    mlb_teamsAL,        # Second argument
                    self.selected_team,  # Third argument
                    self.teamID,        # Fourth argument (team_id)
                    current_round       # Fifth argument (week)
                )

                # Check if the opponent is "BYE"
                if away_team == "BYE" or home_team == "BYE":
                    pyxel.text(10, 10, "Cannot play game with BYE team. Please advance the week.", 8)
                else:
                    # Proceed to Play Game if it's not a BYE week
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
            self.batting_order, self.opponent_batting_order, self.bench = self.play_game_screen.batting_order,self.play_game_screen.opponent_batting_order, self.play_game_screen.bench
            self.game = Game(self.batting_order, self.opponent_batting_order, self.bench)
            self.menu.state = GameState.GAME
            
    def update_game(self):
        if pyxel.btnp(pyxel.KEY_SPACE):
            if not self.game.batter_turn_started or (self.game.strike < 3 and self.game.ball < 4):
                self.game.batter_turn() 
            if self.game.inning > 9 and self.game.home_score != self.game.away_score:
                self.post_game_screen = PostGameScreen(self.game.home_score, self.game.away_score, self.batting_order, self.opponent_batting_order)
                self.menu.state = GameState.POST_GAME
    
    def update_post_game(self):
        # Handle user input for restarting or quitting
        if pyxel.btnp(pyxel.KEY_R):
            # Restart the game
            return 'restart'
        if pyxel.btnp(pyxel.KEY_Q):
            # Quit the game
            pyxel.quit()

game_state_manager = GameStateManager()

def update():
    game_state_manager.update()

def draw():
    game_state_manager.draw()

pyxel.run(update, draw)