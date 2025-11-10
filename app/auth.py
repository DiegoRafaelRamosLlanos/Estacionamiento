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
        # Verificar si tiene asistencia ACTIVA (sin logout)
        active_attendance = user.get_active_attendance()
        
        if active_attendance:
            # YA TIENE UNA SESIÓN ACTIVA
            login_time_str = active_attendance.login_time.strftime('%H:%M:%S')
            duration = active_attendance.get_duration_text()
            flash(f'✅ Sesión continuada - Entrada registrada a las {login_time_str}', 'info')
            flash(f'⏱️ Tiempo transcurrido: {duration}', 'info')
        else:
            # NO TIENE SESIÓN ACTIVA - Verificar si ya tiene registro HOY
            today_attendance = user.get_today_attendance()
            
            if today_attendance:
                # TIENE REGISTRO HOY PERO YA SALIÓ
                # Crear un NUEVO registro de entrada
                attendance = Attendance(
                    user_id=user.id,
                    login_time=datetime.now()
                )
                db.session.add(attendance)
                db.session.commit()
                
                login_time_str = attendance.login_time.strftime('%H:%M:%S')
                flash(f'✅ Nueva entrada registrada a las {login_time_str}', 'success')
                flash(f'ℹ️ Ya tenías un registro completado hoy', 'info')
            else:
                # PRIMER INGRESO DEL DÍA
                attendance = Attendance(
                    user_id=user.id,
                    login_time=datetime.now()
                )
                db.session.add(attendance)
                db.session.commit()
                
                login_time_str = attendance.login_time.strftime('%H:%M:%S')
                flash(f'✅ Asistencia registrada: Entrada a las {login_time_str}', 'success')
        
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
        hours_text = f"{active_attendance.total_hours:.2f}" if active_attendance.total_hours else "0.00"
        flash(f'⏱️ Asistencia finalizada. Tiempo trabajado: {duration} ({hours_text} horas)', 'info')
    else:
        # No tiene asistencia activa (caso raro)
        flash(f'ℹ️ Sesión cerrada (sin registro de asistencia activo)', 'info')
    
    logout_user()
    flash('Sesión cerrada correctamente', 'info')
    return redirect(url_for('auth.login'))