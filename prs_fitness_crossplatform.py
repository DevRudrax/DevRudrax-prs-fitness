import flet as ft
ft.icons = ft.Icons
ft.padding = ft.Padding
ft.margin = ft.Margin
ft.border = ft.Border
ft.border_radius = ft.BorderRadius
ft.colors = ft.Colors
ft.animation = ft
ft.NavigationDestination = ft.NavigationBarDestination

class AlignmentProxy:
    def __getattr__(self, name):
        upper = name.upper()
        if hasattr(ft.Alignment, upper):
            return getattr(ft.Alignment, upper)
        raise AttributeError(f"alignment has no attribute '{name}'")
ft.alignment = AlignmentProxy()



from enum import Enum
from dataclasses import dataclass, field, asdict
from typing import Optional
import json
import os
import math
import time
from datetime import datetime

# ─────────────────────────────────────────────
# DATA MODELS
# ─────────────────────────────────────────────
class ExperienceLevel(str, Enum):
    BEGINNER = "Beginner"
    INTERMEDIATE = "Intermediate"
    PROFESSIONAL = "Professional"

class ScheduleType(str, Enum):
    PPL_3DAY = "Push-Pull-Legs (3 Day)"
    PPL_6DAY = "Push-Pull-Legs (6 Day)"
    UPPER_LOWER = "Upper / Lower Split"
    FULL_BODY = "Full Body (3 Day)"
    BRO_SPLIT = "Bro Split (5 Day)"
    ARNOLD_SPLIT = "Arnold Split (6 Day)"

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
            Exercise("Bench Press", 4, "8-10", 90, "Drive through chest"),
            Exercise("Overhead Press", 3, "8-12", 90, "Brace your core"),
            Exercise("Incline DB Press", 3, "10-12", 75, "Upper chest focus"),
            Exercise("Lateral Raises", 3, "12-15", 60, "Keep posture strict"),
            Exercise("Tricep Pushdowns", 3, "12-15", 60, "Squeeze triceps at bottom"),
        ]
        if level == ExperienceLevel.BEGINNER:
            return base[:4]
        if level == ExperienceLevel.INTERMEDIATE:
            base.append(Exercise("Dips", 3, "8-12", 75, "Lean forward for chest focus"))
            return base
        base += [
            Exercise("Dips", 4, "10-12", 60, "Weighted if possible"),
            Exercise("Cable Flyes", 3, "12-15", 60, "Constant tension at inner chest", is_premium=True),
            Exercise("OH Tricep Extension", 3, "10-12", 60, "Keep elbows tucked"),
        ]
        return base

    @staticmethod
    def pull(level):
        base = [
            Exercise("Deadlift", 4, "5-8", 120, "Keep neutral spine"),
            Exercise("Pull-ups / Lat PD", 4, "8-12", 90, "Pull with elbows"),
            Exercise("Barbell Rows", 4, "8-10", 90, "Pull to lower stomach"),
            Exercise("Face Pulls", 3, "15-20", 60, "Rear delt squeeze"),
            Exercise("Barbell Curls", 3, "10-12", 60, "Do not swing weight"),
        ]
        if level == ExperienceLevel.BEGINNER:
            base[0] = Exercise("Romanian Deadlift", 3, "10-12", 90, "Hinge at the hips")
            return base[:4]
        if level == ExperienceLevel.INTERMEDIATE:
            base.append(Exercise("Hammer Curls", 3, "10-12", 60, "Keep thumbs up"))
            return base
        base += [
            Exercise("Hammer Curls", 3, "10-12", 60, "Cross-body contraction"),
            Exercise("Seated Cable Rows", 3, "10-12", 75, "Controlled squeeze", is_premium=True),
            Exercise("Preacher Curls", 3, "10-12", 60, "Full range of motion"),
        ]
        return base

    @staticmethod
    def legs(level):
        base = [
            Exercise("Squats", 4, "6-10", 120, "Drive below parallel"),
            Exercise("Romanian Deadlift", 3, "10-12", 90, "Focus on hamstring stretch"),
            Exercise("Leg Press", 3, "10-15", 90, "Do not lock knees"),
            Exercise("Leg Curls", 3, "12-15", 60, "Squeeze hamstrings"),
            Exercise("Calf Raises", 4, "15-20", 45, "Hold stretch at bottom"),
        ]
        if level == ExperienceLevel.BEGINNER:
            base[0] = Exercise("Goblet Squats", 3, "12-15", 75, "Keep chest tall")
            return base[:4]
        if level == ExperienceLevel.INTERMEDIATE:
            base.append(Exercise("Walking Lunges", 3, "12 each", 75, "Control knee drop"))
            return base
        base += [
            Exercise("Bulgarian Split Squats", 3, "10 each", 75, "Deep quad stretch"),
            Exercise("Leg Extensions", 3, "12-15", 60, "Hold contraction at top", is_premium=True),
            Exercise("Hip Thrusts", 3, "10-12", 75, "Drive hips to ceiling"),
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
        s.days["Monday"]    = WorkoutDay("Chest Day", "Chest focus and hyper-trophy", [
            Exercise("Bench Press", 4, "8-10", 90), Exercise("Incline DB Press", 4, "10-12", 75),
            Exercise("Cable Flyes", 3, "12-15", 60), Exercise("Dips", 3, "10-12", 75)], 50)
        s.days["Tuesday"]   = WorkoutDay("Back Day", "Back thickness & density", [
            Exercise("Deadlift", 4, "5-8", 120), Exercise("Pull-ups", 4, "8-12", 90),
            Exercise("Barbell Rows", 4, "8-10", 90), Exercise("Seated Cable Rows", 3, "10-12", 75)], 55)
        s.days["Wednesday"] = WorkoutDay("Shoulders", "Delts focus & shaping", [
            Exercise("Overhead Press", 4, "8-10", 90), Exercise("Lateral Raises", 4, "12-15", 60),
            Exercise("Face Pulls", 3, "15-20", 60), Exercise("Rear Delt Flyes", 3, "12-15", 60)], 45)
        s.days["Thursday"]  = WorkoutDay("Legs Day", "Full leg build", WDB.legs(lvl), 60)
        s.days["Friday"]    = WorkoutDay("Arms Day", "Biceps & Triceps overload", [
            Exercise("Barbell Curls", 4, "10-12", 60), Exercise("CG Bench Press", 4, "8-10", 90),
            Exercise("Hammer Curls", 3, "10-12", 60), Exercise("Tricep Pushdowns", 3, "12-15", 60),
            Exercise("Preacher Curls", 3, "10-12", 60), Exercise("OH Tricep Extension", 3, "10-12", 60)], 50)

    @classmethod
    def _arnold(cls, s, lvl):
        cb = WorkoutDay("Chest & Back", "Push-Pull opposing supersets", [
            Exercise("Bench Press", 4, "8-10", 90), Exercise("Pull-ups", 4, "8-12", 90, "Superset with Bench"),
            Exercise("Incline DB Press", 3, "10-12", 75), Exercise("Barbell Rows", 3, "8-10", 90, "Superset with Incline"),
            Exercise("Cable Flyes", 3, "12-15", 60), Exercise("Seated Cable Rows", 3, "10-12", 75)], 65)
        sa = WorkoutDay("Shoulders & Arms", "Delts and arms pump", [
            Exercise("Overhead Press", 4, "8-10", 90), Exercise("Lateral Raises", 4, "12-15", 60),
            Exercise("Barbell Curls", 4, "10-12", 60), Exercise("Tricep Pushdowns", 4, "12-15", 60),
            Exercise("Hammer Curls", 3, "10-12", 60), Exercise("OH Tricep Extension", 3, "10-12", 60)], 60)
        lg = WorkoutDay("Legs Day", "Full leg development", WDB.legs(lvl), 60)
        for day, wd in zip(
            ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday"],
            [cb, sa, lg, _clone_day(cb), _clone_day(sa), _clone_day(lg)],
        ):
            s.days[day] = wd

# ─────────────────────────────────────────────
# UI COLOR CONSTANTS (PREMIUM Sleek Dark Theme)
# ─────────────────────────────────────────────
T_BG = "#080B10"
T_SIDEBAR = "#0D1117"
T_CARD = "#111827"
T_CARD2 = "#1A2233"
T_BORDER = "#1E293B"
T_INPUT = "#1E293B"

T_CYAN = "#00E5FF"
T_CYAN_DIM = "#0A2535"
T_GREEN = "#00FF88"
T_GREEN_DIM = "#0D2E1A"
T_AMBER = "#FFB800"
T_AMBER_DIM = "#2E1F06"
T_RED = "#FF4444"
T_RED_DIM = "#2E0D0B"
T_PURPLE = "#A855F7"

T_WHITE = "#F0F4FF"
T_GRAY = "#64748B"
T_LIGHT = "#94A3B8"

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

# ─────────────────────────────────────────────
# CUSTOM PREMIUM CONTAINER (Interactive scale & glow)
# ─────────────────────────────────────────────
class HoverContainer(ft.Container):
    def __init__(self, content, hover_scale=1.02, hover_border_color=T_CYAN, **kwargs):
        kwargs.setdefault("bgcolor", T_CARD)
        kwargs.setdefault("padding", 20)
        kwargs.setdefault("border_radius", 14)
        kwargs.setdefault("border", ft.border.all(1, T_BORDER))
        kwargs.setdefault("animate_scale", ft.animation.Animation(200, ft.AnimationCurve.EASE_OUT))
        kwargs.setdefault("animate", ft.animation.Animation(200, ft.AnimationCurve.EASE_OUT))
        
        super().__init__(content=content, **kwargs)
        self.hover_scale = hover_scale
        self.hover_border_color = hover_border_color
        self.normal_border_color = self.border.top.color if self.border else T_BORDER
        self.on_hover = self._handle_hover

    def _handle_hover(self, e):
        if e.data == "true":
            self.scale = self.hover_scale
            self.border = ft.border.all(1, self.hover_border_color)
            if self.bgcolor == T_CARD:
                self.bgcolor = T_CARD2
        else:
            self.scale = 1.0
            self.border = ft.border.all(1, self.normal_border_color)
            if self.bgcolor == T_CARD2:
                self.bgcolor = T_CARD
        self.update()

# ─────────────────────────────────────────────
# STATE MANAGEMENT (Cross-Platform client storage)
# ─────────────────────────────────────────────
class AppState:
    def __init__(self, page: ft.Page):
        self.page = page
        self.user = UserProfile()
        self.load_state()

    def load_state(self):
        try:
            # Shifted to client storage API to support iOS, Android, and Windows cleanly
            if self.page.client_storage.contains_key("prs_user_profile"):
                data = self.page.client_storage.get("prs_user_profile")
                if data:
                    parsed = json.loads(data)
                    self.user.username = parsed.get("username", "Athlete")
                    self.user.experience_level = ExperienceLevel(parsed.get("experience_level", ExperienceLevel.INTERMEDIATE))
                    self.user.is_premium = parsed.get("is_premium", False)
                    self.user.last_bmi = parsed.get("last_bmi")
                    self.user.last_bmi_cat = parsed.get("last_bmi_cat")
                    
                    sched_data = parsed.get("current_schedule")
                    if sched_data:
                        sched = WeeklySchedule(
                            schedule_type=ScheduleType(sched_data["schedule_type"]),
                            experience_level=ExperienceLevel(sched_data["experience_level"])
                        )
                        for day, wd_data in sched_data["days"].items():
                            if wd_data:
                                exs = [Exercise(**ex) for ex in wd_data["exercises"]]
                                sched.days[day] = WorkoutDay(wd_data["name"], wd_data["focus"], exs, wd_data["duration_minutes"])
                            else:
                                sched.days[day] = None
                        self.user.current_schedule = sched
            else:
                # Migrate legacy local file storage safely if it exists
                legacy_file = "user_data.json"
                if os.path.exists(legacy_file):
                    with open(legacy_file, "r") as f:
                        data = f.read()
                    if data:
                        parsed = json.loads(data)
                        self.user.username = parsed.get("username", "Athlete")
                        self.user.experience_level = ExperienceLevel(parsed.get("experience_level", ExperienceLevel.INTERMEDIATE))
                        self.user.is_premium = parsed.get("is_premium", False)
                        self.user.last_bmi = parsed.get("last_bmi")
                        self.user.last_bmi_cat = parsed.get("last_bmi_cat")
                        
                        sched_data = parsed.get("current_schedule")
                        if sched_data:
                            sched = WeeklySchedule(
                                schedule_type=ScheduleType(sched_data["schedule_type"]),
                                experience_level=ExperienceLevel(sched_data["experience_level"])
                            )
                            for day, wd_data in sched_data["days"].items():
                                if wd_data:
                                    exs = [Exercise(**ex) for ex in wd_data["exercises"]]
                                    sched.days[day] = WorkoutDay(wd_data["name"], wd_data["focus"], exs, wd_data["duration_minutes"])
                                else:
                                    sched.days[day] = None
                            self.user.current_schedule = sched
                        self.save_state()  # Migrate to native ClientStorage instantly
        except Exception as e:
            print(f"Failed to load user state: {e}")

    def save_state(self):
        try:
            data = json.dumps(asdict(self.user))
            self.page.client_storage.set("prs_user_profile", data)
        except Exception as e:
            print(f"Failed to save user state: {e}")

# ─────────────────────────────────────────────
# MAIN FLET APP
# ─────────────────────────────────────────────
def main(page: ft.Page):
    page.title = "PRS Fitness - Premium Studio"
    page.theme_mode = ft.ThemeMode.DARK
    page.bgcolor = T_BG
    page.padding = 0
    
    # Secure window parameters safely across platforms
    try:
        page.window.width = 1180
        page.window.height = 720
        page.window.min_width = 980
        page.window.min_height = 650
    except Exception:
        pass

    state = AppState(page)

    def show_snack_bar(sb):
        page.snack_bar = sb
        page.snack_bar.open = True
        try:
            page.update()
        except Exception:
            pass
    page.show_snack_bar = show_snack_bar

    # Global UI controls reference for sidebar/appbar status synch
    sidebar_status_text = ft.Text("Free Account", size=12, color=T_GRAY, weight=ft.FontWeight.BOLD)
    header_premium_badge = ft.Container(visible=False)

    def refresh_membership_badges():
        if state.user.is_premium:
            sidebar_status_text.value = "Premium Account ⭐"
            sidebar_status_text.color = T_AMBER
            header_premium_badge.visible = True
        else:
            sidebar_status_text.value = "Free Account"
            sidebar_status_text.color = T_GRAY
            header_premium_badge.visible = False
        try:
            page.update()
        except Exception:
            pass

    # Header premium indicator badge
    header_premium_badge = ft.Container(
        content=ft.Row([
            ft.Icon(ft.icons.STAR, color=T_BG, size=14),
            ft.Text("PRO", size=11, color=T_BG, weight=ft.FontWeight.BOLD)
        ], spacing=3, alignment=ft.MainAxisAlignment.CENTER),
        bgcolor=T_AMBER,
        padding=ft.padding.symmetric(horizontal=8, vertical=3),
        border_radius=5,
        visible=state.user.is_premium
    )

    # ───────────────── CUSTOM WIDGETS ─────────────────
    def PageHeader(title, subtitle=""):
        return ft.Container(
            margin=ft.margin.only(bottom=24),
            content=ft.Column([
                ft.Text(title, size=28, weight=ft.FontWeight.BOLD, color=T_WHITE),
                ft.Text(subtitle, size=14, color=T_GRAY) if subtitle else ft.Container()
            ], spacing=4)
        )

    def PremiumStatCard(icon, label, value, color, **kwargs):
        return HoverContainer(
            hover_border_color=color,
            expand=True,
            content=ft.Column([
                ft.Row([
                    ft.Container(
                        content=ft.Text(icon, size=20),
                        bgcolor=ft.colors.with_opacity(0.15, color),
                        padding=12,
                        border_radius=10
                    ),
                    ft.Column([
                        ft.Text(label, size=12, color=T_GRAY, weight=ft.FontWeight.BOLD),
                        ft.Text(value, size=18, color=T_WHITE, weight=ft.FontWeight.BOLD)
                    ], spacing=2, expand=True)
                ], spacing=12, vertical_alignment=ft.CrossAxisAlignment.CENTER)
            ]),
            **kwargs
        )

    # ───────────────── PAGES BUILDERS ─────────────────

    # --- 1. DASHBOARD ---
    def build_dashboard():
        hour = datetime.now().hour
        greeting = "Good morning" if hour < 12 else ("Good afternoon" if hour < 17 else "Good evening")
        
        today = datetime.now().strftime("%A")
        preview_controls = []
        
        if state.user.current_schedule:
            wd = state.user.current_schedule.days.get(today)
            if wd:
                # Workout Preview
                ex_previews = []
                for idx, ex in enumerate(wd.exercises[:3]):
                    locked = ex.is_premium and not state.user.is_premium
                    badge = " ★ PRO" if ex.is_premium else ""
                    detail = "🔒 Unlock with Premium" if locked else f"{ex.sets} sets × {ex.reps}"
                    ex_previews.append(
                        ft.Row([
                            ft.Icon(ft.icons.FITNESS_CENTER, color=T_CYAN if not locked else T_GRAY, size=14),
                            ft.Text(f"{ex.name}{badge}", color=T_WHITE if not locked else T_GRAY, size=14, weight=ft.FontWeight.BOLD),
                            ft.Text(f"•  {detail}", color=T_LIGHT if not locked else T_AMBER, size=13)
                        ], spacing=8)
                    )
                if len(wd.exercises) > 3:
                    ex_previews.append(ft.Text(f"... and {len(wd.exercises) - 3} more movements", color=T_GRAY, italic=True, size=13))
                
                preview_controls = [
                    ft.Row([
                        ft.Text(f"📍 Today's Session: {wd.name}", size=18, weight=ft.FontWeight.BOLD, color=T_CYAN),
                        ft.Container(
                            content=ft.Text(f"⏱ ~{wd.duration_minutes}m", size=12, color=T_CYAN, weight=ft.FontWeight.BOLD),
                            bgcolor=T_CYAN_DIM,
                            padding=ft.padding.symmetric(horizontal=8, vertical=3),
                            border_radius=5
                        )
                    ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
                    ft.Text(f"Focus Area: {wd.focus}", size=14, color=T_LIGHT),
                    ft.Divider(color=T_BORDER, height=15),
                    ft.Column(ex_previews, spacing=8),
                    ft.Container(height=10),
                    ft.ElevatedButton(
                        "Start Workout Session →",
                        bgcolor=T_CYAN,
                        color=ft.colors.BLACK,
                        style=ft.ButtonStyle(
                            shape=ft.RoundedRectangleBorder(radius=10),
                            padding=ft.padding.all(15)
                        ),
                        on_click=lambda _: navigate_to("/schedule")
                    )
                ]
            else:
                # Rest Day Preview
                preview_controls = [
                    ft.Row([
                        ft.Text("🧘 Rest & Recovery Day", size=18, weight=ft.FontWeight.BOLD, color=T_GREEN),
                        ft.Icon(ft.icons.SPA, color=T_GREEN, size=20)
                    ]),
                    ft.Text("Recovery is where muscle builds. Feed your body clean fuel, hydrate, and stretch today.", color=T_LIGHT, size=14),
                    ft.Divider(color=T_BORDER, height=15),
                    ft.Text("💡 Tip: Try 15 minutes of light stretching or a mobility flow to keep joints healthy.", color=T_GRAY, italic=True, size=13),
                    ft.Container(height=10),
                    ft.ElevatedButton(
                        "View Weekly Routine",
                        bgcolor=T_CARD2,
                        color=T_WHITE,
                        style=ft.ButtonStyle(
                            shape=ft.RoundedRectangleBorder(radius=10),
                            padding=ft.padding.all(15),
                            side=ft.border.BorderSide(1, T_BORDER)
                        ),
                        on_click=lambda _: navigate_to("/schedule")
                    )
                ]
        else:
            # No Schedule Setup Yet
            preview_controls = [
                ft.Row([
                    ft.Text("No Workout Plan Configured", size=18, weight=ft.FontWeight.BOLD, color=T_AMBER),
                    ft.Icon(ft.icons.WARNING, color=T_AMBER, size=20)
                ]),
                ft.Text("You don't have a schedule set up yet. Build a tailored routine matching your availability and level.", color=T_LIGHT, size=14),
                ft.Container(height=15),
                ft.ElevatedButton(
                    "Setup My Workout Routine ✓",
                    bgcolor=T_CYAN,
                    color=ft.colors.BLACK,
                    style=ft.ButtonStyle(
                        shape=ft.RoundedRectangleBorder(radius=10),
                        padding=ft.padding.all(15)
                    ),
                    on_click=lambda _: navigate_to("/builder")
                )
            ]

        # Sync Level theme colors
        lvl_color = {
            ExperienceLevel.BEGINNER: T_GREEN,
            ExperienceLevel.INTERMEDIATE: T_AMBER,
            ExperienceLevel.PROFESSIONAL: T_RED
        }[state.user.experience_level]

        return ft.Column([
            PageHeader(f"{greeting}, {state.user.username}! 💪", "Ready to crush your goals today?"),
            
            # Stat Cards row
            # Stat Cards row
            ft.ResponsiveRow([
                PremiumStatCard(ft.icons.LOCAL_FIRE_DEPARTMENT, "Current Streak", "0 days", T_RED, col={"xs": 12, "md": 3}),
                PremiumStatCard(ft.icons.LEADERBOARD, "Workouts Completed", f"{len(state.user.workout_history)} total", T_CYAN, col={"xs": 12, "md": 3}),
                PremiumStatCard(ft.icons.FITNESS_CENTER, "Experience Level", state.user.experience_level.value, lvl_color, col={"xs": 12, "md": 3}),
                PremiumStatCard(ft.icons.STAR, "Account Status", "Premium Member" if state.user.is_premium else "Free Tier", T_AMBER if state.user.is_premium else T_GRAY, col={"xs": 12, "md": 3}),
            ], spacing=16),
            
            ft.Container(height=24),
            
            # Today's preview card
            HoverContainer(
                hover_border_color=T_CYAN,
                content=ft.Column(preview_controls, spacing=10)
            ),
            
            ft.Container(height=24),
            
            # Quick access grid
            ft.Text("Quick Utilities", size=16, color=T_LIGHT, weight=ft.FontWeight.BOLD),
            ft.Container(height=8),
            ft.ResponsiveRow([
                HoverContainer(
                    hover_border_color=T_CYAN,
                    content=ft.Column([
                        ft.Icon(ft.icons.MONITOR_WEIGHT, color=T_CYAN, size=24),
                        ft.Text("BMI Calculator", weight=ft.FontWeight.BOLD, color=T_WHITE, size=15),
                        ft.Text("Check composition indices", color=T_GRAY, size=12)
                    ], spacing=6),
                    on_click=lambda _: navigate_to("/bmi"),
                    col={"xs": 12, "sm": 4}
                ),
                HoverContainer(
                    hover_border_color=T_GREEN,
                    content=ft.Column([
                        ft.Icon(ft.icons.BUILD, color=T_GREEN, size=24),
                        ft.Text("Builder Studio", weight=ft.FontWeight.BOLD, color=T_WHITE, size=15),
                        ft.Text("Modify active splits", color=T_GRAY, size=12)
                    ], spacing=6),
                    on_click=lambda _: navigate_to("/builder"),
                    col={"xs": 12, "sm": 4}
                ),
                HoverContainer(
                    hover_border_color=T_AMBER,
                    content=ft.Column([
                        ft.Icon(ft.icons.STAR, color=T_AMBER, size=24),
                        ft.Text("Go Premium", weight=ft.FontWeight.BOLD, color=T_WHITE, size=15),
                        ft.Text("Access Arnold/Bro splits", color=T_GRAY, size=12)
                    ], spacing=6),
                    on_click=lambda _: navigate_to("/premium"),
                    col={"xs": 12, "sm": 4}
                ),
            ], spacing=16)
        ], spacing=0)

    # --- 2. BMI CALCULATOR ---
    def build_bmi():
        # Text and results references
        bmi_readout = ft.Text("0.0", size=48, weight=ft.FontWeight.BOLD, color=T_WHITE)
        bmi_cat_label = ft.Text("Calculate BMI", size=20, weight=ft.FontWeight.BOLD, color=T_CYAN)
        bmi_risk_val = ft.Text("N/A", size=14, color=T_WHITE, weight=ft.FontWeight.BOLD)
        bmi_comp_val = ft.Text("N/A", size=14, color=T_WHITE, weight=ft.FontWeight.BOLD)
        bmi_range_desc = ft.Text("Healthy range: 18.5 – 24.9", size=12, color=T_GRAY)
        
        # Radial progress ring
        bmi_radial_ring = ft.ProgressRing(value=0.0, stroke_width=10, color=T_CYAN, bgcolor=T_INPUT, width=130, height=130)

        # Underweight, Normal, Overweight, Obese cards
        bmi_cards = {
            "underweight": ft.Container(content=ft.Text("Underweight\n< 18.5", size=11, color=T_GRAY, text_align=ft.TextAlign.CENTER), bgcolor=T_CARD2, padding=10, border_radius=8, expand=True, border=ft.border.all(1, T_BORDER)),
            "normal": ft.Container(content=ft.Text("Normal\n18.5 – 24.9", size=11, color=T_GRAY, text_align=ft.TextAlign.CENTER), bgcolor=T_CARD2, padding=10, border_radius=8, expand=True, border=ft.border.all(1, T_BORDER)),
            "overweight": ft.Container(content=ft.Text("Overweight\n25 – 29.9", size=11, color=T_GRAY, text_align=ft.TextAlign.CENTER), bgcolor=T_CARD2, padding=10, border_radius=8, expand=True, border=ft.border.all(1, T_BORDER)),
            "obese": ft.Container(content=ft.Text("Obese\n≥ 30", size=11, color=T_GRAY, text_align=ft.TextAlign.CENTER), bgcolor=T_CARD2, padding=10, border_radius=8, expand=True, border=ft.border.all(1, T_BORDER))
        }

        # Sync data to sliders
        weight_card = ft.Slider(min=30, max=200, value=72.5, divisions=170, active_color=T_CYAN, inactive_color=T_BORDER, on_change=lambda _: update_bmi_vals())
        height_card = ft.Slider(min=100, max=220, value=178.0, divisions=120, active_color=T_CYAN, inactive_color=T_BORDER, on_change=lambda _: update_bmi_vals())
        
        weight_txt_badge = ft.Text("72.5 kg", size=14, color=T_CYAN, weight=ft.FontWeight.BOLD)
        height_txt_badge = ft.Text("178.0 cm", size=14, color=T_CYAN, weight=ft.FontWeight.BOLD)

        def update_bmi_vals():
            w = weight_card.value
            h = height_card.value / 100
            
            weight_txt_badge.value = f"{w:.1f} kg"
            height_txt_badge.value = f"{height_card.value:.1f} cm"
            
            bmi = w / (h * h)
            state.user.last_bmi = bmi
            bmi_readout.value = f"{bmi:.1f}"

            # Visual updates
            if bmi < 18.5:
                cat, key, comp, risk, color = "Underweight", "underweight", "Underweight", "High", CAT_COLORS["underweight"]
            elif bmi < 25:
                cat, key, comp, risk, color = "Normal Weight", "normal", "Healthy", "Low", CAT_COLORS["normal"]
            elif bmi < 30:
                cat, key, comp, risk, color = "Overweight", "overweight", "Overweight", "Moderate", CAT_COLORS["overweight"]
            else:
                cat, key, comp, risk, color = "Obese", "obese", "Obese", "Very High", CAT_COLORS["obese"]

            state.user.last_bmi_cat = cat
            state.save_state()

            # Radial track styling
            ring_progress = max(0.0, min(1.0, (bmi - 15) / 25))
            bmi_radial_ring.value = ring_progress
            bmi_radial_ring.color = color

            bmi_cat_label.value = cat
            bmi_cat_label.color = color
            bmi_risk_val.value = risk
            bmi_risk_val.color = color
            bmi_comp_val.value = comp
            bmi_comp_val.color = color
            
            ranges = {
                "underweight": "< 18.5",
                "normal": "18.5 – 24.9",
                "overweight": "25 – 29.9",
                "obese": "≥ 30",
            }
            bmi_range_desc.value = f"Healthy range: {ranges[key]}"

            # Highlight category cards
            for k, box in bmi_cards.items():
                if k == key:
                    box.border = ft.border.all(1.5, color)
                    box.bgcolor = CAT_DIM[k]
                    box.content.color = color
                    box.content.weight = ft.FontWeight.BOLD
                else:
                    box.border = ft.border.all(1, T_BORDER)
                    box.bgcolor = T_CARD2
                    box.content.color = T_GRAY
                    box.content.weight = ft.FontWeight.NORMAL
            
            try:
                page.update()
            except Exception:
                pass

        # Load values from state if they exist
        if state.user.last_bmi:
            # Reverse-calculate height and weight from BMI or load defaults
            pass # Keep slider defaults, just update view instantly
        
        # Immediate sync on layout creation
        page.run_thread(lambda: time.sleep(0.05) or update_bmi_vals())

        return ft.Column([
            PageHeader("BMI Calculator", "Analyze body composition index instantly"),
            
            ft.ResponsiveRow([
                # Slider inputs (Left Panel)
                ft.Column([
                    # Weight card
                    HoverContainer(
                        hover_border_color=T_CYAN,
                        content=ft.Column([
                            ft.Row([
                                ft.Row([
                                    ft.Icon(ft.icons.SCALE, color=T_LIGHT, size=18),
                                    ft.Text("⚖  Body Weight", size=15, weight=ft.FontWeight.BOLD, color=T_WHITE)
                                ], spacing=6),
                                ft.Container(
                                    content=weight_txt_badge,
                                    bgcolor=T_CYAN_DIM,
                                    padding=ft.padding.symmetric(horizontal=10, vertical=4),
                                    border_radius=6
                                )
                            ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
                            weight_card,
                            ft.Row([
                                ft.Text("30 kg", size=11, color=T_GRAY),
                                ft.Text("200 kg", size=11, color=T_GRAY)
                            ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN)
                        ], spacing=6)
                    ),
                    ft.Container(height=6),
                    # Height card
                    HoverContainer(
                        hover_border_color=T_CYAN,
                        content=ft.Column([
                            ft.Row([
                                ft.Row([
                                    ft.Icon(ft.icons.HEIGHT, color=T_LIGHT, size=18),
                                    ft.Text("↕  Height", size=15, weight=ft.FontWeight.BOLD, color=T_WHITE)
                                ], spacing=6),
                                ft.Container(
                                    content=height_txt_badge,
                                    bgcolor=T_CYAN_DIM,
                                    padding=ft.padding.symmetric(horizontal=10, vertical=4),
                                    border_radius=6
                                )
                            ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
                            height_card,
                            ft.Row([
                                ft.Text("100 cm", size=11, color=T_GRAY),
                                ft.Text("220 cm", size=11, color=T_GRAY)
                            ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN)
                        ], spacing=6)
                    ),
                    ft.Container(height=10),
                    # Extra fields mock (Gender / Age)
                    HoverContainer(
                        hover_border_color=T_BORDER,
                        content=ft.Row([
                            ft.Column([
                                ft.Text("Biological Gender", size=11, color=T_GRAY),
                                ft.Dropdown(
                                    options=[ft.dropdown.Option("Male"), ft.dropdown.Option("Female"), ft.dropdown.Option("Other")],
                                    value="Male",
                                    border_color=T_BORDER,
                                    bgcolor=T_CARD2,
                                    height=44,
                                    content_padding=10
                                )
                            ], expand=True, spacing=4),
                            ft.Column([
                                ft.Text("Age Group", size=11, color=T_GRAY),
                                ft.Dropdown(
                                    options=[ft.dropdown.Option("< 18"), ft.dropdown.Option("18-34"), ft.dropdown.Option("35-54"), ft.dropdown.Option("55+")],
                                    value="18-34",
                                    border_color=T_BORDER,
                                    bgcolor=T_CARD2,
                                    height=44,
                                    content_padding=10
                                )
                            ], expand=True, spacing=4)
                        ], spacing=16)
                    )
                ], spacing=10, col={"xs": 12, "md": 7}),
                
                # Results panel (Right Panel)
                HoverContainer(
                    hover_border_color=T_CYAN,
                    col={"xs": 12, "md": 5},
                    content=ft.Column([
                        # Radial Indicator with centered text
                        ft.Container(
                            alignment=ft.alignment.center,
                            content=ft.Stack([
                                bmi_radial_ring,
                                ft.Container(
                                    content=ft.Column([
                                        bmi_readout,
                                        ft.Text("BMI INDEX", size=10, color=T_GRAY, weight=ft.FontWeight.BOLD)
                                    ], alignment=ft.MainAxisAlignment.CENTER, horizontal_alignment=ft.CrossAxisAlignment.CENTER),
                                    width=130,
                                    height=130
                                )
                            ])
                        ),
                        
                        # Classification Text
                        ft.Column([
                            bmi_cat_label,
                            bmi_range_desc
                        ], spacing=2, horizontal_alignment=ft.CrossAxisAlignment.CENTER),
                        
                        # Classification Grid
                        ft.Row([
                            bmi_cards["underweight"],
                            bmi_cards["normal"]
                        ], spacing=8),
                        ft.Row([
                            bmi_cards["overweight"],
                            bmi_cards["obese"]
                        ], spacing=8),
                        
                        # Stats detail rows
                        ft.Container(
                            bgcolor=T_CARD2,
                            border_radius=10,
                            padding=12,
                            content=ft.Row([
                                ft.Column([
                                    ft.Text("BODY COMP", size=10, color=T_GRAY, weight=ft.FontWeight.BOLD),
                                    bmi_comp_val
                                ], spacing=2, expand=True, horizontal_alignment=ft.CrossAxisAlignment.CENTER),
                                ft.VerticalDivider(color=T_BORDER, width=1),
                                ft.Column([
                                    ft.Text("HEALTH RISK", size=10, color=T_GRAY, weight=ft.FontWeight.BOLD),
                                    bmi_risk_val
                                ], spacing=2, expand=True, horizontal_alignment=ft.CrossAxisAlignment.CENTER)
                            ], alignment=ft.MainAxisAlignment.SPACE_EVENLY)
                        )
                    ], spacing=16, horizontal_alignment=ft.CrossAxisAlignment.CENTER)
                )
            ], spacing=16)
        ], spacing=0)

    # --- 3. SCHEDULE BUILDER ---
    def build_builder():
        # Selection States
        selected_level = ft.Text(state.user.experience_level.value, visible=False)
        selected_split = ft.Text(ScheduleType.PPL_3DAY.value, visible=False)

        # Experience level cards
        lvl_beginner_card = ft.Container(
            content=ft.Column([
                ft.Row([ft.Text("Beginner", size=15, weight=ft.FontWeight.BOLD, color=T_WHITE), ft.Icon(ft.icons.STAR_BORDER, color=T_GREEN, size=16)], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
                ft.Text("< 1 year training experience. Lower volume focus.", size=12, color=T_GRAY)
            ], spacing=4),
            bgcolor=T_CARD, padding=16, border_radius=10, border=ft.border.all(1, T_BORDER), col={"xs": 12, "md": 4}
        )
        lvl_inter_card = ft.Container(
            content=ft.Column([
                ft.Row([ft.Text("Intermediate", size=15, weight=ft.FontWeight.BOLD, color=T_WHITE), ft.Icon(ft.icons.STAR_HALF, color=T_AMBER, size=16)], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
                ft.Text("1–3 years training experience. Moderate volume compound splits.", size=12, color=T_GRAY)
            ], spacing=4),
            bgcolor=T_CARD, padding=16, border_radius=10, border=ft.border.all(1, T_BORDER), col={"xs": 12, "md": 4}
        )
        lvl_pro_card = ft.Container(
            content=ft.Column([
                ft.Row([ft.Text("Professional", size=15, weight=ft.FontWeight.BOLD, color=T_WHITE), ft.Icon(ft.icons.STAR, color=T_RED, size=16)], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
                ft.Text("3+ years experience. Intense progressive overload volume.", size=12, color=T_GRAY)
            ], spacing=4),
            bgcolor=T_CARD, padding=16, border_radius=10, border=ft.border.all(1, T_BORDER), col={"xs": 12, "md": 4}
        )

        def set_level(lvl):
            selected_level.value = lvl.value
            for card, l_enum, clr in [
                (lvl_beginner_card, ExperienceLevel.BEGINNER, T_GREEN),
                (lvl_inter_card, ExperienceLevel.INTERMEDIATE, T_AMBER),
                (lvl_pro_card, ExperienceLevel.PROFESSIONAL, T_RED)
            ]:
                if l_enum == lvl:
                    card.border = ft.border.all(1.5, clr)
                    card.bgcolor = T_CARD2
                else:
                    card.border = ft.border.all(1, T_BORDER)
                    card.bgcolor = T_CARD
            try:
                page.update()
            except Exception:
                pass

        lvl_beginner_card.on_click = lambda _: set_level(ExperienceLevel.BEGINNER)
        lvl_inter_card.on_click = lambda _: set_level(ExperienceLevel.INTERMEDIATE)
        lvl_pro_card.on_click = lambda _: set_level(ExperienceLevel.PROFESSIONAL)

        # Training Split Options
        split_items = [
            (ScheduleType.PPL_3DAY, "3 days/week · Balanced compound pushes & pulls.", False),
            (ScheduleType.FULL_BODY, "3 days/week · Compound lifts targeting whole body.", False),
            (ScheduleType.UPPER_LOWER, "4 days/week · Classic upper/lower separation.", False),
            (ScheduleType.PPL_6DAY, "6 days/week · Max stimulant workout frequency.", False),
            (ScheduleType.BRO_SPLIT, "5 days/week · Classic muscle specialization ★", True),
            (ScheduleType.ARNOLD_SPLIT, "6 days/week · Dual opposing supersets ★", True)
        ]

        split_cards = []
        
        def set_split(stype, is_prem):
            if is_prem and not state.user.is_premium:
                # Open purchase alert dialog
                page.show_dialog(
                    ft.AlertDialog(
                        title=ft.Row([ft.Text("Membership Upgrade Required", size=18, weight=ft.FontWeight.BOLD), ft.Icon(ft.icons.STAR, color=T_AMBER)]),
                        content=ft.Text(f"The advanced training split '{stype.value}' is unlocked with GymRat Premium.\n\nGo Premium to gain full access to classic Bro and Arnold splits, detailed nutrition synchronization, and customized coach advice!"),
                        actions=[
                            ft.TextButton("Cancel", on_click=lambda _: close_dlg()),
                            ft.ElevatedButton("Go Premium", bgcolor=T_AMBER, color=T_BG, on_click=lambda _: [close_dlg(), navigate_to("/premium")])
                        ]
                    )
                )
                return

            selected_split.value = stype.value
            for card, s_enum, _, _ in split_cards:
                if s_enum == stype:
                    card.border = ft.border.all(1.5, T_CYAN)
                    card.bgcolor = T_CARD2
                else:
                    card.border = ft.border.all(1, T_BORDER)
                    card.bgcolor = T_CARD
            try:
                page.update()
            except Exception:
                pass

        def close_dlg():
            page.pop_dialog()

        for stype, desc, is_prem in split_items:
            # Create Split Card
            card = ft.Container(
                bgcolor=T_CARD,
                padding=16,
                border_radius=10,
                border=ft.border.all(1, T_BORDER),
                col={"xs": 12, "md": 6}
            )
            
            badge_row = ft.Row([
                ft.Text(stype.value, size=14, weight=ft.FontWeight.BOLD, color=T_AMBER if is_prem else T_WHITE),
            ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN)
            
            if is_prem:
                badge_row.controls.append(
                    ft.Container(
                        content=ft.Text("PRO", size=9, color=T_BG, weight=ft.FontWeight.BOLD),
                        bgcolor=T_AMBER,
                        padding=ft.padding.symmetric(horizontal=6, vertical=2),
                        border_radius=4
                    )
                )
            
            card.content = ft.Column([
                badge_row,
                ft.Text(desc, size=11, color=T_GRAY)
            ], spacing=4)

            # Keep reference
            split_cards.append((card, stype, is_prem, card))
            
            # Setup clicks
            def make_click(s, p):
                return lambda _: set_split(s, p)
            card.on_click = make_click(stype, is_prem)

        def trigger_generation():
            lvl = next(l for l in ExperienceLevel if l.value == selected_level.value)
            stype = next(s for s in ScheduleType if s.value == selected_split.value)
            
            state.user.experience_level = lvl
            state.user.current_schedule = ScheduleGen.generate(stype, lvl)
            state.save_state()

            page.show_snack_bar(
                ft.SnackBar(
                    content=ft.Row([
                        ft.Icon(ft.icons.CHECK_CIRCLE, color=T_BG),
                        ft.Text(f"Workout Schedule Created: {stype.value}", color=T_BG, weight=ft.FontWeight.BOLD)
                    ], spacing=10),
                    bgcolor=T_GREEN,
                    duration=3000
                )
            )
            navigate_to("/schedule")

        # Initialise selections
        page.run_thread(lambda: time.sleep(0.02) or [set_level(state.user.experience_level), set_split(ScheduleType.PPL_3DAY, False)])

        return ft.Column([
            PageHeader("Workout Schedule Builder", "Tailor a custom lifting program to your availability"),
            
            ft.Text("1. Experience Level", size=16, color=T_LIGHT, weight=ft.FontWeight.BOLD),
            ft.Container(height=8),
            # Level selectors in responsive row
            ft.ResponsiveRow([
                lvl_beginner_card,
                lvl_inter_card,
                lvl_pro_card,
            ], spacing=12),
            
            ft.Container(height=24),
            
            ft.Text("2. Training Split", size=16, color=T_LIGHT, weight=ft.FontWeight.BOLD),
            ft.Container(height=8),
            # Split selectors in a responsive grid
            ft.ResponsiveRow([
                item[3] for item in split_cards
            ], spacing=12),
            
            ft.Container(height=28),
            
            # Generate CTA Button
            ft.ElevatedButton(
                "Generate Split Schedule ✓",
                bgcolor=T_CYAN,
                color=ft.colors.BLACK,
                style=ft.ButtonStyle(
                    shape=ft.RoundedRectangleBorder(radius=10),
                    padding=ft.padding.symmetric(horizontal=30, vertical=16),
                ),
                on_click=lambda _: trigger_generation()
            )
        ], spacing=0)

    # --- 4. SCHEDULE VIEW ---
    def build_schedule():
        if not state.user.current_schedule:
            # Empty state
            return ft.Column([
                PageHeader("My Workout Schedule", "Track your active exercise programs"),
                ft.Container(
                    bgcolor=T_CARD,
                    border_radius=14,
                    border=ft.border.all(1, T_BORDER),
                    padding=40,
                    alignment=ft.alignment.center,
                    content=ft.Column([
                        ft.Icon(ft.icons.CALENDAR_TODAY, size=48, color=T_GRAY),
                        ft.Container(height=8),
                        ft.Text("No Program Instantiated Yet", size=18, color=T_WHITE, weight=ft.FontWeight.BOLD),
                        ft.Text("Build a personalized program matching your lifting frequency.", size=13, color=T_GRAY, text_align=ft.TextAlign.CENTER),
                        ft.Container(height=16),
                        ft.ElevatedButton(
                            "Setup Workout Routine →",
                            bgcolor=T_CYAN,
                            color=ft.colors.BLACK,
                            style=ft.ButtonStyle(
                                shape=ft.RoundedRectangleBorder(radius=8),
                                padding=ft.padding.all(15)
                            ),
                            on_click=lambda _: navigate_to("/builder")
                        )
                    ], spacing=6, horizontal_alignment=ft.CrossAxisAlignment.CENTER)
                )
            ], spacing=0)

        # Active Schedule exists
        sched = state.user.current_schedule
        today_name = datetime.now().strftime("%A")
        
        day_cards = []
        for day in WEEKDAYS:
            wd = sched.days.get(day)
            is_today = day == today_name
            
            card_items = []
            
            if wd:
                # Header row
                card_items.append(
                    ft.Row([
                        ft.Row([
                            ft.Text(day, size=16, weight=ft.FontWeight.BOLD, color=T_CYAN if is_today else T_WHITE),
                            ft.Container(
                                content=ft.Text("TODAY" if is_today else f"{wd.duration_minutes}m", size=9, color=T_BG, weight=ft.FontWeight.BOLD),
                                bgcolor=T_CYAN if is_today else T_BORDER,
                                padding=ft.padding.symmetric(horizontal=6, vertical=2),
                                border_radius=4
                            )
                        ], spacing=8),
                        ft.Text(wd.name, size=15, weight=ft.FontWeight.BOLD, color=T_LIGHT)
                    ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN)
                )
                
                card_items.append(ft.Text(f"Focus: {wd.focus}", size=12, color=T_GRAY))
                card_items.append(ft.Divider(color=T_BORDER, height=12))
                
                # Exercises
                ex_cols = []
                for ex in wd.exercises:
                    locked = ex.is_premium and not state.user.is_premium
                    
                    ex_badge = ""
                    if ex.is_premium:
                        ex_badge = " ★ PRO"
                    
                    if locked:
                        ex_details = ft.Row([
                            ft.Icon(ft.icons.LOCK, size=12, color=T_AMBER),
                            ft.Text("Premium membership required to unlock instructions", size=11, color=T_AMBER, italic=True)
                        ], spacing=4)
                    else:
                        ex_details = ft.Text(f"{ex.sets} sets × {ex.reps} reps  ·  ⏱ {ex.rest_seconds}s rest", size=12, color=T_LIGHT)
                    
                    ex_col = ft.Column([
                        ft.Row([
                            ft.Icon(ft.icons.FITNESS_CENTER, size=13, color=T_CYAN if not locked else T_GRAY),
                            ft.Text(f"{ex.name}{ex_badge}", size=13, weight=ft.FontWeight.BOLD, color=T_WHITE if not locked else T_GRAY)
                        ], spacing=6),
                        ex_details
                    ], spacing=2)
                    
                    if ex.notes and not locked:
                        ex_col.controls.append(ft.Text(f"💡 {ex.notes}", size=11, color=T_GRAY, italic=True))
                    
                    ex_cols.append(ft.Container(content=ex_col, padding=ft.padding.only(left=8)))
                
                card_items.append(ft.Column(ex_cols, spacing=10))
            else:
                # Rest Day card
                card_items.append(
                    ft.Row([
                        ft.Row([
                            ft.Text(day, size=16, weight=ft.FontWeight.BOLD, color=T_GREEN if is_today else T_GRAY),
                            ft.Container(
                                content=ft.Text("TODAY" if is_today else "REST", size=9, color=T_BG, weight=ft.FontWeight.BOLD),
                                bgcolor=T_GREEN if is_today else T_BORDER,
                                padding=ft.padding.symmetric(horizontal=6, vertical=2),
                                border_radius=4
                            )
                        ], spacing=8),
                        ft.Text("Rest Day 🧘", size=13, color=T_GREEN, weight=ft.FontWeight.BOLD)
                    ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN)
                )

            # Build card container
            day_card = ft.Container(
                bgcolor=T_CARD2 if not wd else T_CARD,
                padding=16,
                border_radius=12,
                border=ft.border.all(1.5 if is_today else 1, T_CYAN if is_today else T_BORDER),
                content=ft.Column(card_items, spacing=8)
            )
            day_cards.append(day_card)

        return ft.Column([
            PageHeader("My Weekly Program", f"Active split: {sched.schedule_type.value}  ·  Level: {sched.experience_level.value}"),
            ft.Column(day_cards, spacing=12)
        ], spacing=0)

    # --- 5. AI COACH CHATBOT ---
    def build_chatbot():
        chat_list = ft.ListView(expand=True, spacing=10, auto_scroll=True)
        msg_input = ft.TextField(
            hint_text="Ask Coach anything about BMI, routines, or exercises...",
            expand=True,
            border_color=T_BORDER,
            focused_border_color=T_CYAN,
            bgcolor=T_CARD2,
            content_padding=12,
            text_size=14
        )

        def add_msg(sender, msg, is_user):
            bubble = ft.Container(
                content=ft.Column([
                    ft.Text(sender, size=10, color=T_GRAY if is_user else T_CYAN, weight=ft.FontWeight.BOLD),
                    ft.Text(msg, color=ft.colors.BLACK if is_user else T_WHITE, size=13)
                ], spacing=2),
                bgcolor=T_CYAN if is_user else T_CARD2,
                padding=12,
                border_radius=ft.border_radius.only(
                    top_left=14, top_right=14,
                    bottom_left=14 if is_user else 0,
                    bottom_right=0 if is_user else 14
                ),
                border=ft.border.all(1, T_BORDER) if not is_user else None
            )
            
            chat_list.controls.append(
                ft.Row(
                    [bubble], 
                    alignment=ft.MainAxisAlignment.END if is_user else ft.MainAxisAlignment.START
                )
            )
            try:
                page.update()
            except Exception:
                pass

        def send_msg(e=None):
            msg = msg_input.value.strip()
            if not msg:
                return
            add_msg("YOU", msg, True)
            msg_input.value = ""
            try:
                page.update()
            except Exception:
                pass

            # Simulate Coach Reply in a thread with delay
            def coach_reply():
                time.sleep(0.4)
                
                resp = "I'm your adaptive AI Coach! Ask me specific details about your current workout program or BMI composition index."
                m = msg.lower()
                
                if "bmi" in m or "weight" in m or "fat" in m:
                    if state.user.last_bmi:
                        resp = f"Your last calculated Body Mass Index was {state.user.last_bmi:.1f}, putting you in the '{state.user.last_bmi_cat}' category. "
                        if state.user.last_bmi < 18.5:
                            resp += "To build healthy skeletal mass, focus on increasing your daily clean protein intake, maintaining a small surplus, and tracking progressive overload."
                        elif state.user.last_bmi < 25:
                            resp += "You are in a healthy, optimal range! Focus on body recomposition by pushing close to failure on compound movements."
                        else:
                            resp += "To optimize cardiovascular indices and metabolic health, combine standard strength training with a slight caloric deficit and steady state cardio."
                    else:
                        resp = "I see you haven't calculated your BMI yet! Head over to the BMI Calculator tab to input metrics, and I'll analyze your ratios instantly."
                
                elif "routine" in m or "schedule" in m or "split" in m or "workout" in m:
                    if state.user.current_schedule:
                        s = state.user.current_schedule
                        resp = f"You are currently running the {s.schedule_type.value} program calibrated for a '{s.experience_level.value}' level of experience. "
                        if s.experience_level == ExperienceLevel.BEGINNER:
                            resp += "Focus strictly on mastering form before loading heavy weights. Prioritize rest days—that's when muscles recover and grow!"
                        elif s.experience_level == ExperienceLevel.INTERMEDIATE:
                            resp += "Ensure progressive overload by tracking volume. Try adding a single rep or small weight increments each week."
                        else:
                            resp += "Maximize intensity and recovery dynamics. Ensure sleep and clean nutrition align with the high volume of your split."
                    else:
                        resp = "You haven't initialized a workout program yet! Tap on the Build Schedule tab to build a customized, tier-calibrated training program."
                
                elif "premium" in m or "pro" in m:
                    resp = "GymRat Premium unlocks Arnold and Bro splits, eliminates locked exercises, and provides direct macro-nutrition synchronization. Upgrade in the Premium tab!"
                
                elif "hello" in m or "hi" in m:
                    resp = f"Hello, {state.user.username}! I am your AI Coach. Ask me about your routines, weight goals, or optimization recommendations."

                add_msg("COACH", resp, False)

            page.run_thread(coach_reply)

        # Inject initial coach text
        add_msg("COACH", "Hello! I am your adaptive AI fitness coach. How can I help optimize your current training splits or clarify BMI ratios today?", False)
        msg_input.on_submit = send_msg

        return ft.Container(
            bgcolor=T_CARD,
            border_radius=14,
            border=ft.border.all(1, T_BORDER),
            padding=16,
            expand=True,
            content=ft.Column([
                PageHeader("AI Coach Chatbot", "Adaptive fitness analysis & guidance"),
                ft.Container(
                    content=chat_list,
                    expand=True,
                    bgcolor=T_BG,
                    padding=16,
                    border_radius=10,
                    border=ft.border.all(1, T_BORDER)
                ),
                ft.Container(height=4),
                ft.Row([
                    msg_input,
                    ft.IconButton(
                        icon=ft.icons.SEND,
                        icon_color=T_BG,
                        bgcolor=T_CYAN,
                        icon_size=18,
                        width=46,
                        height=46,
                        on_click=send_msg
                    )
                ], spacing=10)
            ], expand=True)
        )

    # --- 6. PROFILE ---
    def build_profile():
        username_field = ft.TextField(
            label="Athlete Name",
            value=state.user.username,
            border_color=T_BORDER,
            focused_border_color=T_CYAN,
            bgcolor=T_CARD2,
            content_padding=12
        )
        
        level_dd = ft.Dropdown(
            label="Experience Level Calibration",
            options=[ft.dropdown.Option(l.value) for l in ExperienceLevel],
            value=state.user.experience_level.value,
            border_color=T_BORDER,
            bgcolor=T_CARD2,
            content_padding=12
        )

        def save_profile_changes():
            state.user.username = username_field.value.strip() or "Athlete"
            state.user.experience_level = next(l for l in ExperienceLevel if l.value == level_dd.value)
            state.save_state()
            page.show_snack_bar(
                ft.SnackBar(
                    content=ft.Text("Profile changes saved successfully ✓", color=T_BG, weight=ft.FontWeight.BOLD),
                    bgcolor=T_GREEN
                )
            )
            refresh_membership_badges()
            navigate_to("/")

        def trigger_premium_switch():
            state.user.is_premium = not state.user.is_premium
            state.save_state()
            refresh_membership_badges()
            
            status = "Premium Activated ⭐" if state.user.is_premium else "Downgraded to Free Tier"
            page.show_snack_bar(
                ft.SnackBar(
                    content=ft.Text(f"Demo Membership Switch: {status}", color=T_BG, weight=ft.FontWeight.BOLD),
                    bgcolor=T_AMBER if state.user.is_premium else T_GRAY
                )
            )
            navigate_to("/profile")

        active_split = state.user.current_schedule.schedule_type.value if state.user.current_schedule else "None"
        lvl_color = {
            ExperienceLevel.BEGINNER: T_GREEN,
            ExperienceLevel.INTERMEDIATE: T_AMBER,
            ExperienceLevel.PROFESSIONAL: T_RED
        }[state.user.experience_level]

        return ft.Column([
            PageHeader("User Settings", "Manage account details and active program tiers"),
            
            ft.ResponsiveRow([
                # Left Panel - Overview Card
                HoverContainer(
                    hover_border_color=T_CYAN,
                    col={"xs": 12, "md": 5},
                    content=ft.Column([
                        ft.Container(
                            content=ft.Text("💪", size=48),
                            alignment=ft.alignment.center,
                            bgcolor=T_CARD2,
                            width=100,
                            height=100,
                            border_radius=50,
                            border=ft.border.all(1.5, T_BORDER)
                        ),
                        ft.Text(state.user.username, size=20, weight=ft.FontWeight.BOLD, color=T_WHITE),
                        
                        ft.Container(
                            content=ft.Text("Premium Subscriber" if state.user.is_premium else "Free Member", size=11, color=T_BG if state.user.is_premium else T_WHITE, weight=ft.FontWeight.BOLD),
                            bgcolor=T_AMBER if state.user.is_premium else T_BORDER,
                            padding=ft.padding.symmetric(horizontal=10, vertical=4),
                            border_radius=5
                        ),
                        
                        ft.Divider(color=T_BORDER, height=20),
                        
                        ft.Row([
                            ft.Column([ft.Text("Program Level", size=10, color=T_GRAY, weight=ft.FontWeight.BOLD), ft.Text(state.user.experience_level.value, color=lvl_color, size=13, weight=ft.FontWeight.BOLD)], expand=True, horizontal_alignment=ft.CrossAxisAlignment.CENTER),
                            ft.VerticalDivider(color=T_BORDER, width=1),
                            ft.Column([ft.Text("Active Split", size=10, color=T_GRAY, weight=ft.FontWeight.BOLD), ft.Text(active_split, color=T_WHITE, size=13, weight=ft.FontWeight.BOLD)], expand=True, horizontal_alignment=ft.CrossAxisAlignment.CENTER),
                        ], alignment=ft.MainAxisAlignment.SPACE_EVENLY),
                        
                        ft.Divider(color=T_BORDER, height=20),
                        
                        ft.ElevatedButton(
                            "Toggle Demo Premium License (FREE)" if not state.user.is_premium else "Deactivate Demo Premium License",
                            bgcolor=T_AMBER if not state.user.is_premium else T_CARD2,
                            color=T_BG if not state.user.is_premium else T_WHITE,
                            style=ft.ButtonStyle(
                                shape=ft.RoundedRectangleBorder(radius=8),
                            ),
                            on_click=lambda _: trigger_premium_switch()
                        )
                    ], spacing=12, horizontal_alignment=ft.CrossAxisAlignment.CENTER)
                ),
                
                # Right Panel - Input Fields
                HoverContainer(
                    hover_border_color=T_BORDER,
                    col={"xs": 12, "md": 7},
                    content=ft.Column([
                        ft.Text("Edit Profile Details", size=16, weight=ft.FontWeight.BOLD, color=T_WHITE),
                        ft.Container(height=4),
                        username_field,
                        level_dd,
                        ft.Container(height=10),
                        ft.ElevatedButton(
                            "Save Changes ✓",
                            bgcolor=T_CYAN,
                            color=ft.colors.BLACK,
                            style=ft.ButtonStyle(shape=ft.RoundedRectangleBorder(radius=8)),
                            on_click=lambda _: save_profile_changes()
                        )
                    ], spacing=16)
                )
            ], spacing=16)
        ], spacing=0)

    # --- 7. PREMIUM ---
    def build_premium():
        features = [
            ("📊", "Advanced Analytics", "Detailed progress metrics, body composition indices, and history tracking."),
            ("🏗", "Custom Routine Builder", "Create, edit, and store unlimited specialized routine templates."),
            ("🤖", "AI Coach Suggestions", "Intelligent exercise modifications matched to active weight levels."),
            ("🥗", "Nutrition Integration", "Macro caloric and meal planning dynamically synchronized to lifting splits."),
            ("🎥", "HD Exercise Video Library", "Instant visual instructions for 500+ standard movements."),
            ("🏋", "Arnold & Bro Splits", "Unlock advanced 5–6 day specialization splits for ultimate stimulate volume.")
        ]

        feature_cards = []
        for icon, title, desc in features:
            card = HoverContainer(
                hover_border_color=T_AMBER,
                col={"xs": 12, "sm": 6},
                content=ft.Column([
                    ft.Row([
                        ft.Container(
                            content=ft.Text(icon, size=18),
                            bgcolor=T_AMBER_DIM,
                            padding=8,
                            border_radius=8
                        ),
                        ft.Text(title, size=14, weight=ft.FontWeight.BOLD, color=T_WHITE)
                    ], spacing=10),
                    ft.Text(desc, size=12, color=T_LIGHT)
                ], spacing=8)
            )
            feature_cards.append(card)

        def purchase_premium():
            state.user.is_premium = True
            state.save_state()
            refresh_membership_badges()
            
            page.show_dialog(
                ft.AlertDialog(
                    title=ft.Row([ft.Text("Welcome to Premium! ⭐", size=18, weight=ft.FontWeight.BOLD), ft.Icon(ft.icons.STAR, color=T_AMBER)]),
                    content=ft.Text("Congratulations! You've unlocked GymRat Premium.\n\nAll specialized splits (Arnold & Bro), advanced nutrition suggestions, and detailed instructional guides are now fully operational!"),
                    actions=[
                        ft.ElevatedButton("Awesome!", bgcolor=T_GREEN, color=T_BG, on_click=lambda _: [close_dlg(), navigate_to("/")])
                    ]
                )
            )

        def close_dlg():
            page.pop_dialog()

        cta_block = []
        if state.user.is_premium:
            cta_block.append(
                ft.Container(
                    bgcolor=T_AMBER_DIM,
                    border_radius=10,
                    border=ft.border.all(1, T_AMBER),
                    padding=16,
                    alignment=ft.alignment.center,
                    content=ft.Row([
                        ft.Icon(ft.icons.CHECK_CIRCLE, color=T_AMBER),
                        ft.Text("You are currently enjoying all premium features!", size=14, color=T_AMBER, weight=ft.FontWeight.BOLD)
                    ], spacing=10, alignment=ft.MainAxisAlignment.CENTER)
                )
            )
        else:
            cta_block.append(
                ft.ElevatedButton(
                    "Demo Upgrade — $14.99/month (DEMO FREE)",
                    bgcolor=T_AMBER,
                    color=T_BG,
                    style=ft.ButtonStyle(
                        shape=ft.RoundedRectangleBorder(radius=10),
                        padding=ft.padding.symmetric(horizontal=30, vertical=18),
                    ),
                    on_click=lambda _: purchase_premium()
                )
            )

        return ft.Column([
            PageHeader("GymRat Premium ⭐", "Maximize your hypertrophy splits with professional tools"),
            
            # Responsive 2x3 Grid
            ft.ResponsiveRow(feature_cards, spacing=12),
            
            ft.Container(height=24),
            
            ft.Column(cta_block, horizontal_alignment=ft.CrossAxisAlignment.CENTER)
        ], spacing=0)

    # ───────────────── LAYOUT SHELL & NAVIGATION ─────────────────
    
    # Active Page container Swap widget
    content_panel = ft.Container(expand=True, padding=24)
    scrollable_host = ft.Column(scroll=ft.ScrollMode.AUTO, expand=True, controls=[content_panel])

    # Mapping routes/keys to builders and indices
    pages_map = {
        "/": (build_dashboard, 0, "Dashboard"),
        "/bmi": (build_bmi, 1, "BMI Calculator"),
        "/schedule": (build_schedule, 2, "My Schedule"),
        "/builder": (build_builder, 3, "Build Schedule"),
        "/chatbot": (build_chatbot, 4, "AI Coach"),
        "/profile": (build_profile, 5, "Profile"),
        "/premium": (build_premium, 6, "Go Premium")
    }

    # Track current active route string
    active_route = "/"

    # Side Navigation Rail (Desktop)
    nav_rail = ft.NavigationRail(
        selected_index=0,
        label_type=ft.NavigationRailLabelType.ALL,
        min_width=90,
        min_extended_width=180,
        bgcolor=T_SIDEBAR,
        on_change=lambda e: handle_nav_change(e.control.selected_index),
        destinations=[
            ft.NavigationRailDestination(icon=ft.icons.DASHBOARD, label="Dashboard"),
            ft.NavigationRailDestination(icon=ft.icons.MONITOR_WEIGHT, label="BMI"),
            ft.NavigationRailDestination(icon=ft.icons.CALENDAR_MONTH, label="Schedule"),
            ft.NavigationRailDestination(icon=ft.icons.BUILD, label="Builder"),
            ft.NavigationRailDestination(icon=ft.icons.SMART_TOY, label="AI Coach"),
            ft.NavigationRailDestination(icon=ft.icons.PERSON, label="Profile"),
            ft.NavigationRailDestination(icon=ft.icons.STAR, label="Go Premium"),
        ]
    )

    # Bottom Navigation Bar (Mobile)
    bottom_nav = ft.NavigationBar(
        selected_index=0,
        bgcolor=T_SIDEBAR,
        on_change=lambda e: handle_nav_change(e.control.selected_index),
        destinations=[
            ft.NavigationBarDestination(icon=ft.icons.DASHBOARD, label="Dashboard"),
            ft.NavigationBarDestination(icon=ft.icons.MONITOR_WEIGHT, label="BMI"),
            ft.NavigationBarDestination(icon=ft.icons.CALENDAR_MONTH, label="Schedule"),
            ft.NavigationBarDestination(icon=ft.icons.BUILD, label="Builder"),
            ft.NavigationBarDestination(icon=ft.icons.SMART_TOY, label="AI Coach")
        ]
    )

    # Main App Layout Row
    main_layout_shell = ft.Row(expand=True, spacing=0)

    def navigate_to(route):
        nonlocal active_route
        active_route = route
        
        if route in pages_map:
            builder, idx, title = pages_map[route]
            content_panel.content = builder()
            
            # Synchronise navigation rail index
            nav_rail.selected_index = idx
            
            # Synchronise bottom navigation index if within mobile scope (0-4)
            if idx < 5:
                bottom_nav.selected_index = idx
            
            try:
                page.update()
            except Exception:
                pass

    def handle_nav_change(idx):
        # Maps index to route
        idx_map = {0: "/", 1: "/bmi", 2: "/schedule", 3: "/builder", 4: "/chatbot", 5: "/profile", 6: "/premium"}
        navigate_to(idx_map[idx])

    # Re-evaluate layout when resizing (Desktop view with sidebar, mobile with bottom bar)
    def handle_resize(e):
        is_mobile = page.width < 760
        
        main_layout_shell.controls.clear()
        
        if is_mobile:
            # Mobile layout
            main_layout_shell.controls.append(scrollable_host)
            page.navigation_bar = bottom_nav
        else:
            # Desktop layout
            main_layout_shell.controls.append(nav_rail)
            main_layout_shell.controls.append(ft.VerticalDivider(width=1, color=T_BORDER))
            main_layout_shell.controls.append(scrollable_host)
            page.navigation_bar = None
            
        try:
            page.update()
        except Exception:
            pass

    page.on_resize = handle_resize

    # Set up global scaffold views
    page.appbar = ft.AppBar(
        title=ft.Row([
            ft.Text("PRS", weight=ft.FontWeight.BOLD, color=T_CYAN, size=20),
            ft.Text("Fitness", weight=ft.FontWeight.BOLD, color=T_WHITE, size=20),
        ], spacing=2),
        bgcolor=T_SIDEBAR,
        elevation=2,
        actions=[
            ft.Container(
                content=ft.Row([
                    header_premium_badge,
                    ft.IconButton(ft.icons.PERSON, icon_color=T_CYAN, on_click=lambda _: navigate_to("/profile")),
                    ft.IconButton(ft.icons.STAR, icon_color=T_AMBER, on_click=lambda _: navigate_to("/premium"))
                ], spacing=10),
                margin=ft.margin.only(right=10)
            )
        ]
    )

    # Initialise layouts and startup page
    refresh_membership_badges()
    page.controls.append(main_layout_shell)
    
    # Run resize check initially to layout standard controls
    handle_resize(None)
    
    # Deep link on initial route
    navigate_to("/")

if __name__ == "__main__":
    ft.app(main)
