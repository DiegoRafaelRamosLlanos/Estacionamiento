from flask import Blueprint, render_template, request, jsonify, current_app
from flask_login import login_required
from app.models.models import Vehicle, MonthlyClient
from app import db
import qrcode
from datetime import datetime
import os

main = Blueprint('main', __name__)

@main.route('/')
@login_required
def index():
    return render_template('index.html')

@main.route('/vehicle/entry', methods=['POST'])
@login_required
def vehicle_entry():
    plate = request.form.get('plate')
    vehicle_type = request.form.get('type')
    
    # Verificar si es cliente mensual
    monthly_client = MonthlyClient.query.filter_by(plate=plate).first()
    is_monthly = monthly_client is not None
    
    # Crear registro de vehículo
    vehicle = Vehicle(
        plate=plate,
        type=vehicle_type,
        is_monthly=is_monthly
    )
    
    # Generar QR
    qr = qrcode.QRCode(version=1, box_size=10, border=5)
    qr.add_data(str(vehicle.id))
    qr.make(fit=True)
    qr_image = qr.make_image(fill_color="black", back_color="white")
    
    # Guardar QR
    qr_path = f"app/static/qr/{vehicle.id}.png"
    qr_image.save(qr_path)
    vehicle.qr_code = f"qr/{vehicle.id}.png"
    
    db.session.add(vehicle)
    db.session.commit()
    
    return jsonify({
        'success': True,
        'vehicle_id': vehicle.id,
        'qr_code': vehicle.qr_code
    })

@main.route('/vehicle/exit', methods=['POST'])
@login_required
def vehicle_exit():
    vehicle_id = request.form.get('vehicle_id')
    vehicle = Vehicle.query.get_or_404(vehicle_id)
    
    if not vehicle.exit_time:
        vehicle.exit_time = datetime.utcnow()
        db.session.commit()
        
        # Calcular tarifa si no es cliente mensual
        if not vehicle.is_monthly:
            hours = (vehicle.exit_time - vehicle.entry_time).total_seconds() / 3600
            rate = calculate_rate(hours, vehicle.type)
        else:
            rate = 0
            
        return jsonify({
            'success': True,
            'hours': round(hours, 2),
            'rate': rate
        })
    
    return jsonify({'success': False, 'message': 'Vehicle already checked out'})

def calculate_rate(hours, vehicle_type):
    # Implementar cálculo de tarifa según tipo de vehículo y tiempo
    base_rate = 5.0 if vehicle_type == 'car' else 3.0  # Por hora
    total_hours = int(hours) + (1 if hours % 1 > 0.5 else 0.5)
    return base_rate * total_hours