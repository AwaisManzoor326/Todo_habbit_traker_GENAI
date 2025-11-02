# streamlit run Todo_Habbit_traker.py


import streamlit as st
from uuid import uuid4
import json
import os
from datetime import date, datetime, timedelta
from typing import List, Dict, Any
import random

# -----------------------
# Constants & Utilities
# -----------------------
DATA_FILE = "app_data.json"
WEEKDAYS = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]

DEFAULT_QUOTES = [
    "Small steps every day. That's how progress is built.",
    "Do something today that your future self will thank you for.",
    "Consistency is what transforms average into excellence.",
    "Don't count the days. Make the days count.",
    "Productivity is never an accident. It is always the result of a commitment."
]

# -----------------------
# Data model helpers
# -----------------------
def init_data_file():
    """Create initial JSON structure if file doesn't exist."""
    if not os.path.exists(DATA_FILE):
        initial = {"tasks": [], "habits": []}
        save_data(initial)

def load_data() -> Dict[str, Any]:
    """Load data from JSON file. Return dict with 'tasks' and 'habits'."""
    init_data_file()
    with open(DATA_FILE, "r", encoding="utf-8") as f:
        return json.load(f)

def save_data(data: Dict[str, Any]):
    """Save dictionary to JSON file."""
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2, default=str)

# -----------------------
# Task-related functions
# -----------------------
def create_task(title: str, description: str, deadline: date) -> Dict[str, Any]:
    """Create a task object."""
    return {
        "id": str(uuid4()),
        "title": title.strip(),
        "description": description.strip(),
        "deadline": deadline.isoformat() if deadline else None,
        "created_at": datetime.now().isoformat(),
        "completed": False
    }

def add_task(task: Dict[str, Any]):
    data = load_data()
    data["tasks"].append(task)
    save_data(data)

def update_task(task_id: str, **changes):
    data = load_data()
    for t in data["tasks"]:
        if t["id"] == task_id:
            t.update(changes)
            break
    save_data(data)

def delete_task(task_id: str):
    data = load_data()
    data["tasks"] = [t for t in data["tasks"] if t["id"] != task_id]
    save_data(data)

# -----------------------
# Habit-related functions
# -----------------------
def create_habit(name: str, desc: str) -> Dict[str, Any]:
    """Create habit object. 'log' stores dates (YYYY-MM-DD) when completed."""
    return {
        "id": str(uuid4()),
        "name": name.strip(),
        "description": desc.strip(),
        "created_at": datetime.now().isoformat(),
        "log": []  # list of ISO date strings representing days when habit was done
    }

def add_habit(habit: Dict[str, Any]):
    data = load_data()
    data["habits"].append(habit)
    save_data(data)

def update_habit(habit_id: str, **changes):
    data = load_data()
    for h in data["habits"]:
        if h["id"] == habit_id:
            h.update(changes)
            break
    save_data(data)

def delete_habit(habit_id: str):
    data = load_data()
    data["habits"] = [h for h in data["habits"] if h["id"] != habit_id]
    save_data(data)

def toggle_habit_for_date(habit_id: str, day_iso: str, is_done: bool):
    """Mark or unmark a habit for a particular date."""
    data = load_data()
    for h in data["habits"]:
        if h["id"] == habit_id:
            if is_done and day_iso not in h["log"]:
                h["log"].append(day_iso)
            if not is_done and day_iso in h["log"]:
                h["log"].remove(day_iso)
            break
    save_data(data)

# -----------------------
# Presentation helpers
# -----------------------
def format_date_iso(iso_str: str):
    if not iso_str:
        return "-"
    try:
        d = datetime.fromisoformat(iso_str).date()
        return d.strftime("%b %d, %Y")
    except Exception:
        return iso_str

def percent(part: int, whole: int) -> int:
    return int((part / whole) * 100) if whole else 0

def get_week_dates(ref_date: date = None) -> List[date]:
    """Return list of 7 dates for the week starting Monday for the reference date."""
    if ref_date is None:
        ref_date = date.today()
    start = ref_date - timedelta(days=(ref_date.weekday()))  # Monday
    return [start + timedelta(days=i) for i in range(7)]

def weekly_completion_for_habit(habit: Dict[str, Any], ref_date: date = None) -> float:
    week = get_week_dates(ref_date)
    week_iso = {d.isoformat() for d in week}
    done = len([d for d in habit.get("log", []) if d in week_iso])
    return percent(done, 7)

def current_streak(habit: Dict[str, Any]) -> int:
    """Compute current consecutive day streak up to today for this habit."""
    log = set(habit.get("log", []))
    streak = 0
    today = date.today()
    day = today
    while day.isoformat() in log:
        streak += 1
        day -= timedelta(days=1)
    return streak

# -----------------------
# Streamlit UI / Layout
# -----------------------
st.set_page_config(page_title="FocusBoard — ToDo + Habits", layout="wide", page_icon="✅")

# Minimal custom CSS to make UI modern/minimal
st.markdown(
    """
    <style>
    /* Minimal, soft theme */
    .stApp { background-color: #f6f7fb; }
    .card {
        background: white;
        padding: 1rem;
        border-radius: 12px;
        box-shadow: 0 6px 18px rgba(30,30,80,0.06);
        margin-bottom: 1rem;
    }
    .muted { color: #6b7280; font-size: 0.9em; }
    .small { font-size: 0.85em; }
    </style>
    """,
    unsafe_allow_html=True
)

# Top bar
col1, col2 = st.columns([7, 3])
with col1:
    st.title("FocusBoard")
    st.write("A minimal productivity dashboard — To-Do + Habit Tracker")
with col2:
    quote = random.choice(DEFAULT_QUOTES)
    st.markdown(f"**💬 Quote:** {quote}")
    st.write("")  # spacing

# Sidebar - navigation and filters
st.sidebar.header("Navigation")
tab = st.sidebar.radio("Go to", ["Dashboard", "To-Do List", "Habit Tracker", "Settings"])

st.sidebar.markdown("---")
st.sidebar.header("To-Do Filters")
filter_status = st.sidebar.selectbox("Show tasks", ["All", "Pending", "Completed"])
st.sidebar.markdown("---")
st.sidebar.header("Quick Add")
with st.sidebar.form("quick_add"):
    qtype = st.selectbox("Add", ["Task", "Habit"])
    if qtype == "Task":
        qtitle = st.text_input("Title")
        q_deadline = st.date_input("Deadline", value=date.today())
        qdesc = st.text_area("Description", height=80)
    else:
        qtitle = st.text_input("Habit name")
        q_deadline = None
        qdesc = st.text_area("Habit description", height=80)
    submitted = st.form_submit_button("Add")
    if submitted:
        if qtype == "Task":
            if qtitle.strip():
                add_task(create_task(qtitle, qdesc, q_deadline))
                st.sidebar.success("Task added!")
            else:
                st.sidebar.error("Task needs a title.")
        else:
            if qtitle.strip():
                add_habit(create_habit(qtitle, qdesc))
                st.sidebar.success("Habit added!")
            else:
                st.sidebar.error("Habit needs a name.")

# Load data
data = load_data()
tasks: List[Dict[str, Any]] = data.get("tasks", [])
habits: List[Dict[str, Any]] = data.get("habits", [])

# -----------------------
# Dashboard Tab
# -----------------------
if tab == "Dashboard" or tab == "To-Do List" and st.session_state.get("force_dashboard", False):
    st.header("Dashboard")
    # Cards row: Tasks progress, Habits weekly completion, Total streaks
    tcol1, tcol2, tcol3 = st.columns(3)
    with tcol1:
        total_tasks = len(tasks)
        completed_tasks = len([t for t in tasks if t.get("completed")])
        st.markdown("<div class='card'>", unsafe_allow_html=True)
        st.subheader("Tasks")
        st.write(f"{completed_tasks} / {total_tasks} completed")
        st.progress(percent(completed_tasks, total_tasks))
        st.markdown("</div>", unsafe_allow_html=True)
    with tcol2:
        st.markdown("<div class='card'>", unsafe_allow_html=True)
        st.subheader("Habits (weekly)")
        if habits:
            avg_weekly = int(sum(weekly_completion_for_habit(h) for h in habits) / len(habits))
        else:
            avg_weekly = 0
        st.write(f"Average weekly completion: {avg_weekly}%")
        st.progress(avg_weekly)
        st.markdown("</div>", unsafe_allow_html=True)
    with tcol3:
        st.markdown("<div class='card'>", unsafe_allow_html=True)
        st.subheader("Streaks")
        if habits:
            best = max(current_streak(h) for h in habits)
        else:
            best = 0
        st.write(f"Best current streak: {best} day(s)")
        st.markdown("</div>", unsafe_allow_html=True)

    st.markdown("---")
    st.subheader("Upcoming tasks (next 7 days)")
    upcoming = []
    today = date.today()
    for t in tasks:
        if t.get("deadline"):
            try:
                d = datetime.fromisoformat(t["deadline"]).date()
                if 0 <= (d - today).days <= 7:
                    upcoming.append((d, t))
            except Exception:
                pass
    upcoming = sorted(upcoming, key=lambda x: x[0])
    if upcoming:
        for d, t in upcoming:
            completed_tag = "✅" if t.get("completed") else "⏳"
            st.write(f"**{t['title']}** — {format_date_iso(t['deadline'])}  {completed_tag}")
            st.write(f"<div class='muted small'>{t.get('description','')}</div>", unsafe_allow_html=True)
    else:
        st.info("No upcoming tasks for the next 7 days. Add one!")

# -----------------------
# To-Do Tab
# -----------------------
if tab == "To-Do List":
    st.header("To-Do List")
    with st.expander("Add a new task", expanded=True):
        with st.form("add_task_form", clear_on_submit=True):
            title = st.text_input("Title", placeholder="Short description of the task")
            deadline = st.date_input("Deadline", value=date.today())
            description = st.text_area("Description", help="Optional details")
            submitted = st.form_submit_button("Add Task")
            if submitted:
                if title.strip():
                    add_task(create_task(title, description, deadline))
                    st.success("Task added ✅")
                    # reload data in-memory
                    data = load_data()
                    tasks = data.get("tasks", [])
                else:
                    st.error("Please provide a title for the task.")

    # Filter tasks by sidebar filter
    if filter_status == "Completed":
        displayed_tasks = [t for t in tasks if t.get("completed")]
    elif filter_status == "Pending":
        displayed_tasks = [t for t in tasks if not t.get("completed")]
    else:
        displayed_tasks = tasks

    # Sorting options
    sort_by = st.selectbox("Sort by", ["Deadline (soonest)", "Created (newest)", "Title (A-Z)"])
    if sort_by == "Deadline (soonest)":
        def key_deadline(t): 
            try:
                return datetime.fromisoformat(t["deadline"]) if t.get("deadline") else datetime.max
            except Exception:
                return datetime.max
        displayed_tasks.sort(key=key_deadline)
    elif sort_by == "Created (newest)":
        displayed_tasks.sort(key=lambda t: datetime.fromisoformat(t["created_at"]) if t.get("created_at") else datetime.min, reverse=True)
    else:
        displayed_tasks.sort(key=lambda t: t.get("title","").lower())

    # Display tasks
    st.markdown("### Tasks")
    if not displayed_tasks:
        st.info("No tasks found — add some using the form above.")
    else:
        for t in displayed_tasks:
            with st.container():
                st.markdown("<div class='card'>", unsafe_allow_html=True)
                c1, c2 = st.columns([8, 2])
                with c1:
                    title_line = t.get("title", "")
                    if t.get("completed"):
                        title_line = f"~~{title_line}~~"
                    st.markdown(f"**{title_line}**")
                    st.markdown(f"<div class='muted small'>Due: {format_date_iso(t.get('deadline'))}</div>", unsafe_allow_html=True)
                    st.write(t.get("description", ""))
                with c2:
                    # Buttons/controls for each task
                    if st.button("Edit", key=f"edit_{t['id']}"):
                        st.session_state["editing_task"] = t["id"]
                    if st.button("Delete", key=f"del_{t['id']}"):
                        delete_task(t["id"])
                        st.experimental_rerun()
                    if st.checkbox("Completed", value=t.get("completed", False), key=f"chk_{t['id']}"):
                        if not t.get("completed"):
                            update_task(t["id"], completed=True)
                            st.experimental_rerun()
                    else:
                        if t.get("completed"):
                            update_task(t["id"], completed=False)
                            st.experimental_rerun()
                st.markdown("</div>", unsafe_allow_html=True)

    # Inline edit panel
    if "editing_task" in st.session_state:
        etid = st.session_state["editing_task"]
        etask = next((x for x in tasks if x["id"] == etid), None)
        if etask:
            st.markdown("---")
            st.subheader("Edit Task")
            with st.form("edit_task_form"):
                new_title = st.text_input("Title", value=etask.get("title", ""))
                new_deadline = st.date_input("Deadline", value=datetime.fromisoformat(etask["deadline"]).date() if etask.get("deadline") else date.today())
                new_desc = st.text_area("Description", value=etask.get("description", ""))
                new_completed = st.checkbox("Completed", value=etask.get("completed", False))
                save_btn = st.form_submit_button("Save changes")
                cancel_btn = st.form_submit_button("Cancel")
                if save_btn:
                    update_task(etid, title=new_title, description=new_desc, deadline=new_deadline.isoformat(), completed=new_completed)
                    st.success("Task updated.")
                    del st.session_state["editing_task"]
                    st.experimental_rerun()
                if cancel_btn:
                    del st.session_state["editing_task"]
                    st.experimental_rerun()

# -----------------------
# Habit Tracker Tab
# -----------------------
if tab == "Habit Tracker":
    st.header("Habit Tracker")

    # Add habit form
    with st.expander("Add a new habit", expanded=False):
        with st.form("add_habit_form", clear_on_submit=True):
            name = st.text_input("Habit name", placeholder="e.g. Read 30 minutes")
            desc = st.text_area("Description (optional)", height=80)
            submitted = st.form_submit_button("Add Habit")
            if submitted:
                if name.strip():
                    add_habit(create_habit(name, desc))
                    st.success("Habit added ✅")
                    data = load_data()
                    habits = data.get("habits", [])
                else:
                    st.error("Habit must have a name.")

    # Week selector (view past weeks if desired)
    week_offset = st.selectbox("Week view", ["This week", "Last week", "2 weeks ago"], index=0)
    offset_days = {"This week": 0, "Last week": 7, "2 weeks ago": 14}
    ref_date = date.today() - timedelta(days=offset_days[week_offset])
    week_dates = get_week_dates(ref_date)

    st.markdown(f"**Week:** {week_dates[0].strftime('%b %d')} — {week_dates[-1].strftime('%b %d')}")
    # Table header
    header_cols = st.columns([3] + [1]*7)
    header_cols[0].markdown("**Habit**")
    for i, d in enumerate(week_dates):
        header_cols[i+1].markdown(f"**{WEEKDAYS[d.weekday()]}<br><div class='muted small'>{d.day}</div>**", unsafe_allow_html=True)

    # Habit rows
    if not habits:
        st.info("No habits yet. Add one to start tracking daily progress.")
    else:
        for h in habits:
            row_cols = st.columns([3] + [1]*7)
            name_col = row_cols[0]
            name_col.markdown(f"**{h['name']}**")
            name_col.markdown(f"<div class='muted small'>{h.get('description','')}</div>", unsafe_allow_html=True)
            # Render checkboxes for each day in the selected week
            for i, d in enumerate(week_dates):
                iso = d.isoformat()
                done = iso in h.get("log", [])
                # Allow marking only for current week and current day (optional: make all days toggleable)
                # We'll allow toggling for any visible day but prefer to guide marking for current day.
                if row_cols[i+1].checkbox("", value=done, key=f"{h['id']}_{iso}"):
                    if not done:
                        toggle_habit_for_date(h["id"], iso, True)
                        st.experimental_rerun()
                else:
                    if done:
                        toggle_habit_for_date(h["id"], iso, False)
                        st.experimental_rerun()

            # Small controls for habit: edit / delete / streak / weekly %
            control_cols = st.columns([1,1,1,4])
            with control_cols[0]:
                if st.button("Edit", key=f"edit_h_{h['id']}"):
                    st.session_state["editing_habit"] = h["id"]
            with control_cols[1]:
                if st.button("Delete", key=f"del_h_{h['id']}"):
                    delete_habit(h["id"])
                    st.experimental_rerun()
            with control_cols[2]:
                st.markdown(f"**Streak:** {current_streak(h)}d")
            with control_cols[3]:
                st.markdown(f"**Week:** {weekly_completion_for_habit(h, ref_date)}%")

    # Edit habit panel
    if "editing_habit" in st.session_state:
        hid = st.session_state["editing_habit"]
        habit = next((x for x in habits if x["id"] == hid), None)
        if habit:
            st.markdown("---")
            st.subheader("Edit Habit")
            with st.form("edit_habit_form"):
                n = st.text_input("Name", value=habit.get("name", ""))
                d = st.text_area("Description", value=habit.get("description", ""))
                save = st.form_submit_button("Save")
                cancel = st.form_submit_button("Cancel")
                if save:
                    update_habit(hid, name=n, description=d)
                    st.success("Habit updated.")
                    del st.session_state["editing_habit"]
                    st.experimental_rerun()
                if cancel:
                    del st.session_state["editing_habit"]
                    st.experimental_rerun()

# -----------------------
# Settings Tab
# -----------------------
if tab == "Settings":
    st.header("Settings")
    st.write("Manage app storage and preferences.")
    st.write(f"Data file: `{os.path.abspath(DATA_FILE)}`")
    if st.button("Backup data to backup_data.json"):
        data = load_data()
        with open("backup_data.json", "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        st.success("Backup saved as backup_data.json")
    if st.button("Reset all data (DELETE!)"):
        if st.confirm("Are you sure? This will delete all tasks & habits permanently."):
            save_data({"tasks": [], "habits": []})
            st.success("Data reset.")
            st.experimental_rerun()

# -----------------------
# Footer / small tips
# -----------------------
st.markdown("---")
st.markdown("<div class='muted small'>Tips: Use the sidebar Quick Add to add items quickly. Mark habits daily to build a streak. This app saves data to a file named <code>app_data.json</code> in the same folder.</div>", unsafe_allow_html=True)
