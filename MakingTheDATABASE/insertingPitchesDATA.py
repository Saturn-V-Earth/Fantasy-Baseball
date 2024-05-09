import pandas as pd
import sqlite3

def insert_team_data(team_abbreviation, league_name, division_name):
    url = f"https://www.baseball-reference.com/teams/{team_abbreviation}/2023.shtml#team_pitchings"

    tables = pd.read_html(url)

    team_data_table = tables[1]

    conn = sqlite3.connect("baseball_teams.db")

    team_id = conn.execute('''
        SELECT TeamID FROM Teams WHERE Abbreviation = ?
    ''', (team_abbreviation,)).fetchone()[0]

    team_data_table['TeamID'] = team_id
    team_data_table.to_sql(team_abbreviation, conn, index=False, if_exists="replace")

    conn.commit()
    conn.close()

    print(f"Data for {team_abbreviation} inserted successfully.")

teams_data = [
    ("PHI", "National League", "East Division"),
    ("NYM", "National League", "East Division"),
    ("ATL", "National League", "East Division"),
    ("MIA", "National League", "East Division"),
    ("WSN", "National League", "East Division"),
    ("MIL", "National League", "Central Division"),
    ("CHC", "National League", "Central Division"),
    ("CIN", "National League", "Central Division"),
    ("PIT", "National League", "Central Division"),
    ("STL", "National League", "Central Division"),
    ("LAD", "National League", "West Division"),
    ("ARI", "National League", "West Division"),
    ("SDP", "National League", "West Division"),
    ("SFG", "National League", "West Division"),
    ("COL", "National League", "West Division"),
    ("BAL", "American League", "East Division"),
    ("TBR", "American League", "East Division"),
    ("TOR", "American League", "East Division"),
    ("NYY", "American League", "East Division"),
    ("BOS", "American League", "East Division"),
    ("MIN", "American League", "Central Division"),
    ("DET", "American League", "Central Division"),
    ("CLE", "American League", "Central Division"),
    ("CHW", "American League", "Central Division"),
    ("KCR", "American League", "Central Division"),
    ("HOU", "American League", "West Division"),
    ("TEX", "American League", "West Division"),
    ("SEA", "American League", "West Division"),
    ("LAA", "American League", "West Division"),
    ("OAK", "American League", "West Division")
]

for team_data in teams_data:
    insert_team_data(*team_data)