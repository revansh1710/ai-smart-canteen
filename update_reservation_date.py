from app import db, app
from sqlalchemy import inspect, text
from datetime import datetime

with app.app_context():
    inspector = inspect(db.engine)

    if 'date' not in [col['name'] for col in inspector.get_columns('reservation')]:
        with db.engine.connect() as conn:
            conn.execute(text("ALTER TABLE reservation ADD COLUMN date TEXT"))
            conn.commit()
        print("Added 'date' column to Reservation table.")
    else:
        print("'date' column already exists.")
