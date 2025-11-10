from datetime import datetime, timedelta
from app import db
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin
from app import login_manager

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), unique=True, nullable=False)
    password_hash = db.Column(db.String(128))
    name = db.Column(db.String(100))
    role = db.Column(db.String(20), default='operador')  # 'operador' o 'admin'
    
    # Relación con asistencias
    attendances = db.relationship('Attendance', backref='user', lazy='dynamic')
    
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)
    
    def is_admin(self):
        """Verifica si el usuario tiene rol de administrador"""
        return self.role == 'admin'
    
    def is_operator(self):
        """Verifica si el usuario tiene rol de operador"""
        return self.role == 'operador'
    
    def get_active_attendance(self):
        """Obtiene la asistencia activa (sin hora de salida) del usuario"""
        return Attendance.query.filter_by(
            user_id=self.id,
            logout_time=None
        ).first()
    
    def get_today_attendance(self):
        """Obtiene la asistencia del día actual"""
        today = datetime.now().date()
        return Attendance.query.filter(
            Attendance.user_id == self.id,
            db.func.date(Attendance.login_time) == today
        ).first()

class Attendance(db.Model):
    """Registro de asistencia de empleados"""
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    login_time = db.Column(db.DateTime, nullable=False, default=datetime.now)
    logout_time = db.Column(db.DateTime, nullable=True)
    total_hours = db.Column(db.Float, nullable=True)  # Horas trabajadas
    notes = db.Column(db.String(200), nullable=True)  # Notas opcionales
    
    def calculate_hours(self):
        """Calcula las horas trabajadas"""
        if self.logout_time:
            diff = self.logout_time - self.login_time
            self.total_hours = diff.total_seconds() / 3600
            return self.total_hours
        return 0
    
    def get_duration_text(self):
        """Retorna duración en formato legible"""
        if not self.logout_time:
            # Calcular tiempo actual
            diff = datetime.now() - self.login_time
        else:
            diff = self.logout_time - self.login_time
        
        hours = int(diff.total_seconds() // 3600)
        minutes = int((diff.total_seconds() % 3600) // 60)
        
        if hours > 0:
            return f"{hours}h {minutes}m"
        else:
            return f"{minutes}m"
    
    def is_active(self):
        """Verifica si la asistencia está activa (sin logout)"""
        return self.logout_time is None
    
    def __repr__(self):
        return f'<Attendance {self.user.username} - {self.login_time}>'

class Vehicle(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    plate = db.Column(db.String(10), nullable=False)
    type = db.Column(db.String(10), nullable=False)  # 'auto' or 'moto'
    entry_time = db.Column(db.DateTime, default=datetime.now)
    exit_time = db.Column(db.DateTime, nullable=True)
    qr_code = db.Column(db.Text, nullable=True)  # Base64 del QR
    is_monthly = db.Column(db.Boolean, default=False)
    total_cost = db.Column(db.Float, default=0.0)
    operator_name = db.Column(db.String(64))  # Operador que registró ingreso
    exit_operator_name = db.Column(db.String(64))  # Operador que registró salida
    
    def __repr__(self):
        return f'<Vehicle {self.plate}>'

class MonthlyClient(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    plate = db.Column(db.String(10), nullable=False, unique=True)
    owner_name = db.Column(db.String(100), nullable=False)
    model = db.Column(db.String(50))
    phone = db.Column(db.String(20))
    start_date = db.Column(db.DateTime, nullable=False)
    duration_months = db.Column(db.Integer, default=1)
    vehicle_type = db.Column(db.String(10), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.now)
    registered_by = db.Column(db.String(64))
    
    def get_expiration_date(self):
        days = 30 * self.duration_months
        return self.start_date + timedelta(days=days)
    
    def is_expired(self):
        return self.get_expiration_date() < datetime.now()
    
    def days_remaining(self):
        expiration = self.get_expiration_date()
        remaining = (expiration - datetime.now()).days
        return max(0, remaining)
    
    def get_duration_text(self):
        if self.duration_months == 1:
            return "1 mes"
        elif self.duration_months == 3:
            return "3 meses"
        elif self.duration_months == 6:
            return "6 meses"
        elif self.duration_months == 12:
            return "1 año"
        else:
            return f"{self.duration_months} meses"
    
    def __repr__(self):
        return f'<MonthlyClient {self.plate} - {self.owner_name}>'

@login_manager.user_loader
def load_user(id):
    return User.query.get(int(id))