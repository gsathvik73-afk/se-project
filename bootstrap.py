from app import app
from smartexpense.database import initialize_database

with app.app_context():
    initialize_database()
print("SmartExpense schema ready.")
