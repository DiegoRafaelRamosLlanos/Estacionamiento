from flask import Blueprint, render_template, request, jsonify, current_app, flash, redirect, url_for
from flask_login import login_required, current_user
from app.models.models import Vehicle, MonthlyClient, User, Attendance
from app import db
import qrcode
from datetime import datetime
import os
import io
import base64
from flask import send_file, abort
from datetime import datetime, timedelta
from functools import wraps
from flask import abort

main = Blueprint('main', __name__)

@main.route('/')
@login_required
def index():
    return render_template('index.html')

@main.route('/entry')
@login_required
def entry_page():
    return render_template('entry.html')

@main.route('/exit')
@login_required
def exit_page():
    return render_template('exit.html')

@main.route('/monthly')
@login_required
def monthly_page():
    clients = MonthlyClient.query.all()
    return render_template('monthly.html', clients=clients)

@main.route('/status')
@login_required
def status_page():
    active_vehicles = Vehicle.query.filter_by(exit_time=None).all()
    return render_template('status.html', vehicles=active_vehicles, now=datetime.now())

@main.route('/vehicle/entry', methods=['POST'])
@login_required
def vehicle_entry():
    try:
        plate = request.form.get('plate').upper().strip()
        vehicle_type = request.form.get('type')
        
        # Verificar si es cliente mensual
        monthly_client = MonthlyClient.query.filter_by(plate=plate).first()
        
        if monthly_client:
            # Verificar si está vencido
            if monthly_client.is_expired():
                return jsonify({
                    'success': False,
                    'message': 'El abono mensual ha vencido. Por favor, renovar.'
                }), 400
            
            is_monthly = True
        else:
            is_monthly = False
        
        # Crear registro de vehículo
        vehicle = Vehicle(
            plate=plate,
            type=vehicle_type,
            is_monthly=is_monthly,
            operator_name=current_user.username
        )
        
        db.session.add(vehicle)
        db.session.commit()
        
        # Generar QR en memoria
        qr = qrcode.QRCode(version=1, box_size=10, border=4)
        qr.add_data(str(vehicle.id))
        qr.make(fit=True)
        
        img = qr.make_image(fill_color="black", back_color="white")
        
        # Convertir a base64
        buffer = io.BytesIO()
        img.save(buffer, format='PNG')
        buffer.seek(0)
        img_base64 = base64.b64encode(buffer.getvalue()).decode()
        
        vehicle.qr_code = img_base64
        db.session.commit()
        
        return jsonify({
            'success': True,
            'vehicle_id': vehicle.id,
            'qr_code': img_base64,
            'is_monthly': is_monthly,
            'plate': vehicle.plate,
            'entry_time': vehicle.entry_time.strftime('%H:%M:%S')
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'message': str(e)
        }), 500

#
@main.route('/vehicle/exit', methods=['POST'])
@login_required
def vehicle_exit():
    try:
        vehicle_id = request.form.get('vehicle_id')
        
        if not vehicle_id:
            # Buscar por patente si no hay ID
            plate = request.form.get('plate', '').upper().strip()
            if plate:
                vehicle = Vehicle.query.filter_by(
                    plate=plate,
                    exit_time=None
                ).first()
            else:
                return jsonify({
                    'success': False,
                    'message': 'Debe proporcionar un ID o patente'
                }), 400
        else:
            vehicle = Vehicle.query.get(vehicle_id)
        
        if not vehicle:
            return jsonify({
                'success': False,
                'message': 'Vehículo no encontrado'
            }), 404
        
        if vehicle.exit_time:
            return jsonify({
                'success': False,
                'message': 'El vehículo ya ha salido'
            }), 400
        
        # Registrar salida
        vehicle.exit_time = datetime.now()
        vehicle.exit_operator_name = current_user.username
        
        # Calcular tarifa si no es cliente mensual
        cost = 0
        hours_decimal = 0
        
        if not vehicle.is_monthly:
            time_diff = vehicle.exit_time - vehicle.entry_time
            total_minutes = time_diff.total_seconds() / 60
            hours_decimal = total_minutes / 60
            
            # ⭐ NUEVO CÁLCULO: CADA 15 MINUTOS
            # Tarifas según tipo
            if vehicle.type == 'auto':
                first_hour_rate = 500
                quarter_hour_rate = 125  # $500 / 4 = $125 cada 15 min
            else:  # moto
                first_hour_rate = 300
                quarter_hour_rate = 75   # $300 / 4 = $75 cada 15 min
            
            # Cálculo: primera hora completa + cuartos de hora adicionales
            if total_minutes <= 60:
                cost = first_hour_rate
            else:
                cost = first_hour_rate
                remaining_minutes = total_minutes - 60
                # Calcular cuartos de hora (redondear hacia arriba)
                quarter_hours = int(remaining_minutes / 15)
                if remaining_minutes % 15 > 0:
                    quarter_hours += 1
                cost += quarter_hours * quarter_hour_rate
        
        vehicle.total_cost = cost
        db.session.commit()
        
        return jsonify({
            'success': True,
            'vehicle': {
                'id': vehicle.id,
                'plate': vehicle.plate,
                'type': vehicle.type,
                'entry_time': vehicle.entry_time.strftime('%Y-%m-%d %H:%M:%S'),
                'exit_time': vehicle.exit_time.strftime('%Y-%m-%d %H:%M:%S'),
                'hours': round(hours_decimal, 2),
                'cost': cost,
                'is_monthly': vehicle.is_monthly,
                'operator': vehicle.operator_name,
                'exit_operator': vehicle.exit_operator_name
            }
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'message': str(e)
        }), 500

@main.route('/monthly/add', methods=['POST'])
@login_required
def add_monthly_client():
    try:
        plate = request.form.get('plate').upper().strip()
        owner_name = request.form.get('owner_name', '').strip()
        model = request.form.get('model')
        phone = request.form.get('phone')
        vehicle_type = request.form.get('type')
        start_date = datetime.strptime(request.form.get('start_date'), '%Y-%m-%d')
        duration_months = int(request.form.get('duration_months', 1))
        
        if not owner_name:
            return jsonify({
                'success': False,
                'message': 'El nombre del titular es obligatorio'
            }), 400
        
        existing = MonthlyClient.query.filter_by(plate=plate).first()
        if existing:
            return jsonify({
                'success': False,
                'message': 'Ya existe un cliente mensual con esta patente'
            }), 400
        
        client = MonthlyClient(
            plate=plate,
            owner_name=owner_name,
            model=model,
            phone=phone,
            vehicle_type=vehicle_type,
            start_date=start_date,
            duration_months=duration_months,
            registered_by=current_user.username  # ⭐ AGREGAR ESTA LÍNEA
        )
        
        db.session.add(client)
        db.session.commit()
        
        duration_text = client.get_duration_text()
        expiration = client.get_expiration_date()
        
        return jsonify({
            'success': True,
            'message': f'Cliente mensual registrado correctamente.\n' + 
                      f'Titular: {owner_name}\n' +
                      f'Abono de {duration_text} válido hasta {expiration.strftime("%d/%m/%Y")}\n' +
                      f'Registrado por: {current_user.username}'  # ⭐ AGREGAR ESTO
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'message': str(e)
        }), 500

@main.route('/monthly/renew/<int:id>', methods=['POST'])
@login_required
def renew_monthly_client(id):
    """
    Ruta para renovar (vencidos) o extender (activos) abonos mensuales
    """
    try:
        client = MonthlyClient.query.get_or_404(id)
        duration_months_to_add = int(request.form.get('duration_months', 1))
        
        if client.is_expired():
            # ============================================
            # CASO 1: RENOVAR (Cliente VENCIDO)
            # ============================================
            # Reiniciar completamente desde hoy
            client.start_date = datetime.now()
            client.duration_months = duration_months_to_add
            
            expiration = client.get_expiration_date()
            duration_text = client.get_duration_text()
            
            db.session.commit()
            
            return jsonify({
                'success': True,
                'message': f'✅ Abono RENOVADO exitosamente.\n' + 
                          f'Duración: {duration_text}\n' +
                          f'Válido hasta: {expiration.strftime("%d/%m/%Y")}'
            })
        else:
            # ============================================
            # CASO 2: EXTENDER (Cliente ACTIVO)
            # ============================================
            # Sumar la duración manteniendo la fecha de inicio original
            
            # Duración actual en meses
            current_duration = client.duration_months
            
            # Nueva duración total = actual + lo que se agrega
            new_total_duration = current_duration + duration_months_to_add
            
            # Actualizar
            client.duration_months = new_total_duration
            
            # Obtener nueva fecha de vencimiento
            expiration = client.get_expiration_date()
            
            # Textos para el mensaje
            added_text = f"{duration_months_to_add} {'mes' if duration_months_to_add == 1 else 'meses'}"
            total_text = client.get_duration_text()
            
            # Calcular días para mostrar
            total_days = new_total_duration * 30
            added_days = duration_months_to_add * 30
            
            db.session.commit()
            
            return jsonify({
                'success': True,
                'message': f'✅ Abono EXTENDIDO exitosamente.\n' +
                          f'Se agregaron: {added_text} ({added_days} días)\n' +
                          f'Duración total: {total_text} ({total_days} días)\n' +
                          f'Nuevo vencimiento: {expiration.strftime("%d/%m/%Y")}'
            })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'message': f'Error: {str(e)}'
        }), 500

@main.route('/monthly/delete/<int:id>', methods=['POST'])
@login_required
def delete_monthly_client(id):
    try:
        client = MonthlyClient.query.get_or_404(id)
        db.session.delete(client)
        db.session.commit()
        
        flash('Cliente mensual eliminado correctamente', 'success')
        return redirect(url_for('main.monthly_page'))
        
    except Exception as e:
        db.session.rollback()
        flash(f'Error al eliminar cliente: {str(e)}', 'error')
        return redirect(url_for('main.monthly_page'))

@main.route('/monthly/edit/<int:id>', methods=['GET', 'POST'])
@login_required
def edit_monthly_client(id):
    """Editar datos de un cliente mensual (solo admins)"""
    if current_user.role != 'admin':
        flash('Acceso denegado. Solo administradores pueden editar clientes.', 'danger')
        return redirect(url_for('main.monthly_page'))
    
    client = MonthlyClient.query.get_or_404(id)
    
    if request.method == 'POST':
        try:
            # Obtener datos del formulario
            new_plate = request.form.get('plate').upper().strip()
            owner_name = request.form.get('owner_name', '').strip()
            model = request.form.get('model')
            phone = request.form.get('phone')
            vehicle_type = request.form.get('type')
            
            if not owner_name:
                return jsonify({
                    'success': False,
                    'message': 'El nombre del titular es obligatorio'
                }), 400
            
            # Verificar si la nueva patente ya existe (si cambió)
            if new_plate != client.plate:
                existing = MonthlyClient.query.filter_by(plate=new_plate).first()
                if existing:
                    return jsonify({
                        'success': False,
                        'message': f'Ya existe un cliente con la patente {new_plate}'
                    }), 400
            
            # Actualizar datos
            client.plate = new_plate
            client.owner_name = owner_name
            client.model = model
            client.phone = phone
            client.vehicle_type = vehicle_type
            
            db.session.commit()
            
            return jsonify({
                'success': True,
                'message': f'Cliente actualizado correctamente.\n' +
                          f'Patente: {new_plate}\n' +
                          f'Titular: {owner_name}'
            })
            
        except Exception as e:
            db.session.rollback()
            return jsonify({
                'success': False,
                'message': str(e)
            }), 500
    
    # GET: Retornar datos del cliente en formato JSON
    return jsonify({
        'id': client.id,
        'plate': client.plate,
        'owner_name': client.owner_name,
        'model': client.model,
        'phone': client.phone,
        'vehicle_type': client.vehicle_type
    })

@main.route('/reports')
@login_required
def reports_page():
    # Estadísticas del día
    today = datetime.now().date()
    today_vehicles = Vehicle.query.filter(
        db.func.date(Vehicle.entry_time) == today
    ).all()
    
    total_vehicles = len(today_vehicles)
    total_earnings = sum(v.total_cost or 0 for v in today_vehicles if v.exit_time)
    active_vehicles = len([v for v in today_vehicles if not v.exit_time])
    
    return render_template('reports.html', 
                         total_vehicles=total_vehicles,
                         total_earnings=total_earnings,
                         active_vehicles=active_vehicles,
                         vehicles=today_vehicles)

# ============================================
# RUTAS PARA PANEL DE AUDITORÍA
# ============================================

@main.route('/admin/audit')
@login_required
def audit_panel():
    """Panel de auditoría con acceso a reportes y backups"""
    return render_template('audit.html')

@main.route('/admin/reports/list')
@login_required
def list_reports():
    """Listar todos los reportes disponibles"""
    reports_dir = os.path.join(os.path.dirname(__file__), '..', 'reportes_diarios')
    
    if not os.path.exists(reports_dir):
        return jsonify({'reports': []})
    
    reports = []
    for file in os.listdir(reports_dir):
        if file.endswith(('.json', '.csv', '.txt')):
            file_path = os.path.join(reports_dir, file)
            file_stat = os.stat(file_path)
            
            reports.append({
                'filename': file,
                'size': file_stat.st_size,
                'created': datetime.fromtimestamp(file_stat.st_ctime).strftime('%Y-%m-%d %H:%M:%S'),
                'type': file.split('.')[-1].upper()
            })
    
    # Ordenar por fecha (más reciente primero)
    reports.sort(key=lambda x: x['created'], reverse=True)
    
    return jsonify({'reports': reports})

@main.route('/admin/reports/download/<filename>')
@login_required
def download_report(filename):
    """Descargar un reporte específico"""
    reports_dir = os.path.join(os.path.dirname(__file__), '..', 'reportes_diarios')
    file_path = os.path.join(reports_dir, filename)
    
    if not os.path.exists(file_path) or '..' in filename:
        abort(404)
    
    return send_file(file_path, as_attachment=True)

@main.route('/admin/backups/list')
@login_required
def list_backups():
    """Listar todos los backups disponibles"""
    backups_dir = os.path.join(os.path.dirname(__file__), '..', 'backups')
    
    if not os.path.exists(backups_dir):
        return jsonify({'backups': []})
    
    backups = []
    for root, dirs, files in os.walk(backups_dir):
        for file in files:
            if file.endswith('.db'):
                file_path = os.path.join(root, file)
                file_stat = os.stat(file_path)
                
                backups.append({
                    'filename': file,
                    'size': round(file_stat.st_size / (1024 * 1024), 2),  # MB
                    'created': datetime.fromtimestamp(file_stat.st_ctime).strftime('%Y-%m-%d %H:%M:%S'),
                    'path': os.path.relpath(file_path, backups_dir)
                })
    
    backups.sort(key=lambda x: x['created'], reverse=True)
    
    return jsonify({'backups': backups})

@main.route('/admin/audit/search', methods=['POST'])
@login_required
def audit_search():
    """Buscar transacciones específicas para auditoría"""
    start_date = request.form.get('start_date')
    end_date = request.form.get('end_date')
    plate = request.form.get('plate', '').upper().strip()
    operator = request.form.get('operator', '').strip()
    
    query = Vehicle.query
    
    if start_date:
        query = query.filter(Vehicle.entry_time >= datetime.strptime(start_date, '%Y-%m-%d'))
    
    if end_date:
        end_datetime = datetime.strptime(end_date, '%Y-%m-%d') + timedelta(days=1)
        query = query.filter(Vehicle.entry_time < end_datetime)
    
    if plate:
        query = query.filter(Vehicle.plate.like(f'%{plate}%'))
    
    if operator:
        query = query.filter(
            (Vehicle.operator_name.like(f'%{operator}%')) | 
            (Vehicle.exit_operator_name.like(f'%{operator}%'))
        )
    
    vehicles = query.order_by(Vehicle.entry_time.desc()).limit(100).all()
    
    results = []
    for v in vehicles:
        results.append({
            'id': v.id,
            'plate': v.plate,
            'type': v.type,
            'entry_time': v.entry_time.strftime('%Y-%m-%d %H:%M:%S'),
            'exit_time': v.exit_time.strftime('%Y-%m-%d %H:%M:%S') if v.exit_time else None,
            'cost': v.total_cost,
            'is_monthly': v.is_monthly,
            'operator': v.operator_name,
            'exit_operator': v.exit_operator_name
        })
    
    return jsonify({'results': results, 'count': len(results)})

@main.route('/admin/stats/summary')
@login_required
def stats_summary():
    """Estadísticas generales para el panel"""
    # Última semana
    week_ago = datetime.now() - timedelta(days=7)
    week_vehicles = Vehicle.query.filter(Vehicle.entry_time >= week_ago).all()
    
    # Último mes
    month_ago = datetime.now() - timedelta(days=30)
    month_vehicles = Vehicle.query.filter(Vehicle.entry_time >= month_ago).all()
    
    # Todo el tiempo
    total_vehicles = Vehicle.query.count()
    
    stats = {
        'ultima_semana': {
            'vehiculos': len(week_vehicles),
            'recaudacion': sum(v.total_cost or 0 for v in week_vehicles if v.exit_time)
        },
        'ultimo_mes': {
            'vehiculos': len(month_vehicles),
            'recaudacion': sum(v.total_cost or 0 for v in month_vehicles if v.exit_time)
        },
        'total': {
            'vehiculos': total_vehicles,
            'clientes_mensuales': MonthlyClient.query.count()
        }
    }
    
    return jsonify(stats)

# ============================================
# RUTAS PARA GESTIÓN DE HORARIOS (Solo Admin)
# ============================================
# AGREGAR ESTAS RUTAS AL FINAL DE app/routes.py


def admin_required(f):
    """Decorador para rutas que requieren rol admin"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or current_user.role != 'admin':
            flash('Acceso denegado. Solo administradores pueden acceder a esta sección.', 'danger')
            return redirect(url_for('main.index'))
        return f(*args, **kwargs)
    return decorated_function

@main.route('/admin/attendance')
@login_required
@admin_required
def attendance_panel():
    """Panel de control de asistencias"""
    # Asistencias del día actual
    today = datetime.now().date()
    today_attendances = Attendance.query.filter(
        db.func.date(Attendance.login_time) == today
    ).order_by(Attendance.login_time.desc()).all()
    
    # Usuarios actualmente trabajando
    active_users = Attendance.query.filter_by(logout_time=None).all()
    
    return render_template('attendance.html', 
                         today_attendances=today_attendances,
                         active_users=active_users,
                         now=datetime.now())

@main.route('/admin/attendance/history')
@login_required
@admin_required
def attendance_history():
    """Historial completo de asistencias"""
    # Parámetros de filtro
    user_id = request.args.get('user_id', type=int)
    start_date = request.args.get('start_date')
    end_date = request.args.get('end_date')
    
    query = Attendance.query
    
    # Aplicar filtros
    if user_id:
        query = query.filter_by(user_id=user_id)
    
    if start_date:
        query = query.filter(Attendance.login_time >= datetime.strptime(start_date, '%Y-%m-%d'))
    
    if end_date:
        end_datetime = datetime.strptime(end_date, '%Y-%m-%d') + timedelta(days=1)
        query = query.filter(Attendance.login_time < end_datetime)
    
    attendances = query.order_by(Attendance.login_time.desc()).limit(200).all()
    users = User.query.all()
    
    return render_template('attendance_history.html', 
                         attendances=attendances,
                         users=users,
                         now=datetime.now())

@main.route('/admin/attendance/report/<int:user_id>')
@login_required
@admin_required
def attendance_user_report(user_id):
    """Reporte de asistencia individual de un usuario"""
    user = User.query.get_or_404(user_id)
    
    # Parámetros de fecha
    start_date = request.args.get('start_date')
    end_date = request.args.get('end_date')
    
    # Por defecto: último mes
    if not start_date:
        start_date = (datetime.now() - timedelta(days=30)).strftime('%Y-%m-%d')
    if not end_date:
        end_date = datetime.now().strftime('%Y-%m-%d')
    
    query = Attendance.query.filter_by(user_id=user_id)
    query = query.filter(Attendance.login_time >= datetime.strptime(start_date, '%Y-%m-%d'))
    
    end_datetime = datetime.strptime(end_date, '%Y-%m-%d') + timedelta(days=1)
    query = query.filter(Attendance.login_time < end_datetime)
    
    attendances = query.order_by(Attendance.login_time.desc()).all()
    
    # Calcular estadísticas
    total_days = len(attendances)
    total_hours = sum(a.total_hours or 0 for a in attendances)
    avg_hours = total_hours / total_days if total_days > 0 else 0
    
    # Días con más/menos horas
    completed_attendances = [a for a in attendances if a.total_hours]
    max_hours_day = max(completed_attendances, key=lambda x: x.total_hours) if completed_attendances else None
    min_hours_day = min(completed_attendances, key=lambda x: x.total_hours) if completed_attendances else None
    
    stats = {
        'total_days': total_days,
        'total_hours': round(total_hours, 2),
        'avg_hours': round(avg_hours, 2),
        'max_hours_day': max_hours_day,
        'min_hours_day': min_hours_day
    }
    
    return render_template('attendance_user_report.html',
                         user=user,
                         attendances=attendances,
                         stats=stats,
                         start_date=start_date,
                         end_date=end_date)

@main.route('/admin/attendance/stats')
@login_required
@admin_required
def attendance_stats():
    """Estadísticas generales de asistencia"""
    # Semana actual
    today = datetime.now()
    week_start = today - timedelta(days=today.weekday())
    week_attendances = Attendance.query.filter(
        Attendance.login_time >= week_start
    ).all()
    
    # Mes actual
    month_start = today.replace(day=1)
    month_attendances = Attendance.query.filter(
        Attendance.login_time >= month_start
    ).all()
    
    # Todos los empleados con sus totales
    users = User.query.all()
    user_stats = []
    
    for user in users:
        month_user_attendances = [a for a in month_attendances if a.user_id == user.id]
        total_hours = sum(a.total_hours or 0 for a in month_user_attendances)
        total_days = len(month_user_attendances)
        
        user_stats.append({
            'user': user,
            'total_days': total_days,
            'total_hours': round(total_hours, 2),
            'avg_hours': round(total_hours / total_days, 2) if total_days > 0 else 0
        })
    
    # Ordenar por horas totales
    user_stats.sort(key=lambda x: x['total_hours'], reverse=True)
    
    return render_template('attendance_stats.html',
                         user_stats=user_stats,
                         week_start=week_start,
                         month_start=month_start)

@main.route('/admin/attendance/export')
@login_required
@admin_required
def attendance_export():
    """Exportar asistencias a CSV"""
    import csv
    from io import StringIO
    from flask import Response
    
    # Parámetros
    start_date = request.args.get('start_date')
    end_date = request.args.get('end_date')
    
    query = Attendance.query
    
    if start_date:
        query = query.filter(Attendance.login_time >= datetime.strptime(start_date, '%Y-%m-%d'))
    
    if end_date:
        end_datetime = datetime.strptime(end_date, '%Y-%m-%d') + timedelta(days=1)
        query = query.filter(Attendance.login_time < end_datetime)
    
    attendances = query.order_by(Attendance.login_time.desc()).all()
    
    # Crear CSV
    si = StringIO()
    writer = csv.writer(si)
    
    # Encabezados
    writer.writerow(['ID', 'Usuario', 'Nombre', 'Rol', 'Fecha', 'Hora Entrada', 
                    'Hora Salida', 'Horas Trabajadas', 'Estado'])
    
    # Datos
    for a in attendances:
        writer.writerow([
            a.id,
            a.user.username,
            a.user.name,
            a.user.role,
            a.login_time.strftime('%Y-%m-%d'),
            a.login_time.strftime('%H:%M:%S'),
            a.logout_time.strftime('%H:%M:%S') if a.logout_time else 'En curso',
            f"{a.total_hours:.2f}" if a.total_hours else '0.00',
            'Completado' if a.logout_time else 'Activo'
        ])
    
    # Preparar respuesta
    output = si.getvalue()
    si.close()
    
    filename = f"asistencias_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
    
    return Response(
        output,
        mimetype="text/csv",
        headers={"Content-Disposition": f"attachment;filename={filename}"}
    )
