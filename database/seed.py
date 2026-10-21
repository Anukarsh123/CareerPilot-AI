import sqlite3
import os

def get_db_connection():
    # Database path pointing to project root
    db_path = os.path.join(os.path.dirname(__file__), "..", "instance", "careerpilot.db")
    os.makedirs(os.path.dirname(db_path), exist_ok=True)
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    return conn

def seed_database():
    schema_path = os.path.join(os.path.dirname(__file__), "schema.sql")
    
    if not os.path.exists(schema_path):
        print(f"Error: Could not find schema file at {schema_path}")
        return

    conn = get_db_connection()
    cursor = conn.cursor()

    print("Executing schema setup...")
    with open(schema_path, "r") as f:
        schema_sql = f.read()
        cursor.executescript(schema_sql)

    print("Seeding initial achievements...")
    initial_achievements = [
        ("Resume Pioneer", "Uploaded and parsed your first resume.", "file-text", 50),
        ("Interview Rookie", "Completed your first mock interview session.", "mic", 100),
        ("Skill Collector", "Added 5 core technical skills to your profile.", "award", 75),
        ("Roadmap Navigator", "Completed 25% of your career learning roadmap.", "map-pin", 150),
        ("Bug Hunter", "Submitted your first clean practice code submission.", "code", 50)
    ]

    for title, desc, icon, xp in initial_achievements:
        cursor.execute("""
            INSERT INTO achievements (title, description, icon_name, xp_reward)
            SELECT ?, ?, ?, ?
            WHERE NOT EXISTS (SELECT 1 FROM achievements WHERE title = ?)
        """, (title, desc, icon, xp, title))

    conn.commit()
    conn.close()
    print("Database seeding completed successfully!")

if __name__ == "__main__":
    seed_database()