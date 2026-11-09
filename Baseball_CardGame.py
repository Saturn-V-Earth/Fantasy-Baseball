import pyxel
import mlbstatsapi
import pickle
import os
import time
import random
import numpy as np

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
    DIFFICULTY = 10
    BUDGET = 11
    VIEW_ROSTER = 12
    FREE_AGENTS = 13
        
class Menu:
    def __init__(self):
        self.state = GameState.MENU
        self.length = 160
        self.width = 130
        pyxel.init(self.length, self.width, title="Fantasy Baseball")
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
    
    def draw_centered_text(self, x_center, y, text, color):
        text_width = len(text) * pyxel.FONT_WIDTH  # pyxel.FONT_WIDTH is typically 4
        x = x_center - (text_width // 2)
        pyxel.text(x, y, text, color)

    def draw(self):
        pyxel.cls(12)
        title = "Fantasy Baseball"
        
        # Center the title
        self.draw_centered_text(self.length // 2, 40, title, 1)
        
        # Center the options
        for i, option in enumerate(self.options):
            y = 60 + i * 10
            if i == self.selected:
                self.draw_centered_text(self.length // 2, y, "> " + option, 0)
            else:
                self.draw_centered_text(self.length // 2, y, option, 7)

class TeamSelectionScreen:
    def __init__(self, mlb_teamsNL, mlb_teamsAL):
        self.mlb_teamsNL = mlb_teamsNL
        self.mlb_teamsAL = mlb_teamsAL
        self.teams = {
            "American League": self.mlb_teamsAL,
            "National League": self.mlb_teamsNL
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
            y = 30 + i * 6
            if i == self.selected_team:
                pyxel.text(10 if self.selected_section == "American League" else 10, y, "> " + team, 0)
            else:
                pyxel.text(10 if self.selected_section == "American League" else 10, y, team, 7)

class loadGame():
    def __init__(self):
        self.saved_games = []
        self.selected_index = 0
        self.loaded_data = None
        self.refresh_saved_games_list()

    def refresh_saved_games_list(self):
        # Refreshes the saved game list dynamically
        self.saved_games = sorted(
            [f for f in os.listdir() if f.endswith('_account.pkl')],
            key=lambda x: os.path.getmtime(x),
            reverse=True
        )
        if not self.saved_games:
            self.selected_index = 0
        else:
            self.selected_index = min(self.selected_index, len(self.saved_games) - 1)
    
    def update(self):
        if not self.saved_games:
            if pyxel.btnp(pyxel.KEY_RETURN):
                self.refresh_saved_games_list()
            return

        if pyxel.btnp(pyxel.KEY_UP):
            self.selected_index = (self.selected_index - 1) % len(self.saved_games)
        elif pyxel.btnp(pyxel.KEY_DOWN):
            self.selected_index = (self.selected_index + 1) % len(self.saved_games)
        elif pyxel.btnp(pyxel.KEY_RETURN):
            self.load_selected_game()

    def load_selected_game(self):
        if not self.saved_games:
            self.refresh_saved_games_list()
            return None
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

        self.round_num = self.loaded_data['round_num']

        self.wins = self.loaded_data['wins']
        self.losses = self.loaded_data['losses']

        self.difficulty = self.loaded_data['difficulty']
        self.revenue = self.loaded_data['revenue']

        self.salary_cap = self.loaded_data['salary_cap']

        self.budget = self.loaded_data['budget']

        return self.teamID, self.selected_team, self.CoachingCredits, self.stadium, self.training_facilitys, self.rehab_facilitys, self.coachFirstName, self.coachLastName, self.round_num, self.wins, self.losses, self.difficulty, self.revenue, self.salary_cap, self.budget

    def draw(self):
        pyxel.cls(12)
        pyxel.text(10, 10, "Load Game Save", 1)
        if not self.saved_games:
            pyxel.text(10, 25, "No save files found.", 8)
            pyxel.text(10, 35, "Press ENTER to refresh.", 7)
            return
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

        self.round_num = 0

        self.wins = 0
        self.losses = 0

    def get_coachFirstName(self):
        return self.coachFirstName

    def get_coachLastName(self):
        return self.coachLastName
    
    def get_CoachingCredits(self):
        return self.CoachingCredits
    
    def get_round_num(self):
        return self.round_num

    def get_stadium(self):
        return self.stadium
    
    def get_training_facilitys(self):
        return self.training_facilitys
    
    def get_rehab_facilitys(self):
        return self.rehab_facilitys

    def get_wins(self):
        return self.wins

    def get_losses(self):
        return self.losses

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
            'rehab_facilitys': self.rehab_facilitys,
            'round_num': self.round_num,
            'wins': self.wins,
            'losses': self.losses,
            'difficulty': None,
            'revenue': None,
            'salary_cap': None,
            'budget': None
        }

        filename = f"{self.coachFirstName}_{self.coachLastName}_account.pkl"
        with open(filename, 'wb') as f:
            pickle.dump(account_data, f)
        print(f"Account saved to {filename}")

    def run(self):
        pyxel.run(self.update, self.draw)

class PlayerTeamScreen:
    def __init__(self, selected_team, teamID, schedule, coachingCredits, round_num, coachFirstName, coachLastName, wins, losses, difficulty, revenue, salary_cap, budget):
        self.budget = budget
        self.difficulty = difficulty
        self.revenue = revenue
        self.salary_cap = salary_cap
        self.wins = wins
        self.losses = losses
        self.coachFirstName = coachFirstName
        self.coachLastName = coachLastName
        self.selected_team = selected_team
        self.teamID = teamID
        self.optionsPlayer = ["Play Game", "Front Office", "Roster", "Advance Week", "Options"]
        self.CoachingCredits = coachingCredits
        self.selectedPlayer = 0
        self.schedule = schedule
        self.current_round = round_num
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
                self.save_account()

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
        pyxel.text(15, 120, f"Wins: {self.wins}      Losses: {self.losses}", 1)

        self.draw_schedule()
        for i, option in enumerate(self.optionsPlayer):
            y = 30 + i * 10
            if i == self.selectedPlayer:
                pyxel.text(30, y, "> " + option, 0)
            else:
                pyxel.text(30, y, option, 7)

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
        account_data['round_num'] = self.current_round

        # Write updated data back to the file
        with open(filename, 'wb') as f:
            pickle.dump(account_data, f)
        print(f"Account saved to {filename}")

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
            pyxel.text(15, 85, "Increase Salary Cap For 10 CC", 8)
            if self.axis == "horizontal" and j == self.selectedHorizontalOption:
                pyxel.text(x, 100, "> " + option, 0)
            else:
                pyxel.text(x, 100, option, 7)

class Budget:
    def __init__(self, coachFirstName, coachLastName, revnue, salary_cap):
        self.coachFirstName = coachFirstName
        self.coachLastName = coachLastName
        self.free_agents = []
        self.staff = []
        self.coaches = []
        self.revenue = revnue
        self.budget = 0
        self.salary_cap = salary_cap
        
        # Add an instance of Difficulty
        self.difficulty = Difficulty(self.coachFirstName, self.coachLastName)
        

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
        account_data['revenue'] = self.revenue
        account_data['budget'] = self.budget

        # Write updated data back to the file
        with open(filename, 'wb') as f:
            pickle.dump(account_data, f)
        print(f"Account saved to {filename}")

    def teamRevenue(self):
        return self.revenue

    def revenueSharing(self):
        # Example: Assume a percentage of revenue is shared with the league
        total_revenue = self.teamRevenue()
        revenue_share_percentage = 0.10  # Assume 10% of revenue is shared
        revenue_shared = total_revenue * revenue_share_percentage

        return revenue_shared

    def playerSalaries(self):
        return self.salary_cap

    def staffSalaries(self):
        total_salary = sum(staff_member['salary'] for staff_member in self.staff)
        return total_salary

    def CompetitiveBalanceTax(self):
        total_salary = self.playerSalaries() + self.staffSalaries()
        if total_salary > self.salary_cap:
            tax_rate = 0.20  # Assume 20% tax on over-the-cap amount
            over_the_cap = total_salary - self.salary_cap
            tax = over_the_cap * tax_rate
        else:
            tax = 0
        return tax

    def AvailableBudget(self):
        total_revenue = self.teamRevenue()
        total_salaries = self.playerSalaries() + self.staffSalaries()
        tax = self.CompetitiveBalanceTax()
        
        self.budget = total_revenue - total_salaries - tax
        self.save_account()
        return self.budget


class Difficulty:
    def __init__(self, coachFirstName, coachLastName):
        self.coachFirstName = coachFirstName
        self.coachLastName = coachLastName
        self.optionsDifficulty = ['Easy', 'Medium', 'Hard']
        self.selected_difficulty = 0
        self.revenue = 0  # This will store the calculated budget for the selected difficulty
        # Define the mean and standard deviation for revenue budget
        self.mean = 218.9
        self.std_dev = 38.75766
        self.length = 160
        self.width = 130
        
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
        account_data['difficulty'] = self.optionsDifficulty[self.selected_difficulty]
        account_data['revenue'] = self.revenue

        # Write updated data back to the file
        with open(filename, 'wb') as f:
            pickle.dump(account_data, f)
        print(f"Account saved to {filename}")
    
    def update(self):
        if pyxel.btnp(pyxel.KEY_DOWN):
            self.selected_difficulty = (self.selected_difficulty + 1) % len(self.optionsDifficulty)
        if pyxel.btnp(pyxel.KEY_UP):
            self.selected_difficulty = (self.selected_difficulty - 1) % len(self.optionsDifficulty)
        if pyxel.btnp(pyxel.KEY_RETURN):
            selectedOption = self.optionsDifficulty[self.selected_difficulty]


            if selectedOption == 'Easy':
                self.revenue = min(self.mean + self.std_dev, np.random.normal(self.mean + self.std_dev, self.std_dev * 0.2))

            elif selectedOption == 'Medium':
                self.revenue = np.random.normal(self.mean, self.std_dev * 0.5)

            elif selectedOption == 'Hard':
                self.revenue = max(self.mean - self.std_dev, np.random.normal(self.mean - self.std_dev, self.std_dev * 0.2))


            # Ensure the budget is within a realistic range
            self.revenue = max(50, min(self.revenue, 350))  # Example limits to keep values reasonable
            
            self.revenue = round(self.revenue, 2)  # Round to 2 decimal places

            self.save_account()

    def draw_centered_text(self, x_center, y, text, color):
        text_width = len(text) * pyxel.FONT_WIDTH  # pyxel.FONT_WIDTH is typically 4
        x = x_center - (text_width // 2)
        pyxel.text(x, y, text, color)

    def draw(self):
        pyxel.cls(12)
        title = "Difficulty"
        
        # Center the title
        self.draw_centered_text(self.length // 2, 40, title, 1)
        
        # Center the options
        for i, option in enumerate(self.optionsDifficulty):
            y = 60 + i * 10
            if i == self.selected_difficulty:
                self.draw_centered_text(self.length // 2, y, "> " + option, 0)
            else:
                self.draw_centered_text(self.length // 2, y, option, 7)

class FreeAgents:
    def __init__(self, difficulty, salary_cap, budget, teamID, coachFirstName, coachLastName, training_facilitys):
        self.difficulty_level = difficulty
        self.salary_cap = salary_cap
        self.budget = budget
        self.team_id = teamID
        self.coachFirstName = coachFirstName
        self.coachLastName = coachLastName
        self.training_facilitys = training_facilitys

        self.current_free_agent_index = 0

        self.free_agents = []
        self.free_agent_players = []
        self.free_agent_BA = []
        self.free_agent_Fld = []
        self.free_agent_star_ratings = []
        self.free_agent_salaries = []
        
        self.original_players = []
        self.BA = []
        self.Fld = []
        self.star_ratings = []
        self.salaries = []
        self.load_player_data(self.team_id)

        self.positions = ['P', 'C', '1B', '2B', '3B', 'SS', 'LF', 'CF', 'RF', 'DH']

        self.randomNames = self.generate_random_names()
        self.free_agents = self.generate_free_agents()

    def generate_random_names(self):
        return [
            'John Doe', 'Michael Johnson', 'David Wilson', 'Robert Lee', 
            'William Martinez', 'Matthew Curtis', 'Brandon Attram', 
            'Joshua Bryan', 'Andreas Pham', 'Yong Burnett', 'Chauncey Meyer', 
            'Adalberto Green', 'Stanley Olsen', 'Jewel Pineda', 'Jame Kerr', 
            'Russel Rowland', 'Corey Becker', 'Rosendo Glover', 'Kris Chan', 
            'Tyler Compton', 'Sheldon Simpson', 'George Martinez', 'Guy Fisher', 
            'Claude Price', 'Leonard Yu', 'Carter Atkins', 'Raul Frye', 
            'Drew Koch', 'Victor Kirby', 'Benton Mcintyre', 'Damion Costa', 
            'Ernest Forbes', 'Fredric Crane', 'Darell Pittman', 'Rickey Huber', 
            'Marcelo Phelps', 'Bertram Vaughn', 'Sal Armstrong', 
            'Jefferson Richardson', 'Tory Clay', 'Austin Hickman', 
            'William Woods', 'Jody Bowers', 'Stacy Mccoy', 'Sang Patton', 
            'Vern Ford', 'Gonzalo Peck', 'Jose Pierce', 'Armand Francis', 
            'Jamaal Cortez', 'Blaine Espinoza', 'Eugenio Matthews', 
            'William Floyd', 'Porfirio Perry', 'Jeramy Gibson', 
            'Seth Beltran', 'Ricky Mathis'
        ]

    def generate_free_agents(self):
        free_agents = [
            self.generate_free_agent('low'), *[self.generate_free_agent('mid') for _ in range(3)],
            self.generate_free_agent('high')
        ]
        self.distribute_salaries()
        return free_agents

    def generate_free_agent(self, level):
        # Generate player details
        fullname = random.choice(self.randomNames)
        position = random.choice(self.positions)

        if position == 'P':  # Pitcher
            era = round(random.uniform(2.00, 5.50) if level == 'low' else (random.uniform(2.00, 2.50) if level == 'high' else random.uniform(3.00, 4.00)), 3)
            ba, fa = None, round(random.uniform(0.950, 0.990), 3)
        else:  # Non-pitcher
            ba = round(random.uniform(0.200, 0.330) if level == 'high' else random.uniform(0.240, 0.280), 3)
            fa, era = round(random.uniform(0.950, 0.990), 3), None

        # Calculate star ratings
        ba_stars, fa_stars, era_stars = self.calculate_star_rating(ba, fa, era)

        # Append to lists for separate storage
        self.free_agent_players.append({'fullname': fullname, 'position': position, 'era': era})
        self.free_agent_BA.append(ba)
        self.free_agent_Fld.append(fa)
        self.free_agent_star_ratings.append((ba_stars, fa_stars, era_stars))
        
        return fullname  # Reference by name for simplicity

    def calculate_star_rating(self, ba=None, fa=None, era=None):
        ba_min, ba_max = 0.200, 0.300
        fa_min, fa_max = 0.950, 0.990
        era_min, era_max = 2.00, 5.00

        if ba is not None:
            normalized_ba = self.normalize_stat(ba, ba_min, ba_max)
            ba_stars = self.stat_to_stars(normalized_ba)
        else:
            ba_stars = None

        normalized_fa = self.normalize_stat(fa, fa_min, fa_max)
        fa_stars = self.stat_to_stars(normalized_fa)

        if era is not None:
            normalized_era = self.normalize_stat(era, era_min, era_max, invert=True)
            era_stars = self.stat_to_stars(normalized_era)
        else:
            era_stars = None

        return ba_stars, fa_stars, era_stars

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
    
    def generate_salary_cap(self):
        # Set budget based on difficulty level
        mean, std_dev = 139, 45
        if self.difficulty_level == 'Easy':
            return min(mean + std_dev, np.random.normal(mean + std_dev, std_dev * 0.2))
        elif self.difficulty_level == 'Medium':
            return np.random.normal(mean, std_dev * 0.5)
        elif self.difficulty_level == 'Hard':
            return max(mean - std_dev, np.random.normal(mean - std_dev, std_dev * 0.2))
        else:
            return mean  # Default to mean if no valid difficulty level is provided

    def distribute_salaries(self):
        total_stars = sum((ba or 0) + (fa or 0) + (era or 0) for ba, fa, era in self.free_agent_star_ratings)
        
        # Calculate the deduction based on the training facilities level
        facility_deduction = self.training_facilitys * 1  # 1M per level
        
        self.free_agent_salaries = [
            round((self.salary_cap * ((ba or 0) + (fa or 0) + (era or 0)) / total_stars - facility_deduction), 2) if total_stars else 0
            for ba, fa, era in self.free_agent_star_ratings
        ]

    def draw(self):
        pyxel.cls(12)  # Clear the screen with a black background
        pyxel.text(10, 10, "Free Agents", 1)


        if self.free_agents:
            if self.current_free_agent_index >= len(self.free_agent_players):
                self.current_free_agent_index = 0  # Reset to the first index if out of range

            player = self.free_agent_players[self.current_free_agent_index]
            batting_average = self.free_agent_BA[self.current_free_agent_index]
            fielding_average = self.free_agent_Fld[self.current_free_agent_index]
            ba_stars, fa_stars, era_stars = self.free_agent_star_ratings[self.current_free_agent_index]
            salary = self.free_agent_salaries[self.current_free_agent_index]

            pyxel.rect(20, 30, 120, 80, 12)  # Player card background
            pyxel.text(30, 35, f"Player Name: {player['fullname']}", 7)
            pyxel.text(30, 45, f"Position: {player['position']}", 7)
            pyxel.text(30, 55, f"Batting: {batting_average} ({ba_stars} stars)" if ba_stars is not None else f"Batting: {batting_average}", 7)
            pyxel.text(30, 65, f"Pitching: {player['era']} ({era_stars} stars)" if era_stars is not None else f"Pitching: {player['era']}", 7)
            pyxel.text(30, 75, f"Fielding: {fielding_average} ({fa_stars} stars)" if fa_stars is not None else f"Fielding: {fielding_average}", 7)
            pyxel.text(30, 85, f"Salary: ${salary:,}", 7)
            pyxel.text(20, 100, "Too Buy Free Agent Click Enter", 1)
        else:
            pyxel.text(30, 30, "No more Free Agents Avalible", 7)

    def load_player_data(self, team_id):
        filename = f'team_{team_id}_roster.pkl'
        with open(filename, 'rb') as f:
            data = pickle.load(f)
            
        # Check format immediately after loading
        if not all(k in data for k in ['players', 'BA', 'Fld', 'star_ratings', 'salaries']):
            raise ValueError("Loaded player data is not in the expected format.")

        self.original_players = data['players']
        self.BA = data['BA']
        self.Fld = data['Fld']
        self.star_ratings = data['star_ratings']
        self.salaries = data['salaries']

    def update(self):
        # Navigate through the free agents with left and right arrow keys
        if pyxel.btnp(pyxel.KEY_RIGHT):
            self.current_free_agent_index = (self.current_free_agent_index + 1) % len(self.free_agents)
        elif pyxel.btnp(pyxel.KEY_LEFT):
            self.current_free_agent_index = (self.current_free_agent_index - 1) % len(self.free_agents)

        # Check if the user presses the "buy" button (e.g., RETURN key)
        if pyxel.btnp(pyxel.KEY_RETURN):
            # Get the current free agent's details
            agent = self.free_agent_players[self.current_free_agent_index]
            salary = self.free_agent_salaries[self.current_free_agent_index]

            # Check if the user has enough budget to buy this player
            if salary <= self.budget:
                position = agent['position']
                
                # Attempt to find a player with the same position
                try:
                    position_index = next((i for i, player in enumerate(self.original_players) if player['position'] == position), None)
                except TypeError:
                    print("Error: `selected_players` is not a list of dictionaries.")
                    return  # Exit the function if there's an error
                
                if position_index is not None:  # Replace if a player is already in this position
                    self.original_players[position_index] = {
                        'fullname': self.free_agent_players[self.current_free_agent_index]['fullname'],
                        'era': self.free_agent_players[self.current_free_agent_index].get('era'),  # This will be None if 'era' is not present
                        'position': self.free_agent_players[self.current_free_agent_index]['position']
                    }

                    self.BA[position_index] = self.free_agent_BA[self.current_free_agent_index]
                    self.Fld[position_index] = self.free_agent_Fld[self.current_free_agent_index]
                    self.star_ratings[position_index] = self.free_agent_star_ratings[self.current_free_agent_index]
                    self.salaries[position_index] = self.free_agent_salaries[self.current_free_agent_index]  # Using the salary calculated for the free agent
                
                # Deduct agent's salary from the remaining budget
                self.budget -= salary

                # Mark the free agent as bought by removing them from the list or setting a flag
                self.free_agent_players.pop(self.current_free_agent_index)
                self.free_agent_BA.pop(self.current_free_agent_index)
                self.free_agent_Fld.pop(self.current_free_agent_index)
                self.free_agent_star_ratings.pop(self.current_free_agent_index)
                self.free_agent_salaries.pop(self.current_free_agent_index)

                # Reset the current index if it exceeds the length of the list
                if self.current_free_agent_index >= len(self.free_agent_players):
                    self.current_free_agent_index = 0

                self.save_updated_roster()
                self.save_account()

            else:
                print("Not enough budget to buy this player.")
    
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
        account_data['budget'] = self.budget

        # Write updated data back to the file
        with open(filename, 'wb') as f:
            pickle.dump(account_data, f)
        print(f"Account saved to {filename}")

    def save_updated_roster(self):
        updated_data = {
            'players': self.original_players,
            'BA': self.BA,
            'Fld': self.Fld,
            'star_ratings': self.star_ratings,
            'salaries': self.salaries
        }

        filename = f"team_{self.team_id}_roster.pkl"
        with open(filename, "wb") as f:
            pickle.dump(updated_data, f)
        print("Roster updated and saved to file.")


class RosterScreen:
    def __init__(self, coachFirstName, coachLastName, selected_team, teamID, difficulty):
        self.coachFirstName = coachFirstName
        self.coachLastName = coachLastName

        self.selected_team = selected_team
        self.teamID = teamID

        self.difficulty_level = difficulty

        self.players = []
        self.BA = []
        self.Fld = []
        self.star_ratings = []
        self.salaries = []
        self.roster = self.get_or_load_roster()

        self.salary_cap = self.generate_salary_cap()

        self.save_account()

        self.current_player_index = 0

        self.total_salary = sum(self.salaries)
        self.selected_players = []
        self.position_limits = {'P': 2, 'C': 1, '1B': 1, '2B': 1, '3B': 1, 'SS': 1, 'LF': 1, 'CF': 1, 'RF': 1, 'DH': 1}

        self.scroll_offset = 0

        self.temp_dh_index = None
        self.original_positions = {i: player['position'] for i, player in enumerate(self.players)}

    def generate_salary_cap(self):
        # Set budget based on difficulty level
        mean, std_dev = 139, 45
        if self.difficulty_level == 'Easy':
            return min(mean + std_dev, np.random.normal(mean + std_dev, std_dev * 0.2))
        elif self.difficulty_level == 'Medium':
            return np.random.normal(mean, std_dev * 0.5)
        elif self.difficulty_level == 'Hard':
            return max(mean - std_dev, np.random.normal(mean - std_dev, std_dev * 0.2))
        else:
            return mean  # Default to mean if no valid difficulty level is provided
        
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
        account_data['salary_cap'] = round(self.salary_cap, 3)

        # Write updated data back to the file
        with open(filename, 'wb') as f:
            pickle.dump(account_data, f)
        print(f"Account saved to {filename}")

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
    
    def distribute_salaries(self):
        # Ensure self.salaries has an entry for each player
        self.salaries = [0] * len(self.star_ratings)

        # Distribute total budget based on star ratings
        total_stars = sum((ba or 0) + (fa or 0) + (era or 0) for ba, fa, era in self.star_ratings)
        
        for idx, (ba_stars, fa_stars, era_stars) in enumerate(self.star_ratings):
            player_stars = (ba_stars or 0) + (fa_stars or 0) + (era_stars or 0)
            if total_stars > 0:
                self.salaries[idx] = round(self.salary_cap * (player_stars / total_stars), 2)
            else:
                self.salaries[idx] = 0

    def finalize_team_selection(self, selected_player_indices):
        # Filter out only the selected players, star ratings, and stats
        self.players = [self.players[i] for i in selected_player_indices]
        self.BA = [self.BA[i] for i in selected_player_indices]
        self.Fld = [self.Fld[i] for i in selected_player_indices]
        self.star_ratings = [self.star_ratings[i] for i in selected_player_indices]

        # Distribute salaries based on selected players
        self.distribute_salaries()
        
        # Save selected team to a pickle file
        filename = f"team_{self.teamID}_roster.pkl"
        with open(filename, "wb") as f:
            data = {
                'players': self.players,
                'BA': self.BA,
                'Fld': self.Fld,
                'star_ratings': self.star_ratings,
                'salaries': self.salaries
            }
            pickle.dump(data, f)
        print("Saved selected roster with salaries to file")

    def confirm_selection(self):
        # Verify the selection criteria (one per position, two pitchers, 11 players)
        if len(self.selected_players) == 11:
            selected_indices = [self.players.index(player) for player in self.selected_players]
            self.finalize_team_selection(selected_indices)
        else:
            print("Selection incomplete or invalid. Please select 11 players.")

    def draw_salary_bar(self):
        filled_width = min(120, int((self.total_salary / self.salary_cap) * 120))
        pyxel.rectb(20, 110, 120, 10, 1)
        pyxel.rect(21, 111, filled_width, 8, 3)

    def update(self):
        # Handle scrolling
        if pyxel.btnp(pyxel.KEY_DOWN):
            # Move hovered index down and scroll if needed
            if self.current_player_index < len(self.players) - 1:
                self.current_player_index += 1
                if self.current_player_index >= self.scroll_offset + 12:
                    self.scroll_offset += 1

        elif pyxel.btnp(pyxel.KEY_UP):
            # Move hovered index up and scroll if needed
            if self.current_player_index > 0:
                self.current_player_index -= 1
                if self.current_player_index < self.scroll_offset:
                    self.scroll_offset -= 1

        elif pyxel.btnp(pyxel.KEY_RIGHT):
            # Check if there's no DH yet and current player isn't a pitcher
            if self.temp_dh_index is None and self.players[self.current_player_index]['position'] != 'P':
                self.temp_dh_index = self.current_player_index  # Mark current player as DH temporarily
                self.original_positions[self.current_player_index] = self.players[self.current_player_index]['position']
                self.players[self.current_player_index]['position'] = 'DH'
        
        # Left arrow: Revert the DH position if it's the current player
        elif pyxel.btnp(pyxel.KEY_LEFT):
            if self.temp_dh_index == self.current_player_index:
                # Revert the DH player to their original position
                original_position = self.original_positions.get(self.current_player_index)
                if original_position:
                    self.players[self.current_player_index]['position'] = original_position
                self.temp_dh_index = None

        elif pyxel.btnp(pyxel.KEY_S):
            # Extract player and their position
            player = self.players[self.current_player_index]
            position = player['position']

            # Proceed only if the total number of selected players is below the limit
            if len(self.selected_players) < 11:
                # Check if DH is missing and this player can be a DH
                dh_selected = any(p['position'] == 'DH' for p in self.selected_players)
                print(self.BA[self.current_player_index], self.Fld[self.current_player_index])
                
                if position in self.position_limits:
                    # Check if this position has not reached its limit
                    if sum(1 for p in self.selected_players if p['position'] == position) < self.position_limits[position]:
                        self.selected_players.append(player)
                elif position not in [p['position'] for p in self.selected_players] or (not dh_selected and position != 'P'):
                    # Allow the selected player to be DH if no DH is selected
                    self.selected_players.append(player)
                    
                    # Reset temporary DH if player is selected
                    if self.temp_dh_index == self.current_player_index:
                        self.temp_dh_index = None

        elif pyxel.btnp(pyxel.KEY_BACKSPACE):
            player = self.players[self.current_player_index]
            if player in self.selected_players:
                self.selected_players.remove(player)

        if len(self.selected_players) == 11:
            if pyxel.btnp(pyxel.KEY_RETURN):
                print(self.BA[self.current_player_index], self.Fld[self.current_player_index])
                self.confirm_selection()

    def draw(self):
            pyxel.cls(12)
            pyxel.text(65, 10, "ROSTER SELECTION", 1)

            visible_count = 12  # Number of players that can fit on screen
            start_index = self.scroll_offset
            end_index = min(start_index + visible_count, len(self.players))

            # Draw the list of available players, highlighting selected and hovered ones
            for i, player in enumerate(self.players[start_index:end_index], start=start_index):
                is_selected = player in self.selected_players
                is_hovered = i == self.current_player_index
                color = 3 if is_selected else (8 if is_hovered else 7)  # Change color if hovered
                
                pyxel.text(5, 35 + (i - start_index) * 7, f"{player['fullname']} - {player['position']}", color)

            # Display selected players separately
            pyxel.text(85, 28, "Selected Players:", 1)
            for i, player in enumerate(self.selected_players):
                pyxel.text(85, 35 + i * 7, f"{player['fullname']} - {player['position']}", 3)

    def get_or_load_roster(self):
        teamID = self.teamID
        filename = f"non_user_team_{teamID}_roster.pkl"
        if os.path.exists(filename):
            with open(filename,"rb") as f:
                data = pickle.load(f)
            print("Loaded roster from file")
            self.players = data['players']
            self.BA = data['BA']
            self.Fld = data['Fld']
            self.star_ratings = data['star_ratings']
            return self.players, self.BA, self.Fld, self.star_ratings
        else:
            roster = mlb.get_team_roster(teamID, roster_type=['fullRoster'], season=['2024'])

            for player_info in roster:
                player_id = mlb.get_people_id(player_info.fullname)[0]
                position = player_info.primaryposition.abbreviation

                batter_avg = 0.250
                try: 
                    batter_stats = mlb.get_player_stats(player_id, stats=['season'], groups=['hitting'], season=2024)
                    season_stats = batter_stats['hitting']['season']
                    for split in season_stats.splits:
                        batter_avg = float('0' + split.stat.avg) if split.stat.avg != '0.0' else 0.250
                        break
                except KeyError:
                    pass
                except TypeError:
                    pass
                
                era = None
                try:
                    pitcher_stats = mlb.get_player_stats(player_id, stats=['season'], groups=['pitching'], season=2024)
                    season_stats = pitcher_stats['pitching']['season']
                    for split in season_stats.splits:
                        era = float(split.stat.era) if split.stat.era != '0.0' else 3.0
                        break
                except KeyError:
                    pass
                except TypeError:
                    pass

                fielding_avg = 0.950
                try:
                    fielding_stats = mlb.get_player_stats(player_id, stats=['season'], groups=['fielding'], season=2024)
                    season_stats = fielding_stats['fielding']['season']
                    for split in season_stats.splits:
                        fielding_avg = float('0' + split.stat.fielding) if split.stat.fielding != '1.000' else 1.0
                        break
                except KeyError:
                    pass
                except TypeError:
                    pass
                
                print(f"Player: {player_info.fullname}, BA: {batter_avg}, ERA: {era}, FA: {fielding_avg}")

                self.players.append({'fullname': player_info.fullname, 'era': era, 'position': position})
                self.BA.append(batter_avg)
                self.Fld.append(fielding_avg)

                ba_stars, fa_stars, era_stars = self.calculate_star_rating(batter_avg, fielding_avg, era)
                self.star_ratings.append((ba_stars, fa_stars, era_stars))

            with open(filename, "wb") as f:
                data = {
                    'players': self.players,
                    'BA': self.BA,
                    'Fld': self.Fld,
                    'star_ratings': self.star_ratings,
                }
                pickle.dump(data, f)
                print("Saved roster to file")
                return self.players, self.BA, self.Fld, self.star_ratings
            
class ViewRoster:
    def __init__(self, selected_team, teamID, salary_cap, budget):
        self.selected_team = selected_team
        self.teamID = teamID
        self.salary_cap = salary_cap
        self.current_player_index = 0
        self.budget = budget
        
        self.filename = f"team_{self.teamID}_roster.pkl"

        with open(self.filename,"rb") as f:
            data = pickle.load(f)
        print("Loaded roster from file")
        self.players = data['players']
        self.BA = data['BA']
        self.Fld = data['Fld']
        self.star_ratings = data['star_ratings']
        self.salaries = data['salaries']
    
    def draw_salary_bar(self):
        filled_width = min(120, int((self.salary_cap / (self.salary_cap + self.budget)) * 120))
        pyxel.rectb(20, 110, 120, 10, 1)
        pyxel.rect(21, 111, filled_width, 8, 3)
    
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
            pyxel.text(30, 100, f"BUDGET ${self.salary_cap:.1f}M / ${round((self.salary_cap + self.budget), 3)}M", 7)
            pyxel.text(30, 35, f"Player Name: {player['fullname']}", 7)
            pyxel.text(30, 45, f"Position: {player['position']}", 7)
            pyxel.text(30, 55, f"Batting: {batting_average} ({ba_stars} stars)" if ba_stars is not None else f"Batting: {batting_average}", 7)
            pyxel.text(30, 65, f"Pitching: {player['era']} ({era_stars} stars)" if era_stars is not None else f"Pitching: {player['era']}", 7)
            pyxel.text(30, 75, f"Fielding: {fielding_average} ({fa_stars} stars)" if fa_stars is not None else f"Fielding: {fielding_average}", 7)
            pyxel.text(30, 85, f"Salary: ${salary:,}", 7)
        else:
            pyxel.text(30, 30, "No players in roster", 7)

    def update(self):
        if pyxel.btnp(pyxel.KEY_LEFT) and len(self.players) > 1:
            self.current_player_index = (self.current_player_index - 1) % len(self.players)
        elif pyxel.btnp(pyxel.KEY_RIGHT) and len(self.players) > 1:
            self.current_player_index = (self.current_player_index + 1) % len(self.players)

class Schedule:
    def __init__(self, mlb_teamsNL, mlb_teamsAL, selected_team, round_num):
        self.mlb_teamsNL = mlb_teamsNL
        self.mlb_teamsAL = mlb_teamsAL
        self.selected_team = selected_team
        self.week = round_num
        
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

        for home, away in self.schedule[self.week - 1]:
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

    def get_opponent_ID(self):
        return self.opponent_team_id

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
            if position == 'P' and self.pitcher == None:
                self.pitcher = player  # Assign the pitcher
            elif len(self.batting_order) < 9 and position != 'P':
                self.batting_order.append(player)
                filled_positions.add(position)
            else:
                self.bench.append(player)

        # Populate remaining players list
        self.remaining_players = [player for player in self.bench]  # Initialize remaining players from bench

        for player in self.opponent_players:
            position = player['position']
            if position == 'P':
                self.opponent_pitcher = player  # Assign the opponent pitcher
            elif len(self.opponent_batting_order) < 9:
                self.opponent_batting_order.append(player)
                filled_positions.add(position)
            else:
                self.opponent_bench.append(player)


    def swap_players(self):
        """Swap the currently selected player from the remaining players with a player in the batting order or the pitcher."""
        if self.remaining_players:
            selected_player = self.remaining_players[self.current_player_index]
            print(f"Swapping with: {selected_player['fullname']} (Position: {selected_player['position']})")  # Debug statement

            # Check if the selected player is the pitcher
            if selected_player['position'] == 'P':
                if self.pitcher != selected_player:  # Ensure we're not swapping the same player
                    print(f"Swapping pitcher: {self.pitcher['fullname']} with {selected_player['fullname']}")  # Debug statement
                    self.remaining_players.append(self.pitcher)  # Add current pitcher to the bench
                    self.pitcher = selected_player  # Set new pitcher
                    self.remaining_players.remove(selected_player)  # Remove from remaining players
                else:
                    print("Selected player is already the pitcher, no swap performed.")  # Debug statement
            else:
                # Find the position of the selected player in the batting order
                for i, player in enumerate(self.batting_order):
                    if player['position'] == selected_player['position']:
                        print(f"Swapping {player['fullname']} with {selected_player['fullname']}")  # Debug statement
                        self.batting_order[i] = selected_player  # Replace player in batting order
                        self.remaining_players.remove(selected_player)  # Remove from remaining players
                        self.bench.append(player)  # Add the replaced player to the bench
                        break
                else:
                    print("No player in batting order with the same position to swap.")  # Debug statement
 # Call draw to refresh the screen after a swap
        else:
            print("No remaining players to swap with.")  # Debug statement



    def update(self):
        if self.mode == 'cycle':
            if pyxel.btnp(pyxel.KEY_LEFT) and len(self.remaining_players) > 1:
                self.current_player_index = (self.current_player_index - 1) % len(self.remaining_players)
            elif pyxel.btnp(pyxel.KEY_RIGHT) and len(self.remaining_players) > 1:
                self.current_player_index = (self.current_player_index + 1) % len(self.remaining_players)
            elif pyxel.btnp(pyxel.KEY_DOWN):
                self.mode = 'play'
            elif pyxel.btnp(pyxel.KEY_S):
                self.swap_players()
                self.draw() 
            elif pyxel.btnp(pyxel.KEY_B):
                self.mode = 'Batting Order'
            elif pyxel.btnp(pyxel.KEY_D):
                self.mode = 'Other Team'
        elif self.mode == 'play':
            if pyxel.btnp(pyxel.KEY_UP):
                self.mode = 'cycle'
        elif self.mode == 'Batting Order':
            if pyxel.btnp(pyxel.KEY_O):  # Example key to change batting order
                self.current_player_index = 0
                self.mode = 'Change Batting Order'
            if pyxel.btnp(pyxel.KEY_B):
                self.mode = 'cycle'

        elif self.mode == 'Change Batting Order':
            if pyxel.btnp(pyxel.KEY_UP):
                # Move the selected player up in the order
                if self.current_player_index > 0:
                    self.batting_order[self.current_player_index], self.batting_order[self.current_player_index - 1] = \
                        self.batting_order[self.current_player_index - 1], self.batting_order[self.current_player_index]
                    self.current_player_index -= 1
            elif pyxel.btnp(pyxel.KEY_DOWN):
                # Move the selected player down in the order
                if self.current_player_index < len(self.batting_order) - 1:
                    self.batting_order[self.current_player_index], self.batting_order[self.current_player_index + 1] = \
                        self.batting_order[self.current_player_index + 1], self.batting_order[self.current_player_index]
                    self.current_player_index += 1
            elif pyxel.btnp(pyxel.KEY_B):  # Press B to go back to cycle mode
                self.current_player_index = 0
                self.mode = 'Batting Order'

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

        if self.mode == 'Change Batting Order':
            y = 20
            pyxel.text(10, 10, 'Change Batting Order', 7)
            for i, player in enumerate(self.batting_order):
                text = f"{i + 1}. {player['fullname']} - {player['position']}"
                if i == self.current_player_index:
                    pyxel.text(20, y, text, 8)  # Highlight selected player
                else:
                    pyxel.text(20, y, text, 0)
                y += 10
        
        if self.mode =='play':
            x, y = 40, 50
            pyxel.text(x, y, f"{self.selected_team} \n \n         vs.         \n \n{self.opponent_team}", 0)
            pyxel.text(5, 110, "> Play", 7)

        # Display the players from the selected team
        if self.mode == 'cycle':
                for player in self.batting_order:
                    position = player['position']
                    if position in self.position_coords and position not in filled_positions:
                        x, y = self.position_coords[position]
                        text = f"{player['fullname']} \n{position}"
                        pyxel.text(x, y, text, 0)
                        filled_positions.add(position)

                # Display the pitcher separately
                if self.pitcher:
                    x, y = self.position_coords['P']
                    text = f"{self.pitcher['fullname']} \nP"
                    pyxel.text(x, y, text, 0)

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
    def __init__(self, deck=None, batting_avarage=0.250 ,star_rating=4):
        self.seed = int(time.time() * 1000)
        self.star_rating = star_rating
        self.batting_avarage = batting_avarage
        self.deck = deck if deck is not None else self.create_weighted_deck()

    def create_weighted_deck(self):
        print("created new deck with batting avarge", self.batting_avarage)
        deck = []
        
        # Adjust weights based on player stats
        hit_weight = self.batting_avarage * 10
        out_weight = (1 - self.batting_avarage) * 10

        # Hit cards
        deck.extend(["single"] * int(hit_weight * 2))
        deck.extend(["double"] * int(hit_weight * 1.5))
        deck.extend(["triple"] * int(hit_weight * 0.5))
        deck.extend(["home_run"] * int(hit_weight * 0.2))

        # Out cards
        deck.extend(["strike"] * int(out_weight * 5))
        deck.extend(["fly_out"] * int(out_weight * 2))
        deck.extend(["ground_out"] * int(out_weight * 2))

        # Other cards
        deck.extend(["ball"] * 10)
        deck.extend(["foul_ball"] * 2)
        deck.extend(["hit_by_pitcher"] * 1)
        """
        deck.extend(["stolen_base"] * 1)
        """

        # Modify for star rating
        if self.star_rating >= 4:
            deck.extend(["home_run"] * 2)
            deck.extend(["double"] * 3)

        self.deck = deck
        return self.deck

    def custom_random_number(self, min_value, max_value):
        self.seed = (self.seed * 1103515245 + 12345) & 0x7FFFFFFF
        random_value = self.seed % (max_value - min_value + 1)
        return min_value + random_value

    def riffle_shuffle(self):
        if len(self.deck) <= 1:
            return self.deck

        split_point = self.custom_random_number(1, len(self.deck) - 1)
        left_half = self.deck[:split_point]
        right_half = self.deck[split_point:]

        shuffled_deck = []
        while left_half or right_half:
            if left_half and right_half:
                if self.custom_random_number(0, 1) == 0:
                    shuffled_deck.append(left_half.pop(0))
                else:
                    shuffled_deck.append(right_half.pop(0))
            elif left_half:
                shuffled_deck.append(left_half.pop(0))
            elif right_half:
                shuffled_deck.append(right_half.pop(0))

        self.deck = shuffled_deck
        return self.deck

    def overhand_shuffle(self):
        shuffled_deck = []
        while self.deck:
            num_cards = self.custom_random_number(1, min(5, len(self.deck)))
            shuffled_deck = self.deck[:num_cards] + shuffled_deck
            self.deck = self.deck[num_cards:]
        self.deck = shuffled_deck
        return self.deck

    def smoosh_shuffle(self):
        for i in range(len(self.deck)):
            j = self.custom_random_number(0, len(self.deck) - 1)
            self.deck[i], self.deck[j] = self.deck[j], self.deck[i]
        return self.deck

    def mega_shuffle(self):
        shuffle_funcs = [self.riffle_shuffle, self.overhand_shuffle, self.smoosh_shuffle]
        for _ in range(3):
            for shuffle in sorted(shuffle_funcs, key=lambda _: self.custom_random_number(0, 2)):
                shuffle()
        return self.deck

    def shuffle_and_get_deck(self):
        return self.mega_shuffle()

class Game:
    def __init__(self, batting_order, opponent_batting_order, bench, teamID, opponent_team_id):
        # Initialize game state variables
        pyxel.images[0].load(0, 0, "istockphoto-667849798-612x612 (3).jpg")
        pyxel.images[1].load(0, 0, "PXL_20241013_152554353.MP~3 (2).jpg")
        self.power_bar = SlidingBar(105, 5, 50, 10, direction='horizontal')
        self.angle_bar = SlidingBar(145, 20, 10, 50, direction='vertical')
        self.batting_order = batting_order
        self.opponent_batting_order = opponent_batting_order
        self.bench = bench
        self.current_card = None
        self.inning = 1
        self.outs = 0
        self.home_score = 0
        self.away_score = 0

        self.current_batter_index = 1
        self.opponent_current_batter_index = 1

        self.field = [None, None, None]  # Represents bases (first, second, third)
        self.difficulty = 'easy'
        self.batter_turn_started = False  # Flag to indicate if the batter's turn has started
        self.strike = 0
        self.ball = 0

        self.teamID = teamID
        self.opponent_team_id = opponent_team_id
        
        self.players = []
        self.BA = []
        self.Fld = []
        self.star_ratings = []
        self.salaries = []
        self.roster = self.get_or_load_roster()

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

    def get_or_load_roster(self):
        if self.inning % 2 == 1:
            teamID = self.teamID
        else:
            teamID = self.opponent_team_id
        filename = f"team_{teamID}_roster.pkl"
        if os.path.exists(filename):
            with open(filename, "rb") as f:
                data = pickle.load(f)
            print("Loaded roster from file")
            self.players = data['players']
            self.BA = data['BA']  # Batting averages
            self.Fld = data['Fld']
            self.star_ratings = data['star_ratings']
            self.salaries = data['salaries']
            return self.players, self.BA, self.Fld, self.star_ratings, self.salaries

    def get_current_batter_stats(self):
        # Get the current batter's name
        current_batter = self.batting_order[self.current_batter_index - 1]['fullname'] if self.inning % 2 == 1 else self.opponent_batting_order[self.opponent_current_batter_index - 1]['fullname']
        self.get_or_load_roster()
        current_batter = current_batter.strip()

        # Find the index of the current batter in self.players
        index = None
        for idx, player in enumerate(self.players):
            player_name = player['fullname'].strip()
            if player_name.lower() == current_batter.lower():
                index = idx
                break

        if index is not None:
            # Use the index to find the batting average from self.BA
            batting_average = self.BA[index]
            return batting_average
        else:
            return None

    def new_deck(self):
        batting_average = self.get_current_batter_stats()
        if batting_average is None:
            batting_average = 0.250  # Default batting average if not found
        # Pass the retrieved batting average to DeckShuffler
        deck_shuffler = DeckShuffler(batting_avarage=batting_average)
        # Shuffle the deck and get the result
        self.deck = deck_shuffler.shuffle_and_get_deck()
        return self.deck

    def start_inning(self):
        # Start a new inning by resetting outs and incrementing the inning count
        self.strike = 0
        self.ball = 0
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
        elif self.current_card == "ground_out":
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
        if self.inning % 2 == 1:
            self.current_batter_index = (self.current_batter_index + 1) % 9
        else:
            self.opponent_current_batter_index = (self.opponent_current_batter_index + 1) % 9
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
        current_batter = self.batting_order[self.current_batter_index - 1]['fullname'] if self.inning % 2 == 1 else self.opponent_batting_order[self.opponent_current_batter_index - 1]['fullname']
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

        self.power_bar.draw()
        self.angle_bar.draw()
        
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
                pyxel.text(x, y, "RUNNER", 8)
        
        # Display the current card
        if self.current_card:
            pyxel.text(self.score_coords['card'][0], self.score_coords['card'][1], f"Card: {self.current_card}", 7)
            #pyxel.blt(0, 0, 1, 0, 0, 70, 103)  

        # Display the current batter
        if self.inning % 2 == 1:
            current_batter = str({self.batting_order[self.current_batter_index - 1]['fullname']})
            current_batter = current_batter.translate({ord("'"): None})
            current_batter = current_batter.translate({ord("{"): None})
            current_batter = current_batter.translate({ord("}"): None})
            if self.current_batter_index == 0:
                self.current_batter_index = 9
            pyxel.text(self.score_coords['batter'][0], self.score_coords['batter'][1], f"{self.current_batter_index}. Batter: {current_batter}", 7)
        else:
            current_batter = str({self.opponent_batting_order[self.opponent_current_batter_index - 1]['fullname']})
            current_batter = current_batter.translate({ord("'"): None})
            current_batter = current_batter.translate({ord("{"): None})
            current_batter = current_batter.translate({ord("}"): None})
            if self.opponent_current_batter_index == 0:
                self.opponent_current_batter_index = 9
            pyxel.text(self.score_coords['batter'][0], self.score_coords['batter'][1], f"{self.opponent_current_batter_index}. Batter: {current_batter}", 7)

class PostGameScreen:
    def __init__(self, home_score, away_score, batting_order, opponent_batting_order, wins, losses, coachFirstName, coachLastName, round_num, CoachingCredits, rehab_facilitys):
        self.rehab_facilitys = rehab_facilitys
        self.CoachingCredits = CoachingCredits
        self.round_num = round_num
        self.coachFirstName = coachFirstName
        self.coachLastName = coachLastName
        self.home_score = home_score
        self.away_score = away_score
        self.wins = wins
        self.losses = losses
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

        self.win_loss()

    def win_loss(self):
        if self.winner == "Home":
            self.wins += 1
            self.losses = self.losses
            self.round_num += 1
            if self.rehab_facilitys > 2:
                self.CoachingCredits += 6
                if self.rehab_facilitys > 4:
                    self.CoachingCredits += 1
                    if self.rehab_facilitys > 6:
                        self.CoachingCredits += 1
                        if self.rehab_facilitys > 8:
                            self.CoachingCredits += 1
                            if self.rehab_facilitys == 10:
                                self.CoachingCredits += 1
            else:
                self.CoachingCredits += 5
            self.save_account()
        elif self.winner == "Away":
            self.losses += 1
            self.wins = self.wins
            self.round_num += 1
            if self.rehab_facilitys > 2:
                self.CoachingCredits += 3
                if self.rehab_facilitys > 4:
                    self.CoachingCredits += 1
                    if self.rehab_facilitys > 6:
                        self.CoachingCredits += 1
                        if self.rehab_facilitys > 8:
                            self.CoachingCredits += 1
                            if self.rehab_facilitys == 10:
                                self.CoachingCredits += 1
            else:
                self.CoachingCredits += 2
            self.save_account()
        else:
            pass

    def draw(self):
        # Clear the screen for the post-game view
        pyxel.cls(5)

        # Display the final scores
        pyxel.text(self.score_coords['home'][0], self.score_coords['home'][1], f"Home: {self.home_score}", 7)
        pyxel.text(self.score_coords['away'][0], self.score_coords['away'][1], f"Away: {self.away_score}", 7)

        # Display the winner
        pyxel.text(self.score_coords['winner'][0], self.score_coords['winner'][1], f"Winner: {self.winner}", 7)

        # Optionally display some player statistics
        pyxel.text(10, 120, "Press R to restart or Q to quit", 7)

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
        account_data['wins'] = self.wins
        account_data['losses'] = self.losses
        account_data['round_num'] = self.round_num
        account_data['CoachingCredits'] = self.CoachingCredits

        # Write updated data back to the file
        with open(filename, 'wb') as f:
            pickle.dump(account_data, f)
        print(f"Account saved to {filename}")

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
        self.difficulty_screen = None
        self.budget_screen = None
        self.view_roster = None
        self.free_agents = None

    def update(self):
        if self.menu.state == GameState.MENU:
            self.menu.update()
        elif self.menu.state == GameState.TEAM_SELECTION:
            self.update_team_selection()
        elif self.menu.state == GameState.LOAD_GAME:
            self.update_load_game()
        elif self.menu.state == GameState.CREATE_ACCOUNT:
            self.update_create_account()

        elif self.menu.state == GameState.DIFFICULTY:
            self.update_difficulty_screen()

        elif self.menu.state == GameState.PLAYER_TEAM_SCREEN:
            self.update_player_team_screen()

            """
        elif self.menu.state == GameState.BUDGET:
            self.update_budget_screen()
            """

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
        elif self.menu.state == GameState.VIEW_ROSTER:
            self.update_view_roster()
        elif self.menu.state == GameState.FREE_AGENTS:
            self.update_free_agents()

    def draw(self):
        if self.menu.state == GameState.MENU:
            self.menu.draw()
        elif self.menu.state == GameState.TEAM_SELECTION:
            self.team_selection_screen.draw()
        elif self.menu.state == GameState.CREATE_ACCOUNT:
            self.create_account_screen.draw()

        elif self.menu.state == GameState.DIFFICULTY:
            self.difficulty_screen.draw()

        elif self.menu.state == GameState.LOAD_GAME:
            self.load_game.draw()
        elif self.menu.state == GameState.PLAYER_TEAM_SCREEN:
            self.player_team_screen.draw()

            """
        elif self.menu.state == GameState.BUDGET:
            self.budget_screen.draw()
            """

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
        elif self.menu.state == GameState.VIEW_ROSTER and self.view_roster:
            self.view_roster.draw()
        elif self.menu.state == GameState.FREE_AGENTS and self.free_agents:
            self.free_agents.draw()

    def update_team_selection(self):
        self.selected_team, self.teamID = self.team_selection_screen.update()
        if self.selected_team:
            self.create_account_screen = CreateAccountScreen(self.teamID, self.selected_team)
            self.menu.state = GameState.CREATE_ACCOUNT

    def update_load_game(self):
        self.load_game.update()
        if pyxel.btnp(pyxel.KEY_RETURN):
            loaded_game = self.load_game.load_selected_game()
            if loaded_game is None:
                return
            self.teamID, self.selected_team, self.CoachingCredits, self.stadium, self.training_facilitys, self.rehab_facilitys, self.coachFirstName, self.coachLastName, self.round_num, self.wins, self.losses, self.difficulty, self.revenue, self.salary_cap, self.budget = loaded_game

            schedule_ = Schedule(mlb_teamsNL, mlb_teamsAL, self.selected_team, self.round_num)
            self.schedule = schedule_.get_schedule()
            self.player_team_screen = PlayerTeamScreen(self.selected_team, self.teamID, self.schedule, self.CoachingCredits, self.round_num, self.coachFirstName, self.coachLastName, self.wins, self.losses, self.difficulty, self.revenue, self.salary_cap, self.budget)
            self.menu.state = GameState.PLAYER_TEAM_SCREEN

    def update_create_account(self):
        self.create_account_screen.update()
        if self.create_account_screen.createdAccount:
            # Check if player_team_screen is initialized

            self.CoachingCredits = self.create_account_screen.CoachingCredits
            self.round_num = self.create_account_screen.round_num
            self.coachFirstName = self.create_account_screen.coachFirstName
            self.coachLastName = self.create_account_screen.coachLastName
            self.wins = self.create_account_screen.wins
            self.losses = self.create_account_screen.losses

            self.difficulty_screen = Difficulty(self.coachFirstName, self.coachLastName)
            self.menu.state = GameState.DIFFICULTY

    def update_difficulty_screen(self):
        self.difficulty_screen.update()
        if pyxel.btnp(pyxel.KEY_RETURN):
            selected_option = self.difficulty_screen.optionsDifficulty[self.difficulty_screen.selected_difficulty]

            if selected_option == "Easy":
                self.difficulty = "Easy"
            elif selected_option == "Medium":
                self.difficulty = "Medium"
            elif selected_option == "Hard":
                self.difficulty = "Hard"

            self.revenue = self.difficulty_screen.revenue
            
            self.coachFirstName, self.coachLastName = self.create_account_screen.coachFirstName, self.create_account_screen.coachLastName
            self.teamID, self.selected_team = self.create_account_screen.teamID, self.create_account_screen.selected_team
            self.roster_screen = RosterScreen(self.coachFirstName, self.coachLastName, self.selected_team, self.teamID, self.difficulty)
            self.menu.state = GameState.ROSTER_SCREEN

    def update_player_team_screen(self):
        self.player_team_screen.update()

        if pyxel.btnp(pyxel.KEY_RETURN):
            selected_option = self.player_team_screen.optionsPlayer[self.player_team_screen.selectedPlayer]
            
            if selected_option == "Front Office":
                self.teamID, self.selected_team, self.CoachingCredits, self.stadium, self.training_facilitys, self.rehab_facilitys, self.coachFirstName, self.coachLastName, self.round_num, self.wins, self.losses, self.difficulty, self.revenue, self.salary_cap, self.budget = self.load_game.load_selected_game()

                self.front_office = FrontOffice(self.CoachingCredits, self.stadium, self.training_facilitys, self.rehab_facilitys, self.coachFirstName, self.coachLastName)
                self.menu.state = GameState.FRONT_OFFICE

            elif selected_option == "Roster":
                self.teamID, self.selected_team, self.CoachingCredits, self.stadium, self.training_facilitys, self.rehab_facilitys, self.coachFirstName, self.coachLastName, self.round_num, self.wins, self.losses, self.difficulty, self.revenue, self.salary_cap, self.budget = self.load_game.load_selected_game()

                self.view_roster = ViewRoster(self.selected_team, self.teamID, self.salary_cap, self.budget)
                self.menu.state = GameState.VIEW_ROSTER

            elif selected_option == "Play Game":
                self.teamID, self.selected_team, self.CoachingCredits, self.stadium, self.training_facilitys, self.rehab_facilitys, self.coachFirstName, self.coachLastName, self.round_num, self.wins, self.losses, self.difficulty, self.revenue, self.salary_cap, self.budget = self.load_game.load_selected_game()

                self.play_game_screen = PlayGameScreen(
                    mlb_teamsNL,        # First argument
                    mlb_teamsAL,        # Second argument
                    self.selected_team,  # Third argument
                    self.teamID,        # Fourth argument (team_id)
                    self.round_num       # Fifth argument (week)
                )

                self.menu.state = GameState.PLAY_GAME_SCREEN

    def update_view_roster(self):
        if self.view_roster:
            self.view_roster.update()
        if pyxel.btnp(pyxel.KEY_BACKSPACE):
            self.menu.state = GameState.PLAYER_TEAM_SCREEN

    def update_roster_screen(self):
        if self.roster_screen:
            self.roster_screen.update()
        if len(self.roster_screen.selected_players) == 11:
            if pyxel.btnp(pyxel.KEY_RETURN):
                self.teamID, self.selected_team = self.create_account_screen.teamID, self.create_account_screen.selected_team

                print(self.selected_team, self.teamID)

                if self.player_team_screen is not None:
                    current_round = self.player_team_screen.current_round
                else:
                    current_round = 0  # Default to 0 or some appropriate fallback

                self.salary_cap = self.roster_screen.salary_cap
                self.revenue = self.difficulty_screen.revenue

                budget = Budget(self.coachFirstName, self.coachLastName, self.revenue, self.salary_cap)
                self.budget = budget.AvailableBudget()

                schedule_ = Schedule(mlb_teamsNL, mlb_teamsAL, self.selected_team, current_round)
                self.schedule = schedule_.get_schedule()

                self.player_team_screen = PlayerTeamScreen(self.selected_team, self.teamID, self.schedule, self.CoachingCredits, current_round, self.coachFirstName, self.coachLastName, self.wins, self.losses, self.difficulty, self.revenue, self.salary_cap, self.budget)
                self.menu.state = GameState.PLAYER_TEAM_SCREEN
                

    def update_front_office(self):
        if self.front_office:
            self.front_office.update()
            if pyxel.btnp(pyxel.KEY_RETURN):
                if self.front_office.axis == "vertical":
                    selected_option = self.front_office.Verticaloptions[self.front_office.selectedVerticalOption]
                else:
                    selected_option = self.front_office.Horizontaloptions[self.front_office.selectedHorizontalOption]
                
                if selected_option == "Free \n Agents":
                    self.teamID, self.selected_team, self.CoachingCredits, self.stadium, self.training_facilitys, self.rehab_facilitys, self.coachFirstName, self.coachLastName, self.round_num, self.wins, self.losses, self.difficulty, self.revenue, self.salary_cap, self.budget = self.load_game.load_selected_game()

                    self.free_agents = FreeAgents(self.difficulty, self.salary_cap, self.budget, self.teamID, self.coachFirstName, self.coachLastName, self.training_facilitys)
                    self.menu.state = GameState.FREE_AGENTS

                if selected_option == "Increase \n Salary Cap":
                    self.teamID, self.selected_team, self.CoachingCredits, self.stadium, self.training_facilitys, self.rehab_facilitys, self.coachFirstName, self.coachLastName, self.round_num, self.wins, self.losses, self.difficulty, self.revenue, self.salary_cap, self.budget = self.load_game.load_selected_game()
                    if self.CoachingCredits >= 10:
                        self.CoachingCredits -= 10
                        self.budget += 10

                        filename = f"{self.coachFirstName}_{self.coachLastName}_account.pkl"
            
                        # Check if file exists and load existing data
                        if os.path.exists(filename):
                            with open(filename, 'rb') as f:
                                account_data = pickle.load(f)
                        else:
                            # If no file exists, create a new dictionary
                            account_data = {}

                        # Update the relevant fields in the loaded account data
                        account_data['budget'] = self.budget
                        account_data['CoachingCredits'] = self.CoachingCredits

                        # Write updated data back to the file
                        with open(filename, 'wb') as f:
                            pickle.dump(account_data, f)
                        print(f"Account saved to {filename}")

                        self.teamID, self.selected_team, self.CoachingCredits, self.stadium, self.training_facilitys, self.rehab_facilitys, self.coachFirstName, self.coachLastName, self.round_num, self.wins, self.losses, self.difficulty, self.revenue, self.salary_cap, self.budget = self.load_game.load_selected_game()

                        self.front_office = FrontOffice(self.CoachingCredits, self.stadium, self.training_facilitys, self.rehab_facilitys, self.coachFirstName, self.coachLastName)
                        self.menu.state = GameState.FRONT_OFFICE
                
                if selected_option == "Upgrade Stadium":
                    self.teamID, self.selected_team, self.CoachingCredits, self.stadium, self.training_facilitys, self.rehab_facilitys, self.coachFirstName, self.coachLastName, self.round_num, self.wins, self.losses, self.difficulty, self.revenue, self.salary_cap, self.budget = self.load_game.load_selected_game()
                    if self.CoachingCredits >= 1:
                        self.budget += 0.5

                        filename = f"{self.coachFirstName}_{self.coachLastName}_account.pkl"

                        # Check if file exists and load existing data
                        if os.path.exists(filename):
                            with open(filename, 'rb') as f:
                                account_data = pickle.load(f)
                        else:
                            # If no file exists, create a new dictionary
                            account_data = {}

                        # Update the relevant fields in the loaded account data
                        account_data['budget'] = self.budget
                        account_data['CoachingCredits'] = self.CoachingCredits

                        # Write updated data back to the file
                        with open(filename, 'wb') as f:
                            pickle.dump(account_data, f)
                        print(f"Account saved to {filename}")

                        self.teamID, self.selected_team, self.CoachingCredits, self.stadium, self.training_facilitys, self.rehab_facilitys, self.coachFirstName, self.coachLastName, self.round_num, self.wins, self.losses, self.difficulty, self.revenue, self.salary_cap, self.budget = self.load_game.load_selected_game()

                        self.front_office = FrontOffice(self.CoachingCredits, self.stadium, self.training_facilitys, self.rehab_facilitys, self.coachFirstName, self.coachLastName)
                        self.menu.state = GameState.FRONT_OFFICE
            
            if pyxel.btnp(pyxel.KEY_BACKSPACE):
                self.teamID, self.selected_team, self.CoachingCredits, self.stadium, self.training_facilitys, self.rehab_facilitys, self.coachFirstName, self.coachLastName, self.round_num, self.wins, self.losses, self.difficulty, self.revenue, self.salary_cap, self.budget = self.load_game.load_selected_game()
                self.player_team_screen = PlayerTeamScreen(self.selected_team, self.teamID, self.schedule, self.CoachingCredits, self.round_num, self.coachFirstName, self.coachLastName, self.wins, self.losses, self.difficulty, self.revenue, self.salary_cap, self.budget)
                self.menu.state = GameState.PLAYER_TEAM_SCREEN
            
    def update_free_agents(self):
        if self.free_agents:
            self.free_agents.update()
        if pyxel.btnp(pyxel.KEY_BACKSPACE):
            self.menu.state = GameState.FRONT_OFFICE
 
    def update_play_game_screen(self):
        if self.play_game_screen:
            self.play_game_screen.update()
        if pyxel.btnp(pyxel.KEY_BACKSPACE):
            self.menu.state = GameState.PLAYER_TEAM_SCREEN
        if pyxel.btnp(pyxel.KEY_RETURN):
            self.teamID, self.selected_team, self.CoachingCredits, self.stadium, self.training_facilitys, self.rehab_facilitys, self.coachFirstName, self.coachLastName, self.round_num, self.wins, self.losses, self.difficulty, self.revenue, self.salary_cap, self.budget = self.load_game.load_selected_game()
            self.batting_order, self.opponent_batting_order, self.bench = self.play_game_screen.batting_order, self.play_game_screen.opponent_batting_order, self.play_game_screen.bench
            self.opponent_team_id = self.play_game_screen.opponent_team_id
            self.game = Game(self.batting_order, self.opponent_batting_order, self.bench, self.teamID, self.opponent_team_id)
            self.menu.state = GameState.GAME
            
    def update_game(self):
        self.game.power_bar.update()
        self.game.angle_bar.update()
        if pyxel.btnp(pyxel.KEY_SPACE):
            self.game.power_bar.update()
            self.game.angle_bar.update()
            if not self.game.batter_turn_started or (self.game.strike < 3 and self.game.ball < 4):
                self.game.batter_turn() 
            if self.game.inning > 9 and self.game.home_score != self.game.away_score:
                self.teamID, self.selected_team, self.CoachingCredits, self.stadium, self.training_facilitys, self.rehab_facilitys, self.coachFirstName, self.coachLastName, self.round_num, self.wins, self.losses, self.difficulty, self.revenue, self.salary_cap, self.budget = self.load_game.load_selected_game()
                self.batting_order, self.opponent_batting_order, self.bench = self.play_game_screen.batting_order, self.play_game_screen.opponent_batting_order, self.play_game_screen.bench
                self.post_game_screen = PostGameScreen(self.game.home_score, self.game.away_score, self.batting_order, self.opponent_batting_order, self.wins, self.losses, self.coachFirstName, self.coachLastName, self.round_num, self.CoachingCredits, self.rehab_facilitys)
                self.menu.state = GameState.POST_GAME
    
    def update_post_game(self):
        if pyxel.btnp(pyxel.KEY_RETURN):
            self.teamID, self.selected_team, self.CoachingCredits, self.stadium, self.training_facilitys, self.rehab_facilitys, self.coachFirstName, self.coachLastName, self.round_num, self.wins, self.losses, self.difficulty, self.revenue, self.salary_cap, self.budget = self.load_game.load_selected_game()
            self.player_team_screen = PlayerTeamScreen(self.selected_team, self.teamID, self.schedule, self.CoachingCredits, self.round_num, self.coachFirstName, self.coachLastName, self.wins, self.losses, self.difficulty, self.revenue, self.salary_cap, self.budget)
            self.menu.state = GameState.PLAYER_TEAM_SCREEN
        if pyxel.btnp(pyxel.KEY_Q):
            pyxel.quit()

game_state_manager = GameStateManager()

def update():
    game_state_manager.update()

def draw():
    game_state_manager.draw()

pyxel.run(update, draw)