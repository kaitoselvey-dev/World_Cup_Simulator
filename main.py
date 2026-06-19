import sqlite3
from lists import *
from functions import *
from collections import defaultdict

def main(conn, ID="kaito_dev", iso=False):
    cur = conn.cursor()
    cur.execute("UPDATE teams SET pts = 0, goals_scored = 0, goals_conceded = 0")
    cur.execute("DELETE FROM results")
    cur.execute("DELETE FROM sqlite_sequence WHERE name='results'")

    conn_dev = sqlite3.connect("developer.db")
    cur_dev = conn_dev.cursor()

    group_names = ["A","B","C","D","E","F","G","H","I","J","K","L"]
    groups = [groupA,groupB,groupC,groupD,groupE,groupF,groupG,groupH,groupI,groupJ,groupK,groupL]
    tnmt_idx = [20, 4, 28, 5, 16, 7, 12, 26, 0, 18, 6, 17, 14, 27, 10, 25, 2, 19, 24, 11, 30, 8, 22, 9]
    tournament = [None] * 32
    thirds = []

    prob_dict_score, prob_dict_win_loss = make_prob_score()

    finished_gs_results = []
    for gn in group_names:
        cur_dev.execute(f"SELECT team_a, goals_a, goals_b, team_b FROM {gn}_fin ")
        for result in cur_dev.fetchall():
            if result[1] != None and result[2] != None:
                finished_gs_results.append(result)

    predicted_gs_results = []
    for gn in group_names:
        cur.execute(f"SELECT team_a, goals_a, goals_b, team_b FROM {gn}_fin ")
        for result in cur.fetchall():
            if result[1] != None and result[2] != None:
                predicted_gs_results.append(result)

    # グループステージ実施
    for i in range(12):
        group = groups[i]
        for j in range(3):
            for k in range(3-j):
                game_group_stage(cur, group[j],group[j+k+1], predicted_gs_results, finished_gs_results, prob_dict_score, prob_dict_win_loss)

    # グループ内順位決定 & トーナメント表への割り振り
    for i, group in enumerate(groups):
        group_sorted = group_to_tournament(cur, group)

        tournament[tnmt_idx[2*i]] = group_sorted[0]
        tournament[tnmt_idx[2*i+1]] = group_sorted[1]
        thirds.append(group_sorted[2])
        
    #３位チームの割り振り
    thirds_sorted = group_to_tournament(cur, thirds, thirds=True)[:8]

    thirds_idx = {"A": 21, "B": 29, "D": 13, "E": 1, "G": 15, "I": 3, "K": 31, "L": 23}
    thirds_group = []

    for team in thirds_sorted:
        for i,g in enumerate(groups):
            if team in g:
                thirds_group.append(group_names[i])
                break
    thirds_dict = dict(zip(thirds_group, thirds_sorted))
    thirds_group.sort()

    thirds_opponent = thirds_to_opponent[tuple(thirds_group)]
    for thr_g, opp_g in zip(thirds_group, thirds_opponent):
        idx = thirds_idx[opp_g]
        tournament[idx] = thirds_dict[thr_g]

    # グループステージ結果表作成
    for i, group in enumerate(groups):
        g = group_names[i]

        cur.execute(f"DROP TABLE IF EXISTS group{g}")

        cur.execute(f"""
            CREATE TABLE group{g} AS
            SELECT *, (goals_scored - goals_conceded) AS goal_diff FROM teams
            WHERE name IN (?, ?, ?, ?)
            ORDER BY pts DESC, goal_diff DESC, goals_scored DESC
        """, group)

    # ノックアウトステージ実施
    record_add = defaultdict(lambda: {
        "ko": 0,
        32: 0,
        16: 0,
        8: 0,
        4: 0,
        3: 0,
        2: 0,
        1: 0
    })

    tournament_record = [tournament]

    for g in groups:
        for t in g:
            if t not in tournament:
                record_add[t]["ko"] = 1

    for num in [16, 8, 4, 2, 1]:
        next_round = []
        for i in range(0, len(tournament), 2):
            team1 = tournament[i]
            team2 = tournament[i + 1]
            next_round.append(game_tournament(cur, team1, team2, prob_dict_score, prob_dict_win_loss))
        tournament = next_round
        tournament_record.append(tournament)
    # 3位決定
    for_third = [x for x in tournament_record[3] if x not in tournament_record[4]]
    third = [game_tournament(cur, for_third[0], for_third[1], prob_dict_score, prob_dict_win_loss), *tournament_record[4]]
    tournament_record.insert(4, third)

    return_list = tournament_record.copy()

    if True:
        # ここに重複処理
        for i in range(6):
            tournament_record[i] = [x for x in tournament_record[i] if x not in tournament_record[i + 1]]

    for i, round_num in enumerate([32, 16, 8, 4, 3, 2, 1]):
        for team in tournament_record[i]:
            record_add[team][round_num] = 1
    
    for team, rec in record_add.items():
        cur.execute("""
            UPDATE record
            SET knocked_out = knocked_out + ?,
                r32 = r32 + ?,
                r16 = r16 + ?,
                r8 = r8 + ?,
                fourth = fourth + ?,
                third = third + ?,
                second = second + ?,
                Champion = Champion + ?
            WHERE name = ?
        """, (
            rec["ko"],
            rec[32],
            rec[16],
            rec[8],
            rec[4],
            rec[3],
            rec[2],
            rec[1],
            team
        ))
    
    cur.execute("""
        INSERT INTO results_all
        (match, winner, goals_winner, goals_loser, loser, rating_diff)
        SELECT match, winner, goals_winner, goals_loser, loser, rating_diff FROM results;
    """)

    conn.commit()

    if iso:
        for i, r in enumerate(tournament_record):
            for j, t in enumerate(r):
                tournament_record[i][j] = iso3_map[t]

    return return_list

if __name__=="__main__":
    conn = sqlite3.connect("user_db/developer.db")
    tournament = main(conn=conn, ID="developer")
    print(tournament[0])