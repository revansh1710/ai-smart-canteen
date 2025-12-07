from app import db, User, app

with app.app_context():
    admin_user = User.query.filter_by(username='admin').first()
    print("Admin user:", admin_user.username, "is_admin =", admin_user.is_admin)
