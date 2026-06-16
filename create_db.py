import sqlite3
from lists import groups
import csv
import os
from paths import app_path, resource_path

def create_user_DB(ID="worldcup"):     
    allowed_teams = {team_name for group in groups for team_name in group}
    
    team_rating = {}
    teams = []
    ELO_CSV = resource_path("data_box/elo.csv")
    with open(ELO_CSV, "r", encoding="utf-8") as f:
        reader = csv.reader(f)
        next(reader)

        for team, rating, iso3 in reader:
            team_rating[team] = int(rating)
            teams.append((team, rating, iso3))

    USER_DB_DIR = app_path("user_db")
    os.makedirs(USER_DB_DIR, exist_ok=True)

    db_path = os.path.join(USER_DB_DIR, f"{ID}.db")
    conn = sqlite3.connect(db_path)
    cur = conn.cursor()

    cur.execute("DROP TABLE IF EXISTS teams")
    cur.execute("""
    CREATE TABLE teams (
        id INTEGER PRIMARY KEY,
        name TEXT,
        rating REAL,
        shortened TEXT,
        pts INTEGER DEFAULT 0,
        goals_scored INTEGER DEFAULT 0,
        goals_conceded INTEGER DEFAULT 0
    );
    """)

    cur.execute("DROP TABLE IF EXISTS results")
    cur.execute("""
    CREATE TABLE results (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        match TEXT,
        winner TEXT,
        goals_winner INTEGER DEFAULT 0,
        goals_loser INTEGER DEFAULT 0,
        loser TEXT,
        rating_diff INTEGER DEFAULT 0
    );
    """)

    cur.execute("DROP TABLE IF EXISTS results_all")
    cur.execute("""
    CREATE TABLE results_all (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        match TEXT,
        winner TEXT,
        goals_winner INTEGER DEFAULT 0,
        goals_loser INTEGER DEFAULT 0,
        loser TEXT,
        rating_diff INTEGER DEFAULT 0
    );
    """)

    for team in teams:
        if team[0] in allowed_teams:
            cur.execute(
                "insert into teams (name, rating, shortened) values (?, ?, ?)",
                (team[0],team[1],team[2])
            )
        


    cur.execute("DROP TABLE IF EXISTS record")
    cur.execute("""
    CREATE TABLE record (
        name TEXT,
        knocked_out INTEGER DEFAULT 0,
        r32 INTEGER DEFAULT 0,
        r16 INTEGER DEFAULT 0,
        r8 INTEGER DEFAULT 0,
        fourth INTEGER DEFAULT 0,
        third INTEGER DEFAULT 0,
        second INTEGER DEFAULT 0,
        Champion INTEGER DEFAULT 0
    );
    """)

    for team in teams:
        if team[0] in allowed_teams:
            cur.execute("insert into record (name) values (?)", (team[0],))

    
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

    conn.commit()
    conn.close()

if __name__=="__main__":
    create_user_DB(ID="developer")
