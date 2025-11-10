"""
Script para agregar la tabla Attendance a la base de datos existente
Ejecutar: python migrate_add_attendance.py
"""

from app import create_app, db
from app.models.models import Attendance, User
from datetime import datetime

def migrate_add_attendance():
    app = create_app()
    
    with app.app_context():
        print("\n" + "="*70)
        print("🔄 MIGRACIÓN: AGREGAR SISTEMA DE CONTROL DE HORARIOS")
        print("="*70 + "\n")
        
        # Crear la tabla Attendance
        print("📋 Creando tabla 'attendance'...")
        try:
            db.create_all()
            print("✅ Tabla 'attendance' creada exitosamente")
        except Exception as e:
            print(f"⚠️  Posible error (puede ser normal si ya existe): {e}")
        
        # Verificar que la tabla existe
        from sqlalchemy import inspect
        inspector = inspect(db.engine)
        tables = inspector.get_table_names()
        
        if 'attendance' in tables:
            print("✅ Tabla 'attendance' confirmada en la base de datos")
            
            # Mostrar estructura
            columns = inspector.get_columns('attendance')
            print("\n📊 Estructura de la tabla 'attendance':")
            for col in columns:
                print(f"  - {col['name']:20} : {col['type']}")
        else:
            print("❌ ERROR: No se pudo crear la tabla 'attendance'")
            return
        
        # Verificar usuarios
        print("\n" + "="*70)
        print("👥 USUARIOS DISPONIBLES")
        print("="*70)
        
        users = User.query.all()
        if users:
            print(f"\nTotal: {len(users)} usuario(s)\n")
            for user in users:
                role_text = "ADMIN" if user.role == 'admin' else "OPERADOR"
                print(f"  {user.username:15} | {user.name:25} | {role_text}")
        else:
            print("\n⚠️  No hay usuarios en la base de datos")
            print("Ejecute: python init_db.py")
        
        # Verificar registros de asistencia
        attendance_count = Attendance.query.count()
        print(f"\n📝 Registros de asistencia actuales: {attendance_count}")
        
        if attendance_count > 0:
            print("\nÚltimas asistencias registradas:")
            recent = Attendance.query.order_by(Attendance.login_time.desc()).limit(5).all()
            for a in recent:
                status = "ACTIVO" if a.is_active() else "FINALIZADO"
                print(f"  {a.user.username:15} | {a.login_time.strftime('%d/%m/%Y %H:%M')} | {status}")
        
        print("\n" + "="*70)
        print("✅ MIGRACIÓN COMPLETADA")
        print("="*70)
        
        print("\n💡 PRÓXIMOS PASOS:")
        print("   1. Reemplazar app/models/models.py con el nuevo código")
        print("   2. Reemplazar app/auth.py con el nuevo código")
        print("   3. Agregar las nuevas rutas al final de app/routes.py")
        print("   4. Crear el archivo app/templates/attendance.html")
        print("   5. Actualizar el menú en app/templates/base.html")
        print("   6. Reiniciar: python run.py")
        
        print("\n🔐 FUNCIONALIDADES NUEVAS:")
        print("   - Registro automático de entrada al hacer login")
        print("   - Registro automático de salida al hacer logout")
        print("   - Panel de control de asistencias (solo admin)")
        print("   - Historial completo de horarios")
        print("   - Estadísticas por empleado")
        print("   - Exportación a CSV")
        
        print("\n📍 ACCESO:")
        print("   Solo usuarios ADMIN pueden ver:")
        print("   - http://localhost:8080/admin/attendance")
        print("   - Menu: Admin → Control de Horarios")
        
        print("\n" + "="*70 + "\n")

if __name__ == '__main__':
    migrate_add_attendance()