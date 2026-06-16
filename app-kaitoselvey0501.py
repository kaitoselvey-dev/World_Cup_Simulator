from tkinter import *
from tkinter import ttk
import sqlite3
from functions import create_user_DB, ensure_user_fin_tables
from main import main
import os
from paths import APP_DIR, ensure_app_data, resource_path

BASE_DIR = APP_DIR

conn_dev = sqlite3.connect(ensure_app_data())
cur_dev = conn_dev.cursor()

root = Tk()
root.geometry("1080x680")
root.minsize(1000, 680)
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
        cur_dev.execute("SELECT tournament_flag FROM user_pw WHERE user_ID = 'development'")
        if cur_dev.fetchone()[0] == 1:
            self.finished_tournament_list = self.get_tournament(sqlite3.connect("user_DB/developer.DB"))

    # functions
    def show_start(self):
        self.forget()
        self.start_frame.pack(expand=True)

    def forget(self):
        self.root.minsize(1000, 680)
        self.start_frame.pack_forget()
        self.main_frame.pack_forget()
        self.simulation_frame.pack_forget()
        self.prediction_frame.pack_forget()
        self.dev_frame.pack_forget()
        self.dev_group_stage_frame.pack_forget()
        self.dev_tournament_frame.pack_forget()

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

        self.cur_user.execute("SELECT seq FROM sqlite_sequence WHERE name = 'results_all'")
        total_num = int(int(self.cur_user.fetchone()[0])/104)

        self.cur_user.execute("SELECT * FROM record")
        rows = self.cur_user.fetchall()

        self.cur_user.execute("PRAGMA table_info(record)")
        columns = [col[1] for col in self.cur_user.fetchall()]
        columns[0] = f"n = {total_num}"

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

        for col in columns:
            tree.heading(col, text=col)
            tree.column(col, anchor="center", width=100)

        for row in rows:
            display_row = [row[0]]

            for value in row[1:]:
                percent = round(value / total_num * 100, 1)
                display_row.append(f"{percent}%")

            tree.insert("", END, values=display_row)

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

        Button(self.prediction_body_frame, text="clear", width=8, command=self.reset_prediction).pack(pady=5)

        reset_frame = Frame(self.prediction_body_frame)
        reset_frame.pack()
        Label(reset_frame, text="RESET DATA?").pack(side="left")
        self.choice = StringVar(value="NO")
        Radiobutton(reset_frame, text="NO", variable=self.choice, value="NO").pack(side="left")
        Radiobutton(reset_frame, text="YES", variable=self.choice, value="YES").pack(side="left")
        Button(reset_frame, text="submit", width=8, command=self.submit_prediction).pack(pady=5, side="right")

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

    def create_widgets(self):
        # permenant
        quit_btn = Button(self, text="close", width=8, command=self.root.destroy)
        quit_btn.pack(side='bottom')

        # start frame
        self.start_frame = Frame(self)
        self.start_frame.pack(expand=True)
        Label(self.start_frame, text="World Cup Simulator", font=FONT_TITLE, pady=10).pack()

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

        Button(self.start_frame, text="login", width=8, command=self.login).pack(pady=5)
        Button(self.start_frame, text="sign up", width=8, command=self.sign_up).pack(pady=5)
        Button(self.start_frame, text="developer page", width=15, command=self.dev_page).pack(pady=5)

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
        self.attempt_num_box.pack( padx=5,side="left")
        Button(self.attempt_num_frame, text="simulation", width=15, command=self.simulation).pack(pady=5, padx=5, side="right")

        group_combo = ttk.Combobox(self.main_body_frame, textvariable=self.group, state="readonly")
        group_combo["values"] = ('Group A', 'Group B', 'Group C', 'Group D', 'Group E', 'Group F', 'Group G', 'Group H', 'Group I', 'Group J', 'Group K', 'Group L')
        group_combo.pack(pady=5, padx=5, side="left")
        Button(self.main_body_frame, text="score prediction", width=15, command=self.score_prediction).pack(pady=5, padx=5, side="right")

            # footer        
        self.main_footer_frame = Frame(self.main_frame)    
        self.main_footer_frame.pack(fill="x")
        self.reset_button = Button(self.main_footer_frame, text="reset data", width=15, command=self.reset_data)
        self.reset_button.pack(pady=5)
        Button(self.main_footer_frame, text="return", width=8, command=self.show_start).pack(pady=5)

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
        self.simulation_body_frame.pack(expand=True)

            # footer
        simulation_footer_frame = Frame(self.simulation_frame)
        simulation_footer_frame.pack(fill="x")

        self.re_attempt_num_frame = Frame(simulation_footer_frame)
        self.re_attempt_num_frame.pack(pady=5)
        Label(self.re_attempt_num_frame, text="number of attempts", width=20).pack(side="left")
        self.re_attempt_num_box = Entry(self.re_attempt_num_frame, width=10, justify="center")
        self.re_attempt_num_box.pack( padx=5,side="left")
        Button(self.re_attempt_num_frame, text="simulation", width=15, command=self.re_simulation).pack(pady=5, padx=5, side="right")

        Button(simulation_footer_frame, text="return", width=8, command=self.show_main).pack(pady=5, side="bottom")

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
        Button(prediction_footer_frame, text="return", width=8, command=self.show_main).pack(pady=5, side="bottom")



        ## developer frames ##



        # developer page frame
        self.dev_frame = Frame(self)
        self.dev_group = StringVar()
        self.dev_group.set("choose the group")
            # header
        dev_header_frame = Frame(self.dev_frame)
        dev_header_frame.pack()
        Label(dev_header_frame, text="Developer Tools", font=FONT_TITLE).pack(side="top", pady=(0, 14))

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
        Button(dev_footer_frame, text="return", width=8, command=self.show_start).pack(pady=5, side="bottom")

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
        Button(dev_group_stage_footer_frame, text="return", width=8, command=self.show_start).pack(pady=5, side="bottom")

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
        dev_tournament_footer_frame.pack(fill="x")
        Button(dev_tournament_footer_frame, text="return", width=8, command=self.show_start).pack(pady=5, side="bottom")


    ## developer tools ##
    def dev_page(self):
        self.forget()
        self.dev_frame.pack(expand=True, fill="both")

    def dev_group_stage(self):
        self.dev_group_name = self.dev_group.get()[-1]
        if self.dev_group_name in "ABCDEEFGHIJKL":
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
        
        Button(self.dev_group_stage_body_frame, text="clear", width=8, command=self.dev_reset_results).pack(pady=5)

        dev_reset_frame = Frame(self.dev_group_stage_body_frame)
        dev_reset_frame.pack()
        Label(dev_reset_frame, text="RESET DATA?").pack(side="left")
        self.dev_choice = StringVar(value="NO")
        Radiobutton(dev_reset_frame, text="NO", variable=self.dev_choice, value="NO").pack(side="left")
        Radiobutton(dev_reset_frame, text="YES", variable=self.dev_choice, value="YES").pack(side="left")
        Button(self.dev_group_stage_body_frame, text="submit", width=8, command=self.dev_submit_results).pack(pady=5)

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

    def dev_Null_check(self, score_tuple):
        return any(None in row for row in score_tuple)
    
    def get_tournament(self, conn):
        tournament = main(conn=conn, ID="developer")[0]
        tm_game_list = []

        for i in range(16):
            tm_game_list.append((tournament[i * 2], tournament[i * 2+1]))

        return tm_game_list
    
    def dev_tournament(self):
        cur_dev.execute("SELECT tournament_flag FROM user_pw WHERE user_ID = 'development'")
        if cur_dev.fetchone()[0] == 0:
            for g in "ABCDEFGHIJKL":
                cur_dev.execute(f"SELECT 1 FROM {g}_fin WHERE goals_a is NULL OR goals_b is NULL LIMIT 1")
                if cur_dev.fetchone() is not None:
                    error_label = Label(self.dev_body_frame, text="group stage hasn't finished yet")
                    error_label.pack()
                    self.dev_body_frame.after(1000, error_label.destroy)
                    return
            cur_dev.execute("UPDATE user_pw SET tournament_flag = 1 WHERE user_ID = 'development'")
            conn_dev.commit()

        conn = sqlite3.connect("user_db/developer.db")
        self.finished_tournament_list = self.get_tournament(conn)
        self.forget()
        self.dev_tournament_frame.pack(expand=True, fill="both")
        self.dev_make_tm_match_list()
    
    def dev_make_tm_match_list(self):
        
        self.root.minsize(1580, 850)
        buttons_32l = []
        for m in self.finished_tournament_list[:8]:
            buttons_32l.append(Button(self.dev_tournament_body_frame, text=m[0], width=20))
            buttons_32l.append(Button(self.dev_tournament_body_frame, text=m[1], width=20))

        for i in range(8):
            buttons_32l[i*2].place(x=0, y=85*i)
            buttons_32l[i*2+1].place(x=0, y=85*i+35)

        pad = [16, 60, 145]
        buttons_16l = []
        buttons_16r = []
        buttons_8l = []
        buttons_8r = []
        for i in range(3):
            for j in range(2**(3-i)):
                Button(self.dev_tournament_body_frame, text="None", width=20).place(x=200*(i+1), y=j * 85*2**(i) + pad[i])

        for i in range(3):
            for j in range(2**(1+i)):
                Button(self.dev_tournament_body_frame, text="None", width=20).place(x=200*(i+4), y=j * 85*2**(2-i) + pad[2-i])

        buttons_32r = []
        for i, m in enumerate(self.finished_tournament_list[8:]):
            buttons_32r.append(Button(self.dev_tournament_body_frame, text=m[0], width=20))
            buttons_32r.append(Button(self.dev_tournament_body_frame, text=m[1], width=20))

        for i in range(8):
            buttons_32r[i*2].place(x=1400, y=85*i)
            buttons_32r[i*2+1].place(x=1400, y=85*i+35) 


app = Application(root=root)
root.mainloop()
