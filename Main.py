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
    def __init__(self, selected_team, teamID):
        self.selected_team = selected_team
        self.teamID = teamID
        self.optionsPlayer = ["Next Game","Front Office", "Roster", "Hall of Fame", "Options"]
        self.selectedPlayer = 0

    def update(self):
        if pyxel.btnp(pyxel.KEY_DOWN):
            self.selectedPlayer = (self.selectedPlayer + 1) % len(self.optionsPlayer)
        if pyxel.btnp(pyxel.KEY_UP):
            self.selectedPlayer = (self.selectedPlayer - 1) % len(self.optionsPlayer)
        if pyxel.btnp(pyxel.KEY_RETURN):
            selected_option = self.optionsPlayer[self.selectedPlayer]
            if selected_option == "Roster":
                menu.state = GameState.ROSTER_SCREEN
            if selected_option == "Front Office":
                menu.state = GameState.FRONT_OFFICE

    def draw(self):
        pyxel.cls(12)
        pyxel.text(15, 10, f"Your Team: {self.selected_team}", 1)
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

        if pyxel.btnp(pyxel.KEY_BACKSPACE):
            menu.state = GameState.PLAYER_TEAM_SCREEN

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
        elif pyxel.btnp(pyxel.KEY_BACKSPACE):
            menu.state = GameState.PLAYER_TEAM_SCREEN

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

mlb_teamsNL = [
    ("Philadelphia Phillies"), ("New York Mets"), ("Atlanta Braves"), ("Miami Marlins"), ("Washington Nationals"),
    ("Milwaukee Brewers"), ("Chicago Cubs"), ("Cincinnati Reds"), ("Pittsburgh Pirates"), ("St. Louis Cardinals"),
    ("Los Angeles Dodgers"), ("Arizona Diamondbacks"), ("San Diego Padres"), ("San Francisco Giants"), ("Colorado Rockies")
]

mlb_teamsAL = [
    ("Baltimore Orioles"), ("Tampa Bay Rays"), ("Toronto Blue Jays"), ("New York Yankees"), ("Boston Red Sox"),
    ("Minnesota Twins"), ("Detroit Tigers"), ("Cleveland Guardians"), ("Chicago White Sox"), ("Kansas City Royals"),
    ("Houston Astros"), ("Texas Rangers"), ("Seattle Mariners"), ("Los Angeles Angels"), ("Oakland Athletics")
]

menu = Menu()
team_selection_screen = TeamSelectionScreen(mlb_teamsNL, mlb_teamsAL)
load_game = loadGame()
roster_screen = None
front_office = None

def update():
    global selected_team, teamID, player_team_screen, roster_screen, front_office, create_account_screen
    if menu.state == GameState.MENU:
        menu.update()
    elif menu.state == GameState.TEAM_SELECTION:
        selected_team, teamID = team_selection_screen.update()
        if selected_team:
            create_account_screen = CreateAccountScreen(selected_team, teamID)
            menu.state = GameState.CREATE_ACCOUNT
    elif menu.state == GameState.LOAD_GAME:
        load_game.update()
        if pyxel.btnp(pyxel.KEY_RETURN):
            selected_team, teamID = load_game.load_selected_game()
            player_team_screen = PlayerTeamScreen(selected_team, teamID)
            menu.state = GameState.PLAYER_TEAM_SCREEN
    elif menu.state == GameState.CREATE_ACCOUNT:
        create_account_screen.update()
        if create_account_screen.createdAccount:
            player_team_screen = PlayerTeamScreen(selected_team, teamID)
            menu.state = GameState.PLAYER_TEAM_SCREEN
    elif menu.state == GameState.PLAYER_TEAM_SCREEN:
        player_team_screen.update()
        if pyxel.btnp(pyxel.KEY_RETURN):
            selected_option = player_team_screen.optionsPlayer[player_team_screen.selectedPlayer]
            if selected_option == "Front Office":
                front_office = FrontOffice()
                menu.state = GameState.FRONT_OFFICE
            if selected_option == "Roster":
                selected_team, teamID = player_team_screen.selected_team, player_team_screen.teamID
                roster_screen = RosterScreen(selected_team, teamID)
                menu.state = GameState.ROSTER_SCREEN
    elif menu.state == GameState.ROSTER_SCREEN:
        if roster_screen:
            roster_screen.update()
    elif menu.state == GameState.FRONT_OFFICE:
        if front_office:
            front_office.update()

def draw():
    if menu.state == GameState.MENU:
        menu.draw()
    elif menu.state == GameState.TEAM_SELECTION:
        team_selection_screen.draw()
    elif menu.state == GameState.CREATE_ACCOUNT:
        create_account_screen.draw()
    elif menu.state == GameState.LOAD_GAME:
        load_game.draw()
    elif menu.state == GameState.PLAYER_TEAM_SCREEN:
        player_team_screen.draw()
    elif menu.state == GameState.ROSTER_SCREEN:
        if roster_screen:
            roster_screen.draw()
    elif menu.state == GameState.FRONT_OFFICE:
        if front_office:
            front_office.draw()

pyxel.run(update, draw)
