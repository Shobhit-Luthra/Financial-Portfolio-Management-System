import db
import traceback

def check_schema():
    conn = db.get_db_connection()
    if not conn:
        print("Failed to connect to database.")
        return
    
    with open('schema_fixed.txt', 'w', encoding='utf-8') as f:
        f.write("Successfully connected to database.\n")
        
        tables = db.execute_query("SHOW TABLES", fetch=True)
        f.write(f"Tables: {tables}\n")
        
        if tables:
            for t in tables:
                table_name = list(t.values())[0]
                f.write(f"\nSchema for {table_name}:\n")
                schema = db.execute_query(f"DESCRIBE {table_name}", fetch=True)
                for col in schema:
                    f.write(f"  - {col['Field']}: {col['Type']}\n")

if __name__ == "__main__":
    check_schema()
