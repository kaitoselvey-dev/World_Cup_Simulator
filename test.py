from tkinter import *
from tkinter import ttk
import sqlite3
from functions import create_user_DB, ensure_user_fin_tables
from main import main
import os
from paths import APP_DIR, ensure_app_data, resource_path
import json

BASE_DIR = APP_DIR

conn_dev = sqlite3.connect(ensure_app_data())
cur_dev = conn_dev.cursor()

root = Tk()
root.geometry("800x680")
root.minsize(800, 680)
root.resizable(True, True)
root.title("WC Simulator")

COLORS = {
    "bg": "#f4f7fb",
    "surface": "#ffffff",
    "surface_alt": "#eef3f8",
    "text": "#172033",
    "muted": "#5f6b7a",
    "primary": "#0f766e",
    "primary_dark": "#0b5f59",
    "danger": "#b42318",
    "border": "#d8e0ea",
}

FONT_BODY = ("Segoe UI", 10)
FONT_TITLE = ("Segoe UI Semibold", 22)
FONT_SECTION = ("Segoe UI Semibold", 15)


def setup_theme(root):
    root.configure(bg=COLORS["bg"])
    try:
        root.iconbitmap(resource_path("data_box/wc_trophy.ico"))
    except Exception:
        pass

    root.option_add("*Font", FONT_BODY)
    root.option_add("*Background", COLORS["bg"])
    root.option_add("*Foreground", COLORS["text"])
    root.option_add("*Entry.Background", COLORS["surface"])
    root.option_add("*Entry.Foreground", COLORS["text"])
    root.option_add("*Entry.InsertBackground", COLORS["text"])
    root.option_add("*Button.Background", COLORS["primary"])
    root.option_add("*Button.Foreground", "#ffffff")
    root.option_add("*Button.ActiveBackground", COLORS["primary_dark"])
    root.option_add("*Button.ActiveForeground", "#ffffff")
    root.option_add("*Button.Relief", "flat")
    root.option_add("*Button.BorderWidth", 0)
    root.option_add("*Button.Padx", 12)
    root.option_add("*Button.Pady", 6)

    style = ttk.Style(root)
    try:
        style.theme_use("clam")
    except TclError:
        pass

    style.configure("TCombobox", padding=5, fieldbackground=COLORS["surface"])
    style.configure(
        "Treeview",
        background=COLORS["surface"],
        fieldbackground=COLORS["surface"],
        foreground=COLORS["text"],
        rowheight=26,
        borderwidth=0,
    )
    style.configure(
        "Treeview.Heading",
        background=COLORS["surface_alt"],
        foreground=COLORS["text"],
        font=("Segoe UI Semibold", 10),
        padding=6,
    )
    style.map("Treeview", background=[("selected", COLORS["primary"])])

setup_theme(root)

class Application(Frame):
    def __init__(self, root=None):
        super().__init__(root, width=980, height=580,
                         borderwidth=0, relief='flat', bg=COLORS["bg"])
        self.root = root
        self.pack(expand=True, fill="both", padx=18, pady=18)
        self.pack_propagate(0)
        self.main_title = StringVar(value="main_title")
        self.create_widgets() 

    # functions
    def show_start(self):
        self.forget()
        self.start_frame.pack(expand=True)

    def forget(self):
        self.root.geometry("800x680")
        self.start_frame.pack_forget()
        self.main_frame.pack_forget()
        self.simulation_frame.pack_forget()
        self.prediction_frame.pack_forget()
        self.dev_frame.pack_forget()
        self.dev_group_stage_frame.pack_forget()
        self.dev_tournament_frame.pack_forget()
        self.see_tournament_frame.pack_forget()

    def show_main(self):
        self.forget()
        self.main_frame.pack(expand=True, fill="both")

    def login(self):

        self.ID = self.login_ID_box.get()
        password = self.login_password_box.get()

        cur_dev.execute("SELECT password FROM user_pw WHERE user_ID = ?", (self.ID,))
        existing = cur_dev.fetchone()
        if not existing:
            if self.ID == "":
                error_label = Label(self.start_frame, text="Enter your ID")
                error_label.pack()
                self.start_frame.after(1000, error_label.destroy)
            else:
                error_label = Label(self.start_frame, text="This ID does not exist")
                error_label.pack()
                self.start_frame.after(1000, error_label.destroy)
                self.login_ID_box.delete(0, END)
                self.login_password_box.delete(0, END)

        else:
            if existing[0] == password:
                self.forget()
                self.show_main()
                self.login_ID_box.delete(0, END)
                self.login_password_box.delete(0, END)  
                self.main_title.set(f"{self.ID}'s main page")    

                db_path = os.path.join(BASE_DIR, "user_db", f"{self.ID}.db")
                self.conn_user = sqlite3.connect(db_path)
                self.cur_user = self.conn_user.cursor()

            else:
                error_label = Label(self.start_frame, text="Wrong password")
                error_label.pack()
                self.start_frame.after(1000, error_label.destroy)
                self.login_password_box.delete(0, END)      

    def sign_up(self):
        self.ID = self.login_ID_box.get()
        password = self.login_password_box.get()
        cur_dev.execute("SELECT * FROM user_pw WHERE user_ID = ?", (self.ID,))

        check = cur_dev.fetchone()
        if check:
            error_label = Label(self.start_frame, text="This ID is already used")
            error_label.pack()
            self.start_frame.after(1000, error_label.destroy)

        elif self.ID == "" or password == "":
            error_label = Label(self.start_frame, text="Enter ID or password")
            error_label.pack()
            self.start_frame.after(1000, error_label.destroy)
        else:
            cur_dev.execute("""
            insert into user_pw (user_ID, password) values (?, ?)
            """, (self.ID, password))
            conn_dev.commit()
            create_user_DB(self.ID)
            self.main_title.set(f"{self.ID}'s main page") 
            self.forget()
            self.show_main()

            db_path = os.path.join(BASE_DIR, "user_db", f"{self.ID}.db")
            self.conn_user = sqlite3.connect(db_path)
            self.cur_user = self.conn_user.cursor()

            self.login_ID_box.delete(0, END)
            self.login_password_box.delete(0, END)

    def reset_data(self):
        self.cur_user.execute("""
                                UPDATE record
                                SET knocked_out = 0,
                                    r32 = 0,
                                    r16 = 0,
                                    r8 = 0,
                                    fourth = 0,
                                    third = 0,
                                    second = 0,
                                    Champion = 0
                            """)
        self.cur_user.execute("DELETE FROM results_all")
        self.cur_user.execute("UPDATE sqlite_sequence SET seq = 0 where name = 'results_all'")

        success_label = Label(self.main_footer_frame, text="Data has been successfully reset")
        success_label.pack(before=self.reset_button)
        self.start_frame.after(1000, success_label.destroy)
        self.conn_user.commit()

    def simulation(self):
        try:
            num = int(self.attempt_num_box.get())
            if num > 9999:
                error_label = Label(self.attempt_num_frame, text="overlimit")
                error_label.pack(pady=5)
                self.start_frame.after(1000, error_label.destroy)
            elif num == 0:
                self.cur_user.execute("SELECT seq FROM sqlite_sequence WHERE name = 'results_all'")
                total_num = int(int(self.cur_user.fetchone()[0])/104)
                if total_num == 0:
                    error_label = Label(self.attempt_num_frame, text="underlimit (no data)")
                    error_label.pack(pady=5)
                    self.start_frame.after(1000, error_label.destroy)
                else:
                    for _ in range(num):
                        main(self.conn_user, self.ID)
                    self.attempt_num_box.delete(0, END)
                    self.forget()
                    self.simulation_frame.pack(expand=True, fill="both")
                    self.show_result_table()
            else:
                for _ in range(num):
                    main(self.conn_user, self.ID)
                self.attempt_num_box.delete(0, END)
                self.forget()
                self.simulation_frame.pack(expand=True, fill="both")
                self.show_result_table()

        except ValueError:
            error_label = Label(self.attempt_num_frame, text="input an integer")
            error_label.pack(pady=5)
            self.start_frame.after(1000, error_label.destroy)

    def re_simulation(self):
        try:
            num = int(self.re_attempt_num_box.get())
            for _ in range(num):
                main(self.conn_user, self.ID)
            self.re_attempt_num_box.delete(0, END)
            self.show_result_table()

        except ValueError:
            error_label = Label(self.re_attempt_num_frame, text="input an integer")
            error_label.pack(pady=5)
            self.start_frame.after(1000, error_label.destroy)

    def show_result_table(self):
        for widget in self.simulation_body_frame.winfo_children():
            widget.destroy()

        self.root.geometry("1000x680")

        self.cur_user.execute("SELECT seq FROM sqlite_sequence WHERE name = 'results_all'")
        total_num = int(int(self.cur_user.fetchone()[0])/104)

        self.cur_user.execute("SELECT * FROM record")
        rows = self.cur_user.fetchall()

        self.cur_user.execute("PRAGMA table_info(record)")
        columns = [col[1] for col in self.cur_user.fetchall()]
        columns[0] = f"n = {total_num}"

        # 表示用データを先に作っておく
        display_rows = []
        for row in rows:
            display_row = [row[0]]
            for value in row[1:]:
                percent = round(value / total_num * 100, 1)
                display_row.append(percent)  # ←ソート用に数値のまま保持
            display_rows.append(display_row)

        table_frame = Frame(self.simulation_body_frame)
        table_frame.pack(expand=True, fill="both")

        y_scroll = Scrollbar(table_frame, orient="vertical")
        y_scroll.pack(side="right", fill="y")

        x_scroll = Scrollbar(table_frame, orient="horizontal")
        x_scroll.pack(side="bottom", fill="x")

        tree = ttk.Treeview(
            table_frame,
            columns=columns,
            show="headings",
            yscrollcommand=y_scroll.set,
            xscrollcommand=x_scroll.set
        )

        y_scroll.config(command=tree.yview)
        x_scroll.config(command=tree.xview)

        # ソート状態管理: {col: "asc" | "desc" | None}
        sort_state = {col: None for col in columns}

        def refresh_tree(data):
            tree.delete(*tree.get_children())
            for r in data:
                display = [r[0]] + [f"{v}%" for v in r[1:]]
                tree.insert("", END, values=display)

        def sort_by(col):
            col_idx = columns.index(col)
            state = sort_state[col]

            # 状態を次に進める: None→asc→desc→None
            if state is None:
                sort_state[col] = "asc"
            elif state == "asc":
                sort_state[col] = "desc"
            else:
                sort_state[col] = None

            # 他の列のソート状態をリセット
            for c in columns:
                if c != col:
                    sort_state[c] = None

            new_state = sort_state[col]

            if new_state is None:
                sorted_data = display_rows  # 元の順序に戻す
            else:
                sorted_data = sorted(
                    display_rows,
                    key=lambda r: r[col_idx] if isinstance(r[col_idx], (int, float)) else 0,
                    reverse=(new_state == "desc")
                )

            refresh_tree(sorted_data)

            # ヘッダーに矢印を表示
            for c in columns:
                s = sort_state[c]
                arrow = " ▲" if s == "asc" else " ▼" if s == "desc" else ""
                tree.heading(c, text=c + arrow)

        for col in columns:
            tree.heading(col, text=col, command=lambda c=col: sort_by(c))
            tree.column(col, anchor="center", width=100)

        refresh_tree(display_rows)

        tree.pack(expand=True, fill="both")

    def score_prediction(self):
        self.group_name = self.group.get()[-1]
        if self.group_name in "ABCDEFGHIJKL":
            self.forget()
            self.prediction_frame.pack(expand=True, fill="both")
            self.make_match_list()
        else:
            error_label = Label(self.main_body_frame, text="group unselected")
            error_label.pack()
            self.main_body_frame.after(1000, error_label.destroy)

    def make_match_list(self):
        self.cur_user.execute(f"SELECT rating_a, team_a, goals_a, goals_b, team_b, rating_b FROM {self.group_name}_fin ")
        match_list = self.cur_user.fetchall()
        cur_dev.execute(f"SELECT rating_a, team_a, goals_a, goals_b, team_b, rating_b FROM {self.group_name}_fin")
        match_finished = cur_dev.fetchall()
        fin_match_list = []
        fin_match_set = []
        fin_match_goals = []
        for f in match_finished:
            if f[2] != None and f[3] != None:
                fin_match_list.append((f[1], f[4]))
                fin_match_set.append({f[1], f[4]})
                fin_match_goals.append((f[2], f[3]))

        self.match_name = [(m[1], m[4]) for m in match_list]
        for widget in self.prediction_body_frame.winfo_children():
            widget.destroy()

        self.goal_as_input = []
        self.goal_bs_input = []

        for match in match_list:
            rating_a, team_a, goals_a, goals_b, team_b, rating_b = match
            row = Frame(self.prediction_body_frame)
            row.pack(pady=10)

            Label(row, text=rating_a, width=6).pack(side="left")
            Label(row, text=team_a, width=20).pack(side="left")

            if {team_a, team_b} in fin_match_set:
                idx = fin_match_set.index({team_a, team_b})
                Label(row, text=fin_match_goals[idx][0], width=3, justify="center").pack(side="left", padx=2)
                Label(row, text="-").pack(side="left")
                Label(row, text=fin_match_goals[idx][1], width=3, justify="center").pack(side="left", padx=2)

                self.goal_as_input.append(StringVar(value="fin"))
                self.goal_bs_input.append(StringVar(value="fin"))

            else:
                goal_a_entry = Entry(row, width=3, justify="center")
                goal_a_entry.pack(side="left", padx=2)

                Label(row, text="-").pack(side="left")

                goal_b_entry = Entry(row, width=3, justify="center")
                goal_b_entry.pack(side="left", padx=2)


                if goals_a != None and goals_b != None:
                    goal_a_entry.insert(0, goals_a)
                    goal_b_entry.insert(0, goals_b)   

                self.goal_as_input.append(goal_a_entry)
                self.goal_bs_input.append(goal_b_entry)                

            Label(row, text=team_b, width=20).pack(side="left")
            Label(row, text=rating_b, width=6).pack(side="left")

        Button(self.prediction_body_frame, text="clear", width=10, command=self.reset_prediction).pack(pady=5)

        reset_frame = Frame(self.prediction_body_frame)
        reset_frame.pack()
        Label(reset_frame, text="RESET DATA?").pack(side="left")
        self.choice = StringVar(value="NO")
        Radiobutton(reset_frame, text="NO", variable=self.choice, value="NO").pack(side="left")
        Radiobutton(reset_frame, text="YES", variable=self.choice, value="YES").pack(side="left")
        Button(reset_frame, text="submit", width=10, command=self.submit_prediction).pack(pady=5, side="right")

    def submit_prediction(self):
        if self.choice.get() == "YES":
            self.cur_user.execute("""
                                    UPDATE record
                                    SET knocked_out = 0,
                                        r32 = 0,
                                        r16 = 0,
                                        r8 = 0,
                                        fourth = 0,
                                        third = 0,
                                        second = 0,
                                        Champion = 0
                                """)
            self.cur_user.execute("DELETE FROM results_all")
            self.cur_user.execute("UPDATE sqlite_sequence SET seq = 0 where name = 'results_all'")
        for i, (ga, gb) in enumerate(zip(self.goal_as_input, self.goal_bs_input)):
            a = ga.get()
            b = gb.get()
            if a.isdigit() and b.isdigit():
                self.cur_user.execute(f"""
                                UPDATE {self.group_name}_fin
                                SET goals_a = ?, goals_b = ?
                                WHERE team_a = ?
                                AND team_b = ? 
                                """, (a, b, *self.match_name[i]))
                self.conn_user.commit()
            
            elif a == "" and b == "":
                a = None
                b = None
                self.cur_user.execute(f"""
                                UPDATE {self.group_name}_fin
                                SET goals_a = ?, goals_b = ?
                                WHERE team_a = ?
                                AND team_b = ? 
                                """, (a, b, *self.match_name[i]))
                self.conn_user.commit()
        
        self.forget()
        self.main_frame.pack(expand=True, fill="both")

    def reset_prediction(self):
        for e in self.goal_as_input:
            try:
                e.delete(0, END)
            except AttributeError:
                pass
        for e in self.goal_bs_input:
            try:
                e.delete(0, END)
            except AttributeError:
                pass

    def see_tournament(self):
        self.fin_tournament_32 = self.get_tournament()
        self.forget()
        self.see_tournament_frame.pack(expand=True, fill="both")
        self.make_tm_match_list()

    def input_fin_tournament(self):
                
        cur_dev.execute("""
        SELECT round32, round16, round8, round4, round2, champion
        FROM tournament_fin
        WHERE id=1
        """)

        row = cur_dev.fetchone()
        if row is None or all(v is None for v in row):
            return

        if row[0] is not None:

            dev_t_32 = json.loads(row[0])
            dev_t_16 = json.loads(row[1])
            dev_t_8 = json.loads(row[2])
            dev_t_4 = json.loads(row[3])
            dev_t_2 = json.loads(row[4])
            champion = row[5]

        for button, text in zip(self.buttons_32l + self.buttons_32r, dev_t_32):
            button.config(text=text)

        for i, (button, text) in enumerate(zip(self.buttons_16l + self.buttons_16r, dev_t_16)):
            if text != "None":
                button.config(text=text)
                if i < 8:
                    self.buttons_32l[2*i].config(state="disabled")
                    self.buttons_32l[2*i+1].config(state="disabled")
                else:

                    self.buttons_32r[2*(i-8)].config(state="disabled")
                    self.buttons_32r[2*(i-8)+1].config(state="disabled")

        for i, (button, text) in enumerate(zip(self.buttons_8l + self.buttons_8r, dev_t_8)):
            if text != "None":
                button.config(text=text)
                if i < 4:
                    self.buttons_16l[2*i].config(state="disabled")
                    self.buttons_16l[2*i+1].config(state="disabled")
                else:
                    self.buttons_16r[2*(i-4)].config(state="disabled")
                    self.buttons_16r[2*(i-4)+1].config(state="disabled")

        for i, (button, text) in enumerate(zip(self.buttons_4l + self.buttons_4r, dev_t_4)):
            if text != "None":
                button.config(text=text, state="disabled")
                if i < 2:
                    self.buttons_8l[2*i].config(state="disabled")
                    self.buttons_8l[2*i+1].config(state="disabled")
                else:
                    self.buttons_8r[2*(i-2)].config(state="disabled")
                    self.buttons_8r[2*(i-2)+1].config(state="disabled")

        if dev_t_2[0] != "None":
            self.button_2l.config(text=dev_t_2[0])
            self.buttons_4l[0].config(state="disabled")
            self.buttons_4l[1].config(state="disabled")
        if dev_t_2[1] != "None":
            self.button_2r.config(text=dev_t_2[1])
            self.buttons_4r[0].config(state="disabled")
            self.buttons_4r[1].config(state="disabled")

        if champion != "None":
            self.button_champ.config(text=champion)
            self.button_2l.config(state="disabled")
            self.button_2r.config(state="disabled")

    def make_tm_match_list(self):
        for widget in self.see_tournament_body_frame.winfo_children():
            widget.destroy()

        self.root.geometry("1700x900")
        self.root.maxsize(1700, 900)
        canvas = Canvas(self.see_tournament_body_frame, width=1700, height=655)
        hbar = Scrollbar(self.see_tournament_body_frame, orient="horizontal", command=canvas.xview)
        hbar.pack(side="bottom", fill="x")
        vbar = Scrollbar(self.see_tournament_body_frame, orient="vertical", command=canvas.yview)
        vbar.pack(side="right", fill="y")
        canvas.configure(xscrollcommand=hbar.set, yscrollcommand=vbar.set)

        canvas.pack(fill="both", expand=True)

        def place_btn(widget, x, y):
            canvas.create_window(x, y, window=widget, anchor="nw")

        self.buttons_32l = []
        for i,m in enumerate(self.fin_tournament_32[:8]):
            self.buttons_32l.append(Button(canvas, text=m[0], width=20, command=lambda idx=i*2: self.to_16l(idx), disabledforeground="#ffffff"))
            self.buttons_32l.append(Button(canvas, text=m[1], width=20, command=lambda idx=i*2+1: self.to_16l(idx), disabledforeground="#ffffff"))
            place_btn(self.buttons_32l[i*2],   0, 85*i)
            place_btn(self.buttons_32l[i*2+1], 0, 85*i+35)

        pad = [16, 60, 145]

        self.buttons_16l = []
        self.buttons_8l = []
        self.buttons_4l = []
        self.buttons_l = [self.buttons_16l, self.buttons_8l, self.buttons_4l]
        funcs_l = [self.to_8l, self.to_4l, self.to_2l]
        for i in range(3):
            for j in range(2**(3-i)):
                b = Button(canvas, text="None", width=20, command=lambda idx1=i, idx2=j: funcs_l[idx1](idx2), disabledforeground="#ffffff")
                place_btn(b, 200*(i+1), j * 85*2**(i) + pad[i])
                self.buttons_l[i].append(b)

        self.button_2l = Button(canvas, text="None", width=20, command=lambda: self.to_champ(0), disabledforeground="#ffffff")
        place_btn(self.button_2l, 650, 315)

        self.buttons_16r = []
        self.buttons_8r = []
        self.buttons_4r = []
        self.buttons_r = [self.buttons_16r, self.buttons_8r, self.buttons_4r]
        funcs_r = [self.to_8r, self.to_4r, self.to_2r]
        for i in range(3):
            for j in range(2**(1+i)):
                b = Button(canvas, text="None", width=20, command=lambda idx1=2-i, idx2=j: funcs_r[idx1](idx2), disabledforeground="#ffffff")
                place_btn(b, 200*(i+4) + 100, j * 85*2**(2-i) + pad[2-i])
                self.buttons_r[2-i].append(b)

        self.button_2r = Button(canvas, text="None", width=20, command=lambda: self.to_champ(1), disabledforeground="#ffffff")
        place_btn(self.button_2r, 850, 315)

        self.buttons_32r = []
        for i, m in enumerate(self.fin_tournament_32[8:]):
            self.buttons_32r.append(Button(canvas, text=m[0], width=20, command=lambda idx=i*2: self.to_16r(idx), disabledforeground="#ffffff"))
            self.buttons_32r.append(Button(canvas, text=m[1], width=20, command=lambda idx=i*2+1: self.to_16r(idx), disabledforeground="#ffffff"))
            place_btn(self.buttons_32r[i*2],   1500, 85*i)
            place_btn(self.buttons_32r[i*2+1], 1500, 85*i+35)

        self.button_champ = Button(canvas, text="None", width=20, disabledforeground="#ffffff")
        place_btn(self.button_champ, 750, 380)
        lbl = Label(canvas, text="Champion 🏆", font="Arial")
        canvas.create_window(765, 350, window=lbl, anchor="nw")

        for i in range(8):
            canvas.create_line(145, 85*i+12, 175, 85*i+12)
            canvas.create_line(145, 85*i+47, 175, 85*i+47)
            canvas.create_line(175, 85*i+12, 175, 85*i+48)
            canvas.create_line(175, 85*i+30, 200, 85*i+30)

        for i in range(4):
            canvas.create_line(345, 85*2*i+30, 375, 85*2*i+30)
            canvas.create_line(345, 85*2*i+115, 375, 85*2*i+115)
            canvas.create_line(375, 85*2*i+30, 375, 85*2*i+116)
            canvas.create_line(375, 85*2*i+73, 400, 85*2*i+73)

        for i in range(2):
            canvas.create_line(545, 85*4*i+73, 575, 85*4*i+73)
            canvas.create_line(545, 85*4*i+243, 575, 85*4*i+243)
            canvas.create_line(575, 85*4*i+73, 575, 85*4*i+244)
            canvas.create_line(575, 85*4*i+159, 600, 85*4*i+159)

        for i in range(8):
            canvas.create_line(1505, 85*i+12, 1470, 85*i+12)
            canvas.create_line(1505, 85*i+47, 1470, 85*i+47)
            canvas.create_line(1470, 85*i+12, 1470, 85*i+49)
            canvas.create_line(1470, 85*i+30, 1445, 85*i+30)

        for i in range(4):
            canvas.create_line(1300, 85*2*i+30, 1270, 85*2*i+30)
            canvas.create_line(1300, 85*2*i+115, 1270, 85*2*i+115)
            canvas.create_line(1270, 85*2*i+30, 1270, 85*2*i+116)
            canvas.create_line(1270, 85*2*i+73, 1245, 85*2*i+73)

        for i in range(2):
            canvas.create_line(1100, 85*4*i+73, 1070, 85*4*i+73)
            canvas.create_line(1100, 85*4*i+243, 1070, 85*4*i+243)
            canvas.create_line(1070, 85*4*i+73, 1070, 85*4*i+244)
            canvas.create_line(1070, 85*4*i+159, 1045, 85*4*i+159)

        canvas.create_line(610, 159, 610, 499)
        canvas.create_line(610, 330, 680, 330)
        canvas.create_line(1035, 159, 1035, 499)
        canvas.create_line(1035, 330, 965, 330)

        def _scroll_y(event):
            canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")

        def _scroll_x(event):
            canvas.xview_scroll(int(-1 * (event.delta / 120)), "units")

        def _on_mousewheel(event):
            if event.state & 0x4:  # Ctrlキーが押されているか
                _scroll_x(event)
            else:
                _scroll_y(event)

        canvas.bind("<MouseWheel>", _on_mousewheel)

        canvas.configure(scrollregion=(0,0,1700,655))

        self.input_fin_tournament()

    def clear_all(self):
        cur_dev.execute("""
        SELECT round32, round16, round8, round4, round2, champion FROM tournament_fin WHERE id=1
        """)

        row = cur_dev.fetchone()
        dev_t_16 = []
        dev_t_8 = []
        dev_t_4 = []
        dev_t_2 = []
        champion = []

        if row[0] is not None:
            dev_t_16 = json.loads(row[1])
            dev_t_8 = json.loads(row[2])
            dev_t_4 = json.loads(row[3])
            dev_t_2 = json.loads(row[4])
            champion = row[5]
        
        for b in self.buttons_16l + self.buttons_16r:
            if b["text"] not in dev_t_16:
                b.config(text="None", bg=COLORS["primary"], activebackground=COLORS["primary_dark"])
        
        for b in self.buttons_8l + self.buttons_8r:
            if b["text"] not in dev_t_8:
                b.config(text="None", bg=COLORS["primary"], activebackground=COLORS["primary_dark"])

        for b in self.buttons_4l + self.buttons_4r:
            if b["text"] not in dev_t_4:
                b.config(text="None", bg=COLORS["primary"], activebackground=COLORS["primary_dark"])

        if self.button_2l["text"] not in dev_t_2:
            self.button_2l.config(text="None", bg=COLORS["primary"], activebackground=COLORS["primary_dark"])

        if self.button_2r["text"] not in dev_t_2:
            self.button_2r.config(text="None", bg=COLORS["primary"], activebackground=COLORS["primary_dark"])
        
        if self.button_champ["text"] != champion:
            self.button_champ.config(text="None", bg=COLORS["primary"], activebackground=COLORS["primary_dark"])
            
    def create_widgets(self):
        # permenant
        quit_btn = Button(self, text="close", width=10, command=self.root.destroy)
        quit_btn.pack(side='bottom')

        # start frame
        self.start_frame = Frame(self)
        self.start_frame.pack(expand=True)
        Label(self.start_frame, text="World Cup Simulator", font=FONT_TITLE, pady=10).pack()
        
        Label(self.start_frame, text="Sign in/up and predict the results!").pack(pady=10)

        login_ID_row = Frame(self.start_frame)
        login_ID_row.pack(pady=5)
        Label(login_ID_row, text="ID ", width=10).pack(side="left")
        self.login_ID_box = Entry(login_ID_row, width=10)
        self.login_ID_box.pack(side="left")

        login_password_row = Frame(self.start_frame)
        login_password_row.pack(pady=5)
        Label(login_password_row, text="password ", width=10).pack(side="left")
        self.login_password_box = Entry(login_password_row, width=10, show="*")
        self.login_password_box.pack(side="left")

        Button(self.start_frame, text="sign in", width=10, command=self.login).pack(pady=5)
        Button(self.start_frame, text="sign up", width=10, command=self.sign_up).pack(pady=5)
        Button(self.start_frame, text="developer page", width=15, command=self.dev_page).pack(pady=5)

        Label(self.start_frame, text="Update the finished games at developer page").pack(pady=10)

        # main page frame
        self.main_frame = Frame(self)
        self.group = StringVar()
        self.group.set("choose the group")

            # header
        main_header_frame = Frame(self.main_frame)
        main_header_frame.pack()
        Label(main_header_frame, textvariable=self.main_title, font=FONT_TITLE).pack(pady=(0, 18))

            # body
        main_margin_frame = Frame(self.main_frame)
        main_margin_frame.pack(expand=True, fill="both")
        self.main_body_frame = Frame(main_margin_frame)
        self.main_body_frame.pack(expand=True)


        self.attempt_num_frame = Frame(self.main_body_frame)
        self.attempt_num_frame.pack(pady=5)

        Label(self.attempt_num_frame, text="number of attempts", width=20).pack(side="left")
        self.attempt_num_box = Entry(self.attempt_num_frame, width=10, justify="center")
        self.attempt_num_box.pack(side="left", padx=5)

        group_combo_frame = Frame(self.main_body_frame)
        group_combo_frame.pack(pady=5)

        group_combo = ttk.Combobox(group_combo_frame, textvariable=self.group, state="readonly")
        group_combo["values"] = ('Group A', 'Group B', 'Group C', 'Group D', 'Group E', 'Group F',
                                'Group G', 'Group H', 'Group I', 'Group J', 'Group K', 'Group L')
        group_combo.pack(side="left", padx=5)

        button_frame = Frame(self.main_body_frame)
        button_frame.pack(pady=10)

        Button(button_frame, text="simulation", width=15, command=self.simulation).pack(pady=5)
        Button(button_frame, text="score prediction", width=15, command=self.score_prediction).pack(pady=5)
        Button(button_frame, text="see tournament", width=15, command=self.see_tournament).pack(pady=5)

            # footer        
        self.main_footer_frame = Frame(self.main_frame)    
        self.main_footer_frame.pack(fill="x")
        self.reset_button = Button(self.main_footer_frame, text="reset data", width=15, command=self.reset_data)
        self.reset_button.pack(pady=5)
        Button(self.main_footer_frame, text="return", width=10, command=self.show_start).pack(pady=5)

        # simulation frame
        self.simulation_frame = Frame(self)

            # header
        simulation_header_frame = Frame(self.simulation_frame)
        simulation_header_frame.pack()
        Label(simulation_header_frame, text="Simulation Result", font=FONT_TITLE).pack(side="top", pady=(0, 14))

            # main
        simulation_margin_frame = Frame(self.simulation_frame)
        simulation_margin_frame.pack(expand=True, fill="both")
        self.simulation_body_frame = Frame(simulation_margin_frame)
        self.simulation_body_frame.pack(expand=True, fill="both")

            # footer
        simulation_footer_frame = Frame(self.simulation_frame)
        simulation_footer_frame.pack(fill="x")

        self.re_attempt_num_frame = Frame(simulation_footer_frame)
        self.re_attempt_num_frame.pack(pady=5)
        Label(self.re_attempt_num_frame, text="number of attempts", width=20).pack(side="left")
        self.re_attempt_num_box = Entry(self.re_attempt_num_frame, width=10, justify="center")
        self.re_attempt_num_box.pack( padx=5,side="left")
        Button(self.re_attempt_num_frame, text="simulation", width=15, command=self.re_simulation).pack(pady=5, padx=5, side="right")

        Button(simulation_footer_frame, text="return", width=10, command=self.show_main).pack(pady=5, side="bottom")

        # score prediction frame
        self.prediction_frame = Frame(self)

            # header
        prediction_header_frame = Frame(self.prediction_frame)
        prediction_header_frame.pack()
        Label(prediction_header_frame, text="Score Prediction", font=FONT_TITLE).pack(side="top", pady=(0, 14))

            # main
        prediction_margin_frame = Frame(self.prediction_frame)
        prediction_margin_frame.pack(expand=True, fill="both")
        self.prediction_body_frame = Frame(prediction_margin_frame)
        self.prediction_body_frame.pack(expand=True)

            # footer
        prediction_footer_frame = Frame(self.prediction_frame)
        prediction_footer_frame.pack(fill="x")
        Button(prediction_footer_frame, text="return", width=10, command=self.show_main).pack(pady=5, side="bottom")

        # see tournament frame
        self.see_tournament_frame = Frame(self)

            # header
        see_tournament_header_frame = Frame(self.see_tournament_frame)
        see_tournament_header_frame.pack()
        Label(see_tournament_header_frame, text="See Tournament Stage", font=FONT_TITLE).pack(side="top", pady=(0, 14))
        Label(see_tournament_header_frame, text="Based on finished games, your prediction, and simulation").pack(side="top", pady=(0, 14))

            # main
        see_tournament_margin_frame = Frame(self.see_tournament_frame)
        see_tournament_margin_frame.pack(expand=True, fill="both")
        self.see_tournament_body_frame = Frame(see_tournament_margin_frame)
        self.see_tournament_body_frame.pack(expand=True, fill="both")

            # footer
        see_tournament_footer_frame = Frame(self.see_tournament_frame)
        see_tournament_footer_frame.pack()
        Button(see_tournament_footer_frame, text="return", width=10, command=self.show_main).pack(padx=5, pady=5, side="left")
        Button(see_tournament_footer_frame, text="clear all", width=10, command=self.clear_all).pack(padx=5, pady=5, side="right")

        ## developer frames ##

        # developer page frame
        self.dev_frame = Frame(self)
        self.dev_group = StringVar()
        self.dev_group.set("choose the group")
            # header
        dev_header_frame = Frame(self.dev_frame)
        dev_header_frame.pack()
        Label(dev_header_frame, text="Developer Tools", font=FONT_TITLE).pack(side="top", pady=(0, 14))
        Label(dev_header_frame, text="Choose the group to update finished games in group stage").pack(pady=10)
        Label(dev_header_frame, text="Updated games will be applied to any simulation").pack(pady=10)

            # main
        dev_margin_frame = Frame(self.dev_frame)
        dev_margin_frame.pack(expand=True, fill="both")
        self.dev_body_frame = Frame(dev_margin_frame)
        self.dev_body_frame.pack(expand=True)

        dev_group_combo = ttk.Combobox(self.dev_body_frame, textvariable=self.dev_group, state="readonly")
        dev_group_combo["values"] = ('Group A', 'Group B', 'Group C', 'Group D', 'Group E', 'Group F', 'Group G', 'Group H', 'Group I', 'Group J', 'Group K', 'Group L')
        dev_group_combo.pack(pady=5)
        Button(self.dev_body_frame, text="update group stage", width=25, command=self.dev_group_stage).pack(pady=5)
        Button(self.dev_body_frame, text="update tournament stage", width=25, command=self.dev_tournament).pack(pady=5)

            # footer
        dev_footer_frame = Frame(self.dev_frame)
        dev_footer_frame.pack(fill="x")
        Button(dev_footer_frame, text="return", width=10, command=self.show_start).pack(pady=5, side="bottom")

        # dev update group stage frame
        self.dev_group_stage_frame = Frame(self)

            # header
        dev_group_stage_header_frame = Frame(self.dev_group_stage_frame)
        dev_group_stage_header_frame.pack()
        Label(dev_group_stage_header_frame, text="Update Group Stage", font=FONT_TITLE).pack(side="top", pady=(0, 14))

            # main
        dev_group_stage_margin_frame = Frame(self.dev_group_stage_frame)
        dev_group_stage_margin_frame.pack(expand=True, fill="both")
        
        self.dev_group_stage_body_frame = Frame(dev_group_stage_margin_frame)
        self.dev_group_stage_body_frame.pack(expand=True)
            # footer
        dev_group_stage_footer_frame = Frame(self.dev_group_stage_frame)
        dev_group_stage_footer_frame.pack(fill="x")
        Button(dev_group_stage_footer_frame, text="return", width=10, command=self.show_start).pack(pady=5, side="bottom")

        # dev update tournament frame
        self.dev_tournament_frame = Frame(self)

            # header
        dev_tournament_header_frame = Frame(self.dev_tournament_frame)
        dev_tournament_header_frame.pack()
        Label(dev_tournament_header_frame, text="Update Tournament Stage", font=FONT_TITLE).pack(side="top", pady=(0, 14))

            # main
        dev_tournament_margin_frame = Frame(self.dev_tournament_frame)
        dev_tournament_margin_frame.pack(expand=True, fill="both")
        self.dev_tournament_body_frame = Frame(dev_tournament_margin_frame)
        self.dev_tournament_body_frame.pack(expand=True, fill="both")

            # footer
        dev_tournament_footer_frame = Frame(self.dev_tournament_frame)
        dev_tournament_footer_frame.pack()
        Button(dev_tournament_footer_frame, text="return", width=10, command=self.show_start).pack(padx=5, pady=5, side="left")
        Button(dev_tournament_footer_frame, text="clear all", width=10, command=self.dev_clear_all).pack(padx=5, pady=5, side="right")
        Button(dev_tournament_footer_frame, text="submit", width=10, command=self.dev_submit_tm).pack(padx=5, pady=5, side="bottom")


    ## developer tools ##
    def dev_page(self):
        self.forget()
        self.dev_frame.pack(expand=True, fill="both")

    def dev_group_stage(self):
        self.dev_group_name = self.dev_group.get()[-1]
        if self.dev_group_name in "ABCDEFGHIJKL":
            self.forget()
            self.dev_group_stage_frame.pack(expand=True, fill="both")
            self.dev_make_gs_match_list()
        else:
            error_label = Label(self.dev_body_frame, text="group unselected")
            error_label.pack()
            self.dev_body_frame.after(1000, error_label.destroy)

    def dev_make_gs_match_list(self):
        cur_dev.execute(f"SELECT rating_a, team_a, goals_a, goals_b, team_b, rating_b FROM {self.dev_group_name}_fin ")
        match_list = cur_dev.fetchall()
        self.dev_match_name = [(m[1], m[4]) for m in match_list]
        for widget in self.dev_group_stage_body_frame.winfo_children():
            widget.destroy()

        self.dev_goal_as_input = []
        self.dev_goal_bs_input = []

        for match in match_list:
            rating_a, team_a, goals_a, goals_b, team_b, rating_b = match
            row = Frame(self.dev_group_stage_body_frame)
            row.pack(pady=10)

            Label(row, text=rating_a, width=6).pack(side="left")
            Label(row, text=team_a, width=20).pack(side="left")

            goal_a_entry = Entry(row, width=3, justify="center")
            goal_a_entry.pack(side="left", padx=2)

            Label(row, text="-").pack(side="left")

            goal_b_entry = Entry(row, width=3, justify="center")
            goal_b_entry.pack(side="left", padx=2)

            if goals_a != None and goals_b != None:
                goal_a_entry.insert(0, goals_a)
                goal_b_entry.insert(0, goals_b)

            Label(row, text=team_b, width=20).pack(side="left")
            Label(row, text=rating_b, width=6).pack(side="left")
            self.dev_goal_as_input.append(goal_a_entry)
            self.dev_goal_bs_input.append(goal_b_entry)
        
        Button(self.dev_group_stage_body_frame, text="clear", width=10, command=self.dev_reset_results).pack(pady=5)

        dev_reset_frame = Frame(self.dev_group_stage_body_frame)
        dev_reset_frame.pack()
        Label(dev_reset_frame, text="RESET DATA?").pack(side="left")
        self.dev_choice = StringVar(value="NO")
        Radiobutton(dev_reset_frame, text="NO", variable=self.dev_choice, value="NO").pack(side="left")
        Radiobutton(dev_reset_frame, text="YES", variable=self.dev_choice, value="YES").pack(side="left")
        Button(self.dev_group_stage_body_frame, text="submit", width=10, command=self.dev_submit_results).pack(pady=5)

    def dev_submit_results(self):
        if self.dev_choice.get() == "YES":
            user_db_dir = os.path.join(BASE_DIR, "user_db")
            for filename in os.listdir(user_db_dir):
                if filename.endswith(".db"):
                    db_path = os.path.join(user_db_dir, filename)

                    conn = sqlite3.connect(db_path)
                    cur = conn.cursor()
                    if not ensure_user_fin_tables(conn):
                        conn.close()
                        continue
                    cur.execute("""
                                    UPDATE record
                                    SET knocked_out = 0,
                                        r32 = 0,
                                        r16 = 0,
                                        r8 = 0,
                                        fourth = 0,
                                        third = 0,
                                        second = 0,
                                        Champion = 0
                                """)
                    cur.execute("DELETE FROM results_all")
                    cur.execute("UPDATE sqlite_sequence SET seq = 0 where name = 'results_all'")
                    conn.commit()
                    conn.close()
                    
        for i, (ga, gb) in enumerate(zip(self.dev_goal_as_input, self.dev_goal_bs_input)):
            a = ga.get()
            b = gb.get()    
            if a.isdigit() and b.isdigit():
                cur_dev.execute(f"""
                                UPDATE {self.dev_group_name}_fin
                                SET goals_a = ?, goals_b = ?
                                WHERE team_a = ?
                                AND team_b = ? 
                                """, (a, b, *self.dev_match_name[i]))
                conn_dev.commit()

                user_db_dir = os.path.join(BASE_DIR, "user_db")

                for filename in os.listdir(user_db_dir):
                    if filename.endswith(".db"):
                        conn = sqlite3.connect(os.path.join(user_db_dir, filename))
                        cur = conn.cursor()
                        if not ensure_user_fin_tables(conn):
                            conn.close()
                            continue
                        cur.execute(f"""
                                UPDATE {self.dev_group_name}_fin
                                SET goals_a = ?, goals_b = ?
                                WHERE team_a = ?
                                AND team_b = ? 
                                """, (a, b, *self.dev_match_name[i]))
                        conn.commit()
                        conn.close()
                                 
            elif a == "" and b == "":
                a = None
                b = None
                cur_dev.execute(f"""
                                UPDATE {self.dev_group_name}_fin
                                SET goals_a = ?, goals_b = ?
                                WHERE team_a = ?
                                AND team_b = ? 
                                """, (a, b, *self.dev_match_name[i]))
                conn_dev.commit()
            
                user_db_dir = os.path.join(BASE_DIR, "user_db")

                for filename in os.listdir(user_db_dir):
                    if filename.endswith(".db"):
                        conn = sqlite3.connect(os.path.join(user_db_dir, filename))
                        cur = conn.cursor()
                        if not ensure_user_fin_tables(conn):
                            conn.close()
                            continue
                        cur.execute(f"""
                                UPDATE {self.dev_group_name}_fin
                                SET goals_a = ?, goals_b = ?
                                WHERE team_a = ?
                                AND team_b = ? 
                                """, (a, b, *self.dev_match_name[i]))
                        conn.commit()
                        conn.close()
        
        self.forget()
        self.dev_frame.pack(expand=True, fill="both")
    
    def dev_reset_results(self):
        for e in self.dev_goal_as_input:
            e.delete(0, END)
        for e in self.dev_goal_bs_input:
            e.delete(0, END)

    def Null_check(self, score_tuple):
        return any(None in row for row in score_tuple)
    
    def get_tournament(self):
        cur_dev.execute("SELECT tournament_flag FROM user_pw WHERE user_ID = 'development'")
        if cur_dev.fetchone()[0] == 1:
            tournament = main(conn=sqlite3.connect("user_db/developer.db"), ID="developer")[0]
            tm_game_list = []

            for i in range(16):
                tm_game_list.append((tournament[i * 2], tournament[i * 2+1]))

        else:
            tournament = main(conn=self.conn_user, ID=self.ID)[0]
            tm_game_list = []

            for i in range(16):
                tm_game_list.append((tournament[i * 2], tournament[i * 2+1]))

        return tm_game_list
    
    def dev_tournament(self):

        for g in "ABCDEFGHIJKL":
            cur_dev.execute(f"SELECT 1 FROM {g}_fin WHERE goals_a is NULL OR goals_b is NULL LIMIT 1")
            if cur_dev.fetchone() is not None:
                error_label = Label(self.dev_body_frame, text="group stage hasn't finished yet")
                error_label.pack()
                self.dev_body_frame.after(1000, error_label.destroy)
                cur_dev.execute("UPDATE user_pw SET tournament_flag = 0 WHERE user_ID = 'development'")
                conn_dev.commit()
                return
            cur_dev.execute("UPDATE user_pw SET tournament_flag = 1 WHERE user_ID = 'development'")
            conn_dev.commit()

        self.fin_tournament_32 = self.get_tournament()
        self.forget()
        self.dev_tournament_frame.pack(expand=True, fill="both")
        self.dev_make_tm_match_list()

    def dev_input_fin_tournament(self):
                
        cur_dev.execute("""
        SELECT round32, round16, round8, round4, round2, champion
        FROM tournament_fin
        WHERE id=1
        """)

        row = cur_dev.fetchone()

        if row is None:
            return

        if row[0] is not None:

            dev_t_32 = json.loads(row[0])
            dev_t_16 = json.loads(row[1])
            dev_t_8 = json.loads(row[2])
            dev_t_4 = json.loads(row[3])
            dev_t_2 = json.loads(row[4])

            champion = row[5]

            for button, text in zip(self.buttons_32l + self.buttons_32r, dev_t_32):
                button["text"] = text

            for button, text in zip(self.buttons_16l + self.buttons_16r, dev_t_16):
                button["text"] = text

            for button, text in zip(self.buttons_8l + self.buttons_8r, dev_t_8):
                button["text"] = text

            for button, text in zip(self.buttons_4l + self.buttons_4r, dev_t_4):
                button["text"] = text

            self.button_2l["text"] = dev_t_2[0]
            self.button_2r["text"] = dev_t_2[1]

            self.button_champ["text"] = champion
            
    def dev_make_tm_match_list(self):
        for widget in self.dev_tournament_body_frame.winfo_children():
            widget.destroy()

        self.root.geometry("1700x900")
        self.root.maxsize(1700, 855)

        hbar = Scrollbar(self.dev_tournament_body_frame, orient="horizontal")
        hbar.pack(side="bottom", fill="x")
        vbar = Scrollbar(self.dev_tournament_body_frame, orient="vertical")
        vbar.pack(side="right", fill="y")

        canvas = Canvas(self.dev_tournament_body_frame, width=1700, height=655,
                        xscrollcommand=hbar.set, yscrollcommand=vbar.set)
        canvas.pack(fill="both", expand=True)
        hbar.config(command=canvas.xview)
        vbar.config(command=canvas.yview)

        def _on_mousewheel(event):
            if event.state & 0x4:
                canvas.xview_scroll(int(-1 * (event.delta / 120)), "units")
            else:
                canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")

        canvas.bind("<MouseWheel>", _on_mousewheel)

        def place_btn(widget, x, y):
            canvas.create_window(x, y, window=widget, anchor="nw")

        self.buttons_32l = []
        for i, m in enumerate(self.fin_tournament_32[:8]):
            self.buttons_32l.append(Button(canvas, text=m[0], width=20, command=lambda idx=i*2: self.to_16l(idx)))
            self.buttons_32l.append(Button(canvas, text=m[1], width=20, command=lambda idx=i*2+1: self.to_16l(idx)))
            place_btn(self.buttons_32l[i*2],   0, 85*i)
            place_btn(self.buttons_32l[i*2+1], 0, 85*i+35)

        pad = [16, 60, 145]

        self.buttons_16l = []
        self.buttons_8l = []
        self.buttons_4l = []
        self.buttons_l = [self.buttons_16l, self.buttons_8l, self.buttons_4l]
        funcs_l = [self.to_8l, self.to_4l, self.to_2l]
        for i in range(3):
            for j in range(2**(3-i)):
                b = Button(canvas, text="None", width=20, command=lambda idx1=i, idx2=j: funcs_l[idx1](idx2))
                place_btn(b, 200*(i+1), j * 85*2**(i) + pad[i])
                self.buttons_l[i].append(b)

        self.button_2l = Button(canvas, text="None", width=20, command=lambda: self.to_champ(0))
        place_btn(self.button_2l, 650, 315)

        self.buttons_16r = []
        self.buttons_8r = []
        self.buttons_4r = []
        self.buttons_r = [self.buttons_16r, self.buttons_8r, self.buttons_4r]
        funcs_r = [self.to_8r, self.to_4r, self.to_2r]
        for i in range(3):
            for j in range(2**(1+i)):
                b = Button(canvas, text="None", width=20, command=lambda idx1=2-i, idx2=j: funcs_r[idx1](idx2))
                place_btn(b, 200*(i+4) + 100, j * 85*2**(2-i) + pad[2-i])
                self.buttons_r[2-i].append(b)

        self.button_2r = Button(canvas, text="None", width=20, command=lambda: self.to_champ(1))
        place_btn(self.button_2r, 850, 315)

        self.buttons_32r = []
        for i, m in enumerate(self.fin_tournament_32[8:]):
            self.buttons_32r.append(Button(canvas, text=m[0], width=20, command=lambda idx=i*2: self.to_16r(idx)))
            self.buttons_32r.append(Button(canvas, text=m[1], width=20, command=lambda idx=i*2+1: self.to_16r(idx)))
            place_btn(self.buttons_32r[i*2],   1500, 85*i)
            place_btn(self.buttons_32r[i*2+1], 1500, 85*i+35)

        self.button_champ = Button(canvas, text="None", width=20)
        place_btn(self.button_champ, 750, 380)
        lbl = Label(canvas, text="Champion 🏆", font="Arial")
        canvas.create_window(765, 350, window=lbl, anchor="nw")

        for i in range(8):
            canvas.create_line(145, 85*i+12, 175, 85*i+12)
            canvas.create_line(145, 85*i+47, 175, 85*i+47)
            canvas.create_line(175, 85*i+12, 175, 85*i+48)
            canvas.create_line(175, 85*i+30, 200, 85*i+30)

        for i in range(4):
            canvas.create_line(345, 85*2*i+30, 375, 85*2*i+30)
            canvas.create_line(345, 85*2*i+115, 375, 85*2*i+115)
            canvas.create_line(375, 85*2*i+30, 375, 85*2*i+116)
            canvas.create_line(375, 85*2*i+73, 400, 85*2*i+73)

        for i in range(2):
            canvas.create_line(545, 85*4*i+73, 575, 85*4*i+73)
            canvas.create_line(545, 85*4*i+243, 575, 85*4*i+243)
            canvas.create_line(575, 85*4*i+73, 575, 85*4*i+244)
            canvas.create_line(575, 85*4*i+159, 600, 85*4*i+159)

        for i in range(8):
            canvas.create_line(1505, 85*i+12, 1470, 85*i+12)
            canvas.create_line(1505, 85*i+47, 1470, 85*i+47)
            canvas.create_line(1470, 85*i+12, 1470, 85*i+49)
            canvas.create_line(1470, 85*i+30, 1445, 85*i+30)

        for i in range(4):
            canvas.create_line(1300, 85*2*i+30, 1270, 85*2*i+30)
            canvas.create_line(1300, 85*2*i+115, 1270, 85*2*i+115)
            canvas.create_line(1270, 85*2*i+30, 1270, 85*2*i+116)
            canvas.create_line(1270, 85*2*i+73, 1245, 85*2*i+73)

        for i in range(2):
            canvas.create_line(1100, 85*4*i+73, 1070, 85*4*i+73)
            canvas.create_line(1100, 85*4*i+243, 1070, 85*4*i+243)
            canvas.create_line(1070, 85*4*i+73, 1070, 85*4*i+244)
            canvas.create_line(1070, 85*4*i+159, 1045, 85*4*i+159)

        canvas.create_line(610, 159, 610, 499)
        canvas.create_line(610, 330, 680, 330)
        canvas.create_line(1035, 159, 1035, 499)
        canvas.create_line(1035, 330, 965, 330)

        canvas.configure(scrollregion=(0, 0, 1700, 655))

        self.dev_input_fin_tournament()

    def to_16l(self, idx):
        b = self.buttons_16l[idx//2]
        b["text"] = self.buttons_32l[idx]["text"]
        if b["text"] != "None":
            b.config(bg="red", activebackground="white")
        else:
            b.config(bg=COLORS["primary"], activebackground=COLORS["primary_dark"])

    def to_16r(self, idx):
        b = self.buttons_16r[idx//2]
        b["text"] = self.buttons_32r[idx]["text"]
        if b["text"] != "None":
            b.config(bg="red", activebackground="white")
        else:
            b.config(bg=COLORS["primary"], activebackground=COLORS["primary_dark"])
    
    def to_8l(self, idx):
        b = self.buttons_8l[idx//2]
        b["text"] = self.buttons_16l[idx]["text"]
        if b["text"] != "None":
            b.config(bg="red", activebackground="white")
        else:
            b.config(bg=COLORS["primary"], activebackground=COLORS["primary_dark"])
   
    def to_8r(self, idx):
        b = self.buttons_8r[idx//2]
        b["text"] = self.buttons_16r[idx]["text"]
        if b["text"] != "None":
            b.config(bg="red", activebackground="white")
        else:
            b.config(bg=COLORS["primary"], activebackground=COLORS["primary_dark"])

    def to_4l(self, idx):
        b = self.buttons_4l[idx//2]
        b["text"] = self.buttons_8l[idx]["text"]
        if b["text"] != "None":
            b.config(bg="red", activebackground="white")
        else:
            b.config(bg=COLORS["primary"], activebackground=COLORS["primary_dark"])
    
    def to_4r(self, idx):
        b = self.buttons_4r[idx//2]
        b["text"] = self.buttons_8r[idx]["text"]
        if b["text"] != "None":
            b.config(bg="red", activebackground="white")
        else:
            b.config(bg=COLORS["primary"], activebackground=COLORS["primary_dark"])

    def to_2l(self, idx):
        b = self.button_2l
        b["text"] = self.buttons_4l[idx]["text"]
        if b["text"] != "None":
            b.config(bg="red", activebackground="white")
        else:
            b.config(bg=COLORS["primary"], activebackground=COLORS["primary_dark"])

    def to_2r(self, idx):
        b = self.button_2r
        b["text"] = self.buttons_4r[idx]["text"]
        if b["text"] != "None":
            b.config(bg="red", activebackground="white")
        else:
            b.config(bg=COLORS["primary"], activebackground=COLORS["primary_dark"])

    def to_champ(self, idx):
        if idx == 0:
            self.button_champ["text"] = self.button_2l["text"]
        else:
            self.button_champ["text"] = self.button_2r["text"]

        if self.button_champ["text"] != "None":
            self.button_champ.config(bg="red", activebackground="white")
        else:
            self.button_champ.config(bg=COLORS["primary"], activebackground=COLORS["primary_dark"])

    def dev_submit_tm(self):
        dev_t_32 = [b["text"] for b in self.buttons_32l] + [b["text"] for b in self.buttons_32r]
        dev_t_16 = [b["text"] for b in self.buttons_16l] + [b["text"] for b in self.buttons_16r]
        dev_t_8 = [b["text"] for b in self.buttons_8l] + [b["text"] for b in self.buttons_8r]
        dev_t_4 = [b["text"] for b in self.buttons_4l] + [b["text"] for b in self.buttons_4r]
        dev_t_2 = [self.button_2l["text"], self.button_2r["text"]]
        dev_t_champ = self.button_champ["text"]

        cur_dev.execute("""
        UPDATE tournament_fin
        SET round32=?,
            round16=?,
            round8=?,
            round4=?,
            round2=?,
            champion=?
        WHERE id=1
        """, (
            json.dumps(dev_t_32, ensure_ascii=False),
            json.dumps(dev_t_16, ensure_ascii=False),
            json.dumps(dev_t_8, ensure_ascii=False),
            json.dumps(dev_t_4, ensure_ascii=False),
            json.dumps(dev_t_2, ensure_ascii=False),
            dev_t_champ
        ))
        conn_dev.commit()

    def dev_clear_all(self):
        buttons = [*self.buttons_l, *self.buttons_r, [self.button_2l, self.button_2r, self.button_champ]]
        for bs in buttons:
            for b in bs:
                b.config(text="None", bg=COLORS["primary"], activebackground=COLORS["primary_dark"])
    
app = Application(root=root)
root.mainloop()
