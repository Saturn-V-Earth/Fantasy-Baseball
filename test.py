"""
import pyxel

# Initialize Pyxel with a window size of 160x120
pyxel.init(160, 120)

# Load an image file into image bank 0 at position (0, 0)
pyxel.images[0].load(0, 0, )

# Define the update function
def update():
    if pyxel.btnp(pyxel.KEY_Q):
        pyxel.quit()

# Define the draw function
def draw():
    pyxel.cls(0)
    # Draw the image from image bank 0 at position (10, 10) on the screen
    pyxel.blt(0, 0, 0, 0, 0, 200, 200)

# Run the Pyxel application
pyxel.run(update, draw)
"""

def generate_round_robin_schedule(teams):
    if len(teams) % 2:
        teams.append('BYE')  # If the number of teams is odd, add a dummy team "BYE"

    num_rounds = len(teams) - 1
    num_matches_per_round = len(teams) // 2
    schedule = []

    for round in range(num_rounds):
        round_matches = []
        for match in range(num_matches_per_round):
            home = teams[match]
            away = teams[-(match + 1)]
            round_matches.append((home, away))
        teams.insert(1, teams.pop())  # Rotate teams to generate new pairs
        schedule.append(round_matches)

    return schedule

def generate_home_away_schedule(teams):
    round_robin_schedule = generate_round_robin_schedule(teams)
    home_away_schedule = []

    for round_matches in round_robin_schedule:
        home_away_schedule.append(round_matches)
        home_away_schedule.append([(away, home) for home, away in round_matches])

    return home_away_schedule

# Example usage
teams = [
    ("Philadelphia Phillies"), ("New York Mets"), ("Atlanta Braves"), ("Miami Marlins"), ("Washington Nationals"),
    ("Milwaukee Brewers"), ("Chicago Cubs"), ("Cincinnati Reds"), ("Pittsburgh Pirates"), ("St. Louis Cardinals"),
    ("Los Angeles Dodgers"), ("Arizona Diamondbacks"), ("San Diego Padres"), ("San Francisco Giants"), ("Colorado Rockies")
]
schedule = generate_home_away_schedule(teams)

for round_num, round_matches in enumerate(schedule):
    print(f"Round {round_num + 1}:")
    for home, away in round_matches:
        if home != 'BYE' and away != 'BYE':
            print(f"{home} vs {away}")
