import pandas as pd
import sqlite3

DB_PATH = 'db/stops.db'
TABLE_NAME = 'stops'
CSV_PATH = 'data/simulated_stops.csv'

# Connect to SQLite database (creates file if not exists)
conn = sqlite3.connect(DB_PATH)
cursor = conn.cursor() 

print("CREATING stops TABLE: IN")

# Create table command
create_table_sql = f"""
CREATE TABLE IF NOT EXISTS stops (
            stop_id TEXT PRIMARY KEY,
            stop_type_id TEXT,
            stop_type_name TEXT,
            start_at TEXT,
            ends_at TEXT,
            duration_minutes REAL
        );
"""

conn.execute(create_table_sql)
conn.commit()
print("CREATING stops TABLE: OUT")

# Load data in DataFrame
data = pd.read_csv(CSV_PATH)

# Prepare data as a list of row values for insertion
row_values = [[val for val in row[1]] for row in data.iterrows()]

print("DATA LOADING: IN")
print(f"Inserting data into db: {TABLE_NAME}")

# Insert data
cursor.executemany(f"""
    INSERT INTO {TABLE_NAME}
    (stop_id, stop_type_id, stop_type_name, start_at, ends_at, duration_minutes)
    VALUES (?, ?, ?, ?, ?, ?)
""", row_values)
conn.commit()

print(f"Loaded {len(row_values)} rows into db: {TABLE_NAME}")
print("DATA LOADING: OUT")

conn.close()
