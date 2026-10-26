import streamlit as st
import pandas as pd
import sqlite3
import os
import uuid
import re
import hashlib
from datetime import date, time, datetime

st.set_page_config(page_title="UniNotify | CHRIST University", page_icon="🔔", layout="wide")
os.makedirs("posters", exist_ok=True)
db = sqlite3.connect("uninotify.db", check_same_thread=False)

# Database tables
db.execute("""CREATE TABLE IF NOT EXISTS events (
    id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT, category TEXT,
    department TEXT, event_date TEXT, event_time TEXT, venue TEXT,
    description TEXT, poster TEXT)""")
cols = [r[1] for r in db.execute("PRAGMA table_info(events)")]
if "poster" not in cols:
    db.execute("ALTER TABLE events ADD COLUMN poster TEXT")
db.execute("""CREATE TABLE IF NOT EXISTS reminders (
    event_id INTEGER PRIMARY KEY, reminder_time TEXT)""")
db.execute("""CREATE TABLE IF NOT EXISTS users (
    name TEXT, email TEXT PRIMARY KEY, phone TEXT, password TEXT)""")
db.commit()

# Login / Sign Up page (shown before the event portal)
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

if not st.session_state.logged_in:
    st.markdown("<h1 style='text-align:center;color:#003B71'>🔔 UniNotify</h1>", unsafe_allow_html=True)
    st.markdown("<p style='text-align:center'>University Event Management Portal</p>", unsafe_allow_html=True)
    _, form, _ = st.columns([1, 2, 1])

    with form:
        choice = st.radio("Welcome", ["Login", "Sign Up"], horizontal=True)

        if choice == "Sign Up":
            with st.form("signup"):
                name = st.text_input("Full Name")
                email = st.text_input("Email")
                phone = st.text_input("Phone Number")
                password = st.text_input("Password", type="password")
                confirm = st.text_input("Confirm Password", type="password")
                submit = st.form_submit_button("Create Account", use_container_width=True)

                if submit:
                    if not name.strip():
                        st.error("Enter your name.")
                    elif not re.fullmatch(r"[\w.+-]+@[\w-]+(?:\.[\w-]+)+", email.strip()):
                        st.error("Enter a valid email address.")
                    elif not re.fullmatch(r"(?:\+91[- ]?)?[6-9]\d{9}", phone.strip()):
                        st.error("Enter a valid Indian phone number.")
                    elif not re.fullmatch(r"(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[^A-Za-z0-9]).{8,}", password):
                        st.error("Password needs 8+ characters, uppercase, lowercase, a number and a special character.")
                    elif password != confirm:
                        st.error("Passwords do not match.")
                    else:
                        try:
                            db.execute("INSERT INTO users VALUES (?,?,?,?)", (
                                name.strip(), email.strip().lower(), phone.strip(),
                                hashlib.sha256(password.encode()).hexdigest()))
                            db.commit()
                            st.success("Account created! Select Login to continue.")
                        except sqlite3.IntegrityError:
                            st.error("This email is already registered.")
        else:
            with st.form("login"):
                email = st.text_input("Email")
                password = st.text_input("Password", type="password")
                submit = st.form_submit_button("Login", use_container_width=True)

                if submit:
                    user = db.execute(
                        "SELECT name FROM users WHERE email=? AND password=?",
                        (email.strip().lower(), hashlib.sha256(password.encode()).hexdigest())
                    ).fetchone()
                    if user:
                        st.session_state.logged_in = True
                        st.session_state.user_name = user[0]
                        st.rerun()
                    else:
                        st.error("Invalid email or password.")
    st.stop()

# Main portal styling
st.markdown("""
<style>
.stApp {background:#F5F8FC;color:#26364B}
.block-container {max-width:1400px;padding:2rem 3rem}
h1,h2,h3 {color:#003B71!important}
.header-title {color:#003B71;font-size:32px;font-weight:800}
.header-subtitle {color:#526780;font-size:12px;margin-top:8px}
div[data-testid="stMetric"] {background:white;border:1px solid #D9E3EF;
border-top:4px solid #003B71;border-radius:10px;padding:18px}
.stButton button,.stFormSubmitButton button {background:#003B71;color:white;
border-radius:7px;border:0}
</style>
""", unsafe_allow_html=True)

# Header and navigation
logo, brand, nav = st.columns([1.5, 2.5, 1.7], vertical_alignment="center", gap="large")
with logo:
    if os.path.exists("christ_logo.png"):
        st.image("christ_logo.png", width=230)
    else:
        st.markdown("### CHRIST University")
with brand:
    st.markdown('<div class="header-title">UniNotify</div><div class="header-subtitle">UNIVERSITY EVENT MANAGEMENT PORTAL</div>', unsafe_allow_html=True)
with nav:
    page = st.selectbox("NAVIGATION", ["Dashboard", "All Events", "Add Event", "Statistics", "Manage Events"])

st.sidebar.write(f"Welcome, {st.session_state.get('user_name', 'User')}")
if st.sidebar.button("Logout"):
    st.session_state.logged_in = False
    st.rerun()
st.divider()

def load_events():
    return pd.read_sql_query("SELECT * FROM events", db)

def show_event(e, student_view=False):
    with st.container(border=True):
        img, details = st.columns([1, 2], gap="large")
        with img:
            if pd.notna(e["poster"]) and e["poster"] and os.path.exists(e["poster"]):
                st.image(e["poster"], use_container_width=True)
            else:
                st.markdown("### 📅 University Event")
        with details:
            st.subheader(e["name"])
            st.caption(f"{e['category']} · {e['department']}")
            st.write(f"📅 {e['event_date']} · 🕒 {e['event_time']}")
            st.write(f"📍 {e['venue']}")
            if e["description"]:
                st.write(e["description"])

            if student_view:
                saved = db.execute("SELECT reminder_time FROM reminders WHERE event_id=?", (int(e["id"]),)).fetchone()
                if saved:
                    st.success(f"🔔 Reminder set for {saved[0]}")
                    if st.button("Remove Reminder", key=f"remove_{e['id']}"):
                        db.execute("DELETE FROM reminders WHERE event_id=?", (int(e["id"]),))
                        db.commit()
                        st.rerun()
                else:
                    with st.form(f"reminder_{e['id']}"):
                        reminder_date = st.date_input("Remind me on", value=date.today(), key=f"date_{e['id']}")
                        reminder_clock = st.time_input("Reminder time", value=time(9, 0), key=f"time_{e['id']}")
                        set_reminder = st.form_submit_button("🔔 Set Reminder")
                        if set_reminder:
                            reminder_dt = datetime.combine(reminder_date, reminder_clock)
                            event_dt = datetime.strptime(f"{e['event_date']} {e['event_time']}", "%Y-%m-%d %H:%M")
                            if reminder_dt >= event_dt:
                                st.error("Set the reminder before the event.")
                            elif reminder_dt <= datetime.now():
                                st.error("Choose a future reminder time.")
                            else:
                                db.execute("INSERT OR REPLACE INTO reminders VALUES (?, ?)",
                                           (int(e["id"]), reminder_dt.strftime("%Y-%m-%d %H:%M")))
                                db.commit()
                                st.success("Reminder saved!")
                                st.rerun()

events = load_events()
now = datetime.now()
if not events.empty:
    events["event_datetime"] = pd.to_datetime(events["event_date"] + " " + events["event_time"], errors="coerce")
    upcoming = events[events["event_datetime"] >= now].sort_values("event_datetime")
else:
    upcoming = events.copy()
    upcoming["event_datetime"] = pd.Series(dtype="datetime64[ns]")

# Dashboard
if page == "Dashboard":
    st.title("Dashboard")
    st.caption("Discover university events and manage your reminders.")
    reminder_count = db.execute("SELECT COUNT(*) FROM reminders").fetchone()[0]
    a, b, c, d = st.columns(4)
    a.metric("Total Events", len(events))
    b.metric("Upcoming Events", len(upcoming))
    c.metric("Departments", events["department"].nunique() if not events.empty else 0)
    d.metric("My Saved Reminders", reminder_count)
    left, right = st.columns([1.7, 1], gap="large")
    with left:
        st.subheader("Upcoming Events")
        if upcoming.empty:
            st.info("No upcoming events.")
        else:
            for _, e in upcoming.head(5).iterrows():
                show_event(e)
    with right:
        st.subheader("My Reminders")
        saved = db.execute("""SELECT events.name, reminders.reminder_time
            FROM reminders JOIN events ON events.id=reminders.event_id
            ORDER BY reminders.reminder_time""").fetchall()
        if not saved:
            st.info("You haven't set any reminders yet.")
        else:
            for name, reminder_time in saved:
                st.write(f"🔔 **{name}**")
                st.caption(f"Reminder: {reminder_time}")

# All Events
elif page == "All Events":
    st.title("All University Events")
    search = st.text_input("🔍 Search Events", placeholder="Search name, venue, department or category...")
    if events.empty:
        st.info("No events available yet.")
    else:
        result = events.copy()
        if search.strip():
            cols = ["name", "venue", "department", "category"]
            mask = result[cols].fillna("").apply(lambda col: col.str.contains(search.strip(), case=False, regex=False)).any(axis=1)
            result = result[mask]
        st.caption(f"{len(result)} event(s) found")
        for _, e in result.iterrows():
            show_event(e, student_view=True)

# Add Event
elif page == "Add Event":
    st.title("Add University Event")
    with st.form("add_event", clear_on_submit=True):
        name = st.text_input("Event Name")
        c1, c2 = st.columns(2)
        with c1:
            category = st.selectbox("Category", ["Academic", "Sports", "Cultural", "Technical", "Workshop", "Seminar", "Other"])
            department = st.text_input("Department")
            event_date = st.date_input("Event Date", min_value=date.today())
        with c2:
            venue = st.text_input("Venue")
            event_time = st.time_input("Event Time", value=time(10, 0))
        description = st.text_area("Description")
        poster = st.file_uploader("Upload Event Poster", type=["png", "jpg", "jpeg", "webp"])
        submitted = st.form_submit_button("Add Event")
        if submitted:
            if name.strip() and department.strip() and venue.strip():
                poster_path = None
                if poster:
                    ext = poster.name.rsplit(".", 1)[-1].lower()
                    poster_path = f"posters/{uuid.uuid4().hex}.{ext}"
                    with open(poster_path, "wb") as f:
                        f.write(poster.getbuffer())
                db.execute("""INSERT INTO events
                    (name,category,department,event_date,event_time,venue,description,poster)
                    VALUES (?,?,?,?,?,?,?,?)""",
                    (name.strip(), category, department.strip(), event_date.isoformat(),
                     event_time.strftime("%H:%M"), venue.strip(), description.strip(), poster_path))
                db.commit()
                st.success("Event added successfully!")
                st.rerun()
            else:
                st.error("Enter the event name, department and venue.")

# Edit and Delete Events
elif page == "Manage Events":
    st.title("Manage Events")
    st.caption("Edit event details or delete an event permanently.")
    if events.empty:
        st.info("There are no events to manage.")
    else:
        categories = ["Academic", "Sports", "Cultural", "Technical", "Workshop", "Seminar", "Other"]
        for _, e in events.iterrows():
            with st.container(border=True):
                st.subheader(e["name"])
                st.caption(f"{e['event_date']} · {e['venue']}")
                col1, col2 = st.columns(2)
                with col1:
                    with st.expander("✏️ Edit Event"):
                        with st.form(f"edit_{e['id']}"):
                            name = st.text_input("Event Name", value=e["name"] or "")
                            current = e["category"] if e["category"] in categories else "Other"
                            category = st.selectbox("Category", categories, index=categories.index(current))
                            department = st.text_input("Department", value=e["department"] or "")
                            venue = st.text_input("Venue", value=e["venue"] or "")
                            event_date = st.date_input("Event Date", value=date.fromisoformat(e["event_date"]))
                            event_time = st.time_input("Event Time", value=time.fromisoformat(e["event_time"]))
                            description = st.text_area("Description", value=e["description"] or "")
                            poster = st.file_uploader("Replace Poster (optional)", type=["png", "jpg", "jpeg", "webp"], key=f"poster_{e['id']}")
                            update = st.form_submit_button("Save Changes")
                            if update:
                                if name.strip() and department.strip() and venue.strip():
                                    poster_path = e["poster"]
                                    if poster:
                                        ext = poster.name.rsplit(".", 1)[-1].lower()
                                        poster_path = f"posters/{uuid.uuid4().hex}.{ext}"
                                        with open(poster_path, "wb") as f:
                                            f.write(poster.getbuffer())
                                    db.execute("""UPDATE events SET name=?,category=?,department=?,
                                        event_date=?,event_time=?,venue=?,description=?,poster=? WHERE id=?""",
                                        (name.strip(), category, department.strip(), event_date.isoformat(),
                                         event_time.strftime("%H:%M"), venue.strip(), description.strip(),
                                         poster_path, int(e["id"])))
                                    db.commit()
                                    if poster and e["poster"] and os.path.exists(e["poster"]):
                                        os.remove(e["poster"])
                                    st.success("Event updated successfully!")
                                    st.rerun()
                                else:
                                    st.error("Enter the event name, department and venue.")
                with col2:
                    if st.button("🗑️ Delete Event", key=f"delete_{e['id']}"):
                        db.execute("DELETE FROM reminders WHERE event_id=?", (int(e["id"]),))
                        db.execute("DELETE FROM events WHERE id=?", (int(e["id"]),))
                        if pd.notna(e["poster"]) and e["poster"] and os.path.exists(e["poster"]):
                            os.remove(e["poster"])
                        db.commit()
                        st.success("Event deleted successfully!")
                        st.rerun()

# Statistics
elif page == "Statistics":
    st.title("Event Statistics")
    if events.empty:
        st.info("Statistics will appear when events are added.")
    else:
        a, b, c = st.columns(3)
        a.metric("Total Events", len(events))
        b.metric("Categories", events["category"].nunique())
        c.metric("Saved Reminders", db.execute("SELECT COUNT(*) FROM reminders").fetchone()[0])
        st.subheader("Events by Category")
        st.bar_chart(events["category"].value_counts())
        st.subheader("Events Over Time")
        trend = events.copy()
        trend["event_date"] = pd.to_datetime(trend["event_date"], errors="coerce")
        trend = trend.dropna(subset=["event_date"])
        if not trend.empty:
            trend["Date"] = trend["event_date"].dt.strftime("%Y-%m-%d")
            st.line_chart(trend.groupby("Date").size().sort_index())

# Do not close db here: Streamlit reruns this script on interactions.
