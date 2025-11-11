"""
Script para limpiar SOLO las tablas Attendance y Vehicle
Mantiene intactos: Users y MonthlyClient
Ejecutar: python clean_tables.py
"""

from app import create_app, db
from app.models.models import User, Vehicle, MonthlyClient, Attendance

def mostrar_resumen():
    """Muestra un resumen conciso de lo que se va a hacer"""
    # Contar registros
    total_users = User.query.count()
    total_monthly = MonthlyClient.query.count()
    total_vehicles = Vehicle.query.count()
    total_attendance = Attendance.query.count()
    
    print("\n📊 RESUMEN:")
    print("=" * 60)
    print(f"\n✅ SE MANTENDRÁN:")
    print(f"   👥 Usuarios:           {total_users} registros")
    print(f"   💳 Clientes Mensuales: {total_monthly} registros")
    
    print(f"\n❌ SE ELIMINARÁN:")
    print(f"   🚗 Vehículos:          {total_vehicles} registros")
    print(f"   ⏰ Asistencias:        {total_attendance} registros")
    print("\n" + "=" * 60)
    
    return {
        'users': total_users,
        'monthly': total_monthly,
        'vehicles': total_vehicles,
        'attendance': total_attendance
    }

def confirmar_limpieza():
    """Solicita confirmación antes de proceder"""
    print("\n⚠️  ADVERTENCIA:")
    print("Esta acción eliminará PERMANENTEMENTE los registros de:")
    print("  ❌ Vehículos (ingresos/salidas)")
    print("  ❌ Asistencias del personal")
    print()
    print("Se mantendrán:")
    print("  ✅ Usuarios")
    print("  ✅ Clientes mensuales")
    print()
    
    respuesta = input("¿Confirmar? Escriba 'SI' en mayúsculas: ").strip()
    
    return respuesta == "SI"

def limpiar_tablas():
    """Ejecuta la limpieza de las tablas"""
    app = create_app()
    
    with app.app_context():
        print("\n" + "=" * 60)
        print("🧹 LIMPIEZA DE TABLAS: Vehicle y Attendance")
        print("=" * 60)
        
        # Mostrar resumen
        stats = mostrar_resumen()
        
        # Si no hay nada que borrar
        if stats['vehicles'] == 0 and stats['attendance'] == 0:
            print("\nℹ️  No hay registros para eliminar")
            print("   Las tablas Vehicle y Attendance ya están vacías")
            return
        
        # Pedir confirmación
        if not confirmar_limpieza():
            print("\n❌ Operación cancelada")
            return
        
        print("\n🔄 Limpiando...")
        
        try:
            # Borrar registros
            deleted_vehicles = Vehicle.query.delete()
            deleted_attendance = Attendance.query.delete()
            
            # Confirmar cambios
            db.session.commit()
            
            print("\n✅ LIMPIEZA COMPLETADA")
            print(f"   🚗 Eliminados: {deleted_vehicles} vehículos")
            print(f"   ⏰ Eliminados: {deleted_attendance} asistencias")
            print(f"   👥 Mantenidos: {stats['users']} usuarios")
            print(f"   💳 Mantenidos: {stats['monthly']} clientes")
            print()
            
        except Exception as e:
            db.session.rollback()
            print(f"\n❌ ERROR: {e}")
            print("   Se revirtieron todos los cambios")

if __name__ == '__main__':
    print("\n" + "=" * 60)
    print("🗑️  LIMPIEZA: Vehicle y Attendance")
    print("=" * 60)
    
    limpiar_tablas()