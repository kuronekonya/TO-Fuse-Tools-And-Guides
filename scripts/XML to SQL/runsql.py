import os
import pyodbc

# === CONFIGURATION ===
SQL_SERVER = 'localhost'
DATABASE = 'your_database'
USERNAME = 'your_username'
PASSWORD = 'your_password'

# Optional: change this to your actual driver (check with: pyodbc.drivers())
DRIVER = 'ODBC Driver 17 for SQL Server'

# === SCRIPT START ===
def run_sql_files_in_order():
    script_dir = os.path.dirname(os.path.abspath(__file__))
    sql_files = sorted(f for f in os.listdir(script_dir) if f.endswith('.sql'))

    if not sql_files:
        print("No .sql files found.")
        return

    connection_string = (
        f"DRIVER={{{DRIVER}}};"
        f"SERVER={SQL_SERVER};"
        f"DATABASE={DATABASE};"
        f"UID={USERNAME};"
        f"PWD={PASSWORD}"
    )

    with pyodbc.connect(connection_string, autocommit=True) as conn:
        cursor = conn.cursor()
        for file in sql_files:
            path = os.path.join(script_dir, file)
            print(f"Running: {file}")
            with open(path, 'r', encoding='utf-8') as f:
                sql = f.read()
                try:
                    cursor.execute(sql)
                    print(f"✔️ Success: {file}")
                except Exception as e:
                    print(f"❌ Error in {file}: {e}")

if __name__ == "__main__":
    run_sql_files_in_order()
