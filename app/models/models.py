from datetime import datetime
from app import db
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin
from app import login_manager

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), unique=True, nullable=False)
    password_hash = db.Column(db.String(128))
    
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

class Vehicle(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    plate = db.Column(db.String(10), nullable=False)
    type = db.Column(db.String(10), nullable=False)  # 'car' or 'motorcycle'
    entry_time = db.Column(db.DateTime, default=datetime.utcnow)
    exit_time = db.Column(db.DateTime)
    qr_code = db.Column(db.String(200))
    is_monthly = db.Column(db.Boolean, default=False)

class MonthlyClient(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    plate = db.Column(db.String(10), nullable=False, unique=True)
    model = db.Column(db.String(50))
    phone = db.Column(db.String(20))
    expiration_date = db.Column(db.DateTime, nullable=False)
    vehicle_type = db.Column(db.String(10), nullable=False)  # 'car' or 'motorcycle'

@login_manager.user_loader
def load_user(id):
    return User.query.get(int(id))