"""
نظام تسجيل نقاط البطولة (واجهة رسومية - النسخة الأولى)
=======================================================
تطبيق سطح مكتب بسيط باستخدام tkinter لإدارة فرق البطولة،
اللاعبين، الأحداث، النقاط، والترتيب.

المؤلف: ريماس محمد العاونه
التاريخ: مارس 2026
Python : 3.x (tkinter فقط — بدون تبعيات خارجية)
"""

import tkinter as tk
from tkinter import ttk, messagebox


# ---------------------------------------------------------------------------
#  Data Stores
# ---------------------------------------------------------------------------

# Tournament constraints
MAX_TEAMS = 4
MAX_TEAM_MEMBERS = 5
MAX_INDIVIDUALS = 20
MAX_EVENTS_PER_PARTICIPANT = 5

teams = {}   # { team_name: [player1, player2, ...] }
individuals = {}  # { individual_name: { "events": [event1, event2, ...] } }
events = {}  # { event_name: { "type": str, "category": str, "scores": { participant: score } } }

# Default point system based on ranking
RANKING_POINTS = {1: 100, 2: 80, 3: 60, 4: 40, 5: 20}
DEFAULT_POINTS = 10


# ---------------------------------------------------------------------------
#  Helper Functions
# ---------------------------------------------------------------------------

def find_key_ci(dictionary, name):
    """Find key case-insensitively."""
    for key in dictionary:
        if key.lower() == name.lower():
            return key
    return None


# ---------------------------------------------------------------------------
#  Main Application
# ---------------------------------------------------------------------------

class TournamentApp(tk.Tk):

    def __init__(self):
        super().__init__()
        self.title("نظام تسجيل نقاط البطولة - النسخة الأولى")
        self.geometry("900x650")
        self.configure(bg="white")

        # Create navigation buttons bar
        self._build_navigation()
        
        # Create main content area
        self.content = tk.Frame(self, bg="white")
        self.content.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Show home page
        self.show_home()

    def _build_navigation(self):
        """Create visible navigation buttons bar."""
        nav_frame = tk.Frame(self, bg="lightgray", height=50)
        nav_frame.pack(fill="x", padx=0, pady=0)
        nav_frame.pack_propagate(False)
        
        # Navigation buttons
        buttons = [
            ("الرئيسية", self.show_home, "lightblue"),
            ("تسجيل فريق", self.show_register_team, "lightblue"),
            ("إضافة لاعب", self.show_add_player, "lightgreen"),
            ("تسجيل فرد", self.show_register_individual, "lightgreen"),
            ("إنشاء حدث", self.show_create_event, "orange"),
            ("تسجيل نقاط", self.show_record_score, "lightcoral"),
            ("عرض القائمة", self.show_view_roster, "lightblue"),
            ("نتائج الأحداث", self.show_event_scores, "orange"),
            ("الترتيب العام", self.show_leaderboard, "lightyellow"),
        ]
        
        for text, command, bg_color in buttons:
            btn = tk.Button(nav_frame, text=text, command=command, 
                           bg=bg_color, font=("Arial", 10), 
                           padx=8, pady=5, relief="raised", bd=2)
            btn.pack(side="right", padx=3, pady=5)

    def _clear(self):
        """Clear content area."""
        for w in self.content.winfo_children():
            w.destroy()

    def _create_label(self, parent, text, font=("Arial", 12)):
        """Create a simple label."""
        label = tk.Label(parent, text=text, font=font, bg="white", anchor="e", justify="right")
        return label

    def _create_entry(self, parent, width=30):
        """Create a simple entry field."""
        entry = tk.Entry(parent, width=width, font=("Arial", 11), justify="right")
        return entry

    def _create_button(self, parent, text, command, bg="lightblue"):
        """Create a simple button."""
        btn = tk.Button(parent, text=text, command=command, bg=bg, 
                       font=("Arial", 11), padx=10, pady=5)
        return btn

    # =====================================================================
    #  PAGES
    # =====================================================================

    def show_home(self):
        """Show home page with basic statistics."""
        self._clear()
        
        title = tk.Label(self.content, text="نظام تسجيل نقاط البطولة", 
                        font=("Arial", 18, "bold"), bg="white")
        title.pack(pady=20)
        
        # Simple statistics
        stats_frame = tk.Frame(self.content, bg="white")
        stats_frame.pack(pady=20)
        
        stats = [
            ("الفرق المسجلة:", len(teams), MAX_TEAMS),
            ("الأفراد المسجلون:", len(individuals), MAX_INDIVIDUALS),
            ("الأحداث المنشأة:", len(events), ""),
        ]
        
        for label_text, count, max_val in stats:
            frame = tk.Frame(stats_frame, bg="white")
            frame.pack(pady=5)
            self._create_label(frame, label_text).pack(side="right", padx=10)
            count_text = f"{count}" + (f" / {max_val}" if max_val else "")
            tk.Label(frame, text=count_text, font=("Arial", 12, "bold"), 
                    bg="white", fg="blue").pack(side="right")
        
        # Instructions
        instructions = tk.Label(self.content, 
                               text="استخدم القائمة أعلاه للتنقل بين الصفحات",
                               font=("Arial", 11), bg="white", fg="gray")
        instructions.pack(pady=30)

    def show_register_team(self):
        """Show team registration page."""
        self._clear()
        
        title = tk.Label(self.content, text="تسجيل فريق جديد", 
                        font=("Arial", 16, "bold"), bg="white")
        title.pack(pady=20)
        
        frame = tk.Frame(self.content, bg="white")
        frame.pack(pady=20)
        
        self._create_label(frame, "اسم الفريق:").pack(side="right", padx=10)
        self.team_entry = self._create_entry(frame)
        self.team_entry.pack(side="right", padx=10)
        
        btn_frame = tk.Frame(self.content, bg="white")
        btn_frame.pack(pady=20)
        self._create_button(btn_frame, "تسجيل الفريق", self._do_register_team).pack()

    def _do_register_team(self):
        """Register a new team."""
        name = self.team_entry.get().strip()
        if not name:
            messagebox.showwarning("خطأ", "اسم الفريق لا يمكن أن يكون فارغاً.")
            return
        if find_key_ci(teams, name):
            messagebox.showerror("خطأ", f'فريق باسم "{name}" موجود بالفعل.')
            return
        if len(teams) >= MAX_TEAMS:
            messagebox.showerror("خطأ", f'تم الوصول للحد الأقصى لعدد الفرق ({MAX_TEAMS}).')
            return
        teams[name] = []
        messagebox.showinfo("نجح", f'تم تسجيل الفريق "{name}"!')
        self.team_entry.delete(0, "end")

    def show_register_individual(self):
        """Show individual registration page."""
        self._clear()
        
        title = tk.Label(self.content, text="تسجيل مشارك فردي", 
                        font=("Arial", 16, "bold"), bg="white")
        title.pack(pady=20)
        
        frame = tk.Frame(self.content, bg="white")
        frame.pack(pady=20)
        
        self._create_label(frame, "اسم المشارك:").pack(side="right", padx=10)
        self.ind_entry = self._create_entry(frame)
        self.ind_entry.pack(side="right", padx=10)
        
        btn_frame = tk.Frame(self.content, bg="white")
        btn_frame.pack(pady=20)
        self._create_button(btn_frame, "تسجيل المشارك", self._do_register_individual, bg="lightgreen").pack()

    def _do_register_individual(self):
        """Register a new individual."""
        name = self.ind_entry.get().strip()
        if not name:
            messagebox.showwarning("خطأ", "اسم المشارك لا يمكن أن يكون فارغاً.")
            return
        if find_key_ci(individuals, name):
            messagebox.showerror("خطأ", f'مشارك باسم "{name}" موجود بالفعل.')
            return
        if find_key_ci(teams, name):
            messagebox.showerror("خطأ", f'فريق باسم "{name}" موجود بالفعل.')
            return
        if len(individuals) >= MAX_INDIVIDUALS:
            messagebox.showerror("خطأ", f'تم الوصول للحد الأقصى لعدد الأفراد ({MAX_INDIVIDUALS}).')
            return
        individuals[name] = {"events": []}
        messagebox.showinfo("نجح", f'تم تسجيل المشارك "{name}"!')
        self.ind_entry.delete(0, "end")

    def show_add_player(self):
        """Show add player page."""
        self._clear()
        
        title = tk.Label(self.content, text="إضافة لاعب إلى فريق", 
                        font=("Arial", 16, "bold"), bg="white")
        title.pack(pady=20)
        
        if not teams:
            tk.Label(self.content, text="لا توجد فرق مسجلة بعد.", 
                    font=("Arial", 12), bg="white", fg="red").pack(pady=20)
            return
        
        frame1 = tk.Frame(self.content, bg="white")
        frame1.pack(pady=10)
        self._create_label(frame1, "اختر الفريق:").pack(side="right", padx=10)
        self.team_combo = ttk.Combobox(frame1, values=list(teams.keys()), state="readonly", width=27)
        self.team_combo.pack(side="right", padx=10)
        
        frame2 = tk.Frame(self.content, bg="white")
        frame2.pack(pady=10)
        self._create_label(frame2, "اسم اللاعب:").pack(side="right", padx=10)
        self.player_entry = self._create_entry(frame2)
        self.player_entry.pack(side="right", padx=10)
        
        btn_frame = tk.Frame(self.content, bg="white")
        btn_frame.pack(pady=20)
        self._create_button(btn_frame, "إضافة اللاعب", self._do_add_player, bg="lightgreen").pack()

    def _do_add_player(self):
        """Add a player to a team."""
        team = self.team_combo.get()
        player = self.player_entry.get().strip()
        if not team:
            messagebox.showwarning("خطأ", "يرجى اختيار فريق.")
            return
        if not player:
            messagebox.showwarning("خطأ", "اسم اللاعب لا يمكن أن يكون فارغاً.")
            return
        if len(teams[team]) >= MAX_TEAM_MEMBERS:
            messagebox.showerror("خطأ", f'الفريق "{team}" وصل للحد الأقصى لعدد الأعضاء ({MAX_TEAM_MEMBERS}).')
            return
        teams[team].append(player)
        messagebox.showinfo("نجح", f'تم إضافة "{player}" إلى "{team}"!')
        self.player_entry.delete(0, "end")

    def show_create_event(self):
        """Show create event page."""
        self._clear()
        
        title = tk.Label(self.content, text="إنشاء حدث جديد", 
                        font=("Arial", 16, "bold"), bg="white")
        title.pack(pady=20)
        
        frame1 = tk.Frame(self.content, bg="white")
        frame1.pack(pady=10)
        self._create_label(frame1, "اسم الحدث:").pack(side="right", padx=10)
        self.event_entry = self._create_entry(frame1)
        self.event_entry.pack(side="right", padx=10)
        
        frame2 = tk.Frame(self.content, bg="white")
        frame2.pack(pady=10)
        self._create_label(frame2, "نوع الحدث:").pack(side="right", padx=10)
        self.event_type_var = tk.StringVar(value="جماعي")
        tk.Radiobutton(frame2, text="جماعي", variable=self.event_type_var, 
                      value="جماعي", bg="white").pack(side="right", padx=5)
        tk.Radiobutton(frame2, text="فردي", variable=self.event_type_var, 
                      value="فردي", bg="white").pack(side="right", padx=5)
        
        frame3 = tk.Frame(self.content, bg="white")
        frame3.pack(pady=10)
        self._create_label(frame3, "فئة الحدث:").pack(side="right", padx=10)
        self.category_combo = ttk.Combobox(frame3, 
                                          values=["رياضي", "أكاديمي", "إبداعي", "أخرى"],
                                          state="readonly", width=27)
        self.category_combo.set("رياضي")
        self.category_combo.pack(side="right", padx=10)
        
        btn_frame = tk.Frame(self.content, bg="white")
        btn_frame.pack(pady=20)
        self._create_button(btn_frame, "إنشاء الحدث", self._do_create_event, bg="orange").pack()

    def _do_create_event(self):
        """Create a new event."""
        name = self.event_entry.get().strip()
        if not name:
            messagebox.showwarning("خطأ", "اسم الحدث لا يمكن أن يكون فارغاً.")
            return
        if find_key_ci(events, name):
            messagebox.showerror("خطأ", f'حدث باسم "{name}" موجود بالفعل.')
            return
        event_type_ar = self.event_type_var.get()
        event_type = "team" if event_type_ar == "جماعي" else "individual"
        category_ar = self.category_combo.get()
        category_map = {"رياضي": "athletic", "أكاديمي": "academic", 
                       "إبداعي": "creative", "أخرى": "other"}
        category = category_map.get(category_ar, "other")
        events[name] = {
            "type": event_type,
            "category": category,
            "scores": {}
        }
        messagebox.showinfo("نجح", f'تم إنشاء الحدث "{name}"!')
        self.event_entry.delete(0, "end")

    def show_record_score(self):
        """Show record score page."""
        self._clear()
        
        title = tk.Label(self.content, text="تسجيل نقاط", 
                        font=("Arial", 16, "bold"), bg="white")
        title.pack(pady=20)
        
        if not events:
            tk.Label(self.content, text="لا توجد أحداث منشأة بعد.", 
                    font=("Arial", 12), bg="white", fg="red").pack(pady=20)
            return
        
        frame1 = tk.Frame(self.content, bg="white")
        frame1.pack(pady=10)
        self._create_label(frame1, "اختر الحدث:").pack(side="right", padx=10)
        self.score_event_combo = ttk.Combobox(frame1, values=list(events.keys()), 
                                              state="readonly", width=27)
        self.score_event_combo.pack(side="right", padx=10)
        self.score_event_combo.bind("<<ComboboxSelected>>", self._on_event_selected)
        
        self.participant_frame = tk.Frame(self.content, bg="white")
        self.participant_frame.pack(pady=10)
        self.score_participant_combo = None
        
        frame2 = tk.Frame(self.content, bg="white")
        frame2.pack(pady=10)
        self._create_label(frame2, "النقاط:").pack(side="right", padx=10)
        self.score_entry = self._create_entry(frame2)
        self.score_entry.pack(side="right", padx=10)
        
        btn_frame = tk.Frame(self.content, bg="white")
        btn_frame.pack(pady=20)
        self._create_button(btn_frame, "تسجيل النقاط", self._do_record_score, bg="lightcoral").pack()

    def _on_event_selected(self, event=None):
        """Update participant dropdown based on selected event."""
        event_name = self.score_event_combo.get()
        if not event_name or event_name not in events:
            return
        
        # Clear existing participant dropdown
        for widget in self.participant_frame.winfo_children():
            widget.destroy()
        
        ev_data = events[event_name]
        event_type = ev_data.get("type", "team")
        
        frame = tk.Frame(self.participant_frame, bg="white")
        frame.pack()
        
        if event_type == "team":
            if not teams:
                tk.Label(frame, text="لا توجد فرق مسجلة بعد.", 
                        font=("Arial", 11), bg="white", fg="red").pack()
                self.score_participant_combo = None
                return
            self._create_label(frame, "اختر الفريق:").pack(side="right", padx=10)
            self.score_participant_combo = ttk.Combobox(frame, values=list(teams.keys()), 
                                                       state="readonly", width=27)
            self.score_participant_combo.pack(side="right", padx=10)
        else:
            if not individuals:
                tk.Label(frame, text="لا يوجد أفراد مسجلون بعد.", 
                        font=("Arial", 11), bg="white", fg="red").pack()
                self.score_participant_combo = None
                return
            self._create_label(frame, "اختر المشارك:").pack(side="right", padx=10)
            self.score_participant_combo = ttk.Combobox(frame, values=list(individuals.keys()), 
                                                        state="readonly", width=27)
            self.score_participant_combo.pack(side="right", padx=10)

    def _do_record_score(self):
        """Record a score."""
        event_name = self.score_event_combo.get()
        if not event_name:
            messagebox.showwarning("خطأ", "يرجى اختيار حدث.")
            return
        if not self.score_participant_combo:
            messagebox.showwarning("خطأ", "لا يوجد مشاركون متاحون.")
            return
        
        participant = self.score_participant_combo.get()
        if not participant:
            messagebox.showwarning("خطأ", "يرجى اختيار مشارك.")
            return
        
        try:
            score = float(self.score_entry.get().strip())
        except ValueError:
            messagebox.showwarning("خطأ", "النقاط يجب أن تكون رقماً.")
            return
        
        ev_data = events[event_name]
        event_type = ev_data.get("type", "team")
        
        if event_type == "team" and participant not in teams:
            messagebox.showerror("خطأ", f'"{participant}" ليس فريقاً مسجلاً.')
            return
        if event_type == "individual" and participant not in individuals:
            messagebox.showerror("خطأ", f'"{participant}" ليس مشاركاً فردياً مسجلاً.')
            return
        
        # Check participation limit
        if event_type == "team":
            team_events = sum(1 for ev in events.values() if participant in ev.get("scores", {}))
            if team_events >= MAX_EVENTS_PER_PARTICIPANT:
                messagebox.showwarning("خطأ", 
                    f'الفريق "{participant}" شارك بالفعل في {MAX_EVENTS_PER_PARTICIPANT} أحداث.')
                return
        else:
            ind_events = len(individuals[participant].get("events", []))
            if ind_events >= MAX_EVENTS_PER_PARTICIPANT:
                messagebox.showwarning("خطأ", 
                    f'المشارك "{participant}" شارك بالفعل في {MAX_EVENTS_PER_PARTICIPANT} أحداث.')
                return
        
        ev_data["scores"][participant] = score
        
        if event_type == "individual":
            if event_name not in individuals[participant]["events"]:
                individuals[participant]["events"].append(event_name)
        
        messagebox.showinfo("نجح", f"{participant} حصل على {score} نقطة في {event_name}!")
        self.score_entry.delete(0, "end")

    def show_view_roster(self):
        """Show team roster page."""
        self._clear()
        
        title = tk.Label(self.content, text="عرض قائمة الفريق", 
                        font=("Arial", 16, "bold"), bg="white")
        title.pack(pady=20)
        
        if not teams:
            tk.Label(self.content, text="لا توجد فرق مسجلة بعد.", 
                    font=("Arial", 12), bg="white", fg="red").pack(pady=20)
            return
        
        frame = tk.Frame(self.content, bg="white")
        frame.pack(pady=10)
        self._create_label(frame, "اختر الفريق:").pack(side="right", padx=10)
        self.roster_combo = ttk.Combobox(frame, values=list(teams.keys()), 
                                        state="readonly", width=27)
        self.roster_combo.pack(side="right", padx=10)
        
        btn_frame = tk.Frame(self.content, bg="white")
        btn_frame.pack(pady=10)
        self._create_button(btn_frame, "عرض القائمة", self._do_view_roster).pack()
        
        self.roster_result = tk.Frame(self.content, bg="white")
        self.roster_result.pack(fill="both", expand=True, pady=20)

    def _do_view_roster(self):
        """Display team roster."""
        team = self.roster_combo.get()
        if not team:
            messagebox.showwarning("خطأ", "يرجى اختيار فريق.")
            return
        
        for w in self.roster_result.winfo_children():
            w.destroy()
        
        players = teams[team]
        
        header = tk.Label(self.roster_result, text=f"لاعبو فريق: {team}", 
                         font=("Arial", 14, "bold"), bg="white")
        header.pack(pady=10)
        
        if not players:
            tk.Label(self.roster_result, text="لم يتم إضافة لاعبين بعد.", 
                    font=("Arial", 11), bg="white", fg="gray").pack()
        else:
            for i, player in enumerate(players, 1):
                tk.Label(self.roster_result, text=f"{i}. {player}", 
                        font=("Arial", 11), bg="white").pack(pady=2)

    def show_event_scores(self):
        """Show event scores page."""
        self._clear()
        
        title = tk.Label(self.content, text="نتائج الأحداث", 
                        font=("Arial", 16, "bold"), bg="white")
        title.pack(pady=20)
        
        if not events:
            tk.Label(self.content, text="لا توجد أحداث منشأة بعد.", 
                    font=("Arial", 12), bg="white", fg="red").pack(pady=20)
            return
        
        frame = tk.Frame(self.content, bg="white")
        frame.pack(pady=10)
        self._create_label(frame, "اختر الحدث:").pack(side="right", padx=10)
        self.scores_event_combo = ttk.Combobox(frame, values=list(events.keys()), 
                                              state="readonly", width=27)
        self.scores_event_combo.pack(side="right", padx=10)
        
        btn_frame = tk.Frame(self.content, bg="white")
        btn_frame.pack(pady=10)
        self._create_button(btn_frame, "عرض النقاط", self._do_event_scores, bg="orange").pack()
        
        self.scores_result = tk.Frame(self.content, bg="white")
        self.scores_result.pack(fill="both", expand=True, pady=20)

    def _do_event_scores(self):
        """Display event scores."""
        event_name = self.scores_event_combo.get()
        if not event_name:
            messagebox.showwarning("خطأ", "يرجى اختيار حدث.")
            return
        
        for w in self.scores_result.winfo_children():
            w.destroy()
        
        ev_data = events[event_name]
        scores = ev_data.get("scores", {})
        
        header = tk.Label(self.scores_result, text=f"نتائج حدث: {event_name}", 
                         font=("Arial", 14, "bold"), bg="white")
        header.pack(pady=10)
        
        if not scores:
            tk.Label(self.scores_result, text="لم يتم تسجيل نقاط بعد.", 
                    font=("Arial", 11), bg="white", fg="gray").pack()
        else:
            sorted_scores = sorted(scores.items(), key=lambda x: x[1], reverse=True)
            for rank, (participant, score) in enumerate(sorted_scores, 1):
                points = RANKING_POINTS.get(rank, DEFAULT_POINTS)
                text = f"{rank}. {participant}: {score} نقطة (نقاط الترتيب: {points})"
                tk.Label(self.scores_result, text=text, 
                        font=("Arial", 11), bg="white").pack(pady=2)

    def show_leaderboard(self):
        """Show leaderboard page."""
        self._clear()
        
        title = tk.Label(self.content, text="الترتيب العام", 
                        font=("Arial", 16, "bold"), bg="white")
        title.pack(pady=20)
        
        if not teams and not individuals:
            tk.Label(self.content, text="لا يوجد مشاركون مسجلون بعد.", 
                    font=("Arial", 12), bg="white", fg="red").pack(pady=20)
            return
        
        totals = {}
        for team in teams:
            totals[team] = {"type": "فريق", "points": 0, "events": 0}
        for ind in individuals:
            totals[ind] = {"type": "فرد", "points": 0, "events": len(individuals[ind].get("events", []))}
        
        # Calculate ranking-based points
        for ev_name, ev_data in events.items():
            scores = ev_data.get("scores", {})
            if not scores:
                continue
            sorted_participants = sorted(scores.items(), key=lambda x: x[1], reverse=True)
            for rank, (participant, score) in enumerate(sorted_participants, 1):
                points = RANKING_POINTS.get(rank, DEFAULT_POINTS)
                if participant in totals:
                    totals[participant]["points"] += points
                    totals[participant]["events"] += 1
        
        sorted_participants = sorted(totals.items(), key=lambda x: x[1]["points"], reverse=True)
        
        # Display leaderboard
        header = tk.Label(self.content, text="الترتيب الكامل", 
                         font=("Arial", 14, "bold"), bg="white")
        header.pack(pady=10)
        
        for i, (name, info) in enumerate(sorted_participants, 1):
            text = f"{i}. {name} ({info['type']}) - {info['points']} نقطة - {info['events']} حدث"
            color = "gold" if i == 1 else "silver" if i == 2 else "brown" if i == 3 else "black"
            tk.Label(self.content, text=text, font=("Arial", 11), 
                    bg="white", fg=color).pack(pady=2)


# ---------------------------------------------------------------------------
#  Entry Point
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    app = TournamentApp()
    app.mainloop()
