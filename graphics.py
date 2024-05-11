import pyxel

class GameState:
    MENU = 0
    TEAM_SELECTION = 1

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

class TeamSelectionScreen():
    def __init__(self, mlb_teamsNL, mlb_teamsAL):
        self.mlb_teamsNL = mlb_teamsNL
        self.mlb_teamsAL = mlb_teamsAL
        self.teams = {
            "American League": self.mlb_teamsNL,  # Replace with actual NL teams
            "National League": self.mlb_teamsAL   # Replace with actual AL teams
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
        elif pyxel.btnp(pyxel.KEY_LEFT):
            menu.state = GameState.MENU

    def draw(self):
        pyxel.cls(12)
        pyxel.text(60, 10, "NEW GAME", 1)  # Main title for the new game screen
        pyxel.text(10, 20, "National League", 1 if self.selected_section == "National League" else 7)
        pyxel.text(85, 20, "American League", 1 if self.selected_section == "American League" else 7)

        section_teams = self.teams[self.selected_section]
        for i, team in enumerate(section_teams):
            y = 30 + i/2 * 12
            if i == self.selected_team:
                pyxel.text(10 if self.selected_section == "American League" else 10, y, "> " + team, 0)
            else:
                pyxel.text(10 if self.selected_section == "American League" else 10, y, team, 7)


mlb_teamsNL = [
    ("Philadelphia Phillies"),
    ("New York Mets"),
    ("Atlanta Braves"),
    ("Miami Marlins"),
    ("Washington Nationals"),
    ("Milwaukee Brewers"),
    ("Chicago Cubs"),
    ("Cincinnati Reds"),
    ("Pittsburgh Pirates"),
    ("St. Louis Cardinals"),
    ("Los Angeles Dodgers"),
    ("Arizona Diamondbacks"),
    ("San Diego Padres"),
    ("San Francisco Giants"),
    ("Colorado Rockies")
]

mlb_teamsAL = [
    ("Baltimore Orioles"),
    ("Tampa Bay Rays"),
    ("Toronto Blue Jays"),
    ("New York Yankees"),
    ("Boston Red Sox"),
    ("Minnesota Twins"),
    ("Detroit Tigers"),
    ("Cleveland Guardians"),
    ("Chicago White Sox"),
    ("Kansas City Royals"),
    ("Houston Astros"),
    ("Texas Rangers"),
    ("Seattle Mariners"),
    ("Los Angeles Angels"),
    ("Oakland Athletics")
]

menu = Menu()
team_selection_screen = TeamSelectionScreen(mlb_teamsNL, mlb_teamsAL)

def update():
    if menu.state == GameState.MENU:
        menu.update()
    elif menu.state == GameState.TEAM_SELECTION:
        team_selection_screen.update()

def draw():
    if menu.state == GameState.MENU:
        menu.draw()
    elif menu.state == GameState.TEAM_SELECTION:
        team_selection_screen.draw()

pyxel.run(update, draw)


