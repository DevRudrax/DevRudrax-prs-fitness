# 🏋️‍♂️ PRS Fitness - Premium Studio Application

PRS Fitness is an industry-grade, beautifully designed cross-platform fitness studio application built using **Flet (Flutter for Python)**. It features a curated, harmonized sleek dark design system with active responsive sizing, native client persistence, an advanced BMI calculator, and a dynamic weekly workout split generator.

---

## ✨ Features

- **🎯 Interactive Dashboard**: Tailored greeting, current streaks, statistics tracking, and today's dynamically generated session preview.
- **⚖️ Advanced BMI Calculator**: Instant body composition analysis, interactive sliders for height/weight, radial status ring, health risk levels, and comparative bar graphs.
- **⚙️ Routine Builder Studio**: Allows choosing splits based on availability and skill level. Automatically populates training routines.
- **📅 Weekly Workout Scheduler**: Comprehensive overview of target focus, sets, reps, rests, and safety coaching tips.
- **⭐ Premium Tier**: Unlocks professional-grade split structures (Arnold Split, Bro Split) and advanced premium exercises (Cable Flyes, Bulgarian Split Squats, Leg Extensions).
- **💾 State Persistence**: Native platform client storage for instant offline profile and history retention.

---

## 🎨 Design System & Aesthetics

PRS Fitness is crafted with a high-end visual aesthetic inspired by modern fitness applications:
- **Color Palette**: Dark space background (`#080B10`), dark grey container cards (`#111827`), glowing neon accents (Cyan `#00E5FF`, Emerald Green `#00FF88`, Amber `#FFB800`, Coral Red `#FF4444`).
- **Smooth Micro-Animations**: Active hover containers with automatic scale transitions (`1.02x` magnification) and border-color glow effects on focus.
- **Premium Layouts**: Responsive grid rows that adapt seamlessly across Windows, Android, iOS, and Web viewports.

---

## 🏗️ Architecture & Technology Stack

- **Core Framework**: [Flet](https://flet.dev/) (Native Flutter-powered UI engine in Python).
- **State Management**: Secure local state persistence using the cross-platform Flet `page.client_storage` API.
- **Data Layer**: Structured dataclasses (`Exercise`, `WorkoutDay`, `WeeklySchedule`, `UserProfile`) with clean serialization and migration support from legacy systems.

---

## 🚀 Getting Started

### Prerequisites
- Python 3.8 or higher
- `flet` package installed

### Installation & Run

1. Clone this repository to your local machine:
   ```bash
   git clone https://github.com/DevRudrax/DevRudrax-prs-fitness.git
   cd DevRudrax-prs-fitness
   ```

2. Install dependencies:
   ```bash
   pip install flet
   ```

3. Run the application:
   ```bash
   python prs_fitness_crossplatform.py
   ```

---

## 📁 Repository Contents

To maintain a clean and lightweight repository, only core files are tracked:
- `prs_fitness_crossplatform.py`: The single-entry, highly optimized cross-platform Flet application code.
- `README.md`: Complete description, setup instructions, and architecture manual.
- `.gitignore`: Configured to ignore local caches, build artifacts, and system files.

---

## 📜 License
This project is proprietary and built for premium personal training scheduling. All rights reserved.
