# sport_management

Sports League Manager — a Flask + MySQL web app for running a sports league:
user accounts, teams, players, fixtures, events/tournaments and a dashboard.

## Features

- Register / login (Flask-Login, hashed passwords)
- Teams: add, edit, view roster, delete (owner or admin)
- Players: add, delete, assign to teams
- Events (tournaments/seasons): add, edit, view, delete
- Fixtures: schedule matches between two teams, optionally linked to an event
- Dashboard with teams, players, upcoming fixtures and events

## Tech stack

Python 3 · Flask 3 · Flask-SQLAlchemy / SQLAlchemy 2 · Flask-Login · PyMySQL · MySQL 8

## Setup

1. Create the database and a dedicated MySQL user (run as a MySQL admin):

   ```sql
   CREATE DATABASE IF NOT EXISTS sports_league_manager CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
   CREATE USER IF NOT EXISTS 'sportsuser'@'localhost' IDENTIFIED BY 'your-db-password';
   GRANT ALL PRIVILEGES ON sports_league_manager.* TO 'sportsuser'@'localhost';
   FLUSH PRIVILEGES;
   ```

2. Create a virtual environment and install dependencies:

   ```bash
   python -m venv venv
   venv\Scripts\activate        # Windows  (Linux/macOS: source venv/bin/activate)
   pip install -r requirements.txt
   ```

3. Copy `.env.example` to `.env` and fill in your values
   (URL-encode special characters in `DB_PASS`, e.g. `@` → `%40`).

4. Run the app (tables are created automatically on first start):

   ```bash
   python run.py
   ```

   Open http://127.0.0.1:5000 and register an account.

`sportsDB.sql` contains the equivalent MySQL schema if you prefer to create the tables manually.
