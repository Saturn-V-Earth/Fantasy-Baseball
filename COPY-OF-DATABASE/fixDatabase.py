import sqlite3

# Connect to the database
conn = sqlite3.connect('baseball_teams_COPY.db')
cursor = conn.cursor()

# Query to identify non-player records (Adjust WHERE clause as needed)
cursor.execute("""
    DELETE FROM ARI_Batting
    WHERE Rk LIKE '%Rk%'
       OR Rk IS NULL
       OR Pos LIKE '%P%'
               OR Pos IS NULL;
""")

conn.commit()
# Fetch and print the results to verify
non_player_records = cursor.fetchall()
for record in non_player_records:
    print(record)
