import sqlite3

table_names = [  
    ("PHI", "PHI_Batting"),  
    ("NYM", "NYM_Batting"),
    ("ATL", "ATL_Batting"),
    ("MIA", "MIA_Batting"),
    ("WSN", "WSN_Batting"),
    ("MIL", "MIL_Batting"),
    ("CHC", "CHC_Batting"),
    ("CIN", "CIN_Batting"),
    ("PIT", "PIT_Batting"),
    ("STL", "STL_Batting"),
    ("LAD", "LAD_Batting"),
    ("ARI", "ARI_Batting"),
    ("SDP", "SDP_Batting"),
    ("SFG", "SFG_Batting"),
    ("COL", "COL_Batting"),
    ("BAL", "BAL_Batting"),
    ("TBR", "TBR_Batting"),
    ("TOR", "TOR_Batting"),
    ("NYY", "NYY_Batting"),
    ("BOS", "BOS_Batting"),
    ("MIN", "MIN_Batting"),
    ("DET", "DET_Batting"),
    ("CLE", "CLE_Batting"),
    ("CHW", "CHW_Batting"),
    ("KCR", "KCR_Batting"),
    ("HOU", "HOU_Batting"),
    ("TEX", "TEX_Batting"),
    ("SEA", "SEA_Batting"),
    ("LAA", "LAA_Batting"),
    ("OAK", "OAK_Batting")
]

conn = sqlite3.connect('baseball_teams.db')
cursor = conn.cursor()

for old_name, new_name in table_names:
    cursor.execute(f"ALTER TABLE {old_name} RENAME TO {new_name};")

conn.commit()

conn.close()
