# add_status_column.py
from app import app, db
from sqlalchemy import text

with app.app_context():
    with db.engine.connect() as conn:
        conn.execute(
            text("ALTER TABLE reservation ADD COLUMN status TEXT DEFAULT 'Pending';")
        )
        conn.commit()
    print("Column 'status' added successfully!")
