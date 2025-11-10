from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_user, logout_user, login_required, current_user
from app.models.models import User, Attendance
from app import db
from datetime import datetime

auth = Blueprint('auth', __name__)

@auth.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        # Buscar usuario
        user = User.query.filter_by(username=username).first()
        
        if not user:
            flash(f'Usuario "{username}" no encontrado en el sistema', 'danger')
            return render_template('auth/login.html')
        
        # Verificar contraseña
        if not user.check_password(password):
            flash(f'Contraseña incorrecta para el usuario "{username}"', 'danger')
            return render_template('auth/login.html')
        
        # Login exitoso
        login_user(user)
        
        # ⭐ REGISTRAR ASISTENCIA DE ENTRADA
        # Verificar si ya tiene asistencia activa hoy
        today_attendance = user.get_today_attendance()
        
        if not today_attendance:
            # Crear nuevo registro de asistencia
            attendance = Attendance(
                user_id=user.id,
                login_time=datetime.now()
            )
            db.session.add(attendance)
            db.session.commit()
            
            login_time_str = attendance.login_time.strftime('%H:%M:%S')
            flash(f'✅ Asistencia registrada: Entrada a las {login_time_str}', 'success')
        else:
            # Ya tiene asistencia registrada hoy
            login_time_str = today_attendance.login_time.strftime('%H:%M:%S')
            if today_attendance.is_active():
                flash(f'ℹ️ Sesión continuada (entrada registrada a las {login_time_str})', 'info')
            else:
                flash(f'ℹ️ Ya completaste tu jornada hoy (entrada: {login_time_str})', 'info')
        
        # Mensaje de bienvenida con rol
        role_text = "Administrador" if user.role == 'admin' else "Operador"
        flash(f'Bienvenido {user.name} ({role_text})', 'success')
        
        return redirect(url_for('main.index'))
    
    return render_template('auth/login.html')

@auth.route('/logout')
@login_required
def logout():
    # ⭐ REGISTRAR ASISTENCIA DE SALIDA
    active_attendance = current_user.get_active_attendance()
    
    if active_attendance:
        active_attendance.logout_time = datetime.now()
        active_attendance.calculate_hours()
        db.session.commit()
        
        duration = active_attendance.get_duration_text()
        flash(f'⏱️ Asistencia finalizada. Tiempo trabajado: {duration}', 'info')
    
    logout_user()
    flash('Sesión cerrada correctamente', 'info')
    return redirect(url_for('auth.login'))