from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_user, logout_user, login_required
from app.models.models import User
from app import db

auth = Blueprint('auth', __name__)

@auth.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        # Debug: Buscar usuario
        user = User.query.filter_by(username=username).first()
        
        if not user:
            flash(f'Usuario "{username}" no encontrado en el sistema', 'danger')
            return render_template('auth/login.html')
        
        # Debug: Verificar contraseña
        if not user.check_password(password):
            flash(f'Contraseña incorrecta para el usuario "{username}"', 'danger')
            return render_template('auth/login.html')
        
        # Login exitoso
        login_user(user)
        
        # Mostrar mensaje de bienvenida con rol
        role_text = "Administrador" if user.role == 'admin' else "Operador"
        flash(f'Bienvenido {user.name} ({role_text})', 'success')
        
        return redirect(url_for('main.index'))
    
    return render_template('auth/login.html')

@auth.route('/logout')
@login_required
def logout():
    logout_user()
    flash('Sesión cerrada correctamente', 'info')
    return redirect(url_for('auth.login'))