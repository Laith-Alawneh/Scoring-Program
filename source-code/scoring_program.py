"""
نظام تسجيل نقاط البطولة (واجهة رسومية)
========================================
تطبيق سطح مكتب حديث باستخدام tkinter لإدارة فرق البطولة،
اللاعبين، الأحداث، النقاط، والترتيب.

المؤلف: ريماس محمد العاونه
التاريخ: مارس 2026
Python : 3.x (tkinter فقط — بدون تبعيات خارجية)
"""

import tkinter as tk
from tkinter import ttk, messagebox


# ---------------------------------------------------------------------------
#  Colour Palette & Design Tokens
# ---------------------------------------------------------------------------

COLORS = {
    "bg":            "#0f172a",   # deep navy background
    "sidebar":       "#1e293b",   # dark slate sidebar
    "sidebar_hover": "#334155",   # hover state
    "card":          "#1e293b",   # card surface
    "card_border":   "#334155",   # subtle border
    "accent":        "#6366f1",   # indigo accent
    "accent_hover":  "#818cf8",   # lighter indigo
    "success":       "#22c55e",   # green
    "warning":       "#f59e0b",   # amber
    "danger":        "#ef4444",   # red
    "text":          "#f8fafc",   # near-white text
    "text_dim":      "#94a3b8",   # muted text
    "text_dark":     "#cbd5e1",   # secondary text
    "input_bg":      "#0f172a",   # input field bg
    "input_border":  "#475569",   # input border
    "table_row":     "#1e293b",   # table row
    "table_alt":     "#263548",   # alternate row
    "gold":          "#fbbf24",   # 1st place
    "silver":        "#a8a29e",   # 2nd place
    "bronze":        "#d97706",   # 3rd place
}

FONT_TITLE   = ("Tahoma", 22, "bold")
FONT_HEADING = ("Tahoma", 14, "bold")
FONT_BODY    = ("Tahoma", 11)
FONT_SMALL   = ("Tahoma", 10)
FONT_BUTTON  = ("Tahoma", 11, "bold")
FONT_SIDEBAR = ("Tahoma", 11)
FONT_BADGE   = ("Tahoma", 9, "bold")
FONT_BIG_NUM = ("Tahoma", 28, "bold")

SIDEBAR_ICONS = {
    "home":     "\u2302",
    "team":     "\u2691",
    "player":   "\u263A",
    "event":    "\u2605",
    "score":    "\u270E",
    "roster":   "\u2630",
    "results":  "\u2637",
    "leader":   "\u265B",
}


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
# Event structure: { event_name: { "type": "team"/"individual", "category": "athletic"/"academic"/etc, 
#                                   "scores": { participant_name: score } } }
events = {}  # { event_name: { "type": str, "category": str, "scores": { participant: score } } }

# Default point system based on ranking (can be customized)
# Points for positions: 1st=100, 2nd=80, 3rd=60, 4th=40, 5th=20, others=10
RANKING_POINTS = {1: 100, 2: 80, 3: 60, 4: 40, 5: 20}
DEFAULT_POINTS = 10


# ---------------------------------------------------------------------------
#  Helper
# ---------------------------------------------------------------------------

def find_key_ci(dictionary, name):
    for key in dictionary:
        if key.lower() == name.lower():
            return key
    return None


# ---------------------------------------------------------------------------
#  Custom Widgets
# ---------------------------------------------------------------------------

class StyledButton(tk.Button):
    """A flat button with hover colour change."""

    def __init__(self, parent, text="", command=None,
                 bg_color=COLORS["accent"], hover_color=COLORS["accent_hover"],
                 text_color="white", font=FONT_BUTTON, **kw):
        super().__init__(
            parent, text=text, command=command,
            font=font, fg=text_color, bg=bg_color,
            activebackground=hover_color, activeforeground=text_color,
            bd=0, relief="flat", cursor="hand2",
            padx=20, pady=10, **kw
        )
        self._bg = bg_color
        self._hover = hover_color
        self.bind("<Enter>", lambda e: self.configure(bg=self._hover))
        self.bind("<Leave>", lambda e: self.configure(bg=self._bg))


class Card(tk.Frame):
    """A card-like container with subtle border."""

    def __init__(self, parent, **kw):
        super().__init__(parent, bg=COLORS["card"],
                         highlightbackground=COLORS["card_border"],
                         highlightthickness=1, **kw)


class StatCard(tk.Frame):
    """A small stat display card (icon + number + label)."""

    def __init__(self, parent, icon, value, label, accent=COLORS["accent"], **kw):
        super().__init__(parent, bg=COLORS["card"],
                         highlightbackground=COLORS["card_border"],
                         highlightthickness=1, **kw)
        inner = tk.Frame(self, bg=COLORS["card"])
        inner.pack(padx=24, pady=18)
        tk.Label(inner, text=icon, font=("Tahoma", 24), bg=COLORS["card"],
                 fg=accent).pack()
        tk.Label(inner, text=str(value), font=FONT_BIG_NUM, bg=COLORS["card"],
                 fg=COLORS["text"]).pack()
        tk.Label(inner, text=label, font=FONT_SMALL, bg=COLORS["card"],
                 fg=COLORS["text_dim"]).pack()


# ---------------------------------------------------------------------------
#  Main Application
# ---------------------------------------------------------------------------

class TournamentApp(tk.Tk):

    def __init__(self):
        super().__init__()
        self.title("نظام تسجيل نقاط البطولة")
        self.geometry("1060x660")
        self.minsize(900, 580)
        self.configure(bg=COLORS["bg"])
        # Set RTL direction
        self.tk.call('tk', 'scaling', '-displayof', '.', 1.0)
        try:
            self.option_add('*TkFDialog*foreground', COLORS["text"])
        except:
            pass

        # ttk style for Treeview
        style = ttk.Style(self)
        style.theme_use("clam")
        style.configure("Custom.Treeview",
                         background=COLORS["table_row"],
                         foreground=COLORS["text"],
                         fieldbackground=COLORS["table_row"],
                         rowheight=32,
                         font=FONT_BODY)
        style.configure("Custom.Treeview.Heading",
                         background=COLORS["accent"],
                         foreground="white",
                         font=FONT_HEADING,
                         padding=6)
        style.map("Custom.Treeview",
                   background=[("selected", COLORS["accent"])],
                   foreground=[("selected", "white")])
        style.configure("TCombobox",
                         fieldbackground=COLORS["input_bg"],
                         background=COLORS["card_border"],
                         foreground=COLORS["text"],
                         arrowcolor=COLORS["text_dim"])

        self._active_btn = None
        self._sidebar_btns = []
        self._build_sidebar()
        self._build_content_area()
        self.show_home()

    # =====================================================================
    #  LAYOUT
    # =====================================================================

    def _build_sidebar(self):
        self.sidebar = tk.Frame(self, bg=COLORS["sidebar"], width=220)
        self.sidebar.pack(side="right", fill="y")
        self.sidebar.pack_propagate(False)

        # Logo area
        logo_frame = tk.Frame(self.sidebar, bg=COLORS["sidebar"])
        logo_frame.pack(fill="x", pady=(20, 8), padx=16)
        tk.Label(logo_frame, text="\u265B", font=("Tahoma", 28),
                 bg=COLORS["sidebar"], fg=COLORS["accent"]).pack(side="right")
        tk.Label(logo_frame, text="نظام البطولة ", font=("Tahoma", 20, "bold"),
                 bg=COLORS["sidebar"], fg=COLORS["text"]).pack(side="right")

        # Divider
        tk.Frame(self.sidebar, bg=COLORS["card_border"], height=1).pack(
            fill="x", padx=16, pady=(8, 16))

        nav_items = [
            (SIDEBAR_ICONS["home"],    "الرئيسية",           self.show_home),
            (SIDEBAR_ICONS["team"],    "تسجيل فريق",  self.show_register_team),
            (SIDEBAR_ICONS["player"],  "إضافة لاعب",     self.show_add_player),
            ("\u263A",                 "تسجيل فرد", self.show_register_individual),
            (SIDEBAR_ICONS["event"],   "إنشاء حدث",   self.show_create_event),
            (SIDEBAR_ICONS["score"],   "تسجيل نقاط",   self.show_record_score),
            (SIDEBAR_ICONS["roster"],  "عرض القائمة",    self.show_view_roster),
            (SIDEBAR_ICONS["results"], "نتائج الأحداث",   self.show_event_scores),
            (SIDEBAR_ICONS["leader"],  "الترتيب العام",    self.show_leaderboard),
        ]

        for icon, text, cmd in nav_items:
            btn = tk.Label(
                self.sidebar, text=f"{text}   {icon}  ",
                font=FONT_SIDEBAR, fg=COLORS["text_dim"],
                bg=COLORS["sidebar"], anchor="e",
                padx=18, pady=10, cursor="hand2"
            )
            btn.pack(fill="x")
            btn._cmd = cmd
            btn.bind("<Enter>", lambda e, b=btn: self._sidebar_enter(b))
            btn.bind("<Leave>", lambda e, b=btn: self._sidebar_leave(b))
            btn.bind("<Button-1>", lambda e, b=btn: self._sidebar_click(b))
            self._sidebar_btns.append(btn)

    def _sidebar_enter(self, btn):
        if btn != self._active_btn:
            btn.configure(bg=COLORS["sidebar_hover"], fg=COLORS["text"])

    def _sidebar_leave(self, btn):
        if btn != self._active_btn:
            btn.configure(bg=COLORS["sidebar"], fg=COLORS["text_dim"])

    def _sidebar_click(self, btn):
        # Reset previous
        if self._active_btn:
            self._active_btn.configure(bg=COLORS["sidebar"], fg=COLORS["text_dim"])
        # Activate
        btn.configure(bg=COLORS["accent"], fg="white")
        self._active_btn = btn
        btn._cmd()

    def _build_content_area(self):
        self.content = tk.Frame(self, bg=COLORS["bg"])
        self.content.pack(side="right", fill="both", expand=True)

    # =====================================================================
    #  HELPERS
    # =====================================================================

    def _clear(self):
        for w in self.content.winfo_children():
            w.destroy()

    def _page_title(self, text, subtitle=""):
        frame = tk.Frame(self.content, bg=COLORS["bg"])
        frame.pack(fill="x", padx=30, pady=(28, 4))
        tk.Label(frame, text=text, font=FONT_TITLE,
                 bg=COLORS["bg"], fg=COLORS["text"], anchor="e", justify="right").pack(anchor="e", fill="x")
        if subtitle:
            tk.Label(frame, text=subtitle, font=FONT_BODY,
                     bg=COLORS["bg"], fg=COLORS["text_dim"], anchor="e", justify="right").pack(anchor="e", fill="x", pady=(2, 0))

    def _make_input(self, parent, label_text, placeholder=""):
        wrapper = tk.Frame(parent, bg=COLORS["card"])
        wrapper.pack(fill="x", pady=8)
        tk.Label(wrapper, text=label_text, font=FONT_BODY,
                 bg=COLORS["card"], fg=COLORS["text_dim"], anchor="e", justify="right").pack(anchor="e", fill="x")
        entry = tk.Entry(wrapper, font=FONT_BODY, bg=COLORS["input_bg"],
                         fg=COLORS["text"], insertbackground=COLORS["text"],
                         relief="flat", highlightthickness=1,
                         highlightbackground=COLORS["input_border"],
                         highlightcolor=COLORS["accent"], justify="right")
        entry.pack(fill="x", ipady=8, pady=(4, 0))
        if placeholder:
            entry.insert(0, placeholder)
            entry.configure(fg=COLORS["text_dim"])
            entry.bind("<FocusIn>", lambda e: self._clear_placeholder(entry, placeholder))
            entry.bind("<FocusOut>", lambda e: self._restore_placeholder(entry, placeholder))
        return entry

    def _clear_placeholder(self, entry, placeholder):
        if entry.get() == placeholder:
            entry.delete(0, "end")
            entry.configure(fg=COLORS["text"])

    def _restore_placeholder(self, entry, placeholder):
        if not entry.get().strip():
            entry.delete(0, "end")
            entry.insert(0, placeholder)
            entry.configure(fg=COLORS["text_dim"])

    def _get_entry_value(self, entry, placeholder=""):
        val = entry.get().strip()
        if val == placeholder:
            return ""
        return val

    def _make_dropdown(self, parent, label_text, values):
        wrapper = tk.Frame(parent, bg=COLORS["card"])
        wrapper.pack(fill="x", pady=8)
        tk.Label(wrapper, text=label_text, font=FONT_BODY,
                 bg=COLORS["card"], fg=COLORS["text_dim"], anchor="e", justify="right").pack(anchor="e", fill="x")
        combo = ttk.Combobox(wrapper, values=values, state="readonly",
                             font=FONT_BODY, width=36)
        combo.pack(fill="x", ipady=6, pady=(4, 0))
        return combo
    
    def _make_radio_group(self, parent, label_text, options, default=None):
        """Create a radio button group."""
        wrapper = tk.Frame(parent, bg=COLORS["card"])
        wrapper.pack(fill="x", pady=8)
        tk.Label(wrapper, text=label_text, font=FONT_BODY,
                 bg=COLORS["card"], fg=COLORS["text_dim"], anchor="e", justify="right").pack(anchor="e", fill="x")
        frame = tk.Frame(wrapper, bg=COLORS["card"])
        frame.pack(fill="x", pady=(4, 0))
        var = tk.StringVar(value=default if default else options[0])
        for opt in options:
            rb = tk.Radiobutton(frame, text=opt, variable=var, value=opt,
                               font=FONT_BODY, bg=COLORS["card"],
                               fg=COLORS["text"], selectcolor=COLORS["accent"],
                               activebackground=COLORS["card"],
                               activeforeground=COLORS["text"], anchor="e")
            rb.pack(side="right", padx=(20, 0))
        return var

    def _build_table(self, parent, columns, data, widths=None, rank_colors=False):
        """Build a styled Treeview table."""
        tree_frame = tk.Frame(parent, bg=COLORS["card"])
        tree_frame.pack(fill="both", expand=True, pady=(10, 0))

        tree = ttk.Treeview(tree_frame, columns=[c[0] for c in columns],
                            show="headings", style="Custom.Treeview",
                            height=min(len(data) + 1, 14))
        for i, (col_id, col_text) in enumerate(columns):
            w = widths[i] if widths else 150
            tree.heading(col_id, text=col_text)
            # RTL: anchor right for text columns, center for numbers
            if i == 0 or (i == len(columns)-1 and col_id in ["points", "score", "total", "events"]):
                anchor = "center"
            else:
                anchor = "e"  # Right align for RTL
            tree.column(col_id, width=w, anchor=anchor)

        # Alternate row colours via tags
        tree.tag_configure("odd", background=COLORS["table_row"])
        tree.tag_configure("even", background=COLORS["table_alt"])
        tree.tag_configure("gold", background="#422006", foreground=COLORS["gold"])
        tree.tag_configure("silver", background="#1c1917", foreground=COLORS["silver"])
        tree.tag_configure("bronze", background="#431407", foreground=COLORS["bronze"])

        for idx, row in enumerate(data):
            if rank_colors and idx < 3:
                tag = ["gold", "silver", "bronze"][idx]
            else:
                tag = "even" if idx % 2 else "odd"
            tree.insert("", "end", values=row, tags=(tag,))

        scrollbar = ttk.Scrollbar(tree_frame, orient="vertical", command=tree.yview)
        tree.configure(yscrollcommand=scrollbar.set)
        tree.pack(side="left", fill="both", expand=True)
        if len(data) > 10:
            scrollbar.pack(side="right", fill="y")
        return tree

    def _empty_state(self, text):
        frame = tk.Frame(self.content, bg=COLORS["bg"])
        frame.pack(expand=True)
        tk.Label(frame, text="( )", font=("Tahoma", 36),
                 bg=COLORS["bg"], fg=COLORS["card_border"]).pack()
        tk.Label(frame, text=text, font=FONT_BODY,
                 bg=COLORS["bg"], fg=COLORS["text_dim"]).pack(pady=(8, 0))

    # =====================================================================
    #  PAGES
    # =====================================================================

    # -- Home --------------------------------------------------------------

    def show_home(self):
        self._clear()
        self._page_title("لوحة التحكم", "نظرة عامة على البطولة")

        # Stat cards row
        stats_row = tk.Frame(self.content, bg=COLORS["bg"])
        stats_row.pack(fill="x", padx=30, pady=(20, 10))

        total_players = sum(len(p) for p in teams.values())
        total_scores = sum(
            len(ev.get("scores", {})) for ev in events.values()
        )

        cards_data = [
            ("\u2691", len(teams),    f"الفرق (حد أقصى {MAX_TEAMS})",    COLORS["accent"]),
            ("\u263A", len(individuals),  f"الأفراد (حد أقصى {MAX_INDIVIDUALS})",  COLORS["success"]),
            ("\u2605", len(events),    "الأحداث",   COLORS["warning"]),
            ("\u270E", total_scores,   "النقاط",   COLORS["danger"]),
        ]
        for icon, val, label, accent in cards_data:
            sc = StatCard(stats_row, icon, val, label, accent)
            sc.pack(side="right", padx=(14, 0), ipadx=10)

        # Quick leaderboard preview
        if teams or individuals:
            preview = Card(self.content)
            preview.pack(fill="both", expand=True, padx=30, pady=(10, 24))
            tk.Label(preview, text="الترتيب السريع  \u265B  ",
                     font=FONT_HEADING, bg=COLORS["card"],
                     fg=COLORS["text"], anchor="e", justify="right").pack(anchor="e", fill="x", padx=16, pady=(14, 0))
            tk.Frame(preview, bg=COLORS["card_border"], height=1).pack(
                fill="x", padx=16, pady=8)

            totals = {}
            # Calculate points for teams
            for team in teams:
                totals[team] = {"type": "فريق", "points": 0}
            # Calculate points for individuals
            for ind in individuals:
                totals[ind] = {"type": "فرد", "points": 0}
            
            # Calculate ranking-based points for each event
            for ev_name, ev_data in events.items():
                scores = ev_data.get("scores", {})
                if not scores:
                    continue
                # Sort by score (descending)
                sorted_participants = sorted(scores.items(), key=lambda x: x[1], reverse=True)
                # Assign ranking points
                for rank, (participant, score) in enumerate(sorted_participants, 1):
                    points = RANKING_POINTS.get(rank, DEFAULT_POINTS)
                    if participant in totals:
                        totals[participant]["points"] += points
            
            sorted_t = sorted(totals.items(), key=lambda x: x[1]["points"], reverse=True)[:5]
            data = [(i+1, name, info["type"], info["points"]) for i, (name, info) in enumerate(sorted_t)]
            self._build_table(
                preview,
                [("rank", "الترتيب"), ("name", "المشارك"), ("type", "النوع"), ("points", "إجمالي النقاط")],
                data, widths=[60, 200, 100, 120], rank_colors=True
            )

    # -- Register Team -----------------------------------------------------

    def show_register_team(self):
        self._clear()
        self._page_title("تسجيل فريق جديد", "إضافة فريق إلى البطولة")

        card = Card(self.content)
        card.pack(fill="x", padx=30, pady=20)
        inner = tk.Frame(card, bg=COLORS["card"])
        inner.pack(fill="x", padx=24, pady=20)

        self._rt_entry = self._make_input(inner, "اسم الفريق", "أدخل اسم الفريق...")
        StyledButton(inner, text="  تسجيل الفريق  ", command=self._do_register_team
                     ).pack(anchor="e", pady=(16, 0))

    def _do_register_team(self):
        name = self._get_entry_value(self._rt_entry, "أدخل اسم الفريق...")
        if not name:
            messagebox.showwarning("خطأ في الإدخال", "اسم الفريق لا يمكن أن يكون فارغاً.")
            return
        if find_key_ci(teams, name):
            messagebox.showerror("مكرر", f'فريق باسم "{name}" موجود بالفعل.')
            return
        if len(teams) >= MAX_TEAMS:
            messagebox.showerror("تم الوصول للحد الأقصى", f'تم الوصول للحد الأقصى لعدد الفرق ({MAX_TEAMS}).')
            return
        teams[name] = []
        messagebox.showinfo("نجح", f'تم تسجيل الفريق "{name}"! ({len(teams)}/{MAX_TEAMS} فرق)')
        # Clear the field for the next entry
        self._rt_entry.delete(0, "end")

    # -- Register Individual -----------------------------------------------

    def show_register_individual(self):
        self._clear()
        self._page_title("تسجيل مشارك فردي", "إضافة مشارك فردي إلى البطولة")

        card = Card(self.content)
        card.pack(fill="x", padx=30, pady=20)
        inner = tk.Frame(card, bg=COLORS["card"])
        inner.pack(fill="x", padx=24, pady=20)

        self._ri_entry = self._make_input(inner, "اسم المشارك", "أدخل اسم المشارك...")
        StyledButton(inner, text="  تسجيل المشارك  ", command=self._do_register_individual,
                     bg_color=COLORS["success"], hover_color="#4ade80"
                     ).pack(anchor="e", pady=(16, 0))

    def _do_register_individual(self):
        name = self._get_entry_value(self._ri_entry, "أدخل اسم المشارك...")
        if not name:
            messagebox.showwarning("خطأ في الإدخال", "اسم المشارك لا يمكن أن يكون فارغاً.")
            return
        if find_key_ci(individuals, name):
            messagebox.showerror("مكرر", f'مشارك باسم "{name}" موجود بالفعل.')
            return
        if find_key_ci(teams, name):
            messagebox.showerror("تعارض", f'فريق باسم "{name}" موجود بالفعل. يرجى استخدام اسم مختلف.')
            return
        if len(individuals) >= MAX_INDIVIDUALS:
            messagebox.showerror("تم الوصول للحد الأقصى", f'تم الوصول للحد الأقصى لعدد الأفراد ({MAX_INDIVIDUALS}).')
            return
        individuals[name] = {"events": []}
        messagebox.showinfo("نجح", f'تم تسجيل المشارك "{name}"! ({len(individuals)}/{MAX_INDIVIDUALS} أفراد)')
        # Clear the field for the next entry
        self._ri_entry.delete(0, "end")

    # -- Add Player --------------------------------------------------------

    def show_add_player(self):
        self._clear()
        self._page_title("إضافة لاعب إلى فريق", "تعيين لاعب لفريق موجود")
        if not teams:
            self._empty_state("لا توجد فرق مسجلة بعد. يرجى تسجيل فريق أولاً.")
            return

        card = Card(self.content)
        card.pack(fill="x", padx=30, pady=20)
        inner = tk.Frame(card, bg=COLORS["card"])
        inner.pack(fill="x", padx=24, pady=20)

        self._ap_combo = self._make_dropdown(inner, "اختر الفريق", list(teams.keys()))
        self._ap_entry = self._make_input(inner, "اسم اللاعب", "أدخل اسم اللاعب...")
        StyledButton(inner, text="  إضافة اللاعب  ", command=self._do_add_player,
                     bg_color=COLORS["success"], hover_color="#4ade80"
                     ).pack(anchor="e", pady=(16, 0))

    def _do_add_player(self):
        team = self._ap_combo.get()
        player = self._get_entry_value(self._ap_entry, "أدخل اسم اللاعب...")
        if not team:
            messagebox.showwarning("خطأ في الإدخال", "يرجى اختيار فريق.")
            return
        if not player:
            messagebox.showwarning("خطأ في الإدخال", "اسم اللاعب لا يمكن أن يكون فارغاً.")
            return
        if len(teams[team]) >= MAX_TEAM_MEMBERS:
            messagebox.showerror("تم الوصول للحد الأقصى", f'الفريق "{team}" وصل للحد الأقصى لعدد الأعضاء ({MAX_TEAM_MEMBERS}).')
            return
        teams[team].append(player)
        messagebox.showinfo("نجح", f'تم إضافة "{player}" إلى "{team}"! ({len(teams[team])}/{MAX_TEAM_MEMBERS} أعضاء)')
        # Clear only the player name field, keep team selected
        self._ap_entry.delete(0, "end")

    # -- Create Event ------------------------------------------------------

    def show_create_event(self):
        self._clear()
        self._page_title("إنشاء حدث جديد", "تحديد حدث منافسة")

        card = Card(self.content)
        card.pack(fill="x", padx=30, pady=20)
        inner = tk.Frame(card, bg=COLORS["card"])
        inner.pack(fill="x", padx=24, pady=20)

        self._ce_entry = self._make_input(inner, "اسم الحدث", "أدخل اسم الحدث...")
        self._ce_type = self._make_radio_group(inner, "نوع الحدث", ["جماعي", "فردي"], "جماعي")
        self._ce_category = self._make_dropdown(inner, "فئة الحدث", 
                                                ["رياضي", "أكاديمي", "إبداعي", "أخرى"])
        StyledButton(inner, text="  إنشاء الحدث  ", command=self._do_create_event,
                     bg_color=COLORS["warning"], hover_color="#fbbf24",
                     text_color="#1e293b").pack(anchor="e", pady=(16, 0))

    def _do_create_event(self):
        name = self._get_entry_value(self._ce_entry, "أدخل اسم الحدث...")
        if not name:
            messagebox.showwarning("خطأ في الإدخال", "اسم الحدث لا يمكن أن يكون فارغاً.")
            return
        if find_key_ci(events, name):
            messagebox.showerror("مكرر", f'حدث باسم "{name}" موجود بالفعل.')
            return
        event_type_ar = self._ce_type.get()
        event_type = "team" if event_type_ar == "جماعي" else "individual"
        category_ar = self._ce_category.get()
        category_map = {"رياضي": "athletic", "أكاديمي": "academic", "إبداعي": "creative", "أخرى": "other"}
        category = category_map.get(category_ar, "other")
        if not category:
            category = "other"
        events[name] = {
            "type": event_type,
            "category": category,
            "scores": {}
        }
        messagebox.showinfo("نجح", f'تم إنشاء الحدث "{name}"! (النوع: {event_type_ar}, الفئة: {category_ar})')
        # Clear the field for the next entry
        self._ce_entry.delete(0, "end")

    # -- Record Score ------------------------------------------------------

    def show_record_score(self):
        self._clear()
        self._page_title("تسجيل نقاط", "إدخال نقاط مشارك في حدث")
        if not events:
            self._empty_state("تحتاج إلى حدث واحد على الأقل أولاً.")
            return

        card = Card(self.content)
        card.pack(fill="x", padx=30, pady=20)
        inner = tk.Frame(card, bg=COLORS["card"])
        inner.pack(fill="x", padx=24, pady=20)

        self._rs_event = self._make_dropdown(inner, "اختر الحدث", list(events.keys()))
        self._rs_event.bind("<<ComboboxSelected>>", self._on_event_selected)
        self._rs_participant_frame = tk.Frame(inner, bg=COLORS["card"])
        self._rs_participant_frame.pack(fill="x", pady=8)
        self._rs_participant = None
        # Initialize participant dropdown if an event is selected
        if events and self._rs_event.get():
            self._on_event_selected()
        self._rs_score = self._make_input(inner, "النقاط", "0")
        StyledButton(inner, text="  تسجيل النقاط  ", command=self._do_record_score,
                     bg_color=COLORS["danger"], hover_color="#f87171"
                     ).pack(anchor="e", pady=(16, 0))

    def _on_event_selected(self, event=None):
        """Update participant dropdown based on selected event type."""
        event_name = self._rs_event.get()
        if not event_name or event_name not in events:
            return
        
        # Clear existing participant dropdown
        for widget in self._rs_participant_frame.winfo_children():
            widget.destroy()
        
        ev_data = events[event_name]
        event_type = ev_data.get("type", "team")
        
        if event_type == "team":
            if not teams:
                tk.Label(self._rs_participant_frame, text="لا توجد فرق مسجلة بعد.",
                        font=FONT_BODY, bg=COLORS["card"], fg=COLORS["text_dim"], anchor="e", justify="right").pack(anchor="e", fill="x")
                self._rs_participant = None
                return
            self._rs_participant = self._make_dropdown(self._rs_participant_frame, "اختر الفريق", list(teams.keys()))
        else:  # individual
            if not individuals:
                tk.Label(self._rs_participant_frame, text="لا يوجد أفراد مسجلون بعد.",
                        font=FONT_BODY, bg=COLORS["card"], fg=COLORS["text_dim"], anchor="e", justify="right").pack(anchor="e", fill="x")
                self._rs_participant = None
                return
            self._rs_participant = self._make_dropdown(self._rs_participant_frame, "اختر المشارك", list(individuals.keys()))

    def _do_record_score(self):
        event_name = self._rs_event.get()
        if not event_name:
            messagebox.showwarning("خطأ في الإدخال", "يرجى اختيار حدث.")
            return
        if not self._rs_participant:
            messagebox.showwarning("خطأ في الإدخال", "لا يوجد مشاركون متاحون لهذا النوع من الأحداث.")
            return
        
        participant = self._rs_participant.get()
        if not participant:
            messagebox.showwarning("خطأ في الإدخال", "يرجى اختيار مشارك.")
            return
        
        score_str = self._get_entry_value(self._rs_score, "0")
        if not score_str:
            score_str = "0"
        try:
            score = float(score_str)
        except ValueError:
            messagebox.showwarning("خطأ في الإدخال", "النقاط يجب أن تكون رقماً.")
            return
        
        ev_data = events[event_name]
        event_type = ev_data.get("type", "team")
        
        # Check if participant can participate in this event type
        if event_type == "team" and participant not in teams:
            messagebox.showerror("خطأ", f'"{participant}" ليس فريقاً مسجلاً.')
            return
        if event_type == "individual" and participant not in individuals:
            messagebox.showerror("خطأ", f'"{participant}" ليس مشاركاً فردياً مسجلاً.')
            return
        
        # Check participation limit (1-5 events per participant)
        if event_type == "team":
            # Count events this team has participated in
            team_events = sum(1 for ev in events.values() if participant in ev.get("scores", {}))
            if team_events >= MAX_EVENTS_PER_PARTICIPANT:
                messagebox.showwarning("تم الوصول للحد الأقصى", 
                    f'الفريق "{participant}" شارك بالفعل في {MAX_EVENTS_PER_PARTICIPANT} أحداث (الحد الأقصى المسموح).')
                return
        else:  # individual
            # Count events this individual has participated in
            ind_events = len(individuals[participant].get("events", []))
            if ind_events >= MAX_EVENTS_PER_PARTICIPANT:
                messagebox.showwarning("تم الوصول للحد الأقصى", 
                    f'المشارك "{participant}" شارك بالفعل في {MAX_EVENTS_PER_PARTICIPANT} أحداث (الحد الأقصى المسموح).')
                return
        
        # Record score
        ev_data["scores"][participant] = score
        
        # Track participation for individuals
        if event_type == "individual":
            if event_name not in individuals[participant]["events"]:
                individuals[participant]["events"].append(event_name)
        
        messagebox.showinfo("نجح", f"{participant} حصل على {score} نقطة في {event_name}!")
        # Clear only the score field, keep event and participant selected
        self._rs_score.delete(0, "end")

    # -- View Roster -------------------------------------------------------

    def show_view_roster(self):
        self._clear()
        self._page_title("قائمة الفريق", "عرض اللاعبين في فريق")
        if not teams:
            self._empty_state("لا توجد فرق مسجلة بعد.")
            return

        card = Card(self.content)
        card.pack(fill="x", padx=30, pady=20)
        inner = tk.Frame(card, bg=COLORS["card"])
        inner.pack(fill="x", padx=24, pady=20)

        self._vr_combo = self._make_dropdown(inner, "اختر الفريق", list(teams.keys()))
        StyledButton(inner, text="  عرض القائمة  ", command=self._do_view_roster
                     ).pack(anchor="e", pady=(16, 0))

        self._vr_result = tk.Frame(self.content, bg=COLORS["bg"])
        self._vr_result.pack(fill="both", expand=True, padx=30, pady=(0, 20))

    def _do_view_roster(self):
        team = self._vr_combo.get()
        if not team:
            messagebox.showwarning("خطأ في الإدخال", "يرجى اختيار فريق.")
            return
        for w in self._vr_result.winfo_children():
            w.destroy()

        players = teams[team]
        result_card = Card(self._vr_result)
        result_card.pack(fill="both", expand=True)

        header = tk.Frame(result_card, bg=COLORS["card"])
        header.pack(fill="x", padx=16, pady=(14, 0))
        tk.Label(header, text=f"{team}  \u2691", font=FONT_HEADING,
                 bg=COLORS["card"], fg=COLORS["text"], anchor="e", justify="right").pack(side="right")
        player_count_text = f"{len(players)}/{MAX_TEAM_MEMBERS} لاعب"
        tk.Label(header, text=player_count_text, font=FONT_BADGE,
                 bg=COLORS["accent"], fg="white", padx=8, pady=2).pack(side="left")

        tk.Frame(result_card, bg=COLORS["card_border"], height=1).pack(
            fill="x", padx=16, pady=8)

        if not players:
            tk.Label(result_card, text="لم يتم إضافة لاعبين بعد.",
                     font=FONT_BODY, bg=COLORS["card"],
                     fg=COLORS["text_dim"]).pack(pady=20)
        else:
            data = [(i, p) for i, p in enumerate(players, 1)]
            self._build_table(result_card,
                              [("#", "#"), ("name", "اسم اللاعب")],
                              data, widths=[60, 400])

    # -- Event Scores ------------------------------------------------------

    def show_event_scores(self):
        self._clear()
        self._page_title("نتائج الأحداث", "عرض النقاط لحدث محدد")
        if not events:
            self._empty_state("لم يتم إنشاء أحداث بعد.")
            return

        card = Card(self.content)
        card.pack(fill="x", padx=30, pady=20)
        inner = tk.Frame(card, bg=COLORS["card"])
        inner.pack(fill="x", padx=24, pady=20)

        self._es_combo = self._make_dropdown(inner, "اختر الحدث", list(events.keys()))
        StyledButton(inner, text="  عرض النقاط  ", command=self._do_event_scores,
                     bg_color=COLORS["warning"], hover_color="#fbbf24",
                     text_color="#1e293b").pack(anchor="e", pady=(16, 0))

        self._es_result = tk.Frame(self.content, bg=COLORS["bg"])
        self._es_result.pack(fill="both", expand=True, padx=30, pady=(0, 20))

    def _do_event_scores(self):
        event_name = self._es_combo.get()
        if not event_name:
            messagebox.showwarning("خطأ في الإدخال", "يرجى اختيار حدث.")
            return
        for w in self._es_result.winfo_children():
            w.destroy()

        ev_data = events[event_name]
        scores = ev_data.get("scores", {})
        event_type = ev_data.get("type", "team")
        event_category = ev_data.get("category", "other")
        
        # Map to Arabic
        type_map = {"team": "جماعي", "individual": "فردي"}
        category_map = {"athletic": "رياضي", "academic": "أكاديمي", "creative": "إبداعي", "other": "أخرى"}
        event_type_ar = type_map.get(event_type, event_type)
        event_category_ar = category_map.get(event_category, event_category)
        
        result_card = Card(self._es_result)
        result_card.pack(fill="both", expand=True)

        header = tk.Frame(result_card, bg=COLORS["card"])
        header.pack(fill="x", padx=16, pady=(14, 0))
        tk.Label(header, text=f"{event_name}  \u2605", font=FONT_HEADING,
                 bg=COLORS["card"], fg=COLORS["text"], anchor="e", justify="right").pack(side="right")
        info_text = f"{len(scores)} مشارك | {event_category_ar} | {event_type_ar}"
        tk.Label(header, text=info_text, font=FONT_BADGE,
                 bg=COLORS["warning"], fg="#1e293b", padx=8, pady=2).pack(side="left")

        tk.Frame(result_card, bg=COLORS["card_border"], height=1).pack(
            fill="x", padx=16, pady=8)

        if not scores:
            tk.Label(result_card, text="لم يتم تسجيل نقاط بعد.",
                     font=FONT_BODY, bg=COLORS["card"],
                     fg=COLORS["text_dim"]).pack(pady=20)
        else:
            # Sort by score (descending) and assign ranking points
            sorted_scores = sorted(scores.items(), key=lambda x: x[1], reverse=True)
            data = []
            for rank, (participant, score) in enumerate(sorted_scores, 1):
                points = RANKING_POINTS.get(rank, DEFAULT_POINTS)
                data.append((rank, participant, score, points))
            
            self._build_table(result_card,
                              [("rank", "الترتيب"), ("participant", "المشارك"), ("score", "النقاط"), ("points", "النقاط الممنوحة")],
                              data, widths=[60, 250, 100, 120], rank_colors=True)

    # -- Leaderboard -------------------------------------------------------

    def show_leaderboard(self):
        self._clear()
        self._page_title("الترتيب العام", "الترتيب الشامل لجميع الأحداث")
        if not teams and not individuals:
            self._empty_state("لا يوجد مشاركون مسجلون بعد.")
            return

        totals = {}
        # Initialize totals for teams
        for team in teams:
            totals[team] = {"type": "فريق", "points": 0, "events": 0}
        # Initialize totals for individuals
        for ind in individuals:
            totals[ind] = {"type": "فرد", "points": 0, "events": len(individuals[ind].get("events", []))}
        
        # Calculate ranking-based points for each event
        for ev_name, ev_data in events.items():
            scores = ev_data.get("scores", {})
            if not scores:
                continue
            # Sort by score (descending)
            sorted_participants = sorted(scores.items(), key=lambda x: x[1], reverse=True)
            # Assign ranking points
            for rank, (participant, score) in enumerate(sorted_participants, 1):
                points = RANKING_POINTS.get(rank, DEFAULT_POINTS)
                if participant in totals:
                    totals[participant]["points"] += points
                    totals[participant]["events"] += 1
        
        sorted_participants = sorted(totals.items(), key=lambda x: x[1]["points"], reverse=True)

        # Top 3 podium
        if len(sorted_participants) >= 1:
            podium = tk.Frame(self.content, bg=COLORS["bg"])
            podium.pack(fill="x", padx=30, pady=(16, 6))

            medals = [("\U0001F947", COLORS["gold"]),
                      ("\U0001F948", COLORS["silver"]),
                      ("\U0001F949", COLORS["bronze"])]

            for i in range(min(3, len(sorted_participants))):
                p_name, p_info = sorted_participants[i]
                medal_text, medal_color = medals[i]
                pcard = Card(podium)
                pcard.pack(side="right", padx=(12, 0), ipadx=6)
                inner = tk.Frame(pcard, bg=COLORS["card"])
                inner.pack(padx=18, pady=14)
                tk.Label(inner, text=medal_text, font=("Tahoma", 22),
                         bg=COLORS["card"]).pack()
                tk.Label(inner, text=p_name, font=FONT_HEADING,
                         bg=COLORS["card"], fg=medal_color).pack()
                tk.Label(inner, text=f"{p_info['points']} نقطة", font=FONT_BIG_NUM,
                         bg=COLORS["card"], fg=COLORS["text"]).pack()
                tk.Label(inner, text=p_info["type"], font=FONT_SMALL,
                         bg=COLORS["card"], fg=COLORS["text_dim"]).pack()

        # Full table
        table_card = Card(self.content)
        table_card.pack(fill="both", expand=True, padx=30, pady=(10, 24))
        tk.Label(table_card, text="الترتيب الكامل  ", font=FONT_HEADING,
                 bg=COLORS["card"], fg=COLORS["text"], anchor="e", justify="right").pack(
            anchor="e", fill="x", padx=16, pady=(14, 0))
        tk.Frame(table_card, bg=COLORS["card_border"], height=1).pack(
            fill="x", padx=16, pady=8)

        data = [(i+1, name, info["type"], info["points"], info["events"]) 
                for i, (name, info) in enumerate(sorted_participants)]
        self._build_table(
            table_card,
            [("rank", "الترتيب"), ("name", "المشارك"), ("type", "النوع"), ("points", "إجمالي النقاط"), ("events", "الأحداث")],
            data, widths=[60, 200, 100, 120, 80], rank_colors=True
        )


# ---------------------------------------------------------------------------
#  Entry Point
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    app = TournamentApp()
    app.mainloop()
