# 🔔 UniNotify – University Event Management Portal

UniNotify is a web-based university event management application built using Python and Streamlit. It helps students discover upcoming university events, view event details, and manage personal reminders through a simple interface.

## ✨ Features

- **Dashboard:** View total events, upcoming events, departments, and saved reminders.
- **Login & Sign Up:** Register and log in with email, phone number, and password validation.
- **Event Management:** Add, edit, and delete university events.
- **Event Posters:** Upload and update event posters.
- **Search Events:** Search by event name, venue, department, or category.
- **Personal Reminders:** Set or remove reminders for upcoming events.
- **Event Statistics:** View events by category and event dates.
- **SQLite Database:** Store event details, reminders, and user accounts locally.

## 🛠️ Technologies Used

- Python
- Streamlit
- Pandas
- SQLite
- Regular Expressions (Regex)
- HTML and CSS
- Git and GitHub

## 📋 Requirements

- Python 3.9 or later
- pip

## 🚀 Installation and Setup

### 1. Clone the repository

```bash
git clone https://github.com/MAYANKSHARMA006/UniNotify.git
cd UniNotify
```

### 2. Install dependencies

```bash
pip install -r requirements.txt
```

### 3. Run the application

```bash
streamlit run uninotify.py
```

### 4. Open the application

Streamlit will provide a local URL, usually:

```text
http://localhost:8501
```

Open the URL in your browser to access UniNotify.

## 📁 Project Structure

```text
UniNotify/
├── uninotify.py       # Main application
├── requirements.txt   # Python dependencies
├── christ_logo.png    # University logo
├── posters/           # Event poster images
├── .gitignore         # Files excluded from Git
└── README.md          # Project documentation
```

The SQLite database (`uninotify.db`) is created locally when the application runs and is excluded from Git.

## 🔐 Validation

The registration page validates:
- Email address format using regular expressions.
- Indian phone number format.
- Password length of at least 8 characters.
- Uppercase and lowercase letters, a number, and a special character.
- Password confirmation.

## 🎯 Purpose

UniNotify aims to make university event information easier to access by bringing event discovery, event management, and reminders together in one platform.

## 🔮 Future Improvements

- Email or push notifications for reminders.
- Department-based event filtering.
- Role-based access for administrators and students.
- Cloud database integration.
- Deployment for access from anywhere.

## 👨‍💻 Author

**Mayank Sharma**

Bachelor of Computer Applications (BCA)  
CHRIST (Deemed to be University), Pune Lavasa Campus

---

*Developed as a university project to simplify event discovery and reminder management.*
