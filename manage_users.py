"""
Script para gestionar usuarios OPERADORES
Permite: agregar, eliminar, listar y cambiar contraseñas
Ejecutar: python manage_users.py
"""

from app import create_app, db
from app.models.models import User, Vehicle, MonthlyClient, Attendance

def listar_usuarios():
    """Muestra todos los usuarios del sistema"""
    users = User.query.order_by(User.role.desc(), User.username).all()
    
    if not users:
        print("\n⚠️  No hay usuarios en el sistema")
        return []
    
    print("\n📋 USUARIOS EN EL SISTEMA:")
    print("=" * 70)
    
    # Separar por rol
    admins = [u for u in users if u.role == 'admin']
    operators = [u for u in users if u.role == 'operador']
    
    if admins:
        print("\n🔐 ADMINISTRADORES:")
        for user in admins:
            print(f"   {user.username:15} | {user.name}")
    
    if operators:
        print("\n👥 OPERADORES:")
        for idx, user in enumerate(operators, 1):
            print(f"   {idx}. {user.username:15} | {user.name}")
    
    print("=" * 70)
    return operators

def agregar_operador():
    """Agrega un nuevo operador"""
    print("\n➕ AGREGAR NUEVO OPERADOR")
    print("=" * 70)
    
    # Pedir datos
    username = input("\nNombre de usuario: ").strip().lower()
    
    if not username:
        print("❌ El nombre de usuario no puede estar vacío")
        return
    
    # Verificar si ya existe
    existing = User.query.filter_by(username=username).first()
    if existing:
        print(f"❌ El usuario '{username}' ya existe")
        return
    
    name = input("Nombre completo: ").strip()
    if not name:
        print("❌ El nombre completo no puede estar vacío")
        return
    
    password = input("Contraseña (dejar vacío para usar '1234'): ").strip()
    if not password:
        password = "1234"
    
    # Confirmar
    print(f"\n📝 RESUMEN:")
    print(f"   Usuario:    {username}")
    print(f"   Nombre:     {name}")
    print(f"   Contraseña: {password}")
    print(f"   Rol:        OPERADOR")
    
    confirmar = input("\n¿Crear este usuario? (SI/no): ").strip().upper()
    
    if confirmar not in ['SI', 'S', '']:
        print("❌ Operación cancelada")
        return
    
    try:
        # Crear usuario
        user = User(
            username=username,
            name=name,
            role='operador'
        )
        user.set_password(password)
        db.session.add(user)
        db.session.commit()
        
        print(f"\n✅ Operador '{username}' creado exitosamente")
        print(f"   Puede iniciar sesión con: {username} / {password}")
        
    except Exception as e:
        db.session.rollback()
        print(f"\n❌ Error al crear usuario: {e}")

def eliminar_operador():
    """Elimina un operador existente"""
    print("\n🗑️  ELIMINAR OPERADOR")
    print("=" * 70)
    
    operators = [u for u in User.query.filter_by(role='operador').all()]
    
    if not operators:
        print("\n⚠️  No hay operadores para eliminar")
        return
    
    print("\nSeleccione el operador a eliminar:")
    for idx, user in enumerate(operators, 1):
        print(f"   {idx}. {user.username:15} | {user.name}")
    
    print(f"   0. Cancelar")
    
    try:
        opcion = int(input("\nOpción: ").strip())
        
        if opcion == 0:
            print("❌ Operación cancelada")
            return
        
        if opcion < 1 or opcion > len(operators):
            print("❌ Opción inválida")
            return
        
        user_to_delete = operators[opcion - 1]
        
        # Verificar si tiene registros asociados
        vehicles_count = Vehicle.query.filter(
            (Vehicle.operator_name == user_to_delete.username) | 
            (Vehicle.exit_operator_name == user_to_delete.username)
        ).count()
        
        monthly_count = MonthlyClient.query.filter_by(
            registered_by=user_to_delete.username
        ).count()
        
        attendance_count = Attendance.query.filter_by(
            user_id=user_to_delete.id
        ).count()
        
        # Mostrar advertencia si tiene registros
        print(f"\n⚠️  ADVERTENCIA:")
        print(f"   Usuario: {user_to_delete.username} ({user_to_delete.name})")
        
        if vehicles_count > 0 or monthly_count > 0 or attendance_count > 0:
            print(f"\n   Este usuario tiene registros asociados:")
            if vehicles_count > 0:
                print(f"   🚗 {vehicles_count} registros de vehículos")
            if monthly_count > 0:
                print(f"   💳 {monthly_count} clientes mensuales")
            if attendance_count > 0:
                print(f"   ⏰ {attendance_count} registros de asistencia")
            print(f"\n   Al eliminar el usuario, estos registros quedarán sin operador")
        else:
            print(f"   Este usuario no tiene registros asociados")
        
        confirmar = input(f"\n¿Eliminar '{user_to_delete.username}'? Escriba 'ELIMINAR': ").strip().upper()
        
        if confirmar != 'ELIMINAR':
            print("❌ Operación cancelada")
            return
        
        # Eliminar usuario
        db.session.delete(user_to_delete)
        db.session.commit()
        
        print(f"\n✅ Operador '{user_to_delete.username}' eliminado exitosamente")
        
    except ValueError:
        print("❌ Debe ingresar un número")
    except Exception as e:
        db.session.rollback()
        print(f"\n❌ Error al eliminar usuario: {e}")

def cambiar_contrasena():
    """Cambia la contraseña de un operador"""
    print("\n🔑 CAMBIAR CONTRASEÑA")
    print("=" * 70)
    
    operators = [u for u in User.query.filter_by(role='operador').all()]
    
    if not operators:
        print("\n⚠️  No hay operadores en el sistema")
        return
    
    print("\nSeleccione el operador:")
    for idx, user in enumerate(operators, 1):
        print(f"   {idx}. {user.username:15} | {user.name}")
    
    print(f"   0. Cancelar")
    
    try:
        opcion = int(input("\nOpción: ").strip())
        
        if opcion == 0:
            print("❌ Operación cancelada")
            return
        
        if opcion < 1 or opcion > len(operators):
            print("❌ Opción inválida")
            return
        
        user = operators[opcion - 1]
        
        print(f"\nUsuario seleccionado: {user.username} ({user.name})")
        
        nueva_password = input("Nueva contraseña: ").strip()
        
        if not nueva_password:
            print("❌ La contraseña no puede estar vacía")
            return
        
        confirmar_password = input("Confirmar contraseña: ").strip()
        
        if nueva_password != confirmar_password:
            print("❌ Las contraseñas no coinciden")
            return
        
        # Cambiar contraseña
        user.set_password(nueva_password)
        db.session.commit()
        
        print(f"\n✅ Contraseña cambiada exitosamente")
        print(f"   {user.username} puede iniciar sesión con la nueva contraseña")
        
    except ValueError:
        print("❌ Debe ingresar un número")
    except Exception as e:
        db.session.rollback()
        print(f"\n❌ Error al cambiar contraseña: {e}")

def mostrar_menu():
    """Muestra el menú principal"""
    print("\n" + "=" * 70)
    print("🔧 GESTIÓN DE OPERADORES")
    print("=" * 70)
    print("\n1. Listar todos los usuarios")
    print("2. Agregar nuevo operador")
    print("3. Eliminar operador")
    print("4. Cambiar contraseña de operador")
    print("0. Salir")
    print()

def main():
    """Función principal"""
    app = create_app()
    
    with app.app_context():
        while True:
            mostrar_menu()
            
            try:
                opcion = input("Seleccione una opción: ").strip()
                
                if opcion == '0':
                    print("\n👋 ¡Hasta luego!")
                    break
                
                elif opcion == '1':
                    listar_usuarios()
                    input("\nPresione ENTER para continuar...")
                
                elif opcion == '2':
                    agregar_operador()
                    input("\nPresione ENTER para continuar...")
                
                elif opcion == '3':
                    eliminar_operador()
                    input("\nPresione ENTER para continuar...")
                
                elif opcion == '4':
                    cambiar_contrasena()
                    input("\nPresione ENTER para continuar...")
                
                else:
                    print("\n❌ Opción inválida")
                    input("\nPresione ENTER para continuar...")
            
            except KeyboardInterrupt:
                print("\n\n👋 ¡Hasta luego!")
                break
            except Exception as e:
                print(f"\n❌ Error inesperado: {e}")
                input("\nPresione ENTER para continuar...")

if __name__ == '__main__':
    print("\n" + "=" * 70)
    print("👥 GESTIÓN DE USUARIOS OPERADORES")
    print("=" * 70)
    
    main()