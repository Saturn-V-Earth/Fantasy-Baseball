import sqlite3

table_names = [  
    ("PHI", "PHI_Fielding"),  
    ("NYM", "NYM_Fielding"),
    ("ATL", "ATL_Fielding"),
    ("MIA", "MIA_Fielding"),
    ("WSN", "WSN_Fielding"),
    ("MIL", "MIL_Fielding"),
    ("CHC", "CHC_Fielding"),
    ("CIN", "CIN_Fielding"),
    ("PIT", "PIT_Fielding"),
    ("STL", "STL_Fielding"),
    ("LAD", "LAD_Fielding"),
    ("ARI", "ARI_Fielding"),
    ("SDP", "SDP_Fielding"),
    ("SFG", "SFG_Fielding"),
    ("COL", "COL_Fielding"),
    ("BAL", "BAL_Fielding"),
    ("TBR", "TBR_Fielding"),
    ("TOR", "TOR_Fielding"),
    ("NYY", "NYY_Fielding"),
    ("BOS", "BOS_Fielding"),
    ("MIN", "MIN_Fielding"),
    ("DET", "DET_Fielding"),
    ("CLE", "CLE_Fielding"),
    ("CHW", "CHW_Fielding"),
    ("KCR", "KCR_Fielding"),
    ("HOU", "HOU_Fielding"),
    ("TEX", "TEX_Fielding"),
    ("SEA", "SEA_Fielding"),
    ("LAA", "LAA_Fielding"),
    ("OAK", "OAK_Fielding")
]

conn = sqlite3.connect('baseball_teams.db')
cursor = conn.cursor()

for old_name, new_name in table_names:
    cursor.execute(f"ALTER TABLE {old_name} RENAME TO {new_name};")

conn.commit()

conn.close()
