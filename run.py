from app import create_app
from models import db

app = create_app()

# Create any missing tables on startup (no-op for tables that already exist),
# so `python run.py` and `flask run` work on a fresh database.
with app.app_context():
    db.create_all()

if __name__ == '__main__':
    app.run(debug=True)
