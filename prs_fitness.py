"""
PRS Fitness - Premium Fitness Studio Application
Combines BMI Calculator + Weekly Workout Scheduler
Optimized startup: pure tkinter (no customtkinter), page cache, fixed scroll bindings.
"""

import tkinter as tk
from tkinter import ttk, messagebox
import math
from datetime import datetime
from dataclasses import dataclass, field
from enum import Enum
from typing import Optional

# ─────────────────────────────────────────────
# THEME
# ─────────────────────────────────────────────
class T:
    BG          = "#080B10"
    SIDEBAR     = "#0D1117"
    CARD        = "#111827"
    CARD2       = "#1A2233"
    BORDER      = "#1E293B"
    INPUT       = "#1E293B"

    CYAN        = "#00E5FF"
    CYAN_DIM    = "#0A2535"
    GREEN       = "#00FF88"
    GREEN_DIM   = "#0A2E1A"
    AMBER       = "#FFB800"
    AMBER_DIM   = "#2E1F00"
    RED         = "#FF4444"
    RED_DIM     = "#2E0A0A"
    PURPLE      = "#A855F7"

    WHITE       = "#F0F4FF"
    GRAY        = "#64748B"
    LIGHT       = "#94A3B8"

    CAT_COLORS = {
        "underweight": "#38BDF8",
        "normal":      "#00FF88",
        "overweight":  "#FFB800",
        "obese":       "#FF4444",
    }
    CAT_DIM = {
        "underweight": "#0D2744",
        "normal":      "#0D2E1A",
        "overweight":  "#2E1F06",
        "obese":       "#2E0D0B",
    }

    LEVEL_BEGINNER     = "#00FF88"
    LEVEL_INTERMEDIATE = "#FFB800"
    LEVEL_PRO          = "#FF4444"

    FONT_H1   = ("Segoe UI", 26, "bold")
    FONT_H2   = ("Segoe UI", 18, "bold")
    FONT_H3   = ("Segoe UI", 14, "bold")
    FONT_BODY = ("Segoe UI", 11)
    FONT_BOLD = ("Segoe UI", 11, "bold")
    FONT_SM   = ("Segoe UI", 9)
    FONT_BTN  = ("Segoe UI", 10, "bold")
    FONT_NUM  = ("Segoe UI", 52, "bold")


# ─────────────────────────────────────────────
# DATA MODELS
# ─────────────────────────────────────────────
class ExperienceLevel(Enum):
    BEGINNER     = "Beginner"
    INTERMEDIATE = "Intermediate"
    PROFESSIONAL = "Professional"


class ScheduleType(Enum):
    PPL_3DAY      = "Push-Pull-Legs (3 Day)"
    PPL_6DAY      = "Push-Pull-Legs (6 Day)"
    UPPER_LOWER   = "Upper / Lower Split"
    FULL_BODY     = "Full Body (3 Day)"
    BRO_SPLIT     = "Bro Split (5 Day)"
    ARNOLD_SPLIT  = "Arnold Split (6 Day)"


@dataclass
class Exercise:
    name: str
    sets: int
    reps: str
    rest_seconds: int
    notes: str = ""
    is_premium: bool = False


@dataclass
class WorkoutDay:
    name: str
    focus: str
    exercises: list = field(default_factory=list)
    duration_minutes: int = 60


@dataclass
class WeeklySchedule:
    schedule_type: ScheduleType
    experience_level: ExperienceLevel
    days: dict = field(default_factory=dict)


@dataclass
class UserProfile:
    username: str = "Athlete"
    experience_level: ExperienceLevel = ExperienceLevel.INTERMEDIATE
    is_premium: bool = False
    current_schedule: Optional[WeeklySchedule] = None
    workout_history: list = field(default_factory=list)
    last_bmi: Optional[float] = None
    last_bmi_cat: Optional[str] = None


# ─────────────────────────────────────────────
# WORKOUT DATABASE
# ─────────────────────────────────────────────
class WDB:
    @staticmethod
    def push(level):
        base = [
            Exercise("Bench Press",           4, "8-10",  90, "Drive through chest"),
            Exercise("Overhead Press",         3, "8-12",  90, "Brace your core"),
            Exercise("Incline DB Press",       3, "10-12", 75),
            Exercise("Lateral Raises",         3, "12-15", 60),
            Exercise("Tricep Pushdowns",       3, "12-15", 60),
        ]
        if level == ExperienceLevel.BEGINNER:
            return base[:4]
        if level == ExperienceLevel.INTERMEDIATE:
            base.append(Exercise("Dips", 3, "8-12", 75))
            return base
        base += [
            Exercise("Dips", 4, "10-12", 60),
            Exercise("Cable Flyes", 3, "12-15", 60, is_premium=True),
            Exercise("OH Tricep Extension", 3, "10-12", 60),
        ]
        return base

    @staticmethod
    def pull(level):
        base = [
            Exercise("Deadlift",              4, "5-8",   120, "Neutral spine"),
            Exercise("Pull-ups / Lat PD",     4, "8-12",   90),
            Exercise("Barbell Rows",          4, "8-10",   90),
            Exercise("Face Pulls",            3, "15-20",  60, "Rear delt focus"),
            Exercise("Barbell Curls",         3, "10-12",  60),
        ]
        if level == ExperienceLevel.BEGINNER:
            base[0] = Exercise("Romanian Deadlift", 3, "10-12", 90)
            return base[:4]
        if level == ExperienceLevel.INTERMEDIATE:
            base.append(Exercise("Hammer Curls", 3, "10-12", 60))
            return base
        base += [
            Exercise("Hammer Curls", 3, "10-12", 60),
            Exercise("Seated Cable Rows", 3, "10-12", 75, is_premium=True),
            Exercise("Preacher Curls", 3, "10-12", 60),
        ]
        return base

    @staticmethod
    def legs(level):
        base = [
            Exercise("Squats",            4, "6-10",  120, "Below parallel"),
            Exercise("Romanian Deadlift", 3, "10-12",  90),
            Exercise("Leg Press",         3, "10-15",  90),
            Exercise("Leg Curls",         3, "12-15",  60),
            Exercise("Calf Raises",       4, "15-20",  45),
        ]
        if level == ExperienceLevel.BEGINNER:
            base[0] = Exercise("Goblet Squats", 3, "12-15", 75)
            return base[:4]
        if level == ExperienceLevel.INTERMEDIATE:
            base.append(Exercise("Walking Lunges", 3, "12 each", 75))
            return base
        base += [
            Exercise("Bulgarian Split Squats", 3, "10 each", 75),
            Exercise("Leg Extensions", 3, "12-15", 60, is_premium=True),
            Exercise("Hip Thrusts", 3, "10-12", 75),
        ]
        return base

    @staticmethod
    def upper(level):
        ex = [
            Exercise("Bench Press", 4, "8-10", 90),
            Exercise("Barbell Rows", 4, "8-10", 90),
            Exercise("Overhead Press", 3, "8-12", 75),
            Exercise("Pull-ups / Lat PD", 3, "8-12", 75),
            Exercise("Lateral Raises", 3, "12-15", 60),
            Exercise("Tricep Pushdowns", 3, "12-15", 60),
            Exercise("Barbell Curls", 3, "10-12", 60),
        ]
        return ex[:5] if level == ExperienceLevel.BEGINNER else ex

    @staticmethod
    def lower(level):
        ex = [
            Exercise("Squats", 4, "6-10", 120),
            Exercise("Romanian Deadlift", 4, "8-10", 90),
            Exercise("Leg Press", 3, "10-15", 90),
            Exercise("Leg Curls", 3, "12-15", 60),
            Exercise("Walking Lunges", 3, "12 each", 75),
            Exercise("Calf Raises", 4, "15-20", 45),
        ]
        return ex[:4] if level == ExperienceLevel.BEGINNER else ex

    @staticmethod
    def full_body(level):
        ex = [
            Exercise("Squats", 3, "8-10", 90),
            Exercise("Bench Press", 3, "8-10", 90),
            Exercise("Barbell Rows", 3, "8-10", 90),
            Exercise("Overhead Press", 3, "8-12", 75),
            Exercise("Romanian Deadlift", 3, "10-12", 90),
            Exercise("Pull-ups / Lat PD", 3, "8-12", 75),
        ]
        return ex[:4] if level == ExperienceLevel.BEGINNER else ex


# ─────────────────────────────────────────────
# SCHEDULE GENERATOR
# ─────────────────────────────────────────────
WEEKDAYS = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]


def _clone_day(day: WorkoutDay) -> WorkoutDay:
    return WorkoutDay(day.name, day.focus, list(day.exercises), day.duration_minutes)


class ScheduleGen:
    @classmethod
    def generate(cls, stype, level):
        s = WeeklySchedule(stype, level, {d: None for d in WEEKDAYS})
        {
            ScheduleType.PPL_3DAY:     cls._ppl3,
            ScheduleType.PPL_6DAY:     cls._ppl6,
            ScheduleType.UPPER_LOWER:  cls._ul,
            ScheduleType.FULL_BODY:    cls._fb,
            ScheduleType.BRO_SPLIT:    cls._bro,
            ScheduleType.ARNOLD_SPLIT: cls._arnold,
        }[stype](s, level)
        return s

    @classmethod
    def _ppl3(cls, s, lvl):
        dur = 45 if lvl == ExperienceLevel.BEGINNER else 60
        s.days["Monday"]    = WorkoutDay("Push Day",  "Chest · Shoulders · Triceps", WDB.push(lvl), dur)
        s.days["Wednesday"] = WorkoutDay("Pull Day",  "Back · Biceps",               WDB.pull(lvl), dur)
        s.days["Friday"]    = WorkoutDay("Legs Day",  "Quads · Hamstrings · Glutes", WDB.legs(lvl), dur)

    @classmethod
    def _ppl6(cls, s, lvl):
        p = WorkoutDay("Push Day", "Chest · Shoulders · Triceps", WDB.push(lvl), 60)
        l = WorkoutDay("Pull Day", "Back · Biceps", WDB.pull(lvl), 60)
        g = WorkoutDay("Legs Day", "Quads · Hamstrings · Glutes", WDB.legs(lvl), 60)
        for day, wd in zip(
            ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday"],
            [p, l, g, _clone_day(p), _clone_day(l), _clone_day(g)],
        ):
            s.days[day] = wd

    @classmethod
    def _ul(cls, s, lvl):
        u = WorkoutDay("Upper Body", "Chest · Back · Shoulders · Arms", WDB.upper(lvl), 60)
        lo = WorkoutDay("Lower Body", "Quads · Hamstrings · Glutes · Calves", WDB.lower(lvl), 60)
        s.days["Monday"]   = u
        s.days["Tuesday"]  = lo
        s.days["Thursday"] = _clone_day(u)
        s.days["Friday"]   = _clone_day(lo)

    @classmethod
    def _fb(cls, s, lvl):
        w = WorkoutDay("Full Body", "All Major Muscle Groups", WDB.full_body(lvl), 60)
        for d in ["Monday", "Wednesday", "Friday"]:
            s.days[d] = _clone_day(w)

    @classmethod
    def _bro(cls, s, lvl):
        s.days["Monday"]    = WorkoutDay("Chest Day", "Chest", [
            Exercise("Bench Press", 4, "8-10", 90), Exercise("Incline DB Press", 4, "10-12", 75),
            Exercise("Cable Flyes", 3, "12-15", 60), Exercise("Dips", 3, "10-12", 75)], 50)
        s.days["Tuesday"]   = WorkoutDay("Back Day", "Back", [
            Exercise("Deadlift", 4, "5-8", 120), Exercise("Pull-ups", 4, "8-12", 90),
            Exercise("Barbell Rows", 4, "8-10", 90), Exercise("Seated Cable Rows", 3, "10-12", 75)], 55)
        s.days["Wednesday"] = WorkoutDay("Shoulders", "Delts", [
            Exercise("Overhead Press", 4, "8-10", 90), Exercise("Lateral Raises", 4, "12-15", 60),
            Exercise("Face Pulls", 3, "15-20", 60), Exercise("Rear Delt Flyes", 3, "12-15", 60)], 45)
        s.days["Thursday"]  = WorkoutDay("Legs Day", "Legs", WDB.legs(lvl), 60)
        s.days["Friday"]    = WorkoutDay("Arms Day", "Biceps & Triceps", [
            Exercise("Barbell Curls", 4, "10-12", 60), Exercise("CG Bench Press", 4, "8-10", 90),
            Exercise("Hammer Curls", 3, "10-12", 60), Exercise("Tricep Pushdowns", 3, "12-15", 60),
            Exercise("Preacher Curls", 3, "10-12", 60), Exercise("OH Tricep Extension", 3, "10-12", 60)], 50)

    @classmethod
    def _arnold(cls, s, lvl):
        cb = WorkoutDay("Chest & Back", "Push-Pull Superset", [
            Exercise("Bench Press", 4, "8-10", 90), Exercise("Pull-ups", 4, "8-12", 90, "SS w/ Bench"),
            Exercise("Incline DB Press", 3, "10-12", 75), Exercise("Barbell Rows", 3, "8-10", 90, "SS w/ Incline"),
            Exercise("Cable Flyes", 3, "12-15", 60), Exercise("Seated Cable Rows", 3, "10-12", 75)], 65)
        sa = WorkoutDay("Shoulders & Arms", "Delts & Arms", [
            Exercise("Overhead Press", 4, "8-10", 90), Exercise("Lateral Raises", 4, "12-15", 60),
            Exercise("Barbell Curls", 4, "10-12", 60), Exercise("Tricep Pushdowns", 4, "12-15", 60),
            Exercise("Hammer Curls", 3, "10-12", 60), Exercise("OH Tricep Extension", 3, "10-12", 60)], 60)
        lg = WorkoutDay("Legs Day", "Full Leg Development", WDB.legs(lvl), 60)
        for day, wd in zip(
            ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday"],
            [cb, sa, lg, _clone_day(cb), _clone_day(sa), _clone_day(lg)],
        ):
            s.days[day] = wd


# ─────────────────────────────────────────────
# REUSABLE WIDGETS
# ─────────────────────────────────────────────
def _parent_bg(parent) -> str:
    try:
        return parent.cget("bg")
    except tk.TclError:
        return T.BG


class NavButton(tk.Frame):
    def __init__(self, parent, icon, label, command, active=False, **kw):
        super().__init__(parent, bg=T.SIDEBAR, cursor="hand2", **kw)
        self.command = command
        self.active = active
        self._icon = icon
        self._label = label
        self._bar = tk.Frame(self, bg=T.CYAN if active else T.SIDEBAR, width=3)
        self._bar.pack(side="left", fill="y")
        self._inner = tk.Frame(self, bg=T.CARD if active else T.SIDEBAR, padx=14, pady=12)
        self._inner.pack(fill="x", expand=True)
        fg = T.WHITE if active else T.GRAY
        self._icon_lbl = tk.Label(self._inner, text=icon, font=("Segoe UI", 13), fg=fg, bg=self._inner["bg"])
        self._icon_lbl.pack(side="left")
        self._text_lbl = tk.Label(self._inner, text=f"  {label}", font=T.FONT_BOLD, fg=fg, bg=self._inner["bg"])
        self._text_lbl.pack(side="left")
        self._bind_all()

    def _bind_all(self):
        for w in (self, self._bar, self._inner, self._icon_lbl, self._text_lbl):
            w.bind("<Button-1>", self._on_click)
            w.bind("<Enter>", self._hover_on)
            w.bind("<Leave>", self._hover_off)

    def _on_click(self, _event=None):
        self.command()

    def _hover_on(self, _event=None):
        if not self.active:
            self._set_colors(T.CARD, T.LIGHT)

    def _hover_off(self, _event=None):
        if not self.active:
            self._set_colors(T.SIDEBAR, T.GRAY)

    def _set_colors(self, bg, fg):
        self.configure(bg=bg)
        self._bar.configure(bg=T.CYAN if self.active else bg)
        self._inner.configure(bg=T.CARD if self.active else bg)
        icon_bg = self._inner["bg"]
        self._icon_lbl.configure(bg=icon_bg, fg=fg if not self.active else T.WHITE)
        self._text_lbl.configure(bg=icon_bg, fg=fg if not self.active else T.WHITE)

    def set_active(self, state):
        self.active = state
        bg = T.CARD if state else T.SIDEBAR
        fg = T.WHITE if state else T.GRAY
        self._bar.configure(bg=T.CYAN if state else T.SIDEBAR)
        self._inner.configure(bg=bg)
        self._icon_lbl.configure(bg=bg, fg=fg)
        self._text_lbl.configure(bg=bg, fg=fg)
        self.configure(bg=T.SIDEBAR)


class PRSButton(tk.Canvas):
    STYLES = {
        "cyan":   (T.CYAN,   "#00C0D8", "#000"),
        "green":  (T.GREEN,  "#00CC6A", "#000"),
        "amber":  (T.AMBER,  "#CC9200", "#000"),
        "ghost":  (T.CARD2,  T.CARD,    T.LIGHT),
        "danger": (T.RED,    "#CC2222", "#fff"),
    }

    def __init__(self, parent, text, command=None, style="cyan",
                 width=160, height=44, **kw):
        bg = kw.pop("bg", _parent_bg(parent))
        super().__init__(parent, width=width, height=height,
                         highlightthickness=0, bg=bg, **kw)
        self.text = text
        self.command = command
        self.w = width
        self.h = height
        self.bg, self.hov, self.fg = self.STYLES.get(style, self.STYLES["cyan"])
        self._cur = self.bg
        self._draw()
        self.bind("<Enter>", lambda _e: self._enter())
        self.bind("<Leave>", lambda _e: self._leave())
        self.bind("<Button-1>", lambda _e: command() if command else None)
        self.config(cursor="hand2")

    def _draw(self):
        self.delete("all")
        r = 10
        self.create_polygon(
            r, 0, self.w - r, 0, self.w, r, self.w, self.h - r,
            self.w - r, self.h, r, self.h, 0, self.h - r, 0, r,
            fill=self._cur, smooth=True,
        )
        self.create_text(self.w // 2, self.h // 2, text=self.text,
                         fill=self.fg, font=T.FONT_BTN)

    def _enter(self):
        self._cur = self.hov
        self._draw()

    def _leave(self):
        self._cur = self.bg
        self._draw()


class SliderCard(tk.Frame):
    def __init__(self, parent, title, unit, lo, hi, start, on_change=None, **kw):
        super().__init__(parent, bg=T.CARD, height=120, **kw)
        self.pack_propagate(False)
        self._unit = unit
        self._on_change = on_change

        hdr = tk.Frame(self, bg=T.CARD)
        hdr.pack(fill="x", padx=18, pady=(14, 0))
        tk.Label(hdr, text=title, font=("Segoe UI", 13, "bold"),
                 fg=T.WHITE, bg=T.CARD).pack(side="left")
        badge = tk.Frame(hdr, bg=T.CYAN_DIM, padx=10, pady=3)
        badge.pack(side="right")
        self.val_lbl = tk.Label(badge, text=f"{start:.1f} {unit}",
                                font=("Segoe UI", 13, "bold"), fg=T.CYAN, bg=T.CYAN_DIM)
        self.val_lbl.pack()

        self._var = tk.DoubleVar(master=self, value=start)
        scale_kw = dict(
            orient=tk.HORIZONTAL,
            variable=self._var,
            showvalue=False,
            bg=T.CARD,
            fg=T.WHITE,
            troughcolor=T.INPUT,
            activebackground=T.CYAN,
            highlightthickness=0,
            command=self._slider_changed,
        )
        try:
            self.slider = tk.Scale(self, from_=lo, to=hi, resolution=0.1, **scale_kw)
        except tk.TclError:
            self.slider = tk.Scale(self, from_=lo, to=hi, **scale_kw)
        self.slider.pack(fill="x", padx=18, pady=(8, 0), expand=True)

        rng = tk.Frame(self, bg=T.CARD)
        rng.pack(fill="x", padx=18, pady=(3, 12))
        tk.Label(rng, text=f"{lo} {unit}", font=("Segoe UI", 10),
                 fg=T.GRAY, bg=T.CARD).pack(side="left")
        tk.Label(rng, text=f"{hi} {unit}", font=("Segoe UI", 10),
                 fg=T.GRAY, bg=T.CARD).pack(side="right")

    def _slider_changed(self, _value):
        self.val_lbl.configure(text=f"{self._var.get():.1f} {self._unit}")
        if self._on_change:
            self._on_change()

    def get(self) -> float:
        return self._var.get()

    def set(self, value: float):
        self._var.set(value)
        self.val_lbl.configure(text=f"{value:.1f} {self._unit}")


class SectionHeader(tk.Frame):
    def __init__(self, parent, title, subtitle="", **kw):
        super().__init__(parent, bg=T.BG, **kw)
        tk.Label(self, text=title, font=T.FONT_H1,
                 fg=T.WHITE, bg=T.BG).pack(anchor="w")
        if subtitle:
            tk.Label(self, text=subtitle, font=T.FONT_BODY,
                     fg=T.GRAY, bg=T.BG).pack(anchor="w", pady=(4, 0))


class StatCard(tk.Frame):
    def __init__(self, parent, icon, label, value, color=T.CYAN, **kw):
        super().__init__(parent, bg=T.CARD, padx=22, pady=18, **kw)
        tk.Label(self, text=icon, font=("Segoe UI", 22), bg=T.CARD).pack()
        tk.Label(self, text=value, font=T.FONT_BOLD, fg=color, bg=T.CARD).pack(pady=(6, 0))
        tk.Label(self, text=label, font=T.FONT_SM, fg=T.GRAY, bg=T.CARD).pack()


# ─────────────────────────────────────────────
# MAIN APP
# ─────────────────────────────────────────────
class PRSFitness(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("PRS Fitness")
        self.geometry("1180x720")
        self.minsize(960, 640)
        self.configure(bg=T.BG)

        self.user = UserProfile()
        self.schedule = None
        self._active_nav = None
        self._page_cache: dict[str, tk.Frame] = {}
        self._scroll_canvas: Optional[tk.Canvas] = None
        self._bmi_built = False

        self._build_sidebar()
        self._build_content()

        # Show window immediately; build first page on next event-loop tick.
        self._splash = tk.Label(
            self.content, text="Loading PRS Fitness…",
            font=T.FONT_H2, fg=T.GRAY, bg=T.BG,
        )
        self._splash.pack(expand=True)
        self.after_idle(self._finish_startup)

    def _finish_startup(self):
        self._splash.destroy()
        self._nav_to("dashboard")

    # ──────────────── SIDEBAR ────────────────
    def _build_sidebar(self):
        sb = tk.Frame(self, bg=T.SIDEBAR, width=220)
        sb.pack(side="left", fill="y")
        sb.pack_propagate(False)

        logo_f = tk.Frame(sb, bg=T.SIDEBAR, pady=28, padx=20)
        logo_f.pack(fill="x")
        tk.Label(logo_f, text="PRS", font=("Segoe UI", 28, "bold"),
                 fg=T.CYAN, bg=T.SIDEBAR).pack(side="left")
        tk.Label(logo_f, text=" Fitness", font=("Segoe UI", 20, "bold"),
                 fg=T.WHITE, bg=T.SIDEBAR).pack(side="left")

        tk.Frame(sb, bg=T.BORDER, height=1).pack(fill="x", padx=16, pady=(0, 10))

        nav_items = [
            ("dashboard", "🏠", "Dashboard"),
            ("bmi", "⚖", "BMI Calculator"),
            ("schedule", "📅", "My Schedule"),
            ("builder", "⚙", "Build Schedule"),
            ("chatbot", "🤖", "AI Coach"),
            ("profile", "👤", "Profile"),
            ("premium", "⭐", "Go Premium"),
        ]
        self._nav_btns = {}
        for key, icon, label in nav_items:
            btn = NavButton(sb, icon, label, lambda k=key: self._nav_to(k))
            btn.pack(fill="x")
            self._nav_btns[key] = btn

        bot = tk.Frame(sb, bg=T.SIDEBAR)
        bot.pack(side="bottom", fill="x", pady=20, padx=16)
        tk.Frame(bot, bg=T.BORDER, height=1).pack(fill="x", pady=(0, 12))
        self._status_lbl = tk.Label(bot, text="Free Account",
                                    font=T.FONT_SM, fg=T.GRAY, bg=T.SIDEBAR)
        self._status_lbl.pack()

    # ──────────────── CONTENT / NAV ────────────────
    def _build_content(self):
        self.content = tk.Frame(self, bg=T.BG)
        self.content.pack(side="right", fill="both", expand=True)

    def _detach_scroll(self):
        if self._scroll_canvas:
            for seq in ("<MouseWheel>", "<Button-4>", "<Button-5>"):
                try:
                    self._scroll_canvas.unbind_all(seq)
                except tk.TclError:
                    pass
        self._scroll_canvas = None

    def _hide_pages(self):
        self._detach_scroll()
        for frame in self._page_cache.values():
            frame.pack_forget()

    def _invalidate_pages(self, *keys: str):
        for key in keys:
            if key in self._page_cache:
                self._page_cache[key].destroy()
                del self._page_cache[key]
            if key == "bmi":
                self._bmi_built = False

    def _nav_to(self, key):
        if self._active_nav and self._active_nav in self._nav_btns:
            self._nav_btns[self._active_nav].set_active(False)
        self._active_nav = key
        self._nav_btns[key].set_active(True)

        builders = {
            "dashboard": self._page_dashboard,
            "bmi": self._page_bmi,
            "schedule": self._page_schedule,
            "builder": self._page_builder,
            "chatbot": self._page_chatbot,
            "profile": self._page_profile,
            "premium": self._page_premium,
        }

        self._hide_pages()
        if key not in self._page_cache:
            host = tk.Frame(self.content, bg=T.BG)
            builders[key](host)
            self._page_cache[key] = host
        self._page_cache[key].pack(fill="both", expand=True)

    # ═════════════════════════════════════════
    # PAGE: DASHBOARD
    # ═════════════════════════════════════════
    def _page_dashboard(self, parent):
        c = tk.Frame(parent, bg=T.BG, padx=40, pady=32)
        c.pack(fill="both", expand=True)

        hour = datetime.now().hour
        greet = "Good morning" if hour < 12 else ("Good afternoon" if hour < 17 else "Good evening")
        SectionHeader(c, f"{greet}, {self.user.username}! 💪",
                      "Ready to crush your goals today?").pack(anchor="w", pady=(0, 28))

        row = tk.Frame(c, bg=T.BG)
        row.pack(fill="x", pady=(0, 28))
        lc = self.user.experience_level
        lc_color = {
            ExperienceLevel.BEGINNER: T.LEVEL_BEGINNER,
            ExperienceLevel.INTERMEDIATE: T.LEVEL_INTERMEDIATE,
            ExperienceLevel.PROFESSIONAL: T.LEVEL_PRO,
        }[lc]
        stats = [
            ("🔥", "Current Streak", "0 days", T.RED),
            ("📊", "This Week", "0 workouts", T.CYAN),
            ("💪", "Level", lc.value, lc_color),
            ("⭐", "Status", "Premium" if self.user.is_premium else "Free",
             T.AMBER if self.user.is_premium else T.GRAY),
        ]
        for icon, label, val, clr in stats:
            StatCard(row, icon, label, val, clr).pack(side="left", padx=(0, 14))

        today = datetime.now().strftime("%A")
        preview = tk.Frame(c, bg=T.CARD, padx=28, pady=22)
        preview.pack(fill="x")
        tk.Label(preview, text=f"📅  Today — {today}", font=T.FONT_H3,
                 fg=T.CYAN, bg=T.CARD).pack(anchor="w")

        if self.schedule:
            wd = self.schedule.days.get(today)
            if wd:
                tk.Label(preview, text=f"{wd.name}  ·  {wd.focus}",
                         font=T.FONT_BODY, fg=T.WHITE, bg=T.CARD).pack(anchor="w", pady=(8, 4))
                tk.Label(preview, text=f"⏱  ~{wd.duration_minutes} min   ·   {len(wd.exercises)} exercises",
                         font=T.FONT_SM, fg=T.GRAY, bg=T.CARD).pack(anchor="w", pady=(0, 14))
                PRSButton(preview, "View Full Schedule →",
                          command=lambda: self._nav_to("schedule"),
                          style="cyan", width=200).pack(anchor="w")
            else:
                tk.Label(preview, text="🧘  Rest Day — recovery is progress too.",
                         font=T.FONT_BODY, fg=T.GREEN, bg=T.CARD).pack(anchor="w", pady=10)
        else:
            tk.Label(preview, text="No schedule yet — let's build one for you!",
                     font=T.FONT_BODY, fg=T.GRAY, bg=T.CARD).pack(anchor="w", pady=(10, 14))
            PRSButton(preview, "Build My Schedule",
                      command=lambda: self._nav_to("builder"),
                      style="cyan", width=180).pack(anchor="w")

        ql_row = tk.Frame(c, bg=T.BG)
        ql_row.pack(fill="x", pady=(24, 0))
        tk.Label(ql_row, text="Quick Access", font=T.FONT_H3,
                 fg=T.LIGHT, bg=T.BG).pack(anchor="w", pady=(0, 12))
        qlinks = tk.Frame(ql_row, bg=T.BG)
        qlinks.pack(fill="x")
        for txt, nav_key, sty in [
            ("⚖  BMI Check", "bmi", "cyan"),
            ("⚙  Edit Schedule", "builder", "ghost"),
            ("⭐  Go Premium", "premium", "amber"),
        ]:
            PRSButton(qlinks, txt, command=lambda k=nav_key: self._nav_to(k),
                      style=sty, width=164).pack(side="left", padx=(0, 12))

    # ═════════════════════════════════════════
    # PAGE: BMI CALCULATOR
    # ═════════════════════════════════════════
    def _page_bmi(self, parent):
        outer = tk.Frame(parent, bg=T.BG)
        outer.pack(fill="both", expand=True)

        left = tk.Frame(outer, bg=T.BG)
        right = tk.Frame(outer, bg=T.CARD, width=460)
        left.pack(side="left", fill="both", expand=True, padx=(36, 14), pady=30)
        right.pack(side="right", fill="both", expand=True, padx=(0, 30), pady=30)
        right.pack_propagate(False)

        SectionHeader(left, "BMI Calculator",
                      "Know your Body Mass Index instantly").pack(anchor="w", pady=(0, 24))

        self._w_card = SliderCard(left, "⚖  Weight", "kg", 30, 200, 72.5,
                                  on_change=self._bmi_sync)
        self._w_card.pack(fill="x", pady=(0, 14))
        self._h_card = SliderCard(left, "↕  Height", "cm", 100, 220, 178.0,
                                  on_change=self._bmi_sync)
        self._h_card.pack(fill="x", pady=(0, 28))

        extras = tk.Frame(left, bg=T.BG)
        extras.pack(fill="x", pady=(0, 24))
        for label, opts, default in [
            ("Gender", ["Male", "Female", "Other"], "Male"),
            ("Age Group", ["< 18", "18–34", "35–54", "55+"], "18–34"),
        ]:
            col = tk.Frame(extras, bg=T.BG)
            col.pack(side="left", padx=(0, 14), fill="x", expand=True)
            tk.Label(col, text=label, font=T.FONT_SM, fg=T.GRAY, bg=T.BG).pack(anchor="w")
            sv = tk.StringVar(master=parent, value=default)
            ttk.Combobox(col, textvariable=sv, values=opts, state="readonly",
                         font=T.FONT_BODY, width=12).pack(fill="x", pady=(4, 0))

        PRSButton(left, "Calculate BMI", command=self._bmi_calc,
                  style="cyan", width=200).pack(anchor="w", pady=(0, 10))
        PRSButton(left, "Reset Defaults", command=self._bmi_reset,
                  style="ghost", width=200).pack(anchor="w")

        self._bmi_gauge = tk.Canvas(right, width=340, height=200,
                                    bg=T.CARD, highlightthickness=0)
        self._bmi_gauge.pack(pady=(24, 0))

        self._bmi_num_lbl = tk.Label(right, text="22.9", font=T.FONT_NUM,
                                     fg=T.WHITE, bg=T.CARD)
        self._bmi_num_lbl.pack(pady=(0, 2))

        tk.Label(right, text="Body Mass Index",
                 font=("Segoe UI", 12), fg=T.GRAY, bg=T.CARD).pack()

        self._bmi_cat_lbl = tk.Label(right, text="Normal Weight",
                                     font=("Segoe UI", 20, "bold"),
                                     fg=T.CAT_COLORS["normal"], bg=T.CARD)
        self._bmi_cat_lbl.pack(pady=(10, 2))

        self._bmi_range_lbl = tk.Label(right, text="Healthy range: 18.5 – 24.9",
                                       font=("Segoe UI", 12), fg=T.GRAY, bg=T.CARD)
        self._bmi_range_lbl.pack()

        strip = tk.Frame(right, bg=T.CARD2)
        strip.pack(fill="x", padx=20, pady=18)

        ls = tk.Frame(strip, bg=T.CARD2)
        ls.pack(side="left", padx=22, pady=16)
        tk.Label(ls, text="BODY COMPOSITION", font=T.FONT_SM,
                 fg=T.GRAY, bg=T.CARD2).pack(anchor="w")
        self._bmi_comp_lbl = tk.Label(ls, text="Healthy", font=T.FONT_BOLD,
                                      fg=T.CAT_COLORS["normal"], bg=T.CARD2)
        self._bmi_comp_lbl.pack(anchor="w", pady=(2, 10))
        tk.Label(ls, text="HEALTH RISK", font=T.FONT_SM,
                 fg=T.GRAY, bg=T.CARD2).pack(anchor="w")
        self._bmi_risk_lbl = tk.Label(ls, text="Low", font=T.FONT_BOLD,
                                      fg=T.WHITE, bg=T.CARD2)
        self._bmi_risk_lbl.pack(anchor="w", pady=(2, 0))

        tk.Frame(strip, bg=T.BORDER, width=1).pack(side="left", fill="y", pady=10)

        self._bmi_chart = tk.Canvas(strip, width=160, height=95,
                                    bg=T.CARD2, highlightthickness=0)
        self._bmi_chart.pack(side="right", padx=18, pady=10)

        if not self._bmi_built:
            self._bmi_calc()
            self._bmi_built = True

    def _bmi_sync(self):
        pass  # labels update inside SliderCard

    def _bmi_calc(self):
        w = self._w_card.get()
        h = self._h_card.get() / 100
        bmi = w / (h * h)
        self.user.last_bmi = bmi
        self._bmi_num_lbl.configure(text=f"{bmi:.1f}")

        if bmi < 18.5:
            cat, key, comp, risk = "Underweight", "underweight", "Underweight", "High"
        elif bmi < 25:
            cat, key, comp, risk = "Normal Weight", "normal", "Healthy", "Low"
        elif bmi < 30:
            cat, key, comp, risk = "Overweight", "overweight", "Overweight", "Moderate"
        else:
            cat, key, comp, risk = "Obese", "obese", "Obese", "Very High"

        self.user.last_bmi_cat = cat

        ranges = {
            "underweight": "< 18.5",
            "normal": "18.5 – 24.9",
            "overweight": "25 – 29.9",
            "obese": "≥ 30",
        }

        self._bmi_cat_lbl.configure(text=cat, fg=T.CAT_COLORS[key])
        self._bmi_range_lbl.configure(text=f"Healthy range: {ranges[key]}")
        self._bmi_comp_lbl.configure(text=comp, fg=T.CAT_COLORS[key])
        self._bmi_risk_lbl.configure(text=risk)
        self._bmi_draw_gauge(bmi)
        self._bmi_draw_chart(key)

    def _bmi_reset(self):
        self._w_card.set(72.5)
        self._h_card.set(178.0)
        self._bmi_calc()

    def _bmi_draw_gauge(self, bmi):
        c = self._bmi_gauge
        c.delete("all")
        cx, cy, r, w = 170, 185, 120, 18
        c.create_arc(cx - r, cy - r, cx + r, cy + r, start=0, extent=180,
                     outline="#1E293B", width=w + 6, style="arc")
        for start, ext, key in [
            (180, 45, "underweight"), (135, 55, "normal"),
            (80, 40, "overweight"), (40, 40, "obese"),
        ]:
            c.create_arc(cx - r, cy - r, cx + r, cy + r, start=start, extent=-ext,
                         outline=T.CAT_COLORS[key], width=w, style="arc")

        def zone(mid, lines, key):
            rad = math.radians(mid)
            lx = cx + (r + 30) * math.cos(rad)
            ly = cy - (r + 30) * math.sin(rad)
            c.create_text(lx, ly, text=lines, fill=T.CAT_COLORS[key],
                          font=("Segoe UI", 8, "bold"), justify="center")

        zone(157, "Under\nweight", "underweight")
        zone(107, "Normal", "normal")
        zone(60, "Over\nweight", "overweight")
        zone(20, "Obese", "obese")

        clamped = max(15, min(40, bmi))
        angle = 180 - ((clamped - 15) / 25 * 180)
        rad = math.radians(angle)
        nx = cx + (r - 12) * math.cos(rad)
        ny = cy - (r - 12) * math.sin(rad)
        c.create_line(cx, cy, nx, ny, fill=T.BG, width=5, capstyle="round")
        c.create_line(cx, cy, nx, ny, fill=T.WHITE, width=3, capstyle="round")
        c.create_oval(cx - 8, cy - 8, cx + 8, cy + 8, fill=T.CARD, outline=T.WHITE, width=2)
        c.create_oval(cx - 3, cy - 3, cx + 3, cy + 3, fill=T.WHITE, outline="")

    def _bmi_draw_chart(self, category):
        c = self._bmi_chart
        c.delete("all")
        entries = [("Under", "underweight", 34), ("Normal", "normal", 54),
                   ("Over", "overweight", 42), ("Obese", "obese", 66)]
        bw, bot = 18, 72
        for i, (label, key, h) in enumerate(entries):
            x0 = 10 + i * 38
            y0 = bot - h
            active = key == category
            clr = T.CAT_COLORS[key] if active else T.CAT_DIM[key]
            if active:
                c.create_rectangle(x0 - 2, y0 - 4, x0 + bw + 2, bot + 1,
                                   fill="", outline=T.CAT_COLORS[key], width=1)
            c.create_rectangle(x0, y0, x0 + bw, bot, fill=clr, outline="")
            c.create_text(x0 + bw // 2, bot + 10, text=label,
                          fill=T.CAT_COLORS[key] if active else T.GRAY,
                          font=("Segoe UI", 7))

    # ═════════════════════════════════════════
    # PAGE: MY SCHEDULE
    # ═════════════════════════════════════════
    def _page_schedule(self, parent):
        if not self.schedule:
            self._no_schedule_msg(parent)
            return

        wrapper = tk.Frame(parent, bg=T.BG)
        wrapper.pack(fill="both", expand=True)

        hdr = tk.Frame(wrapper, bg=T.BG, padx=40, pady=24)
        hdr.pack(fill="x")
        SectionHeader(hdr, "My Weekly Schedule",
                      f"{self.schedule.schedule_type.value}  ·  "
                      f"{self.schedule.experience_level.value}").pack(anchor="w")

        canv = tk.Canvas(wrapper, bg=T.BG, highlightthickness=0)
        vsb = ttk.Scrollbar(wrapper, orient="vertical", command=canv.yview)
        sf = tk.Frame(canv, bg=T.BG)
        sf_id = canv.create_window((0, 0), window=sf, anchor="nw")

        def _on_frame_configure(_event=None):
            canv.configure(scrollregion=canv.bbox("all"))

        def _on_canvas_configure(event):
            canv.itemconfigure(sf_id, width=event.width)

        sf.bind("<Configure>", _on_frame_configure)
        canv.bind("<Configure>", _on_canvas_configure)
        canv.configure(yscrollcommand=vsb.set)
        canv.pack(side="left", fill="both", expand=True, padx=40)
        vsb.pack(side="right", fill="y")

        def _on_mousewheel(event):
            if event.delta:
                canv.yview_scroll(int(-event.delta / 120), "units")
            elif event.num == 4:
                canv.yview_scroll(-1, "units")
            elif event.num == 5:
                canv.yview_scroll(1, "units")

        # Bind only while this page is visible (fixes global bind_all leak).
        self._scroll_canvas = canv
        canv.bind("<Enter>", lambda _e: canv.bind_all("<MouseWheel>", _on_mousewheel))
        canv.bind("<Leave>", lambda _e: canv.unbind_all("<MouseWheel>"))
        canv.bind("<Enter>", lambda _e: canv.bind_all("<Button-4>", _on_mousewheel), add="+")
        canv.bind("<Enter>", lambda _e: canv.bind_all("<Button-5>", _on_mousewheel), add="+")
        canv.bind("<Leave>", lambda _e: (
            canv.unbind_all("<Button-4>"),
            canv.unbind_all("<Button-5>"),
        ), add="+")

        today = datetime.now().strftime("%A")
        is_premium = self.user.is_premium
        for day in WEEKDAYS:
            wd = self.schedule.days.get(day)
            is_today = day == today
            border_color = T.CYAN if is_today else T.BORDER

            card = tk.Frame(sf, bg=T.CARD,
                            highlightbackground=border_color,
                            highlightthickness=2 if is_today else 1)
            card.pack(fill="x", pady=6)

            dh = tk.Frame(card, bg=T.CARD, padx=22, pady=14)
            dh.pack(fill="x")
            tk.Label(dh, text=f"{'📍 ' if is_today else ''}{day}",
                     font=T.FONT_H3,
                     fg=T.CYAN if is_today else T.WHITE,
                     bg=T.CARD).pack(side="left")

            if wd:
                tk.Label(dh, text=f"⏱ ~{wd.duration_minutes} min",
                         font=T.FONT_SM, fg=T.GRAY, bg=T.CARD).pack(side="right")
                tk.Label(dh, text=wd.focus, font=T.FONT_BODY,
                         fg=T.LIGHT, bg=T.CARD).pack(side="left", padx=14)

                lines = []
                for ex in wd.exercises:
                    lines.append(self._exercise_line(ex, is_premium))
                body = tk.Label(
                    card, text="\n".join(lines), font=T.FONT_SM,
                    fg=T.LIGHT, bg=T.BG, justify="left", anchor="w",
                    padx=22, pady=10,
                )
                body.pack(fill="x")
            else:
                tk.Label(dh, text="🧘  Rest Day", font=T.FONT_BODY,
                         fg=T.GREEN, bg=T.CARD).pack(side="left", padx=14)

    def _exercise_line(self, ex: Exercise, is_premium: bool) -> str:
        locked = ex.is_premium and not is_premium
        star = "  ★ PRO" if ex.is_premium else ""
        if locked:
            detail = "🔒 Upgrade to unlock"
        else:
            detail = f"{ex.sets} sets × {ex.reps} reps  ·  {ex.rest_seconds}s rest"
        line = f"• {ex.name}{star}\n    {detail}"
        if ex.notes and not locked:
            line += f"\n    💡 {ex.notes}"
        return line

    def _no_schedule_msg(self, parent):
        c = tk.Frame(parent, bg=T.BG)
        c.pack(fill="both", expand=True)
        mid = tk.Frame(c, bg=T.BG)
        mid.place(relx=0.5, rely=0.5, anchor="center")
        tk.Label(mid, text="📅", font=("Segoe UI", 48), bg=T.BG).pack()
        tk.Label(mid, text="No Schedule Yet", font=T.FONT_H2,
                 fg=T.WHITE, bg=T.BG).pack(pady=(10, 4))
        tk.Label(mid, text="Create a personalized workout plan to get started.",
                 font=T.FONT_BODY, fg=T.GRAY, bg=T.BG).pack(pady=(0, 20))
        PRSButton(mid, "Create Schedule",
                  command=lambda: self._nav_to("builder"),
                  style="cyan", width=180).pack()

    # ═════════════════════════════════════════
    # PAGE: SCHEDULE BUILDER
    # ═════════════════════════════════════════
    def _page_builder(self, parent):
        c = tk.Frame(parent, bg=T.BG, padx=40, pady=32)
        c.pack(fill="both", expand=True)

        SectionHeader(c, "Build Your Schedule",
                      "Choose your level and training split").pack(anchor="w", pady=(0, 28))

        canv = tk.Canvas(c, bg=T.BG, highlightthickness=0)
        vsb = ttk.Scrollbar(c, orient="vertical", command=canv.yview)
        sf = tk.Frame(canv, bg=T.BG)
        sf_id = canv.create_window((0, 0), window=sf, anchor="nw")

        def _on_frame_configure(_event=None):
            canv.configure(scrollregion=canv.bbox("all"))

        def _on_canvas_configure(event):
            canv.itemconfigure(sf_id, width=event.width)

        sf.bind("<Configure>", _on_frame_configure)
        canv.bind("<Configure>", _on_canvas_configure)
        canv.configure(yscrollcommand=vsb.set)
        canv.pack(side="left", fill="both", expand=True)
        vsb.pack(side="right", fill="y")

        def _on_mousewheel(event):
            if event.delta:
                canv.yview_scroll(int(-event.delta / 120), "units")
            elif event.num == 4:
                canv.yview_scroll(-1, "units")
            elif event.num == 5:
                canv.yview_scroll(1, "units")

        self._scroll_canvas = canv
        canv.bind("<Enter>", lambda _e: canv.bind_all("<MouseWheel>", _on_mousewheel))
        canv.bind("<Leave>", lambda _e: canv.unbind_all("<MouseWheel>"))
        canv.bind("<Enter>", lambda _e: canv.bind_all("<Button-4>", _on_mousewheel), add="+")
        canv.bind("<Enter>", lambda _e: canv.bind_all("<Button-5>", _on_mousewheel), add="+")
        canv.bind("<Leave>", lambda _e: (
            canv.unbind_all("<Button-4>"),
            canv.unbind_all("<Button-5>"),
        ), add="+")

        form = tk.Frame(sf, bg=T.CARD, padx=30, pady=28)
        form.pack(fill="x")

        tk.Label(form, text="Experience Level", font=T.FONT_BOLD,
                 fg=T.WHITE, bg=T.CARD).pack(anchor="w")
        tk.Label(form, text="Tailors exercise selection and volume to you",
                 font=T.FONT_SM, fg=T.GRAY, bg=T.CARD).pack(anchor="w", pady=(2, 12))

        self._lvl_var = tk.StringVar(master=self, value=self.user.experience_level.value)
        lvl_row = tk.Frame(form, bg=T.CARD)
        lvl_row.pack(anchor="w", pady=(0, 24))
        for lvl, desc, clr in [
            (ExperienceLevel.BEGINNER, "< 1 year", T.LEVEL_BEGINNER),
            (ExperienceLevel.INTERMEDIATE, "1–3 years", T.LEVEL_INTERMEDIATE),
            (ExperienceLevel.PROFESSIONAL, "3+ years", T.LEVEL_PRO),
        ]:
            box = tk.Frame(lvl_row, bg=T.INPUT, padx=14, pady=10)
            box.pack(side="left", padx=(0, 10))
            tk.Radiobutton(box, text=lvl.value, variable=self._lvl_var, value=lvl.value,
                           font=T.FONT_BOLD, fg=clr, bg=T.INPUT,
                           selectcolor=T.CARD,
                           activebackground=T.INPUT).pack(anchor="w")
            tk.Label(box, text=desc, font=T.FONT_SM, fg=T.GRAY, bg=T.INPUT).pack(anchor="w")

        tk.Label(form, text="Training Split", font=T.FONT_BOLD,
                 fg=T.WHITE, bg=T.CARD).pack(anchor="w")
        tk.Label(form, text="Pick a split that matches your weekly availability",
                 font=T.FONT_SM, fg=T.GRAY, bg=T.CARD).pack(anchor="w", pady=(2, 12))

        self._split_var = tk.StringVar(master=self, value=ScheduleType.PPL_3DAY.value)
        grid = tk.Frame(form, bg=T.CARD)
        grid.pack(anchor="w", pady=(0, 28))
        premium_splits = {ScheduleType.ARNOLD_SPLIT, ScheduleType.BRO_SPLIT}
        for i, (stype, desc) in enumerate([
            (ScheduleType.PPL_3DAY, "3 days/week · Great for beginners"),
            (ScheduleType.FULL_BODY, "3 days/week · Efficient compound lifts"),
            (ScheduleType.UPPER_LOWER, "4 days/week · Balanced approach"),
            (ScheduleType.PPL_6DAY, "6 days/week · Max muscle stimulus"),
            (ScheduleType.BRO_SPLIT, "5 days/week · Classic bodybuilding ★"),
            (ScheduleType.ARNOLD_SPLIT, "6 days/week · High-volume supersets ★"),
        ]):
            r, col = i // 2, i % 2
            is_prem = stype in premium_splits
            box = tk.Frame(grid, bg=T.INPUT, padx=14, pady=10)
            box.grid(row=r, column=col, padx=(0, 10), pady=5, sticky="w")
            tk.Radiobutton(
                box,
                text=stype.value + (" ★" if is_prem else ""),
                variable=self._split_var, value=stype.value,
                font=T.FONT_BODY,
                fg=T.AMBER if is_prem else T.WHITE,
                bg=T.INPUT, selectcolor=T.CARD,
                activebackground=T.INPUT,
            ).pack(anchor="w")
            tk.Label(box, text=desc, font=T.FONT_SM,
                     fg=T.GRAY, bg=T.INPUT).pack(anchor="w")

        PRSButton(form, "Generate Schedule ✓",
                  command=self._do_generate,
                  style="cyan", width=210).pack(anchor="w")

    def _do_generate(self):
        lvl_str = self._lvl_var.get()
        spl_str = self._split_var.get()
        level = next(l for l in ExperienceLevel if l.value == lvl_str)
        stype = next(s for s in ScheduleType if s.value == spl_str)

        if stype in {ScheduleType.ARNOLD_SPLIT, ScheduleType.BRO_SPLIT} and not self.user.is_premium:
            messagebox.showinfo(
                "Premium Required",
                f"{stype.value} is a Premium feature.\nUpgrade to unlock all splits!",
            )
            return

        self.user.experience_level = level
        self.schedule = ScheduleGen.generate(stype, level)
        self.user.current_schedule = self.schedule

        self._invalidate_pages("dashboard", "schedule", "profile")
        messagebox.showinfo(
            "Schedule Created ✅",
            f"{stype.value}\n{level.value} level  ·  enjoy your program!",
        )
        self._nav_to("schedule")

    # ═════════════════════════════════════════
    # PAGE: AI COACH CHATBOT
    # ═════════════════════════════════════════
    def _page_chatbot(self, parent):
        c = tk.Frame(parent, bg=T.BG, padx=40, pady=32)
        c.pack(fill="both", expand=True)

        SectionHeader(c, "AI Coach", "Your adaptive professional fitness assistant").pack(anchor="w", pady=(0, 20))

        # Chat history area
        self._chat_history = tk.Text(
            c, bg=T.CARD, fg=T.WHITE, font=T.FONT_BODY,
            wrap="word", state="disabled", highlightthickness=0,
            padx=16, pady=16
        )
        self._chat_history.pack(fill="both", expand=True, pady=(0, 16))

        # Initial message
        self._add_chat_msg("AI Coach", "Hello! I am your adaptive AI fitness coach. I can help you with your routine, provide tips, and analyze your BMI. How can I help you today?")

        # Input area
        inp_frame = tk.Frame(c, bg=T.BG)
        inp_frame.pack(fill="x")

        self._chat_entry = tk.Entry(
            inp_frame, bg=T.INPUT, fg=T.WHITE, font=T.FONT_BODY,
            insertbackground=T.WHITE, highlightthickness=1, highlightbackground=T.BORDER,
            highlightcolor=T.CYAN, relief="flat"
        )
        self._chat_entry.pack(side="left", fill="x", expand=True, ipady=8, padx=(0, 12))
        self._chat_entry.bind("<Return>", lambda e: self._send_chat())

        PRSButton(
            inp_frame, "Send", command=self._send_chat,
            style="cyan", width=100, height=36
        ).pack(side="right")

    def _add_chat_msg(self, sender, msg):
        self._chat_history.config(state="normal")
        self._chat_history.insert("end", f"{sender}: ", "bold")
        self._chat_history.insert("end", f"{msg}\n\n")
        self._chat_history.tag_config("bold", font=("Segoe UI", 11, "bold"), foreground=T.CYAN if sender == "AI Coach" else T.AMBER)
        self._chat_history.config(state="disabled")
        self._chat_history.see("end")

    def _send_chat(self):
        msg = self._chat_entry.get().strip()
        if not msg:
            return
        self._chat_entry.delete(0, "end")
        self._add_chat_msg("You", msg)
        
        # Simulate thinking delay
        self.after(500, lambda: self._process_ai_response(msg.lower()))

    def _process_ai_response(self, msg):
        resp = "I'm here to help with your fitness journey! Try asking about your BMI, your current workout schedule, or general fitness tips."
        
        if "bmi" in msg or "weight" in msg or "fat" in msg:
            if self.user.last_bmi:
                resp = f"Your last calculated BMI was {self.user.last_bmi:.1f}, which falls into the '{self.user.last_bmi_cat}' category. "
                if self.user.last_bmi < 18.5:
                    resp += "To build mass, consider increasing your caloric intake slightly with protein-rich foods, and focus on heavy compound lifts in your routine."
                elif self.user.last_bmi < 25:
                    resp += "You are in a healthy range! Focus on progressive overload in your workouts to maintain and build lean muscle."
                else:
                    resp += "To support a healthy metabolism, try combining your current resistance training with some light cardio, and ensure you are in a slight caloric deficit."
            else:
                resp = "You haven't calculated your BMI yet. Head over to the BMI Calculator tab so I can give you personalized advice!"
                
        elif "routine" in msg or "schedule" in msg or "workout" in msg or "split" in msg:
            if self.user.current_schedule:
                sched = self.user.current_schedule
                resp = f"You are currently running the {sched.schedule_type.value} at a {sched.experience_level.value} level. "
                if sched.experience_level == ExperienceLevel.BEGINNER:
                    resp += "As a beginner, consistency is key! Focus on mastering form over lifting heavy weights. Make sure to take your rest days."
                elif sched.experience_level == ExperienceLevel.INTERMEDIATE:
                    resp += "Since you're an intermediate lifter, you should be focusing on progressive overload. Try adding a rep or a little bit of weight each week!"
                else:
                    resp += "As a pro, you know the drill. Ensure your recovery (sleep and nutrition) is dialed in to support the high volume of your split."
            else:
                resp = "You don't have a schedule set up yet. Go to the 'Build Schedule' tab to create one, and then I can help you optimize it!"

        elif "premium" in msg:
            resp = "Premium gives you access to advanced Arnold and Bro splits, detailed analytics, and custom routine building! Definitely worth it if you want to take your training to the next level."

        self._add_chat_msg("AI Coach", resp)

    # ═════════════════════════════════════════
    # PAGE: PROFILE
    # ═════════════════════════════════════════
    def _page_profile(self, parent):
        c = tk.Frame(parent, bg=T.BG, padx=40, pady=32)
        c.pack(fill="both", expand=True)

        SectionHeader(c, "Profile", "Your fitness account overview").pack(anchor="w", pady=(0, 28))

        card = tk.Frame(c, bg=T.CARD, padx=34, pady=30)
        card.pack(fill="x")

        tk.Label(card, text="💪", font=("Segoe UI", 48), bg=T.CARD).pack()
        tk.Label(card, text=self.user.username, font=T.FONT_H2,
                 fg=T.WHITE, bg=T.CARD).pack(pady=(8, 4))

        status_txt = "⭐  Premium Member" if self.user.is_premium else "Free Account"
        status_color = T.AMBER if self.user.is_premium else T.GRAY
        tk.Label(card, text=status_txt, font=T.FONT_BODY,
                 fg=status_color, bg=T.CARD).pack()

        row = tk.Frame(card, bg=T.CARD)
        row.pack(pady=20)
        for label, val in [
            ("Level", self.user.experience_level.value),
            ("Workouts", str(len(self.user.workout_history))),
            ("Schedule", self.schedule.schedule_type.value if self.schedule else "None"),
        ]:
            box = tk.Frame(row, bg=T.INPUT, padx=18, pady=10)
            box.pack(side="left", padx=6)
            tk.Label(box, text=val, font=T.FONT_BOLD, fg=T.WHITE, bg=T.INPUT).pack()
            tk.Label(box, text=label, font=T.FONT_SM, fg=T.GRAY, bg=T.INPUT).pack()

        PRSButton(
            card,
            "Deactivate Premium" if self.user.is_premium else "Activate Premium (Demo)",
            command=self._toggle_premium,
            style="ghost" if self.user.is_premium else "amber",
            width=220,
        ).pack(pady=(8, 0))

    def _toggle_premium(self):
        self.user.is_premium = not self.user.is_premium
        self._status_lbl.configure(
            text="Premium Account" if self.user.is_premium else "Free Account")
        self._invalidate_pages("dashboard", "profile", "premium", "schedule")
        messagebox.showinfo(
            "Status Updated",
            f"Account: {'Premium ⭐' if self.user.is_premium else 'Free'}",
        )
        self.after(0, lambda: self._nav_to("profile"))

    # ═════════════════════════════════════════
    # PAGE: PREMIUM
    # ═════════════════════════════════════════
    def _page_premium(self, parent):
        c = tk.Frame(parent, bg=T.BG, padx=40, pady=32)
        c.pack(fill="both", expand=True)

        if self.user.is_premium:
            SectionHeader(c, "⭐  You're Premium!", "All features are unlocked.").pack(anchor="w", pady=(0, 28))
        else:
            SectionHeader(c, "Upgrade to Premium",
                          "Unlock every feature and maximize your results").pack(anchor="w", pady=(0, 28))

        features = [
            ("📊", "Advanced Analytics", "Strength curves, volume trends & progress tracking"),
            ("🏗", "Custom Workout Builder", "Create & save unlimited routines"),
            ("🤖", "AI Coach Suggestions", "Personalized adjustments based on performance"),
            ("🥗", "Nutrition Integration", "Macro tracking synced to your training"),
            ("🎥", "HD Exercise Video Library", "Professional demos for 500+ movements"),
            ("🏋", "Arnold & Bro Splits", "Access to advanced 5–6 day programmes"),
        ]
        grid = tk.Frame(c, bg=T.BG)
        grid.pack(fill="both", expand=True)

        for i, (icon, name, desc) in enumerate(features):
            card = tk.Frame(grid, bg=T.CARD, padx=24, pady=20)
            card.grid(row=i // 2, column=i % 2, padx=(0, 12), pady=8, sticky="nsew")
            tk.Label(card, text=icon, font=("Segoe UI", 22), bg=T.CARD).pack(anchor="w")
            tk.Label(card, text=name, font=T.FONT_BOLD, fg=T.AMBER, bg=T.CARD).pack(anchor="w", pady=(6, 2))
            tk.Label(card, text=desc, font=T.FONT_SM, fg=T.LIGHT, bg=T.CARD,
                     wraplength=240, justify="left").pack(anchor="w")

        grid.columnconfigure(0, weight=1)
        grid.columnconfigure(1, weight=1)

        if not self.user.is_premium:
            PRSButton(c, "Get Premium — $14.99/month",
                      command=self._buy_premium,
                      style="amber", width=270, height=50).pack(pady=(20, 0))

    def _buy_premium(self):
        if messagebox.askyesno("Upgrade",
                               "This is a demo — activate premium features now?"):
            self.user.is_premium = True
            self._status_lbl.configure(text="Premium Account")
            self._invalidate_pages("dashboard", "profile", "premium", "schedule")
            messagebox.showinfo("Welcome! ⭐", "All premium features are now unlocked.")
            self.after(0, lambda: self._nav_to("premium"))


def _configure_ttk_styles(root: tk.Misc):
    root_style = ttk.Style(root)
    try:
        root_style.theme_use("clam")
        root_style.configure(
            "TCombobox",
            fieldbackground=T.INPUT,
            background=T.INPUT,
            foreground=T.WHITE,
            arrowcolor=T.WHITE,
        )
        root_style.configure(
            "Vertical.TScrollbar",
            background=T.CARD,
            troughcolor=T.BG,
            bordercolor=T.BG,
            arrowcolor=T.GRAY,
            darkcolor=T.CARD,
            lightcolor=T.CARD,
        )
    except tk.TclError:
        pass


if __name__ == "__main__":
    app = PRSFitness()
    _configure_ttk_styles(app)
    app.mainloop()
