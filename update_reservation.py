from app import db, app
from sqlalchemy import inspect, text

with app.app_context():
    inspector = inspect(db.engine)

    if 'user' not in [col['name'] for col in inspector.get_columns('reservation')]:
        with db.engine.connect() as conn:
            conn.execute(text("ALTER TABLE reservation ADD COLUMN user TEXT"))
            conn.commit()
        print("Added 'user' column to Reservation table.")
    else:
        print("'user' column already exists.")
