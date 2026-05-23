"""
GymRout - Premium Gym Schedule Application
A sophisticated workout scheduling app with tiered membership features
"""

import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime, timedelta
import json
from dataclasses import dataclass, field
from enum import Enum
from typing import Optional
import hashlib


# ═══════════════════════════════════════════════════════════════════════════
# CORE DATA MODELS
# ═══════════════════════════════════════════════════════════════════════════

class ExperienceLevel(Enum):
    BEGINNER = "Beginner"
    INTERMEDIATE = "Intermediate"
    PROFESSIONAL = "Professional"


class ScheduleType(Enum):
    PPL_3DAY = "Push-Pull-Legs (3 Day)"
    PPL_6DAY = "Push-Pull-Legs (6 Day)"
    UPPER_LOWER = "Upper/Lower Split"
    FULL_BODY = "Full Body"
    BRO_SPLIT = "Bro Split (5 Day)"
    ARNOLD_SPLIT = "Arnold Split"


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
    exercises: list[Exercise] = field(default_factory=list)
    duration_minutes: int = 60


@dataclass
class WeeklySchedule:
    schedule_type: ScheduleType
    experience_level: ExperienceLevel
    days: dict[str, Optional[WorkoutDay]] = field(default_factory=dict)


@dataclass
class UserProfile:
    username: str
    experience_level: ExperienceLevel
    is_premium: bool = False
    current_schedule: Optional[WeeklySchedule] = None
    workout_history: list = field(default_factory=list)


# ═══════════════════════════════════════════════════════════════════════════
# WORKOUT DATABASE
# ═══════════════════════════════════════════════════════════════════════════

class WorkoutDatabase:
    """Contains all workout templates for different levels and schedules."""
    
    @staticmethod
    def get_push_exercises(level: ExperienceLevel) -> list[Exercise]:
        base = [
            Exercise("Bench Press", 4, "8-10", 90, "Focus on chest contraction"),
            Exercise("Overhead Press", 3, "8-12", 90, "Keep core tight"),
            Exercise("Incline Dumbbell Press", 3, "10-12", 75),
            Exercise("Lateral Raises", 3, "12-15", 60),
            Exercise("Tricep Pushdowns", 3, "12-15", 60),
        ]
        
        if level == ExperienceLevel.BEGINNER:
            return base[:4]
        elif level == ExperienceLevel.INTERMEDIATE:
            base.append(Exercise("Dips", 3, "8-12", 75))
            return base
        else:
            base.extend([
                Exercise("Dips", 4, "10-12", 60),
                Exercise("Cable Flyes", 3, "12-15", 60, is_premium=True),
                Exercise("Overhead Tricep Extension", 3, "10-12", 60),
            ])
            return base

    @staticmethod
    def get_pull_exercises(level: ExperienceLevel) -> list[Exercise]:
        base = [
            Exercise("Deadlift", 4, "5-8", 120, "Maintain neutral spine"),
            Exercise("Pull-ups/Lat Pulldown", 4, "8-12", 90),
            Exercise("Barbell Rows", 4, "8-10", 90),
            Exercise("Face Pulls", 3, "15-20", 60, "Rear delt focus"),
            Exercise("Barbell Curls", 3, "10-12", 60),
        ]
        
        if level == ExperienceLevel.BEGINNER:
            base[0] = Exercise("Romanian Deadlift", 3, "10-12", 90)
            return base[:4]
        elif level == ExperienceLevel.INTERMEDIATE:
            base.append(Exercise("Hammer Curls", 3, "10-12", 60))
            return base
        else:
            base.extend([
                Exercise("Hammer Curls", 3, "10-12", 60),
                Exercise("Seated Cable Rows", 3, "10-12", 75, is_premium=True),
                Exercise("Preacher Curls", 3, "10-12", 60),
            ])
            return base

    @staticmethod
    def get_legs_exercises(level: ExperienceLevel) -> list[Exercise]:
        base = [
            Exercise("Squats", 4, "6-10", 120, "Depth below parallel"),
            Exercise("Romanian Deadlift", 3, "10-12", 90),
            Exercise("Leg Press", 3, "10-15", 90),
            Exercise("Leg Curls", 3, "12-15", 60),
            Exercise("Calf Raises", 4, "15-20", 45),
        ]
        
        if level == ExperienceLevel.BEGINNER:
            base[0] = Exercise("Goblet Squats", 3, "12-15", 75)
            return base[:4]
        elif level == ExperienceLevel.INTERMEDIATE:
            base.append(Exercise("Walking Lunges", 3, "12 each", 75))
            return base
        else:
            base.extend([
                Exercise("Bulgarian Split Squats", 3, "10 each", 75),
                Exercise("Leg Extensions", 3, "12-15", 60, is_premium=True),
                Exercise("Hip Thrusts", 3, "10-12", 75),
            ])
            return base

    @staticmethod
    def get_upper_exercises(level: ExperienceLevel) -> list[Exercise]:
        exercises = [
            Exercise("Bench Press", 4, "8-10", 90),
            Exercise("Barbell Rows", 4, "8-10", 90),
            Exercise("Overhead Press", 3, "8-12", 75),
            Exercise("Pull-ups/Lat Pulldown", 3, "8-12", 75),
            Exercise("Lateral Raises", 3, "12-15", 60),
            Exercise("Tricep Pushdowns", 3, "12-15", 60),
            Exercise("Barbell Curls", 3, "10-12", 60),
        ]
        
        if level == ExperienceLevel.BEGINNER:
            return exercises[:5]
        return exercises

    @staticmethod
    def get_lower_exercises(level: ExperienceLevel) -> list[Exercise]:
        exercises = [
            Exercise("Squats", 4, "6-10", 120),
            Exercise("Romanian Deadlift", 4, "8-10", 90),
            Exercise("Leg Press", 3, "10-15", 90),
            Exercise("Leg Curls", 3, "12-15", 60),
            Exercise("Walking Lunges", 3, "12 each", 75),
            Exercise("Calf Raises", 4, "15-20", 45),
        ]
        
        if level == ExperienceLevel.BEGINNER:
            return exercises[:4]
        return exercises

    @staticmethod
    def get_full_body_exercises(level: ExperienceLevel) -> list[Exercise]:
        exercises = [
            Exercise("Squats", 3, "8-10", 90),
            Exercise("Bench Press", 3, "8-10", 90),
            Exercise("Barbell Rows", 3, "8-10", 90),
            Exercise("Overhead Press", 3, "8-12", 75),
            Exercise("Romanian Deadlift", 3, "10-12", 90),
            Exercise("Pull-ups/Lat Pulldown", 3, "8-12", 75),
        ]
        
        if level == ExperienceLevel.BEGINNER:
            return exercises[:4]
        return exercises


# ═══════════════════════════════════════════════════════════════════════════
# SCHEDULE GENERATOR
# ═══════════════════════════════════════════════════════════════════════════

class ScheduleGenerator:
    """Generates weekly schedules based on user preferences."""
    
    WEEKDAYS = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
    
    @classmethod
    def generate_schedule(cls, schedule_type: ScheduleType, level: ExperienceLevel) -> WeeklySchedule:
        schedule = WeeklySchedule(
            schedule_type=schedule_type,
            experience_level=level,
            days={day: None for day in cls.WEEKDAYS}
        )
        
        generators = {
            ScheduleType.PPL_3DAY: cls._generate_ppl_3day,
            ScheduleType.PPL_6DAY: cls._generate_ppl_6day,
            ScheduleType.UPPER_LOWER: cls._generate_upper_lower,
            ScheduleType.FULL_BODY: cls._generate_full_body,
            ScheduleType.BRO_SPLIT: cls._generate_bro_split,
            ScheduleType.ARNOLD_SPLIT: cls._generate_arnold_split,
        }
        
        generators[schedule_type](schedule, level)
        return schedule

    @classmethod
    def _generate_ppl_3day(cls, schedule: WeeklySchedule, level: ExperienceLevel):
        schedule.days["Monday"] = WorkoutDay(
            "Push Day", "Chest, Shoulders, Triceps",
            WorkoutDatabase.get_push_exercises(level),
            duration_minutes=45 if level == ExperienceLevel.BEGINNER else 60
        )
        schedule.days["Wednesday"] = WorkoutDay(
            "Pull Day", "Back, Biceps",
            WorkoutDatabase.get_pull_exercises(level),
            duration_minutes=45 if level == ExperienceLevel.BEGINNER else 60
        )
        schedule.days["Friday"] = WorkoutDay(
            "Legs Day", "Quads, Hamstrings, Glutes, Calves",
            WorkoutDatabase.get_legs_exercises(level),
            duration_minutes=45 if level == ExperienceLevel.BEGINNER else 60
        )

    @classmethod
    def _generate_ppl_6day(cls, schedule: WeeklySchedule, level: ExperienceLevel):
        push = WorkoutDay("Push Day", "Chest, Shoulders, Triceps",
                         WorkoutDatabase.get_push_exercises(level), 60)
        pull = WorkoutDay("Pull Day", "Back, Biceps",
                         WorkoutDatabase.get_pull_exercises(level), 60)
        legs = WorkoutDay("Legs Day", "Quads, Hamstrings, Glutes, Calves",
                         WorkoutDatabase.get_legs_exercises(level), 60)
        
        schedule.days["Monday"] = push
        schedule.days["Tuesday"] = pull
        schedule.days["Wednesday"] = legs
        schedule.days["Thursday"] = WorkoutDay(push.name, push.focus, push.exercises.copy(), push.duration_minutes)
        schedule.days["Friday"] = WorkoutDay(pull.name, pull.focus, pull.exercises.copy(), pull.duration_minutes)
        schedule.days["Saturday"] = WorkoutDay(legs.name, legs.focus, legs.exercises.copy(), legs.duration_minutes)

    @classmethod
    def _generate_upper_lower(cls, schedule: WeeklySchedule, level: ExperienceLevel):
        upper = WorkoutDay("Upper Body", "Chest, Back, Shoulders, Arms",
                          WorkoutDatabase.get_upper_exercises(level), 60)
        lower = WorkoutDay("Lower Body", "Quads, Hamstrings, Glutes, Calves",
                          WorkoutDatabase.get_lower_exercises(level), 60)
        
        schedule.days["Monday"] = upper
        schedule.days["Tuesday"] = lower
        schedule.days["Thursday"] = WorkoutDay(upper.name, upper.focus, upper.exercises.copy(), upper.duration_minutes)
        schedule.days["Friday"] = WorkoutDay(lower.name, lower.focus, lower.exercises.copy(), lower.duration_minutes)

    @classmethod
    def _generate_full_body(cls, schedule: WeeklySchedule, level: ExperienceLevel):
        workout = WorkoutDay("Full Body", "All Major Muscle Groups",
                            WorkoutDatabase.get_full_body_exercises(level), 60)
        
        schedule.days["Monday"] = workout
        schedule.days["Wednesday"] = WorkoutDay(workout.name, workout.focus, workout.exercises.copy(), workout.duration_minutes)
        schedule.days["Friday"] = WorkoutDay(workout.name, workout.focus, workout.exercises.copy(), workout.duration_minutes)

    @classmethod
    def _generate_bro_split(cls, schedule: WeeklySchedule, level: ExperienceLevel):
        schedule.days["Monday"] = WorkoutDay("Chest Day", "Chest Focus", [
            Exercise("Bench Press", 4, "8-10", 90),
            Exercise("Incline Dumbbell Press", 4, "10-12", 75),
            Exercise("Cable Flyes", 3, "12-15", 60),
            Exercise("Dips", 3, "10-12", 75),
        ], 50)
        
        schedule.days["Tuesday"] = WorkoutDay("Back Day", "Back Focus", [
            Exercise("Deadlift", 4, "5-8", 120),
            Exercise("Pull-ups", 4, "8-12", 90),
            Exercise("Barbell Rows", 4, "8-10", 90),
            Exercise("Seated Cable Rows", 3, "10-12", 75),
        ], 55)
        
        schedule.days["Wednesday"] = WorkoutDay("Shoulders Day", "Shoulder Focus", [
            Exercise("Overhead Press", 4, "8-10", 90),
            Exercise("Lateral Raises", 4, "12-15", 60),
            Exercise("Face Pulls", 3, "15-20", 60),
            Exercise("Rear Delt Flyes", 3, "12-15", 60),
        ], 45)
        
        schedule.days["Thursday"] = WorkoutDay("Legs Day", "Leg Focus",
                                               WorkoutDatabase.get_legs_exercises(level), 60)
        
        schedule.days["Friday"] = WorkoutDay("Arms Day", "Biceps & Triceps", [
            Exercise("Barbell Curls", 4, "10-12", 60),
            Exercise("Close-Grip Bench Press", 4, "8-10", 90),
            Exercise("Hammer Curls", 3, "10-12", 60),
            Exercise("Tricep Pushdowns", 3, "12-15", 60),
            Exercise("Preacher Curls", 3, "10-12", 60),
            Exercise("Overhead Tricep Extension", 3, "10-12", 60),
        ], 50)

    @classmethod
    def _generate_arnold_split(cls, schedule: WeeklySchedule, level: ExperienceLevel):
        schedule.days["Monday"] = WorkoutDay("Chest & Back", "Push-Pull Superset", [
            Exercise("Bench Press", 4, "8-10", 90),
            Exercise("Pull-ups", 4, "8-12", 90, "Superset with Bench"),
            Exercise("Incline Dumbbell Press", 3, "10-12", 75),
            Exercise("Barbell Rows", 3, "8-10", 90, "Superset with Incline"),
            Exercise("Cable Flyes", 3, "12-15", 60),
            Exercise("Seated Cable Rows", 3, "10-12", 75),
        ], 65)
        
        schedule.days["Tuesday"] = WorkoutDay("Shoulders & Arms", "Delts & Arms", [
            Exercise("Overhead Press", 4, "8-10", 90),
            Exercise("Lateral Raises", 4, "12-15", 60),
            Exercise("Barbell Curls", 4, "10-12", 60),
            Exercise("Tricep Pushdowns", 4, "12-15", 60),
            Exercise("Hammer Curls", 3, "10-12", 60),
            Exercise("Overhead Tricep Extension", 3, "10-12", 60),
        ], 60)
        
        schedule.days["Wednesday"] = WorkoutDay("Legs Day", "Full Leg Development",
                                                WorkoutDatabase.get_legs_exercises(level), 60)
        
        schedule.days["Thursday"] = WorkoutDay(
            schedule.days["Monday"].name,
            schedule.days["Monday"].focus,
            schedule.days["Monday"].exercises.copy(),
            schedule.days["Monday"].duration_minutes
        )
        
        schedule.days["Friday"] = WorkoutDay(
            schedule.days["Tuesday"].name,
            schedule.days["Tuesday"].focus,
            schedule.days["Tuesday"].exercises.copy(),
            schedule.days["Tuesday"].duration_minutes
        )
        
        schedule.days["Saturday"] = WorkoutDay(
            schedule.days["Wednesday"].name,
            schedule.days["Wednesday"].focus,
            schedule.days["Wednesday"].exercises.copy(),
            schedule.days["Wednesday"].duration_minutes
        )


# ═══════════════════════════════════════════════════════════════════════════
# PREMIUM FEATURES
# ═══════════════════════════════════════════════════════════════════════════

class PremiumFeatures:
    """Premium features available for paid subscribers."""
    
    FEATURES = {
        "advanced_analytics": {
            "name": "Advanced Analytics",
            "description": "Detailed progress tracking, strength curves, and volume analytics",
            "price": "$4.99/month"
        },
        "custom_workouts": {
            "name": "Custom Workout Builder",
            "description": "Create and save unlimited custom workout routines",
            "price": "$4.99/month"
        },
        "ai_recommendations": {
            "name": "AI Coach Recommendations",
            "description": "Personalized workout suggestions based on your progress",
            "price": "$7.99/month"
        },
        "nutrition_tracking": {
            "name": "Nutrition Integration",
            "description": "Macro tracking and meal planning synced with workouts",
            "price": "$5.99/month"
        },
        "video_guides": {
            "name": "HD Video Exercise Library",
            "description": "Professional video demonstrations for 500+ exercises",
            "price": "$3.99/month"
        },
        "premium_bundle": {
            "name": "GymRout Premium",
            "description": "All features included + priority support",
            "price": "$14.99/month"
        }
    }
    
    @classmethod
    def get_feature_list(cls) -> list[dict]:
        return list(cls.FEATURES.values())


# ═══════════════════════════════════════════════════════════════════════════
# CUSTOM THEMED WIDGETS
# ═══════════════════════════════════════════════════════════════════════════

class GymRoutTheme:
    """Premium dark theme colors for gym environment."""
    
    # Primary colors
    BG_DARK = "#0D0D0D"
    BG_CARD = "#1A1A1A"
    BG_CARD_HOVER = "#252525"
    BG_INPUT = "#2A2A2A"
    
    # Accent colors
    ACCENT_PRIMARY = "#FF6B35"      # Energetic orange
    ACCENT_SECONDARY = "#00D4AA"    # Teal/mint
    ACCENT_GOLD = "#FFD700"         # Premium gold
    ACCENT_PURPLE = "#9B5DE5"       # Premium purple
    
    # Text colors
    TEXT_PRIMARY = "#FFFFFF"
    TEXT_SECONDARY = "#B0B0B0"
    TEXT_MUTED = "#666666"
    
    # Status colors
    SUCCESS = "#4ADE80"
    WARNING = "#FBBF24"
    ERROR = "#F87171"
    
    # Level colors
    LEVEL_BEGINNER = "#4ADE80"
    LEVEL_INTERMEDIATE = "#FBBF24"
    LEVEL_PRO = "#F87171"
    
    # Fonts
    FONT_HEADING = ("Segoe UI", 24, "bold")
    FONT_SUBHEADING = ("Segoe UI", 16, "bold")
    FONT_BODY = ("Segoe UI", 11)
    FONT_BODY_BOLD = ("Segoe UI", 11, "bold")
    FONT_SMALL = ("Segoe UI", 9)
    FONT_BUTTON = ("Segoe UI", 10, "bold")


class StyledButton(tk.Canvas):
    """Custom styled button with hover effects."""
    
    def __init__(self, parent, text, command=None, style="primary", width=150, height=40, **kwargs):
        super().__init__(parent, width=width, height=height, 
                        bg=GymRoutTheme.BG_DARK, highlightthickness=0, **kwargs)
        
        self.text = text
        self.command = command
        self.width = width
        self.height = height
        
        colors = {
            "primary": (GymRoutTheme.ACCENT_PRIMARY, "#FF8555"),
            "secondary": (GymRoutTheme.BG_CARD, GymRoutTheme.BG_CARD_HOVER),
            "gold": (GymRoutTheme.ACCENT_GOLD, "#FFE44D"),
            "success": (GymRoutTheme.SUCCESS, "#6AEE9A"),
        }
        
        self.bg_color, self.hover_color = colors.get(style, colors["primary"])
        self.current_color = self.bg_color
        
        self._draw_button()
        
        self.bind("<Enter>", self._on_enter)
        self.bind("<Leave>", self._on_leave)
        self.bind("<Button-1>", self._on_click)
    
    def _draw_button(self):
        self.delete("all")
        
        # Rounded rectangle
        r = 8
        self.create_polygon(
            r, 0, self.width - r, 0,
            self.width, r, self.width, self.height - r,
            self.width - r, self.height, r, self.height,
            0, self.height - r, 0, r,
            fill=self.current_color, smooth=True
        )
        
        # Text
        text_color = "#000000" if self.current_color in [GymRoutTheme.ACCENT_GOLD] else "#FFFFFF"
        self.create_text(
            self.width // 2, self.height // 2,
            text=self.text, fill=text_color,
            font=GymRoutTheme.FONT_BUTTON
        )
    
    def _on_enter(self, event):
        self.current_color = self.hover_color
        self._draw_button()
        self.config(cursor="hand2")
    
    def _on_leave(self, event):
        self.current_color = self.bg_color
        self._draw_button()
    
    def _on_click(self, event):
        if self.command:
            self.command()


class ExerciseCard(tk.Frame):
    """Styled card for displaying exercise information."""
    
    def __init__(self, parent, exercise: Exercise, is_premium_user: bool = False, **kwargs):
        super().__init__(parent, bg=GymRoutTheme.BG_CARD, **kwargs)
        
        self.exercise = exercise
        self.is_locked = exercise.is_premium and not is_premium_user
        
        self._create_widgets()
    
    def _create_widgets(self):
        # Main container with padding
        container = tk.Frame(self, bg=GymRoutTheme.BG_CARD, padx=15, pady=12)
        container.pack(fill="x")
        
        # Exercise name row
        name_frame = tk.Frame(container, bg=GymRoutTheme.BG_CARD)
        name_frame.pack(fill="x")
        
        name_label = tk.Label(
            name_frame, text=self.exercise.name,
            font=GymRoutTheme.FONT_BODY_BOLD,
            fg=GymRoutTheme.TEXT_MUTED if self.is_locked else GymRoutTheme.TEXT_PRIMARY,
            bg=GymRoutTheme.BG_CARD
        )
        name_label.pack(side="left")
        
        if self.exercise.is_premium:
            premium_badge = tk.Label(
                name_frame, text="★ PRO",
                font=GymRoutTheme.FONT_SMALL,
                fg=GymRoutTheme.ACCENT_GOLD,
                bg=GymRoutTheme.BG_CARD
            )
            premium_badge.pack(side="left", padx=(10, 0))
        
        # Stats row
        stats_frame = tk.Frame(container, bg=GymRoutTheme.BG_CARD)
        stats_frame.pack(fill="x", pady=(5, 0))
        
        display_text = "🔒 Upgrade to unlock" if self.is_locked else f"{self.exercise.sets} sets × {self.exercise.reps} reps  •  {self.exercise.rest_seconds}s rest"
        
        stats_label = tk.Label(
            stats_frame, text=display_text,
            font=GymRoutTheme.FONT_SMALL,
            fg=GymRoutTheme.ACCENT_GOLD if self.is_locked else GymRoutTheme.TEXT_SECONDARY,
            bg=GymRoutTheme.BG_CARD
        )
        stats_label.pack(side="left")
        
        # Notes (if available and not locked)
        if self.exercise.notes and not self.is_locked:
            notes_label = tk.Label(
                container, text=f"💡 {self.exercise.notes}",
                font=GymRoutTheme.FONT_SMALL,
                fg=GymRoutTheme.ACCENT_SECONDARY,
                bg=GymRoutTheme.BG_CARD
            )
            notes_label.pack(anchor="w", pady=(5, 0))


# ═══════════════════════════════════════════════════════════════════════════
# MAIN APPLICATION
# ═══════════════════════════════════════════════════════════════════════════

class GymRoutApp:
    """Main application class for GymRout."""
    
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("GymRout - Premium Workout Scheduler")
        self.root.geometry("1100x750")
        self.root.configure(bg=GymRoutTheme.BG_DARK)
        self.root.minsize(900, 600)
        
        # Application state
        self.user = UserProfile(
            username="Athlete",
            experience_level=ExperienceLevel.INTERMEDIATE,
            is_premium=False
        )
        self.current_schedule: Optional[WeeklySchedule] = None
        
        # Configure styles
        self._configure_styles()
        
        # Build UI
        self._create_main_layout()
        self._show_welcome_screen()
    
    def _configure_styles(self):
        style = ttk.Style()
        style.theme_use("clam")
        
        style.configure("Dark.TFrame", background=GymRoutTheme.BG_DARK)
        style.configure("Card.TFrame", background=GymRoutTheme.BG_CARD)
        
        style.configure(
            "Dark.TLabel",
            background=GymRoutTheme.BG_DARK,
            foreground=GymRoutTheme.TEXT_PRIMARY,
            font=GymRoutTheme.FONT_BODY
        )
        
        style.configure(
            "Heading.TLabel",
            background=GymRoutTheme.BG_DARK,
            foreground=GymRoutTheme.TEXT_PRIMARY,
            font=GymRoutTheme.FONT_HEADING
        )
        
        style.configure(
            "TCombobox",
            fieldbackground=GymRoutTheme.BG_INPUT,
            background=GymRoutTheme.BG_INPUT,
            foreground=GymRoutTheme.TEXT_PRIMARY,
            arrowcolor=GymRoutTheme.TEXT_PRIMARY
        )
        
        style.configure(
            "Dark.TRadiobutton",
            background=GymRoutTheme.BG_DARK,
            foreground=GymRoutTheme.TEXT_PRIMARY,
            font=GymRoutTheme.FONT_BODY
        )
    
    def _create_main_layout(self):
        # Sidebar
        self.sidebar = tk.Frame(self.root, bg="#111111", width=220)
        self.sidebar.pack(side="left", fill="y")
        self.sidebar.pack_propagate(False)
        
        # Logo area
        logo_frame = tk.Frame(self.sidebar, bg="#111111", pady=25)
        logo_frame.pack(fill="x")
        
        logo_label = tk.Label(
            logo_frame, text="💪 GymRout",
            font=("Segoe UI", 20, "bold"),
            fg=GymRoutTheme.ACCENT_PRIMARY,
            bg="#111111"
        )
        logo_label.pack()
        
        tagline = tk.Label(
            logo_frame, text="Your Personal Trainer",
            font=GymRoutTheme.FONT_SMALL,
            fg=GymRoutTheme.TEXT_MUTED,
            bg="#111111"
        )
        tagline.pack()
        
        # Navigation
        nav_items = [
            ("🏠  Dashboard", self._show_welcome_screen),
            ("📅  My Schedule", self._show_schedule_view),
            ("⚙️  Create Schedule", self._show_schedule_builder),
            ("👤  Profile", self._show_profile),
            ("⭐  Go Premium", self._show_premium_upgrade),
        ]
        
        nav_frame = tk.Frame(self.sidebar, bg="#111111")
        nav_frame.pack(fill="x", pady=20)
        
        for text, command in nav_items:
            btn = tk.Label(
                nav_frame, text=text,
                font=GymRoutTheme.FONT_BODY,
                fg=GymRoutTheme.TEXT_SECONDARY,
                bg="#111111",
                pady=12, padx=20,
                anchor="w"
            )
            btn.pack(fill="x")
            btn.bind("<Enter>", lambda e, b=btn: b.configure(
                bg=GymRoutTheme.BG_CARD, fg=GymRoutTheme.TEXT_PRIMARY
            ))
            btn.bind("<Leave>", lambda e, b=btn: b.configure(
                bg="#111111", fg=GymRoutTheme.TEXT_SECONDARY
            ))
            btn.bind("<Button-1>", lambda e, c=command: c())
        
        # User status at bottom
        status_frame = tk.Frame(self.sidebar, bg="#111111")
        status_frame.pack(side="bottom", fill="x", pady=20, padx=15)
        
        self.user_status_label = tk.Label(
            status_frame,
            text=f"Free Account",
            font=GymRoutTheme.FONT_SMALL,
            fg=GymRoutTheme.TEXT_MUTED,
            bg="#111111"
        )
        self.user_status_label.pack()
        
        # Main content area
        self.content = tk.Frame(self.root, bg=GymRoutTheme.BG_DARK)
        self.content.pack(side="right", fill="both", expand=True)
    
    def _clear_content(self):
        for widget in self.content.winfo_children():
            widget.destroy()
    
    def _show_welcome_screen(self):
        self._clear_content()
        
        # Welcome container
        container = tk.Frame(self.content, bg=GymRoutTheme.BG_DARK, padx=40, pady=30)
        container.pack(fill="both", expand=True)
        
        # Header
        greeting = self._get_greeting()
        header = tk.Label(
            container, text=f"{greeting}, {self.user.username}!",
            font=GymRoutTheme.FONT_HEADING,
            fg=GymRoutTheme.TEXT_PRIMARY,
            bg=GymRoutTheme.BG_DARK
        )
        header.pack(anchor="w")
        
        subtitle = tk.Label(
            container, text="Ready to crush your workout today?",
            font=GymRoutTheme.FONT_BODY,
            fg=GymRoutTheme.TEXT_SECONDARY,
            bg=GymRoutTheme.BG_DARK
        )
        subtitle.pack(anchor="w", pady=(5, 30))
        
        # Quick stats cards
        stats_frame = tk.Frame(container, bg=GymRoutTheme.BG_DARK)
        stats_frame.pack(fill="x", pady=20)
        
        stats = [
            ("🔥", "Current Streak", "0 days", GymRoutTheme.ACCENT_PRIMARY),
            ("📊", "This Week", "0 workouts", GymRoutTheme.ACCENT_SECONDARY),
            ("💪", "Level", self.user.experience_level.value, self._get_level_color()),
            ("⭐", "Status", "Premium" if self.user.is_premium else "Free", 
             GymRoutTheme.ACCENT_GOLD if self.user.is_premium else GymRoutTheme.TEXT_MUTED),
        ]
        
        for i, (icon, title, value, color) in enumerate(stats):
            card = tk.Frame(stats_frame, bg=GymRoutTheme.BG_CARD, padx=20, pady=15)
            card.pack(side="left", padx=(0, 15), fill="y")
            
            icon_label = tk.Label(card, text=icon, font=("Segoe UI", 24), bg=GymRoutTheme.BG_CARD)
            icon_label.pack()
            
            value_label = tk.Label(
                card, text=value,
                font=GymRoutTheme.FONT_BODY_BOLD,
                fg=color, bg=GymRoutTheme.BG_CARD
            )
            value_label.pack(pady=(5, 0))
            
            title_label = tk.Label(
                card, text=title,
                font=GymRoutTheme.FONT_SMALL,
                fg=GymRoutTheme.TEXT_MUTED, bg=GymRoutTheme.BG_CARD
            )
            title_label.pack()
        
        # Today's workout preview
        if self.current_schedule:
            today = datetime.now().strftime("%A")
            today_workout = self.current_schedule.days.get(today)
            
            preview_frame = tk.Frame(container, bg=GymRoutTheme.BG_CARD, padx=25, pady=20)
            preview_frame.pack(fill="x", pady=(30, 0))
            
            preview_header = tk.Label(
                preview_frame, text=f"📅 Today's Workout - {today}",
                font=GymRoutTheme.FONT_SUBHEADING,
                fg=GymRoutTheme.ACCENT_PRIMARY, bg=GymRoutTheme.BG_CARD
            )
            preview_header.pack(anchor="w")
            
            if today_workout:
                workout_info = tk.Label(
                    preview_frame,
                    text=f"{today_workout.name}: {today_workout.focus}\n"
                         f"Duration: ~{today_workout.duration_minutes} minutes  •  "
                         f"{len(today_workout.exercises)} exercises",
                    font=GymRoutTheme.FONT_BODY,
                    fg=GymRoutTheme.TEXT_SECONDARY, bg=GymRoutTheme.BG_CARD,
                    justify="left"
                )
                workout_info.pack(anchor="w", pady=(10, 15))
                
                start_btn = StyledButton(
                    preview_frame, "Start Workout →", 
                    command=self._show_schedule_view,
                    style="primary", width=160
                )
                start_btn.pack(anchor="w")
            else:
                rest_label = tk.Label(
                    preview_frame, text="🧘 Rest Day - Recovery is part of the process!",
                    font=GymRoutTheme.FONT_BODY,
                    fg=GymRoutTheme.ACCENT_SECONDARY, bg=GymRoutTheme.BG_CARD
                )
                rest_label.pack(anchor="w", pady=10)
        else:
            # No schedule - prompt to create
            cta_frame = tk.Frame(container, bg=GymRoutTheme.BG_CARD, padx=30, pady=30)
            cta_frame.pack(fill="x", pady=(30, 0))
            
            cta_text = tk.Label(
                cta_frame, text="You don't have a workout schedule yet.\nLet's create one tailored to your goals!",
                font=GymRoutTheme.FONT_BODY,
                fg=GymRoutTheme.TEXT_SECONDARY, bg=GymRoutTheme.BG_CARD,
                justify="center"
            )
            cta_text.pack(pady=(0, 20))
            
            create_btn = StyledButton(
                cta_frame, "Create My Schedule",
                command=self._show_schedule_builder,
                style="primary", width=180
            )
            create_btn.pack()
    
    def _show_schedule_builder(self):
        self._clear_content()
        
        container = tk.Frame(self.content, bg=GymRoutTheme.BG_DARK, padx=40, pady=30)
        container.pack(fill="both", expand=True)
        
        # Header
        header = tk.Label(
            container, text="Create Your Schedule",
            font=GymRoutTheme.FONT_HEADING,
            fg=GymRoutTheme.TEXT_PRIMARY, bg=GymRoutTheme.BG_DARK
        )
        header.pack(anchor="w")
        
        subtitle = tk.Label(
            container, text="Customize your weekly workout routine",
            font=GymRoutTheme.FONT_BODY,
            fg=GymRoutTheme.TEXT_SECONDARY, bg=GymRoutTheme.BG_DARK
        )
        subtitle.pack(anchor="w", pady=(5, 30))
        
        # Form container
        form_frame = tk.Frame(container, bg=GymRoutTheme.BG_CARD, padx=30, pady=30)
        form_frame.pack(fill="x")
        
        # Experience level selection
        level_label = tk.Label(
            form_frame, text="Experience Level",
            font=GymRoutTheme.FONT_BODY_BOLD,
            fg=GymRoutTheme.TEXT_PRIMARY, bg=GymRoutTheme.BG_CARD
        )
        level_label.pack(anchor="w")
        
        level_desc = tk.Label(
            form_frame, text="This affects exercise selection and volume",
            font=GymRoutTheme.FONT_SMALL,
            fg=GymRoutTheme.TEXT_MUTED, bg=GymRoutTheme.BG_CARD
        )
        level_desc.pack(anchor="w", pady=(2, 10))
        
        self.level_var = tk.StringVar(value=self.user.experience_level.value)
        
        level_options_frame = tk.Frame(form_frame, bg=GymRoutTheme.BG_CARD)
        level_options_frame.pack(anchor="w", pady=(0, 25))
        
        level_info = [
            (ExperienceLevel.BEGINNER, "Less than 1 year of training", GymRoutTheme.LEVEL_BEGINNER),
            (ExperienceLevel.INTERMEDIATE, "1-3 years of training", GymRoutTheme.LEVEL_INTERMEDIATE),
            (ExperienceLevel.PROFESSIONAL, "3+ years of training", GymRoutTheme.LEVEL_PRO),
        ]
        
        for level, desc, color in level_info:
            level_btn_frame = tk.Frame(level_options_frame, bg=GymRoutTheme.BG_CARD)
            level_btn_frame.pack(side="left", padx=(0, 20))
            
            rb = tk.Radiobutton(
                level_btn_frame, text=level.value,
                variable=self.level_var, value=level.value,
                font=GymRoutTheme.FONT_BODY_BOLD,
                fg=color, bg=GymRoutTheme.BG_CARD,
                selectcolor=GymRoutTheme.BG_INPUT,
                activebackground=GymRoutTheme.BG_CARD
            )
            rb.pack(anchor="w")
            
            desc_label = tk.Label(
                level_btn_frame, text=desc,
                font=GymRoutTheme.FONT_SMALL,
                fg=GymRoutTheme.TEXT_MUTED, bg=GymRoutTheme.BG_CARD
            )
            desc_label.pack(anchor="w")
        
        # Schedule type selection
        schedule_label = tk.Label(
            form_frame, text="Schedule Type",
            font=GymRoutTheme.FONT_BODY_BOLD,
            fg=GymRoutTheme.TEXT_PRIMARY, bg=GymRoutTheme.BG_CARD
        )
        schedule_label.pack(anchor="w", pady=(10, 0))
        
        schedule_desc = tk.Label(
            form_frame, text="Choose a split that fits your availability",
            font=GymRoutTheme.FONT_SMALL,
            fg=GymRoutTheme.TEXT_MUTED, bg=GymRoutTheme.BG_CARD
        )
        schedule_desc.pack(anchor="w", pady=(2, 10))
        
        self.schedule_var = tk.StringVar(value=ScheduleType.PPL_3DAY.value)
        
        schedule_info = [
            (ScheduleType.PPL_3DAY, "3 days/week • Great for beginners"),
            (ScheduleType.PPL_6DAY, "6 days/week • Maximum muscle growth"),
            (ScheduleType.UPPER_LOWER, "4 days/week • Balanced approach"),
            (ScheduleType.FULL_BODY, "3 days/week • Efficient training"),
            (ScheduleType.BRO_SPLIT, "5 days/week • Classic bodybuilding"),
            (ScheduleType.ARNOLD_SPLIT, "6 days/week • High volume"),
        ]
        
        schedule_grid = tk.Frame(form_frame, bg=GymRoutTheme.BG_CARD)
        schedule_grid.pack(anchor="w", pady=(0, 30))
        
        for i, (stype, desc) in enumerate(schedule_info):
            row = i // 2
            col = i % 2
            
            option_frame = tk.Frame(schedule_grid, bg=GymRoutTheme.BG_INPUT, padx=15, pady=10)
            option_frame.grid(row=row, column=col, padx=(0, 10), pady=5, sticky="w")
            
            is_premium = stype in [ScheduleType.ARNOLD_SPLIT, ScheduleType.BRO_SPLIT]
            
            rb = tk.Radiobutton(
                option_frame, text=stype.value + (" ★" if is_premium else ""),
                variable=self.schedule_var, value=stype.value,
                font=GymRoutTheme.FONT_BODY,
                fg=GymRoutTheme.ACCENT_GOLD if is_premium else GymRoutTheme.TEXT_PRIMARY,
                bg=GymRoutTheme.BG_INPUT,
                selectcolor=GymRoutTheme.BG_CARD,
                activebackground=GymRoutTheme.BG_INPUT
            )
            rb.pack(anchor="w")
            
            desc_label = tk.Label(
                option_frame, text=desc,
                font=GymRoutTheme.FONT_SMALL,
                fg=GymRoutTheme.TEXT_MUTED, bg=GymRoutTheme.BG_INPUT
            )
            desc_label.pack(anchor="w")
        
        # Generate button
        btn_frame = tk.Frame(form_frame, bg=GymRoutTheme.BG_CARD)
        btn_frame.pack(anchor="w", pady=(10, 0))
        
        generate_btn = StyledButton(
            btn_frame, "Generate Schedule",
            command=self._generate_schedule,
            style="primary", width=180
        )
        generate_btn.pack(side="left")
    
    def _generate_schedule(self):
        # Get selected values
        level_str = self.level_var.get()
        schedule_str = self.schedule_var.get()
        
        # Convert to enums
        level = next(l for l in ExperienceLevel if l.value == level_str)
        schedule_type = next(s for s in ScheduleType if s.value == schedule_str)
        
        # Check premium requirement
        premium_schedules = [ScheduleType.ARNOLD_SPLIT, ScheduleType.BRO_SPLIT]
        if schedule_type in premium_schedules and not self.user.is_premium:
            messagebox.showinfo(
                "Premium Feature",
                f"{schedule_type.value} is a premium feature.\n\n"
                "Upgrade to GymRout Premium to unlock all schedule types!"
            )
            return
        
        # Update user and generate schedule
        self.user.experience_level = level
        self.current_schedule = ScheduleGenerator.generate_schedule(schedule_type, level)
        self.user.current_schedule = self.current_schedule
        
        messagebox.showinfo(
            "Schedule Created!",
            f"Your {schedule_type.value} schedule has been created.\n\n"
            f"Experience Level: {level.value}"
        )
        
        self._show_schedule_view()
    
    def _show_schedule_view(self):
        self._clear_content()
        
        if not self.current_schedule:
            self._show_no_schedule_message()
            return
        
        # Create scrollable container
        container = tk.Frame(self.content, bg=GymRoutTheme.BG_DARK)
        container.pack(fill="both", expand=True)
        
        # Header with schedule info
        header_frame = tk.Frame(container, bg=GymRoutTheme.BG_DARK, padx=40, pady=20)
        header_frame.pack(fill="x")
        
        header = tk.Label(
            header_frame, text="My Weekly Schedule",
            font=GymRoutTheme.FONT_HEADING,
            fg=GymRoutTheme.TEXT_PRIMARY, bg=GymRoutTheme.BG_DARK
        )
        header.pack(anchor="w")
        
        schedule_info = tk.Label(
            header_frame,
            text=f"{self.current_schedule.schedule_type.value}  •  {self.current_schedule.experience_level.value}",
            font=GymRoutTheme.FONT_BODY,
            fg=GymRoutTheme.ACCENT_PRIMARY, bg=GymRoutTheme.BG_DARK
        )
        schedule_info.pack(anchor="w", pady=(5, 0))
        
        # Scrollable area for schedule
        canvas = tk.Canvas(container, bg=GymRoutTheme.BG_DARK, highlightthickness=0)
        scrollbar = ttk.Scrollbar(container, orient="vertical", command=canvas.yview)
        scrollable_frame = tk.Frame(canvas, bg=GymRoutTheme.BG_DARK)
        
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        canvas.pack(side="left", fill="both", expand=True, padx=40)
        scrollbar.pack(side="right", fill="y")
        
        # Mouse wheel scrolling
        def _on_mousewheel(event):
            canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")
        canvas.bind_all("<MouseWheel>", _on_mousewheel)
        
        # Day cards
        today = datetime.now().strftime("%A")
        
        for day in ScheduleGenerator.WEEKDAYS:
            workout = self.current_schedule.days.get(day)
            is_today = day == today
            
            day_card = tk.Frame(
                scrollable_frame,
                bg=GymRoutTheme.BG_CARD,
                highlightbackground=GymRoutTheme.ACCENT_PRIMARY if is_today else GymRoutTheme.BG_CARD,
                highlightthickness=2 if is_today else 0
            )
            day_card.pack(fill="x", pady=8)
            
            # Day header
            day_header = tk.Frame(day_card, bg=GymRoutTheme.BG_CARD, padx=20, pady=15)
            day_header.pack(fill="x")
            
            day_label = tk.Label(
                day_header,
                text=f"{'📍 ' if is_today else ''}{day}",
                font=GymRoutTheme.FONT_SUBHEADING,
                fg=GymRoutTheme.ACCENT_PRIMARY if is_today else GymRoutTheme.TEXT_PRIMARY,
                bg=GymRoutTheme.BG_CARD
            )
            day_label.pack(side="left")
            
            if workout:
                duration_label = tk.Label(
                    day_header,
                    text=f"~{workout.duration_minutes} min",
                    font=GymRoutTheme.FONT_SMALL,
                    fg=GymRoutTheme.TEXT_MUTED, bg=GymRoutTheme.BG_CARD
                )
                duration_label.pack(side="right")
                
                focus_label = tk.Label(
                    day_header, text=workout.focus,
                    font=GymRoutTheme.FONT_BODY,
                    fg=GymRoutTheme.TEXT_SECONDARY, bg=GymRoutTheme.BG_CARD
                )
                focus_label.pack(side="left", padx=(15, 0))
                
                # Exercises
                exercises_frame = tk.Frame(day_card, bg=GymRoutTheme.BG_DARK, padx=15, pady=10)
                exercises_frame.pack(fill="x")
                
                for exercise in workout.exercises:
                    exercise_card = ExerciseCard(
                        exercises_frame, exercise,
                        is_premium_user=self.user.is_premium
                    )
                    exercise_card.pack(fill="x", pady=2)
            else:
                rest_label = tk.Label(
                    day_header, text="🧘 Rest Day",
                    font=GymRoutTheme.FONT_BODY,
                    fg=GymRoutTheme.ACCENT_SECONDARY, bg=GymRoutTheme.BG_CARD
                )
                rest_label.pack(side="left", padx=(15, 0))
    
    def _show_no_schedule_message(self):
        container = tk.Frame(self.content, bg=GymRoutTheme.BG_DARK)
        container.pack(fill="both", expand=True)
        
        center_frame = tk.Frame(container, bg=GymRoutTheme.BG_DARK)
        center_frame.place(relx=0.5, rely=0.5, anchor="center")
        
        icon = tk.Label(
            center_frame, text="📅",
            font=("Segoe UI", 48), bg=GymRoutTheme.BG_DARK
        )
        icon.pack()
        
        message = tk.Label(
            center_frame, text="No Schedule Created Yet",
            font=GymRoutTheme.FONT_SUBHEADING,
            fg=GymRoutTheme.TEXT_PRIMARY, bg=GymRoutTheme.BG_DARK
        )
        message.pack(pady=(10, 5))
        
        submessage = tk.Label(
            center_frame, text="Create your personalized workout schedule to get started",
            font=GymRoutTheme.FONT_BODY,
            fg=GymRoutTheme.TEXT_SECONDARY, bg=GymRoutTheme.BG_DARK
        )
        submessage.pack(pady=(0, 20))
        
        create_btn = StyledButton(
            center_frame, "Create Schedule",
            command=self._show_schedule_builder,
            style="primary", width=160
        )
        create_btn.pack()
    
    def _show_profile(self):
        self._clear_content()
        
        container = tk.Frame(self.content, bg=GymRoutTheme.BG_DARK, padx=40, pady=30)
        container.pack(fill="both", expand=True)
        
        header = tk.Label(
            container, text="Profile Settings",
            font=GymRoutTheme.FONT_HEADING,
            fg=GymRoutTheme.TEXT_PRIMARY, bg=GymRoutTheme.BG_DARK
        )
        header.pack(anchor="w", pady=(0, 30))
        
        # Profile card
        profile_card = tk.Frame(container, bg=GymRoutTheme.BG_CARD, padx=30, pady=30)
        profile_card.pack(fill="x")
        
        # Avatar placeholder
        avatar = tk.Label(
            profile_card, text="💪",
            font=("Segoe UI", 48), bg=GymRoutTheme.BG_CARD
        )
        avatar.pack()
        
        # Username
        name_label = tk.Label(
            profile_card, text=self.user.username,
            font=GymRoutTheme.FONT_SUBHEADING,
            fg=GymRoutTheme.TEXT_PRIMARY, bg=GymRoutTheme.BG_CARD
        )
        name_label.pack(pady=(10, 5))
        
        # Status badge
        status_text = "⭐ Premium Member" if self.user.is_premium else "Free Account"
        status_color = GymRoutTheme.ACCENT_GOLD if self.user.is_premium else GymRoutTheme.TEXT_MUTED
        
        status_label = tk.Label(
            profile_card, text=status_text,
            font=GymRoutTheme.FONT_BODY,
            fg=status_color, bg=GymRoutTheme.BG_CARD
        )
        status_label.pack()
        
        # Stats
        stats_frame = tk.Frame(profile_card, bg=GymRoutTheme.BG_CARD)
        stats_frame.pack(pady=20)
        
        stats = [
            ("Level", self.user.experience_level.value),
            ("Workouts", str(len(self.user.workout_history))),
            ("Schedule", self.current_schedule.schedule_type.value if self.current_schedule else "None"),
        ]
        
        for label, value in stats:
            stat_item = tk.Frame(stats_frame, bg=GymRoutTheme.BG_INPUT, padx=20, pady=10)
            stat_item.pack(side="left", padx=5)
            
            value_lbl = tk.Label(
                stat_item, text=value,
                font=GymRoutTheme.FONT_BODY_BOLD,
                fg=GymRoutTheme.TEXT_PRIMARY, bg=GymRoutTheme.BG_INPUT
            )
            value_lbl.pack()
            
            label_lbl = tk.Label(
                stat_item, text=label,
                font=GymRoutTheme.FONT_SMALL,
                fg=GymRoutTheme.TEXT_MUTED, bg=GymRoutTheme.BG_INPUT
            )
            label_lbl.pack()
        
        # Toggle premium button (for demo)
        toggle_frame = tk.Frame(container, bg=GymRoutTheme.BG_DARK, pady=30)
        toggle_frame.pack(fill="x")
        
        toggle_btn = StyledButton(
            toggle_frame,
            "Deactivate Premium" if self.user.is_premium else "Activate Premium (Demo)",
            command=self._toggle_premium,
            style="gold" if not self.user.is_premium else "secondary",
            width=200
        )
        toggle_btn.pack()
    
    def _show_premium_upgrade(self):
        self._clear_content()
        
        container = tk.Frame(self.content, bg=GymRoutTheme.BG_DARK, padx=40, pady=30)
        container.pack(fill="both", expand=True)
        
        if self.user.is_premium:
            # Already premium
            header = tk.Label(
                container, text="⭐ You're a Premium Member!",
                font=GymRoutTheme.FONT_HEADING,
                fg=GymRoutTheme.ACCENT_GOLD, bg=GymRoutTheme.BG_DARK
            )
            header.pack(anchor="w")
            
            subtitle = tk.Label(
                container, text="Enjoy all premium features",
                font=GymRoutTheme.FONT_BODY,
                fg=GymRoutTheme.TEXT_SECONDARY, bg=GymRoutTheme.BG_DARK
            )
            subtitle.pack(anchor="w", pady=(5, 30))
        else:
            # Upgrade prompt
            header = tk.Label(
                container, text="Upgrade to Premium",
                font=GymRoutTheme.FONT_HEADING,
                fg=GymRoutTheme.TEXT_PRIMARY, bg=GymRoutTheme.BG_DARK
            )
            header.pack(anchor="w")
            
            subtitle = tk.Label(
                container, text="Unlock the full potential of GymRout",
                font=GymRoutTheme.FONT_BODY,
                fg=GymRoutTheme.TEXT_SECONDARY, bg=GymRoutTheme.BG_DARK
            )
            subtitle.pack(anchor="w", pady=(5, 30))
        
        # Features grid
        features_frame = tk.Frame(container, bg=GymRoutTheme.BG_DARK)
        features_frame.pack(fill="both", expand=True)
        
        for i, feature_data in enumerate(PremiumFeatures.get_feature_list()):
            card = tk.Frame(features_frame, bg=GymRoutTheme.BG_CARD, padx=25, pady=20)
            card.grid(row=i // 2, column=i % 2, padx=10, pady=10, sticky="nsew")
            
            # Feature name
            name_label = tk.Label(
                card, text=feature_data["name"],
                font=GymRoutTheme.FONT_BODY_BOLD,
                fg=GymRoutTheme.ACCENT_GOLD, bg=GymRoutTheme.BG_CARD
            )
            name_label.pack(anchor="w")
            
            # Description
            desc_label = tk.Label(
                card, text=feature_data["description"],
                font=GymRoutTheme.FONT_SMALL,
                fg=GymRoutTheme.TEXT_SECONDARY, bg=GymRoutTheme.BG_CARD,
                wraplength=250, justify="left"
            )
            desc_label.pack(anchor="w", pady=(5, 10))
            
            # Price
            price_label = tk.Label(
                card, text=feature_data["price"],
                font=GymRoutTheme.FONT_BODY_BOLD,
                fg=GymRoutTheme.TEXT_PRIMARY, bg=GymRoutTheme.BG_CARD
            )
            price_label.pack(anchor="w")
        
        features_frame.columnconfigure(0, weight=1)
        features_frame.columnconfigure(1, weight=1)
        
        if not self.user.is_premium:
            # CTA button
            cta_frame = tk.Frame(container, bg=GymRoutTheme.BG_DARK, pady=30)
            cta_frame.pack(fill="x")
            
            upgrade_btn = StyledButton(
                cta_frame, "Get Premium - $14.99/month",
                command=self._handle_premium_purchase,
                style="gold", width=250, height=50
            )
            upgrade_btn.pack()
    
    def _toggle_premium(self):
        self.user.is_premium = not self.user.is_premium
        
        status = "Premium" if self.user.is_premium else "Free"
        self.user_status_label.configure(text=f"{status} Account")
        
        messagebox.showinfo(
            "Status Updated",
            f"Your account is now: {status}"
        )
        
        self._show_profile()
    
    def _handle_premium_purchase(self):
        result = messagebox.askyesno(
            "Upgrade to Premium",
            "This is a demo. In a real app, this would process payment.\n\n"
            "Activate premium features now?"
        )
        
        if result:
            self.user.is_premium = True
            self.user_status_label.configure(text="Premium Account")
            messagebox.showinfo(
                "Welcome to Premium! ⭐",
                "All premium features are now unlocked.\n\n"
                "Enjoy your enhanced GymRout experience!"
            )
            self._show_premium_upgrade()
    
    def _get_greeting(self) -> str:
        hour = datetime.now().hour
        if hour < 12:
            return "Good morning"
        elif hour < 17:
            return "Good afternoon"
        return "Good evening"
    
    def _get_level_color(self) -> str:
        colors = {
            ExperienceLevel.BEGINNER: GymRoutTheme.LEVEL_BEGINNER,
            ExperienceLevel.INTERMEDIATE: GymRoutTheme.LEVEL_INTERMEDIATE,
            ExperienceLevel.PROFESSIONAL: GymRoutTheme.LEVEL_PRO,
        }
        return colors.get(self.user.experience_level, GymRoutTheme.TEXT_PRIMARY)
    
    def run(self):
        self.root.mainloop()


# ═══════════════════════════════════════════════════════════════════════════
# ENTRY POINT
# ═══════════════════════════════════════════════════════════════════════════

if __name__ == "__main__":
    app = GymRoutApp()
    app.run()
