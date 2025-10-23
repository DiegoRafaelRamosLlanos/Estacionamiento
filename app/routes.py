from flask import Blueprint, render_template, request, jsonify, current_app, flash, redirect, url_for
from flask_login import login_required, current_user
from app.models.models import Vehicle, MonthlyClient
from app import db
import qrcode
from datetime import datetime
import os
import io
import base64
from flask import send_file, abort
from datetime import datetime, timedelta

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
            if monthly_client.expiration_date < datetime.now():
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
            
            # Calcular costo según tipo
            if vehicle.type == 'auto':
                first_hour_rate = 500
                half_hour_rate = 250
            else:  # moto
                first_hour_rate = 300
                half_hour_rate = 150
            
            # Cálculo: primera hora completa + medias horas adicionales
            if total_minutes <= 60:
                cost = first_hour_rate
            else:
                cost = first_hour_rate
                remaining_minutes = total_minutes - 60
                half_hours = int(remaining_minutes / 30)
                if remaining_minutes % 30 > 0:
                    half_hours += 1
                cost += half_hours * half_hour_rate
        
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
        model = request.form.get('model')
        phone = request.form.get('phone')
        vehicle_type = request.form.get('type')
        expiration_date = datetime.strptime(request.form.get('expiration_date'), '%Y-%m-%d')
        
        # Verificar si ya existe
        existing = MonthlyClient.query.filter_by(plate=plate).first()
        if existing:
            return jsonify({
                'success': False,
                'message': 'Ya existe un cliente mensual con esta patente'
            }), 400
        
        client = MonthlyClient(
            plate=plate,
            model=model,
            phone=phone,
            vehicle_type=vehicle_type,
            expiration_date=expiration_date
        )
        
        db.session.add(client)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'Cliente mensual registrado correctamente'
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'message': str(e)
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