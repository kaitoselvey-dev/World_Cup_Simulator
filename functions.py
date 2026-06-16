import random
import itertools
import pandas as pd
import os
from lists import *
import csv
import sqlite3
from paths import app_path, resource_path

def make_prob_score():

    ELO_RESULT_PATH = resource_path("data_box/elo_result_probs.csv")
    SCORE_DIST_PATH = resource_path("data_box/score_distribution_table.csv")

    probs_df = pd.read_csv(ELO_RESULT_PATH, index_col='elo_bin_10')
    prob_dict_win_loss = probs_df.to_dict(orient='index')

    dist_df = pd.read_csv(SCORE_DIST_PATH)
    prob_dict_score = {}
    for _, row in dist_df.iterrows():
        b, p = row['elo_bin_20'], row['match_pattern']
        if b not in prob_dict_score:
            prob_dict_score[b] = {}
        if p not in prob_dict_score[b]:
            prob_dict_score[b][p] = {"stronger": [], "weaker": [], "weights": []}
        
        prob_dict_score[b][p]["stronger"].append(int(row['stronger_goals']))
        prob_dict_score[b][p]["weaker"].append(int(row['weaker_goals']))
        prob_dict_score[b][p]["weights"].append(row['probability'])

    return prob_dict_score, prob_dict_win_loss

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

def ensure_user_fin_tables(conn):
    cur = conn.cursor()
    existing_tables = {
        row[0]
        for row in cur.execute("SELECT name FROM sqlite_master WHERE type='table'")
    }
    if not {"teams", "record", "results_all"}.issubset(existing_tables):
        return False

    team_rating = {}
    with open(resource_path("data_box/elo.csv"), "r", encoding="utf-8") as f:
        reader = csv.reader(f)
        next(reader)

        for team, rating, iso3 in reader:
            team_rating[team] = int(rating)

    for i, l in enumerate("ABCDEFGHIJKL"):
        cur.execute(f"""
        CREATE TABLE IF NOT EXISTS {l}_fin (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            rating_a INTEGER,
            team_a TEXT,
            goals_a,
            goals_b,
            team_b TEXT,
            rating_b INTEGER
        );
        """)

        count = cur.execute(f"SELECT COUNT(*) FROM {l}_fin").fetchone()[0]
        if count == 0:
            g = groups[i]
            for n in range(4):
                for m in range(n + 1, 4):
                    cur.execute(f"""
                    INSERT INTO {l}_fin
                    (rating_a, team_a, team_b, rating_b)
                    VALUES (?, ?, ?, ?)
                    """, (team_rating[g[n]], g[n], g[m], team_rating[g[m]]))

    conn.commit()
    return True

def result(strong_rating, weak_rating, prob_dict_score, prob_dict_win_loss):

    d = strong_rating - weak_rating
    
    bin_10 = (d // 10) * 10

    match_probs = prob_dict_win_loss[bin_10]
    
    results_pool = ['strong_win', 'draw', 'strong_loss']
    weights_pool = [match_probs['strong_win'], match_probs['draw'], match_probs['strong_loss']]
    
    chosen_result = random.choices(results_pool, weights=weights_pool, k=1)[0]
    
    if chosen_result == 'strong_win':
        match_pattern = 'STRONGER_WIN'
    elif chosen_result == 'draw':
        match_pattern = 'DRAW'
    else:
        match_pattern = 'WEAKER_WIN'

    bin_20 = (d // 20) * 20

    candidates = prob_dict_score[bin_20][match_pattern]

    chosen_idx = random.choices(range(len(candidates["stronger"])), weights=candidates["weights"], k=1)[0]
    
    strong_goals = candidates["stronger"][chosen_idx]
    weak_goals = candidates["weaker"][chosen_idx]
    
    return strong_goals, weak_goals

def game_group_stage(cur, team_1, team_2, predict_list, finished_list, prob_dict_score, prob_dict_win_loss):
    game_name = f"{team_1} vs {team_2}"
    cur.execute("INSERT INTO results (match) VALUES (?)", (game_name,))

    cur.execute("SELECT rating FROM teams WHERE name = ?", (team_1,))
    rating_1 = cur.fetchone()[0]
    cur.execute("SELECT rating FROM teams WHERE name = ?", (team_2,))
    rating_2 = cur.fetchone()[0]
    draw_flag = False
    
    if rating_2 > rating_1:
        team_s, team_w = team_2, team_1
        rating_s, rating_w = rating_2, rating_1
    else:
        team_s, team_w = team_1, team_2
        rating_s, rating_w = rating_1, rating_2

    d = rating_s - rating_w

    predict_match_set = []
    for r in predict_list:
        predict_match_set.append({r[0], r[3]})

    finished_match_set = []
    for r in finished_list:
        finished_match_set.append({r[0], r[3]})

    t1t2 = {team_1, team_2}

    if t1t2 in finished_match_set:
        idx = finished_match_set.index(t1t2)
        result_tuple = finished_list[idx]

        if result_tuple[1] == result_tuple[2]:
            t1 = result_tuple[0]
            t2 = result_tuple[3]
            goals_draw = int(result_tuple[1])
            cur.execute("UPDATE teams SET pts = pts + 1, goals_scored = goals_scored + ?, goals_conceded = goals_conceded + ? WHERE name = ?", (goals_draw, goals_draw, t1))
            cur.execute("UPDATE teams SET pts = pts + 1, goals_scored = goals_scored + ?, goals_conceded = goals_conceded + ? WHERE name = ?", (goals_draw, goals_draw, t2))
            cur.execute("UPDATE results SET winner = 'DRAW', loser = 'DRAW', goals_winner = ?, goals_loser = ?, rating_diff = ? WHERE match = ?", (goals_draw, goals_draw, d, game_name))

        else:
            if result_tuple[1] > result_tuple[2]:
                winner, loser = result_tuple[0], result_tuple[3]
                winner_goals , loser_goals = result_tuple[1], result_tuple[2]
            else:
                winner, loser = result_tuple[3], result_tuple[0]
                winner_goals , loser_goals = result_tuple[2], result_tuple[1]
            cur.execute("UPDATE teams SET pts = pts + 3, goals_scored = goals_scored + ?, goals_conceded = goals_conceded + ? WHERE name = ?", (winner_goals, loser_goals, winner))
            cur.execute("UPDATE teams SET goals_scored = goals_scored + ?, goals_conceded = goals_conceded + ? WHERE name = ?", (loser_goals, winner_goals, loser))
            cur.execute("UPDATE results SET winner = ?, loser = ?, goals_winner = ?, goals_loser = ?, rating_diff = ? WHERE match = ?", (winner, loser, winner_goals, loser_goals, d, game_name))

    elif t1t2 in predict_match_set:
        idx = predict_match_set.index(t1t2)
        result_tuple = predict_list[idx]

        if result_tuple[1] == result_tuple[2]:
            t1 = result_tuple[0]
            t2 = result_tuple[3]
            goals_draw = int(result_tuple[1])
            cur.execute("UPDATE teams SET pts = pts + 1, goals_scored = goals_scored + ?, goals_conceded = goals_conceded + ? WHERE name = ?", (goals_draw, goals_draw, t1))
            cur.execute("UPDATE teams SET pts = pts + 1, goals_scored = goals_scored + ?, goals_conceded = goals_conceded + ? WHERE name = ?", (goals_draw, goals_draw, t2))
            cur.execute("UPDATE results SET winner = 'DRAW', loser = 'DRAW', goals_winner = ?, goals_loser = ?, rating_diff = ? WHERE match = ?", (goals_draw, goals_draw, d, game_name))

        else:
            if result_tuple[1] > result_tuple[2]:
                winner, loser = result_tuple[0], result_tuple[3]
                winner_goals , loser_goals = result_tuple[1], result_tuple[2]
            else:
                winner, loser = result_tuple[3], result_tuple[0]
                winner_goals , loser_goals = result_tuple[2], result_tuple[1]
            cur.execute("UPDATE teams SET pts = pts + 3, goals_scored = goals_scored + ?, goals_conceded = goals_conceded + ? WHERE name = ?", (winner_goals, loser_goals, winner))
            cur.execute("UPDATE teams SET goals_scored = goals_scored + ?, goals_conceded = goals_conceded + ? WHERE name = ?", (loser_goals, winner_goals, loser))
            cur.execute("UPDATE results SET winner = ?, loser = ?, goals_winner = ?, goals_loser = ?, rating_diff = ? WHERE match = ?", (winner, loser, winner_goals, loser_goals, d, game_name))

    else:
        #score decider
        goals_s, goals_w = result(rating_s, rating_w, prob_dict_score, prob_dict_win_loss)
    

        if goals_s > goals_w:
            winner = team_s
            loser = team_w
            winner_goals = goals_s
            loser_goals = goals_w

        elif goals_s == goals_w:
            draw_flag = True
            goals_draw = goals_s
            goals_s, goals_w = goals_draw, goals_draw
            d = -d

        else:
            winner = team_w
            loser = team_s
            winner_goals = goals_w
            loser_goals = goals_s
            d = -d
            
        #recording results
        if draw_flag:
            cur.execute("UPDATE teams SET pts = pts + 1, goals_scored = goals_scored + ?, goals_conceded = goals_conceded + ? WHERE name = ?", (goals_draw, goals_draw, team_s))
            cur.execute("UPDATE teams SET pts = pts + 1, goals_scored = goals_scored + ?, goals_conceded = goals_conceded + ? WHERE name = ?", (goals_draw, goals_draw, team_w))
            cur.execute("UPDATE results SET winner = 'DRAW', loser = 'DRAW', goals_winner = ?, goals_loser = ?, rating_diff = ? WHERE match = ?", (goals_draw, goals_draw, d, game_name))
        else:
            cur.execute("UPDATE teams SET pts = pts + 3, goals_scored = goals_scored + ?, goals_conceded = goals_conceded + ? WHERE name = ?", (winner_goals, loser_goals, winner))
            cur.execute("UPDATE teams SET goals_scored = goals_scored + ?, goals_conceded = goals_conceded + ? WHERE name = ?", (loser_goals, winner_goals, loser))
            cur.execute("UPDATE results SET winner = ?, loser = ?, goals_winner = ?, goals_loser = ?, rating_diff = ? WHERE match = ?", (winner, loser, winner_goals, loser_goals, d, game_name))        

def game_tournament(cur, team_1, team_2, prob_dict_score, prob_dict_win_loss):
    game_name = f"{team_1} vs {team_2}"
    cur.execute("INSERT INTO results (match) VALUES (?)", (game_name,))
    cur.execute("SELECT rating FROM teams WHERE name = ?", (team_1,))
    rating_1 = cur.fetchone()[0]
    cur.execute("SELECT rating FROM teams WHERE name = ?", (team_2,))
    rating_2 = cur.fetchone()[0]
    draw_flag = False
    
    if rating_2 > rating_1:
        team_s, team_w = team_2, team_1
        rating_s, rating_w = rating_2, rating_1
        
    else:
        team_s, team_w = team_1, team_2
        rating_s, rating_w = rating_1, rating_2
    
    d = rating_s - rating_w

    #score decider
    goals_s, goals_w = result(rating_s, rating_w, prob_dict_score, prob_dict_win_loss)

    if goals_s > goals_w:
        winner = team_s
        loser = team_w
        goals_winner = goals_s
        goals_loser = goals_w

    elif goals_s == goals_w:
        pk_d = min(0.1, d/2000)
        if random.random() < 0.5 + pk_d:
            winner = team_s
            loser = team_w
        else:
            winner = team_w
            loser = team_s
            d = -d

        goals_winner = goals_s
        goals_loser = goals_w
        draw_flag = True

    else:
        winner = team_w
        loser = team_s
        goals_winner = goals_w
        goals_loser = goals_s
        d = -d

    #recording results
    if draw_flag:
        cur.execute("UPDATE results SET winner = ?, loser = ?, goals_winner = ?, goals_loser = ?, rating_diff = ? WHERE match = ?", (f"{winner}(PK)", loser, goals_winner, goals_loser, d, game_name))
    else:       
        cur.execute("UPDATE results SET winner = ?, loser = ?, goals_winner = ?, goals_loser = ?, rating_diff = ? WHERE match = ?", (winner, loser, goals_winner, goals_loser, d, game_name))
    return winner

def group_to_tournament(cur, group, thirds=False):
    
    if thirds:
        cur.execute(f"""
            SELECT name, pts, (goals_scored - goals_conceded) AS goal_diff, goals_scored, rating
            FROM teams
            WHERE name IN (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ORDER BY pts DESC, goal_diff DESC, goals_scored DESC, rating DESC
        """, group)

    else:
        cur.execute(f"""
            SELECT name, pts, (goals_scored - goals_conceded) AS goal_diff, goals_scored, rating
            FROM teams
            WHERE name IN (?, ?, ?, ?)
            ORDER BY pts DESC, goal_diff DESC, goals_scored DESC, rating DESC
        """, group)

    groups_status = cur.fetchall()

    if thirds:
        teams_sorted = [row[0] for row in groups_status]
        return teams_sorted

    else:
        pts = [status[1] for status in groups_status]
        match len(set(pts)):
            case 3:
                for i in range(3):
                    if pts[i] == pts[i+1]:
                        (t1, t2) = (groups_status[i][0], groups_status[i+1][0])
                        match_name = [f"{t1} vs {t2}", f"{t2} vs {t1}"]
                        cur.execute("SELECT winner FROM results WHERE match IN (?, ?)", (match_name[0], match_name[1]))
                        winner = cur.fetchone()[0]
                        if winner == t2:
                            (groups_status[i], groups_status[i+1]) = (groups_status[i+1], groups_status[i])
                
                teams_sorted = [row[0] for row in groups_status]
                return teams_sorted

            case 2: 
                
                if pts[0] == pts[1] and pts[2] == pts[3]:
                    (t1, t2, t3, t4) = (groups_status[0][0], groups_status[1][0], groups_status[2][0], groups_status[3][0])
                    match_name = [f"{t1} vs {t2}", f"{t2} vs {t1}"]
                    cur.execute("SELECT winner FROM results WHERE match IN (?, ?)", (match_name[0], match_name[1]))
                    winner = cur.fetchone()[0]
                    if winner == t2:
                        (groups_status[0], groups_status[1]) = (groups_status[1], groups_status[0])
                    
                    match_name = [f"{t3} vs {t4}", f"{t4} vs {t3}"]
                    cur.execute("SELECT winner FROM results WHERE match IN (?, ?)", (match_name[0], match_name[1]))
                    winner = cur.fetchone()[0]
                    if winner == t4:
                        (groups_status[2], groups_status[3]) = (groups_status[3], groups_status[2])
                    
                    teams_sorted = [row[0] for row in groups_status]
                    return teams_sorted

                else:
                    if pts[0] == pts[2]:
                        tied_teams = [row[0] for row in groups_status[0:3]]
                        start_idx = 0
                    elif pts[1] == pts[3]:
                        tied_teams = [row[0] for row in groups_status[1:4]]
                        start_idx = 1

                    mini_league = {team: [0, 0, 0] for team in tied_teams} #name : [pts, diff, goals]
                    
                    for pair in itertools.combinations(tied_teams, 2):
                        (t1, t2) = (pair[0], pair[1])
                        match_name = [f"{t1} vs {t2}", f"{t2} vs {t1}"]
                        cur.execute("SELECT winner, loser, goals_winner, goals_loser FROM results WHERE match IN (?, ?)", (match_name[0], match_name[1]))
                        info = cur.fetchone()
                            
                        if info[0] == t1:
                            mini_league[t1][0] += 3
                            mini_league[t1][1] += info[2] - info[3]
                            mini_league[t2][1] += info[3] - info[2]
                            mini_league[t1][2] += info[2]
                            mini_league[t2][2] += info[3]

                        elif info[0] == t2:
                            mini_league[t2][0] += 3
                            mini_league[t1][1] += info[3] - info[2]
                            mini_league[t2][1] += info[2] - info[3]
                            mini_league[t1][2] += info[3]
                            mini_league[t2][2] += info[2]

                        else:
                            mini_league[t1][0] += 1
                            mini_league[t2][0] += 1
                            mini_league[t1][2] += info[3]
                            mini_league[t2][2] += info[3]
                        
                    mini_league_list = [
                        [team, *vals]
                        for team, vals in mini_league.items()
                    ]

                    mini_league_list = sorted(
                        mini_league_list,
                        key=lambda x: (x[1], x[2], x[3]),
                        reverse=True
                    )

                    teams_mini = [row[0] for row in mini_league_list]
                    teams_val  = [row[1:] for row in mini_league_list]
                    if len(set(tuple(v) for v in teams_val)) == 3:
                        if start_idx == 0:
                            teams_sorted = teams_mini +  [groups_status[3][0]]
                        elif start_idx == 1:
                            teams_sorted = [groups_status[0][0]] + teams_mini
                    
                    elif len(set(tuple(v) for v in teams_val)) == 2:
                        teams = [row[0] for row in groups_status]
                        if teams_val[0] == teams_val[1]:
                            # 同点チーム間の既存の順位の抽出
                            if teams.index(teams_mini[0]) > teams.index(teams_mini[1]):
                                sp = teams_mini[0]
                                inf = teams_mini[1]
                            else:
                                sp = teams_mini[1]
                                inf = teams_mini[0]
                            if start_idx == 0:
                                teams_sorted = [sp, inf, teams_mini[2], groups_status[3][0]]
                            else:
                                teams_sorted = [groups_status[0][0], sp, inf, teams_mini[2]]

                        else:
                            # 同点チーム間の既存の順位の抽出
                            if teams.index(teams_mini[1]) > teams.index(teams_mini[2]):
                                sp = teams_mini[1]
                                inf = teams_mini[2]
                            else:
                                sp = teams_mini[2]
                                inf = teams_mini[1]
                            if start_idx == 0:
                                teams_sorted = [teams_mini[0], sp, inf, groups_status[3][0]]
                            else:
                                teams_sorted = [groups_status[0][0], teams_mini[2], sp, inf]

                    elif len(set(tuple(v) for v in teams_val)) == 1:
                        teams_sorted = [row[0] for row in groups_status] #各チーム完全一致なら全体の結果に帰結

                    return teams_sorted
                 
    teams_sorted = [row[0] for row in groups_status]            
    return teams_sorted

