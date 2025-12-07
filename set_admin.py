from app import db, User, app

with app.app_context():
    admin_user = User.query.filter_by(username='admin').first()
    if admin_user:
        admin_user.is_admin = True
        db.session.commit()
        print("Admin user updated to is_admin=True")
    else:
        print("Admin user not found")
