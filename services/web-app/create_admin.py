# create_admin.py
from app.app import create_app
from app.models import User
from app.extensions import db

app, socketio = create_app()

with app.app_context():
    if User.query.filter_by(account='admin').first():
        print("Admin user already exists.")
    else:
        admin_user = User(account='admin', is_admin=True, is_staff=True)
        admin_user.set_password('admin')
        db.session.add(admin_user)
        db.session.commit()
        print("Admin user 'admin' with password 'admin' created successfully.")
