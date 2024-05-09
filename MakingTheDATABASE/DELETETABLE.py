import sqlite3

def delete_table(table_name, db_name='baseball_teams.db'):
    conn = sqlite3.connect(db_name)
    cursor = conn.cursor()

    drop_table_sql = f"DROP TABLE IF EXISTS {table_name}"

    cursor.execute(drop_table_sql)

    print(f"Table '{table_name}' deleted successfully.")

    conn.commit()
    conn.close()

delete_table('PHI', 'baseball_teams.db')
