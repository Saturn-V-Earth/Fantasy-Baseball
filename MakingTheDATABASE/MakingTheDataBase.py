import pandas as pd
import sqlite3

def insert_team_data(team_abbreviation, league_name, division_name):
    url = f"https://www.baseball-reference.com/teams/{team_abbreviation}/2023.shtml#all_appearances"

    tables = pd.read_html(url)

    team_data_table = tables[0]

    conn = sqlite3.connect("baseball_teams.db")

    #Create Teams table if it doesn't exist
    conn.execute('''
        CREATE TABLE IF NOT EXISTS Teams (
            TeamID INTEGER PRIMARY KEY,
            TeamName TEXT,
            Abbreviation TEXT,
            LeagueID INTEGER,
            DivisionID INTEGER,
            FOREIGN KEY (LeagueID) REFERENCES Leagues(LeagueID),
            FOREIGN KEY (DivisionID) REFERENCES Divisions(DivisionID)
        )
    ''')

    #Create Leagues table if it doesn't exist
    conn.execute('''
        CREATE TABLE IF NOT EXISTS Leagues (
            LeagueID INTEGER PRIMARY KEY,
            LeagueName TEXT UNIQUE
        )
    ''')

    #Create Divisions table if it doesn't exist
    conn.execute('''
        CREATE TABLE IF NOT EXISTS Divisions (
            DivisionID INTEGER PRIMARY KEY,
            DivisionName TEXT UNIQUE
        )
    ''')

    #Create Players table with TeamID as primary key
    conn.execute(f'''
        CREATE TABLE IF NOT EXISTS {team_abbreviation} (
            TeamID INTEGER,
            PlayerName TEXT,
            -- Add other player columns here
            FOREIGN KEY (TeamID) REFERENCES Teams(TeamID)
        )
    ''')

    #Insert league data if it doesn't exist
    conn.execute('''
        INSERT OR IGNORE INTO Leagues (LeagueName) VALUES (?)
    ''', (league_name,))

    #Insert division data if it doesn't exist
    conn.execute('''
        INSERT OR IGNORE INTO Divisions (DivisionName) VALUES (?)
    ''', (division_name,))

    #Get league and division IDs
    league_id = conn.execute('''
        SELECT LeagueID FROM Leagues WHERE LeagueName = ?
    ''', (league_name,)).fetchone()[0]

    division_id = conn.execute('''
        SELECT DivisionID FROM Divisions WHERE DivisionName = ?
    ''', (division_name,)).fetchone()[0]

    #Insert team data into Teams table
    conn.execute('''
        INSERT INTO Teams (TeamName, Abbreviation, LeagueID, DivisionID)
        VALUES (?, ?, ?, ?)
    ''', (team_abbreviation, team_abbreviation, league_id, division_id))

    #Get the TeamID for the inserted team
    team_id = conn.execute('''
        SELECT TeamID FROM Teams WHERE Abbreviation = ?
    ''', (team_abbreviation,)).fetchone()[0]

    #Insert player data into the Players table
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