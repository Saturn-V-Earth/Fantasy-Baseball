import csv
import sqlite3
import re

def sanitize_column_name(name):
    #replace special characters with underscores
    #chatGPT Help for this line     
    return re.sub(r'\W|^(?=\d)', '_', name)

def create_table_from_csv(team_abbreviation, csv_file, db_name='baseball_teams.db'):
    conn = sqlite3.connect(db_name)
    cursor = conn.cursor()

    #Read the CSV file
    with open(csv_file, 'r') as file:
        reader = csv.reader(file)
        
        #check if the file is empty
        try:
            headers = next(reader)  # Read the header row to get column names
        except StopIteration:
            print("CSV file is empty.")
            return
        
        #sanitize column names and handle duplicates
        unique_headers = []
        for header in headers:
            sanitized_name = sanitize_column_name(header)
            while sanitized_name in unique_headers:
                # Append a suffix to make the name unique
                match = re.match(r'^(.*)_(\d+)$', sanitized_name)
                if match:
                    base_name, num = match.groups()
                    sanitized_name = f"{base_name}_{int(num) + 1}"
                else:
                    sanitized_name += "_1"
            unique_headers.append(sanitized_name)
        
        #Create table with the team abbreviation as table name
        table_name = team_abbreviation
        create_table_sql = f"CREATE TABLE IF NOT EXISTS {table_name} ({', '.join([f'{header} TEXT' for header in unique_headers])})"
        cursor.execute(create_table_sql)
        
        #insert data into table
        insert_sql = f"INSERT INTO {table_name} VALUES ({', '.join(['?' for _ in unique_headers])})"
        for row in reader:
            cursor.execute(insert_sql, row)

    #Retrieve TeamID for the given team abbreviation
    team_id = conn.execute('''
        SELECT TeamID FROM Teams WHERE Abbreviation = ?
    ''', (team_abbreviation,)).fetchone()[0]

    #add TeamID to the inserted data
    cursor.execute(f"ALTER TABLE {table_name} ADD COLUMN TeamID INTEGER")
    cursor.execute(f"UPDATE {table_name} SET TeamID = ?", (team_id,))

    print(f"Data for {team_abbreviation} inserted successfully.")

    conn.commit()
    conn.close()

create_table_from_csv('NYM', 'NYM.csv', 'baseball_teams.db')
