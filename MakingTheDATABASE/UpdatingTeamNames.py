import sqlite3

def update_team_name(conn, team_id, new_team_name):
    try:
        conn.execute('''
            UPDATE Teams
            SET TeamName = ?
            WHERE TeamID = ?;
        ''', (new_team_name, team_id))
        conn.commit()
        print(f"Team with TeamID {team_id} updated successfully.")
    except Exception as e:
        print(f"Error updating team with TeamID {team_id}: {e}")

conn = sqlite3.connect("baseball_teams.db")

mlb_teams = [
    (1, "Philadelphia Phillies"),
    (2, "New York Mets"),
    (3, "Atlanta Braves"),
    (4, "Miami Marlins"),
    (5, "Washington Nationals"),
    (6, "Milwaukee Brewers"),
    (7, "Chicago Cubs"),
    (8, "Cincinnati Reds"),
    (9, "Pittsburgh Pirates"),
    (10, "St. Louis Cardinals"),
    (11, "Los Angeles Dodgers"),
    (12, "Arizona Diamondbacks"),
    (13, "San Diego Padres"),
    (14, "San Francisco Giants"),
    (15, "Colorado Rockies"),
    (16, "Baltimore Orioles"),
    (17, "Tampa Bay Rays"),
    (18, "Toronto Blue Jays"),
    (19, "New York Yankees"),
    (20, "Boston Red Sox"),
    (21, "Minnesota Twins"),
    (22, "Detroit Tigers"),
    (23, "Cleveland Guardians"),
    (24, "Chicago White Sox"),
    (25, "Kansas City Royals"),
    (26, "Houston Astros"),
    (27, "Texas Rangers"),
    (28, "Seattle Mariners"),
    (29, "Los Angeles Angels"),
    (30, "Oakland Athletics")
]

for team_id, new_team_name in mlb_teams:
    update_team_name(conn, team_id, new_team_name)

conn.close()
