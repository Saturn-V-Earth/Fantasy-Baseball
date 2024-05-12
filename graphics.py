import pyxel
import sqlite3

class GameState:
    MENU = 0
    TEAM_SELECTION = 1
    PLAYER_TEAM_SCREEN = 2
    ROSTER_SCREEN = 3

class Menu:
    def __init__(self):
        self.state = GameState.MENU
        pyxel.init(160, 120, title="Fantasy Baseball")
        self.options = ["New Game", "Load Game", "Quit"]
        self.selected = 0

    def update(self):
        if pyxel.btnp(pyxel.KEY_DOWN):
            self.selected = (self.selected + 1) % len(self.options)
        if pyxel.btnp(pyxel.KEY_UP):
            self.selected = (self.selected - 1) % len(self.options)
        if pyxel.btnp(pyxel.KEY_RIGHT):
            selected_option = self.options[self.selected]
            if selected_option == "Quit":
                pyxel.quit()
            elif selected_option == "New Game":
                self.state = GameState.TEAM_SELECTION

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
            print(f"Selected team: {selected_team}")
            return selected_team
        return None

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

class PlayerTeamScreen:
    def __init__(self, selected_team):
        self.selected_team = selected_team

    def update(self):
        if pyxel.btnp(pyxel.KEY_RETURN):
            menu.state = GameState.ROSTER_SCREEN

    def draw(self):
        pyxel.cls(12)
        pyxel.text(60, 10, f"Your Team: {self.selected_team}", 1)
        pyxel.text(30, 50, "Press ENTER to view roster", 7)

class RosterScreen:
    def __init__(self, selected_team):
        self.selected_team = selected_team
        self.players = []
        self.current_player_index = 0
        self.get_roster()

    def update(self):
        if pyxel.btnp(pyxel.KEY_LEFT) and len(self.players) > 1:
            self.current_player_index = (self.current_player_index - 1) % len(self.players)
        elif pyxel.btnp(pyxel.KEY_RIGHT) and len(self.players) > 1:
            self.current_player_index = (self.current_player_index + 1) % len(self.players)

    def draw(self):
        pyxel.cls(12)
        pyxel.text(60, 10, "ROSTER", 1)
        if self.players:
            player = self.players[self.current_player_index]
            pyxel.rect(20, 30, 120, 80, 1)  # Player card background
            pyxel.text(30, 35, f"Player Name: {player['name']}", 7)
            pyxel.text(30, 45, f"Batting: ", 7)
            pyxel.text(30, 55, f"Pitching: ", 7)
            pyxel.text(30, 65, f"Fielding: ", 7)
        else:
            pyxel.text(30, 30, "No players in roster", 7)

    def get_roster(self):
        conn = sqlite3.connect("baseball_teams.db")
        teamID = conn.execute('''
        SELECT TeamID FROM Teams WHERE TeamName = ?
        ''', (self.selected_team,)).fetchone()[0]

        abbreviation = conn.execute('''
        SELECT Abbreviation FROM Teams WHERE TeamName = ?
        ''', (self.selected_team,)).fetchone()[0]

        roster = conn.execute(f'''
        SELECT Name FROM {abbreviation}_Batting WHERE TeamID = ?
        ''', (teamID,)).fetchall()

        self.players = [{'name': player[0]} for player in roster]

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
player_team_screen = None
roster_screen = None

def update():
    global player_team_screen, roster_screen
    if menu.state == GameState.MENU:
        menu.update()
    elif menu.state == GameState.TEAM_SELECTION:
        selected_team = team_selection_screen.update()
        if selected_team:
            player_team_screen = PlayerTeamScreen(selected_team)
            menu.state = GameState.PLAYER_TEAM_SCREEN
    elif menu.state == GameState.PLAYER_TEAM_SCREEN:
        player_team_screen.update()
        if pyxel.btnp(pyxel.KEY_RETURN):
            roster_screen = RosterScreen(player_team_screen.selected_team)
            menu.state = GameState.ROSTER_SCREEN
    elif menu.state == GameState.ROSTER_SCREEN:
        if roster_screen:
            roster_screen.update()



def draw():
    if menu.state == GameState.MENU:
        menu.draw()
    elif menu.state == GameState.TEAM_SELECTION:
        team_selection_screen.draw()
    elif menu.state == GameState.PLAYER_TEAM_SCREEN:
        player_team_screen.draw()
    elif menu.state == GameState.ROSTER_SCREEN:
        if roster_screen:
            roster_screen.draw()


pyxel.run(update, draw)
