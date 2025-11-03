"""
Script para corregir/agregar roles a usuarios existentes
Ejecutar: python fix_database.py
"""

from app import create_app, db
from app.models.models import User
from sqlalchemy import inspect

def fix_database():
    app = create_app()
    
    with app.app_context():
        print("\n" + "="*70)
        print("VERIFICANDO ESTRUCTURA DE LA BASE DE DATOS")
        print("="*70)
        
        # Verificar si existe la columna 'role'
        inspector = inspect(db.engine)
        columns = [col['name'] for col in inspector.get_columns('user')]
        
        if 'role' not in columns:
            print("\n⚠️  La columna 'role' NO existe en la tabla User")
            print("Ejecute: python init_db.py para recrear la base de datos")
            return
        
        print("✅ La columna 'role' existe")
        
        # Verificar usuarios actuales
        print("\n" + "="*70)
        print("USUARIOS ACTUALES EN LA BASE DE DATOS")
        print("="*70)
        
        users = User.query.all()
        
        if not users:
            print("\n⚠️  No hay usuarios en la base de datos")
            print("Ejecute: python init_db.py")
            return
        
        for user in users:
            role = user.role if hasattr(user, 'role') else 'NO DEFINIDO'
            print(f"Usuario: {user.username:15} | Nombre: {user.name:25} | Rol: {role}")
        
        # Verificar si existen usuarios admin
        admins = User.query.filter_by(role='admin').all()
        
        if not admins:
            print("\n" + "="*70)
            print("⚠️  NO HAY USUARIOS ADMINISTRADORES")
            print("="*70)
            
            respuesta = input("\n¿Desea crear los usuarios admin1 y admin2? (s/n): ")
            
            if respuesta.lower() == 's':
                # Crear admin1
                admin1 = User(
                    username='admin1',
                    name='Supervisor General',
                    role='admin'
                )
                admin1.set_password('admin123')
                db.session.add(admin1)
                
                # Crear admin2
                admin2 = User(
                    username='admin2',
                    name='Gerente de Operaciones',
                    role='admin'
                )
                admin2.set_password('admin123')
                db.session.add(admin2)
                
                db.session.commit()
                
                print("\n✅ Usuarios administradores creados:")
                print("   - admin1 / admin123")
                print("   - admin2 / admin123")
        else:
            print(f"\n✅ Existen {len(admins)} usuario(s) administrador(es)")
        
        # Actualizar operadores sin rol
        print("\n" + "="*70)
        print("ACTUALIZANDO ROLES DE OPERADORES")
        print("="*70)
        
        operadores = User.query.filter(
            (User.role == None) | (User.role == '') | (User.role == 'operador')
        ).all()
        
        updated_count = 0
        for user in operadores:
            if not user.role or user.role == '':
                user.role = 'operador'
                updated_count += 1
                print(f"✓ Actualizado: {user.username} → 'operador'")
        
        if updated_count > 0:
            db.session.commit()
            print(f"\n✅ Se actualizaron {updated_count} usuario(s)")
        else:
            print("\n✅ Todos los operadores ya tienen rol asignado")
        
        # Resumen final
        print("\n" + "="*70)
        print("RESUMEN FINAL")
        print("="*70)
        
        total_users = User.query.count()
        total_admins = User.query.filter_by(role='admin').count()
        total_operators = User.query.filter_by(role='operador').count()
        
        print(f"\nTotal de usuarios:        {total_users}")
        print(f"Administradores:          {total_admins}")
        print(f"Operadores:               {total_operators}")
        
        if total_admins == 0:
            print("\n⚠️  ADVERTENCIA: No hay usuarios administradores!")
            print("Los reportes y auditoría no serán accesibles.")
        
        print("\n" + "="*70)
        print("CREDENCIALES DE ACCESO")
        print("="*70)
        
        print("\nADMINISTRADORES:")
        admins = User.query.filter_by(role='admin').all()
        for admin in admins:
            print(f"  {admin.username} / admin123 ({admin.name})")
        
        print("\nOPERADORES:")
        operators = User.query.filter_by(role='operador').all()
        for op in operators:
            print(f"  {op.username} / 1234 ({op.name})")
        
        print("\n" + "="*70 + "\n")

if __name__ == '__main__':
    fix_database()