"""
Script para inicializar la base de datos y crear usuarios
Ejecutar: python init_db.py
"""

from app import create_app, db
from app.models.models import User, Vehicle, MonthlyClient
from datetime import datetime, timedelta

def init_database():
    app = create_app()
    
    with app.app_context():
        # Eliminar todas las tablas y recrearlas
        print("Eliminando tablas existentes...")
        db.drop_all()
        
        print("Creando nuevas tablas...")
        db.create_all()
        
        # Crear usuarios operadores
        print("Creando usuarios operadores...")
        operators = [
            {'username': 'operador1', 'password': '1234', 'name': 'Juan Pérez', 'role': 'operador'},
            {'username': 'operador2', 'password': '1234', 'name': 'María García', 'role': 'operador'},
            {'username': 'operador3', 'password': '1234', 'name': 'Carlos López', 'role': 'operador'},
            {'username': 'operador4', 'password': '1234', 'name': 'Ana Martínez', 'role': 'operador'},
        ]
        
        for user_data in operators:
            user = User(
                username=user_data['username'], 
                name=user_data['name'],
                role=user_data['role']
            )
            user.set_password(user_data['password'])
            db.session.add(user)
            print(f"  ✓ Operador creado: {user_data['username']}")
        
        # Crear usuarios administradores
        print("\nCreando usuarios administradores...")
        admins = [
            {'username': 'admin1', 'password': 'admin123', 'name': 'Supervisor General', 'role': 'admin'},
            {'username': 'admin2', 'password': 'admin123', 'name': 'Gerente de Operaciones', 'role': 'admin'},
        ]
        
        for admin_data in admins:
            admin = User(
                username=admin_data['username'],
                name=admin_data['name'],
                role=admin_data['role']
            )
            admin.set_password(admin_data['password'])
            db.session.add(admin)
            print(f"  ✓ Administrador creado: {admin_data['username']}")
        
        # Guardar usuarios primero
        db.session.commit()
        
        # Crear algunos clientes mensuales de ejemplo
        print("\nCreando clientes mensuales de ejemplo...")
        today = datetime.now()
        
        monthly_clients = [
            {
                'plate': 'ABC123',
                'model': 'Toyota Corolla 2020',
                'phone': '3815551234',
                'vehicle_type': 'auto',
                'start_date': today - timedelta(days=10)  # Iniciado hace 10 días
            },
            {
                'plate': 'XYZ789',
                'model': 'Honda CG 150',
                'phone': '3815555678',
                'vehicle_type': 'moto',
                'start_date': today - timedelta(days=25)  # Iniciado hace 25 días (por vencer)
            },
            {
                'plate': 'DEF456',
                'model': 'Ford Focus 2019',
                'phone': '3815559999',
                'vehicle_type': 'auto',
                'start_date': today  # Iniciado hoy
            },
        ]
        
        for client_data in monthly_clients:
            client = MonthlyClient(**client_data)
            db.session.add(client)
            days_remaining = client.days_remaining()
            expiration = client.get_expiration_date()
            print(f"  ✓ Cliente mensual creado: {client_data['plate']} (vence: {expiration.strftime('%d/%m/%Y')}, {days_remaining} días restantes)")
        
        # Guardar cambios finales
        db.session.commit()
        
        print("\n✅ Base de datos inicializada correctamente!")
        print("\n" + "="*70)
        print("📋 CREDENCIALES DE ACCESO")
        print("="*70)
        
        print("\n👥 OPERADORES:")
        for op in operators:
            print(f"  Usuario: {op['username']:15} | Contraseña: {op['password']:10} | {op['name']}")
        
        print("\n🔐 ADMINISTRADORES:")
        for adm in admins:
            print(f"  Usuario: {adm['username']:15} | Contraseña: {adm['password']:10} | {adm['name']}")
        
        print("\n💳 CLIENTES MENSUALES DE EJEMPLO:")
        clients = MonthlyClient.query.all()
        for client in clients:
            status = "✓ ACTIVO" if not client.is_expired() else "✗ VENCIDO"
            if client.days_remaining() <= 7 and not client.is_expired():
                status = "⚠ POR VENCER"
            print(f"  {client.plate:10} | Inicio: {client.start_date.strftime('%d/%m/%Y')} | Vence: {client.get_expiration_date().strftime('%d/%m/%Y')} | {status} ({client.days_remaining()} días)")
        
        print("\n" + "="*70)
        print("🚀 Puede iniciar la aplicación con: python run.py")
        print("="*70 + "\n")

if __name__ == '__main__':
    init_database()