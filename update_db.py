from app import db, User, app
from sqlalchemy import inspect, text

with app.app_context():
    inspector = inspect(db.engine)

    # Check if 'is_admin' exists
    if 'is_admin' not in [col['name'] for col in inspector.get_columns('user')]:
        # Use connection context to run raw SQL
        with db.engine.connect() as conn:
            conn.execute(text('ALTER TABLE user ADD COLUMN is_admin BOOLEAN DEFAULT 0'))
            conn.commit()
        print("Added 'is_admin' column to User table.")
    else:
        print("'is_admin' column already exists.")

    # Ensure admin user exists
    if not User.query.filter_by(username='admin').first():
        admin = User(username='admin', password='admin123', is_admin=True)
        db.session.add(admin)
        db.session.commit()
        print("Admin user created.")
    else:
        print("Admin user already exists.")
