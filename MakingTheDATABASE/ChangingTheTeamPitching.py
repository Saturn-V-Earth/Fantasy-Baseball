import sqlite3

table_names = [  
    ("PHI", "PHI_Pitching"),  
    ("NYM", "NYM_Pitching"),
    ("ATL", "ATL_Pitching"),
    ("MIA", "MIA_Pitching"),
    ("WSN", "WSN_Pitching"),
    ("MIL", "MIL_Pitching"),
    ("CHC", "CHC_Pitching"),
    ("CIN", "CIN_Pitching"),
    ("PIT", "PIT_Pitching"),
    ("STL", "STL_Pitching"),
    ("LAD", "LAD_Pitching"),
    ("ARI", "ARI_Pitching"),
    ("SDP", "SDP_Pitching"),
    ("SFG", "SFG_Pitching"),
    ("COL", "COL_Pitching"),
    ("BAL", "BAL_Pitching"),
    ("TBR", "TBR_Pitching"),
    ("TOR", "TOR_Pitching"),
    ("NYY", "NYY_Pitching"),
    ("BOS", "BOS_Pitching"),
    ("MIN", "MIN_Pitching"),
    ("DET", "DET_Pitching"),
    ("CLE", "CLE_Pitching"),
    ("CHW", "CHW_Pitching"),
    ("KCR", "KCR_Pitching"),
    ("HOU", "HOU_Pitching"),
    ("TEX", "TEX_Pitching"),
    ("SEA", "SEA_Pitching"),
    ("LAA", "LAA_Pitching"),
    ("OAK", "OAK_Pitching")
]

conn = sqlite3.connect('baseball_teams.db')
cursor = conn.cursor()

for old_name, new_name in table_names:
    cursor.execute(f"ALTER TABLE {old_name} RENAME TO {new_name};")

conn.commit()

conn.close()
