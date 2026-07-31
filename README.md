# PawPlan

A pet management application for pet owners to organize and track their pets' health, tasks, and daily activities.

## Overview

PawPlan is a web application built with Flet and Firebase. It allows users to:
- Create and manage multiple pet profiles
- Track pet health records and medication schedules
- Organize pet-related tasks and reminders
- Monitor pet wellness and activities

## Tech Stack

- Frontend: [Flet](https://flet.dev/) (v0.85.3+)
- Backend: Firebase Authentication & Firestore
- Language: Python (3.10+)
- Authentication: Firebase Admin SDK, OAuth 2.0

## Requirements

Dependencies are defined in:
- [`pyproject.toml`](./pyproject.toml)
- [`requirements.txt`](./requirements.txt)

## Installation

**Note: This section is for developers only. Users should use the live application URL below.**

### Prerequisites
- Python 3.10 or higher (>= 3.14 recommended)
- Git
- Firebase project credentials

### Setup

1. Clone the repository:
```bash
git clone <repository-url>
cd PawPlan
```

2. Create and activate virtual environment:
```bash
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Create `.env` file in project root:
```
FIREBASE_API_KEY=your_firebase_api_key
FIREBASE_WEB_API_KEY=your_firebase_web_api_key
GOOGLE_CLIENT_ID=your_google_client_id
GOOGLE_CLIENT_SECRET=your_google_client_secret
```

Obtain these from [Google Cloud Console](https://console.cloud.google.com) → PawPlan project → APIs & Services → Credentials.

5. Download and configure `pawplan_account.json`:
   - Go to Google Cloud Console → IAM & Admin → Service Accounts
   - Select the service account → Keys → Add Key → Create new key → JSON
   - Save as `pawplan_account.json` in project root
   - Add to `.gitignore` (contains sensitive data)

## How to Run

Local development:
```bash
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
flet run main.py
```

Application opens at `http://localhost:8550`

Web deployment:

Live URL: [https://pawplan-production-fbcb.up.railway.app](https://pawplan-production-fbcb.up.railway.app)

## Features

- Email/password and OAuth 2.0 authentication
- Create and manage multiple pet profiles
- Store pet details (name, breed, date of birth, gender)
- Create and manage pet-related tasks
- Set up reminders for medications and appointments
- Track pet wellness and activities
- User account profiles and settings
- Dark/Light theme support

## Project Structure

```
PawPlan/
├── main.py                    # Entry point
├── pyproject.toml            # Project configuration
├── requirements.txt          # Dependencies
├── views/                    # UI screens
│   ├── login.py
│   ├── register.py
│   ├── homepage.py
│   ├── petprofile.py
│   ├── pet_tasks.py
│   ├── taskboard.py
│   └── settings.py
├── model/                    # Business logic
│   ├── firestore_auth.py     # Authentication
│   ├── pet_crud.py           # Pet operations
│   └── task_crud.py          # Task operations
├── setup/                    # Configuration
│   └── firebase_setup.py
└── utility/                  # Helpers
    ├── navigation.py
    ├── theme.py
    └── logging_config.py
```

## Development

PyCharm setup:
- Alt+Cmd+S → Python Interpreter → Add interpreter
- Install Flet 0.85.0+ via package manager
- Delete `.idea` folder if interpreter issues occur

---

Version: 0.1.0 | Last Updated: July 2026
