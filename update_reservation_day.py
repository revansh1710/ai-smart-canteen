from app import db, app
from sqlalchemy import inspect, text

with app.app_context():
    inspector = inspect(db.engine)
    columns = [col['name'] for col in inspector.get_columns('reservation')]

    if 'day' not in columns:
        with db.engine.connect() as conn:
            conn.execute(text("ALTER TABLE reservation ADD COLUMN day INTEGER"))
            conn.commit()
        print("Added 'day' column to Reservation table.")
    else:
        print("'day' column already exists.")
