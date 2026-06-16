import sqlite3
from lists import groups
import csv
from paths import app_path, resource_path

team_rating = {}
yn = input("reset? :").lower()

with open(resource_path("data_box/elo.csv"), "r", encoding="utf-8") as f:
    reader = csv.reader(f)
    next(reader)

    for team, rating, iso3 in reader:
        team_rating[team] = int(rating)

conn = sqlite3.connect(app_path("developer.db"))
cur = conn.cursor()

if yn == "y":
    cur.execute("DROP TABLE IF EXISTS user_pw")
    cur.execute("""
    CREATE TABLE user_pw (
        id INTEGER PRIMARY KEY,
        user_ID TEXT,
        password TEXT,
        tournament_flag INTEGER DEFAULT 0
    );
    """)
    cur.execute("INSERT INTO user_pw (user_ID, password) values ('development', 0)")

    for i, l in enumerate("ABCDEFGHIJKL"):
        cur.execute(f"DROP TABLE IF EXISTS {l}_fin")
        cur.execute(f"""
        CREATE TABLE {l}_fin (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            rating_a INTEGER,
            team_a TEXT,
            goals_a,
            goals_b,
            team_b TEXT,
            rating_b INTEGER
        );
        """)
        
        g = groups[i]
        for n in range(4):
            for m in range(n+1, 4):
                cur.execute(f"""
                INSERT INTO {l}_fin (rating_a, team_a, team_b, rating_b) values (?, ?, ?, ?)
                """,(team_rating[g[n]], g[n], g[m], team_rating[g[m]]))
    
cur.execute("DROP TABLE IF EXISTS tournament_fin")
cur.execute(f"""
CREATE TABLE tournament_fin (
    id INTEGER PRIMARY KEY,
    round32 TEXT,
    round16 TEXT,
    round8 TEXT,
    round4 TEXT,
    round2 TEXT,
    champion TEXT
);
""")

cur.execute("""
INSERT INTO tournament_fin
(id, round32, round16, round8, round4, round2, champion)
VALUES (1, NULL, NULL, NULL, NULL, NULL, NULL)
""")


conn.commit()
conn.close()
