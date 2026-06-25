import tkinter as tk
from tkinter import ttk
from datetime import datetime, timezone
import time

# --- 1. SQT LUNAR CONSTANTS ---
SQT_NAME = "Squirrels Quantum Time"
SQT_ACRONYM = "SQT"
EARTH_HOURS_PER_SQT_DAY = 37.301826
SEC_PER_SQT_DAY = EARTH_HOURS_PER_SQT_DAY * 60 * 60
SQT_EPOCH = datetime(2026, 1, 18, 20, 52, 0, tzinfo=timezone.utc)
LUNAR_CYCLE_SECONDS = 29.53059 * 24 * 60 * 60
SQT_LUNATIONS = {
    1: "Sleepy Moon", 2: "Pinecone Moon", 3: "Scamper Moon",
    4: "Asher Moon", 5: "Bark Stripper Moon", 6: "Canopy Moon",
    7: "Hollow Tree Moon", 8: "Golden Leaf Moon", 9: "Cache Moon",
    10: "Shadow Moon", 11: "Forage Moon", 12: "Chattering Moon"
}
# Master Database of 19 Unique Day Names mapped to their exact Phase Week
SQT_UNIQUE_DAYS = {
    1: ("Truffle-day", "Week 1: The First Nibble"),
    2: ("Sprout-day", "Week 1: The First Nibble"),
    3: ("Sap-day", "Week 1: The First Nibble"),
    4: ("Twig-day", "Week 1: The First Nibble"),
    5: ("Fern-day", "Week 2: The High Canopy"),
    6: ("Chitter-day", "Week 2: The High Canopy"),
    7: ("Stash-day", "Week 2: The High Canopy"),
    8: ("Thicket-day", "Week 2: The High Canopy"),
    9: ("Moss-day", "Week 2: The High Canopy"),
    10: ("Cache-Day", "Week 3: The Great Acorn"),
    11: ("Forage-day", "Week 3: The Great Acorn"),
    12: ("Oak-day", "Week 3: The Great Acorn"),
    13: ("Timber-day", "Week 3: The Great Acorn"),
    14: ("Swindle-day", "Week 3: The Great Acorn"),
    15: ("Scurry-day", "Week 4: The Deep Burrow"),
    16: ("Bark-day", "Week 4: The Deep Burrow"),
    17: ("Willow-day", "Week 4: The Deep Burrow"),
    18: ("Drey-day", "Week 4: The Deep Burrow"),
    19: ("Nap-day", "Week 4: The Deep Burrow")
}

# --- NEW: Calendar theming and structure constants ---
SQT_HIGHLIGHT_BG = "#4AF626"
SQT_HIGHLIGHT_FG = "#1E1E1E"
WEEK_DEFINITIONS = [
    {"start": 1, "end": 4,  "label": "Week 1: The First Nibble"},
    {"start": 5, "end": 9,  "label": "Week 2: The High Canopy"},
    {"start": 10, "end": 14, "label": "Week 3: The Great Acorn"},
    {"start": 15, "end": 19, "label": "Week 4: The Deep Burrow"},
]
day_label_refs = {}
lbl_cal_header = None  # assigned at UI build time


# --- 2. THE ENGINE ---
def get_detailed_sqt():
    now_earth = datetime.now(timezone.utc)
    elapsed_seconds = (now_earth - SQT_EPOCH).total_seconds()
   
    if elapsed_seconds < 0:
        return "Before SQT Lunar Era", "00:00:00", "No Moon Tracked", "No Day", "No Week", 0, "No Lunation"
       
    total_months_elapsed = elapsed_seconds / LUNAR_CYCLE_SECONDS
    current_month_raw = int(total_months_elapsed)
   
    sqt_year = (current_month_raw // 12) + 1
    sqt_month_num = (current_month_raw % 12) + 1
    position_in_month = total_months_elapsed - current_month_raw
   
    # Calculate Day (Strict 1 to 19 layout)
    sqt_day = int(position_in_month * 19) + 1
   
    # --- FETCH DAY NAME AND WEEK VIA UNIQUE MAP ---
    day_name, lunar_week = SQT_UNIQUE_DAYS.get(sqt_day, ("Unknown Day", "Unknown Week"))
   
    # Calculate Time remaining in this exact 37.3018-hour day
    seconds_into_current_month = position_in_month * LUNAR_CYCLE_SECONDS
    seconds_left_in_day = seconds_into_current_month % SEC_PER_SQT_DAY
   
    h = int(seconds_left_in_day // 3600)
    m = int((seconds_left_in_day % 3600) // 60)
    s = int(seconds_left_in_day % 60)
   
    # Static Moon Phase mapping locked entirely to day number
    if sqt_day == 1 or sqt_day == 19:
        moon_phase = "New Moon 🌑"
    elif 2 <= sqt_day <= 4:
        moon_phase = "Waxing Crescent 🌒"
    elif sqt_day == 5:
        moon_phase = "First Quarter 🌓"
    elif 6 <= sqt_day <= 9:
        moon_phase = "Waxing Gibbous 🌔"
    elif sqt_day == 10:
        moon_phase = "Full Moon 🌕"
    elif 11 <= sqt_day <= 14:
        moon_phase = "Waning Gibbous 🌖"
    elif sqt_day == 15:
        moon_phase = "Last Quarter 🌗"
    else:
        moon_phase = "Waning Crescent 🌘"
       
    month_name = SQT_LUNATIONS.get(sqt_month_num, "Unknown Lunation")
   
    date_string = f"Year {sqt_year}, {month_name}"
    time_string = f"{h:02d}:{m:02d}:{s:02d}"
   
    return date_string, time_string, moon_phase, day_name, lunar_week, sqt_day, month_name  # MODIFIED: added sqt_day + month_name for calendar


def get_local_human_time():
    local_time = time.localtime()
    timezone_name = time.tzname[local_time.tm_isdst]
    time_string = time.strftime("%Y-%m-%d %I:%M:%S %p", local_time)
    return f"{time_string} ({timezone_name})"


# --- NEW: Highlight helper (called every second from update loop) ---
def highlight_current_day(current_day):
    """Apply/remove highlight styling on the pre-built day labels. O(19) and flicker-free."""
    for d, lbl in day_label_refs.items():
        if d == current_day:
            lbl.config(
                bg=SQT_HIGHLIGHT_BG,
                fg=SQT_HIGHLIGHT_FG,
                font=("Courier New", 9, "bold")
            )
        else:
            lbl.config(
                bg="#2E2E2E",
                fg="#E0E0E0",
                font=("Courier New", 9, "normal")
            )


# --- 3. UI DASHBOARD ---
def update_dashboard():
    date_str, time_str, moon, day_name, lunar_week, sqt_day, month_name = get_detailed_sqt()
   
    lbl_sqt_date.config(text=date_str)
    lbl_sqt_week.config(text=lunar_week)
    lbl_sqt_dayname.config(text=day_name)
    lbl_sqt_time.config(text=time_str)
    lbl_moon_phase.config(text=moon)
   
    human_time_str = get_local_human_time()
    lbl_human_time.config(text=human_time_str)
   
    # NEW: live highlight + header update
    highlight_current_day(sqt_day)
    if lbl_cal_header is not None:
        lbl_cal_header.config(text=f"🌰 {month_name} • Day {sqt_day}/19 Highlighted 🌰")
   
    root.after(1000, update_dashboard)


# Setup Layout Window
root = tk.Tk()
root.title(f"{SQT_NAME} Engine Dashboard (Unique 19-Day Variant + Visual Calendar)")
root.geometry("480x620")  # Slightly taller to accommodate calendar comfortably
root.configure(bg="#2E2E2E")

title_frame = tk.Frame(root, bg="#1E1E1E")
title_frame.pack(fill=tk.X)

lbl_main_title = tk.Label(
    title_frame,
    text=f"--- Squirrels Quantum Time (SQT) ---",
    font=("Courier New", 18, "bold"),
    fg="#4AF626",
    bg="#1E1E1E",
    pady=12
)
lbl_main_title.pack()

body_frame = tk.Frame(root, bg="#2E2E2E", padx=20, pady=8)
body_frame.pack(fill=tk.BOTH, expand=True)

def create_display_row(parent, label_text, color="#FFFFFF", size=12, is_bold=False):
    font_weight = "bold" if is_bold else "normal"
    lbl_desc = tk.Label(parent, text=label_text, font=("Arial", 10, "bold"), fg="#888888", bg="#2E2E2E")
    lbl_desc.pack(anchor=tk.W, pady=(4, 0))
   
    lbl_val = tk.Label(parent, text="--", font=("Courier New", size, font_weight), fg=color, bg="#2E2E2E")
    lbl_val.pack(anchor=tk.W, pady=(1, 2))
    return lbl_val


# Row Assignments (original)
lbl_sqt_date = create_display_row(body_frame, "CURRENT MOON LUNATION:", color="#E0E0E0", size=13, is_bold=True)
lbl_sqt_week = create_display_row(body_frame, "LUNAR CYCLE PHASE WEEK:", color="#33B5E5", size=11)
lbl_sqt_dayname = create_display_row(body_frame, "UNIQUE SQUIRREL DAY:", color="#FFBB33", size=16, is_bold=True)
lbl_sqt_time = create_display_row(body_frame, "SQUIRREL TIME (37.3h Day):", color="#4AF626", size=20, is_bold=True)
lbl_moon_phase = create_display_row(body_frame, "SKY PHASE DETECTED:", color="#FFFFFF", size=12)

separator = ttk.Separator(body_frame, orient='horizontal')
separator.pack(fill='x', pady=8)

lbl_human_time = create_display_row(body_frame, "LOCAL HUMAN CALENDAR:", color="#FFAAA6", size=11)


# --- NEW: VISUAL SQT LUNATION CALENDAR SECTION ---
cal_header_frame = tk.Frame(body_frame, bg="#2E2E2E")
cal_header_frame.pack(fill=tk.X, pady=(6, 2))

lbl_cal_header = tk.Label(
    cal_header_frame,
    text="🌰 CURRENT LUNATION 19-DAY CALENDAR 🌰",
    font=("Arial", 10, "bold"),
    fg="#FFBB33",
    bg="#2E2E2E"
)
lbl_cal_header.pack(anchor=tk.W)

calendar_container = tk.Frame(body_frame, bg="#2E2E2E")
calendar_container.pack(fill=tk.X, pady=2)

for week in WEEK_DEFINITIONS:
    week_frame = tk.Frame(calendar_container, bg="#2E2E2E")
    week_frame.pack(fill=tk.X, pady=1)
    
    wk_lbl = tk.Label(
        week_frame,
        text=week["label"],
        font=("Arial", 9, "bold"),
        fg="#888888",
        bg="#2E2E2E"
    )
    wk_lbl.pack(anchor=tk.W, pady=(0, 1))
    
    days_row = tk.Frame(week_frame, bg="#2E2E2E")
    days_row.pack(fill=tk.X)
    
    for d in range(week["start"], week["end"] + 1):
        name, _ = SQT_UNIQUE_DAYS[d]
        lbl = tk.Label(
            days_row,
            text=f"{d:2d} {name}",
            font=("Courier New", 9),
            fg="#E0E0E0",
            bg="#2E2E2E",
            width=17,
            anchor="w",
            padx=2,
            pady=1
        )
        lbl.pack(side=tk.LEFT, padx=1)
        day_label_refs[d] = lbl   # store reference for O(1) highlight updates


# Start the live update loop
update_dashboard()

root.mainloop()