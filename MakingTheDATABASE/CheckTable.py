import pandas as pd

url = f"https://www.baseball-reference.com/teams/PHI/2023.shtml#standard_fielding"

tables = pd.read_html(url)

team_data_table = tables[0]

print(team_data_table)