"""
Script completo para gestionar TODOS los usuarios del sistema
Permite: agregar, eliminar, listar, cambiar contraseñas, cambiar roles
Ejecutar: python user_manager.py
"""

from app import create_app, db
from app.models.models import User, Vehicle, MonthlyClient, Attendance

def listar_usuarios():
    """Muestra todos los usuarios del sistema"""
    users = User.query.order_by(User.role.desc(), User.username).all()
    
    if not users:
        print("\n⚠️  No hay usuarios en el sistema")
        return []
    
    print("\n" + "="*80)
    print("📋 USUARIOS EN EL SISTEMA")
    print("="*80)
    
    # Separar por rol
    admins = [u for u in users if u.role == 'admin']
    operators = [u for u in users if u.role == 'operador']
    
    if admins:
        print("\n🔐 ADMINISTRADORES:")
        for idx, user in enumerate(admins, 1):
            print(f"   {idx}. {user.username:15} | {user.name:30} | admin")
    
    if operators:
        print("\n👥 OPERADORES:")
        for idx, user in enumerate(operators, 1):
            print(f"   {idx}. {user.username:15} | {user.name:30} | operador")
    
    print("\n" + "="*80)
    print(f"TOTAL: {len(users)} usuario(s) - {len(admins)} admin(s) - {len(operators)} operador(es)")
    print("="*80)
    
    return users

def agregar_usuario():
    """Agrega un nuevo administrador"""
    print("\n" + "="*80)
    print("➕ AGREGAR NUEVO ADMINISTRADOR")
    print("="*80)
    
    # Pedir datos básicos
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
    
    # Rol fijo: admin
    role = 'admin'
    role_text = 'ADMINISTRADOR'
    
    # Pedir contraseña
    password = input(f"\nContraseña (dejar vacío para 'admin123'): ").strip()
    if not password:
        password = "admin123"
    
    # Confirmar
    print("\n" + "="*80)
    print("📝 RESUMEN:")
    print("="*80)
    print(f"   Usuario:    {username}")
    print(f"   Nombre:     {name}")
    print(f"   Rol:        {role_text}")
    print(f"   Contraseña: {password}")
    print("="*80)
    
    confirmar = input("\n¿Crear este usuario? (SI/no): ").strip().upper()
    
    if confirmar not in ['SI', 'S', '']:
        print("❌ Operación cancelada")
        return
    
    try:
        # Crear usuario
        user = User(
            username=username,
            name=name,
            role=role
        )
        user.set_password(password)
        db.session.add(user)
        db.session.commit()
        
        print(f"\n✅ Usuario '{username}' creado exitosamente")
        print(f"   Credenciales: {username} / {password}")
        print(f"   Rol: {role_text}")
        
    except Exception as e:
        db.session.rollback()
        print(f"\n❌ Error al crear usuario: {e}")

def eliminar_usuario():
    """Elimina un usuario del sistema"""
    print("\n" + "="*80)
    print("🗑️  ELIMINAR USUARIO")
    print("="*80)
    
    users = User.query.order_by(User.role.desc(), User.username).all()
    
    if not users:
        print("\n⚠️  No hay usuarios para eliminar")
        return
    
    print("\nSeleccione el usuario a eliminar:")
    
    admins = [u for u in users if u.role == 'admin']
    operators = [u for u in users if u.role == 'operador']
    
    all_users = admins + operators
    
    for idx, user in enumerate(all_users, 1):
        role_badge = "🔐 ADMIN" if user.role == 'admin' else "👤 OPER"
        print(f"   {idx}. [{role_badge}] {user.username:15} | {user.name}")
    
    print(f"   0. Cancelar")
    
    try:
        opcion = int(input("\nOpción: ").strip())
        
        if opcion == 0:
            print("❌ Operación cancelada")
            return
        
        if opcion < 1 or opcion > len(all_users):
            print("❌ Opción inválida")
            return
        
        user_to_delete = all_users[opcion - 1]
        
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
        
        # Verificar si es el último admin
        if user_to_delete.role == 'admin':
            total_admins = User.query.filter_by(role='admin').count()
            if total_admins <= 1:
                print("\n❌ ERROR: No se puede eliminar el único administrador del sistema")
                print("   Cree otro administrador primero antes de eliminar este")
                return
        
        # Mostrar advertencia
        print("\n" + "="*80)
        print("⚠️  ADVERTENCIA:")
        print("="*80)
        print(f"   Usuario: {user_to_delete.username} ({user_to_delete.name})")
        print(f"   Rol: {'ADMINISTRADOR' if user_to_delete.role == 'admin' else 'OPERADOR'}")
        
        if vehicles_count > 0 or monthly_count > 0 or attendance_count > 0:
            print(f"\n   Este usuario tiene registros asociados:")
            if vehicles_count > 0:
                print(f"   🚗 {vehicles_count} registros de vehículos")
            if monthly_count > 0:
                print(f"   💳 {monthly_count} clientes mensuales")
            if attendance_count > 0:
                print(f"   ⏰ {attendance_count} registros de asistencia")
            print(f"\n   QUÉ SE ELIMINARÁ:")
            if attendance_count > 0:
                print(f"   ❌ Las {attendance_count} asistencias serán ELIMINADAS permanentemente")
            print(f"\n   QUÉ SE MANTENDRÁ:")
            if vehicles_count > 0:
                print(f"   ✓ Los {vehicles_count} registros de vehículos (con '{user_to_delete.username}' como operador)")
            if monthly_count > 0:
                print(f"   ✓ Los {monthly_count} clientes mensuales (con '{user_to_delete.username}' como registrador)")
            print(f"\n   ℹ️  Los registros históricos mantendrán el nombre del usuario eliminado")
        else:
            print(f"\n   ✅ Este usuario no tiene registros asociados")
        
        print("="*80)
        
        confirmar = input(f"\n¿Eliminar '{user_to_delete.username}'? Escriba 'ELIMINAR': ").strip().upper()
        
        if confirmar != 'ELIMINAR':
            print("❌ Operación cancelada")
            return
        
        # Eliminar asistencias primero (CASCADE)
        if attendance_count > 0:
            Attendance.query.filter_by(user_id=user_to_delete.id).delete()
            print(f"   ✓ Eliminadas {attendance_count} asistencias")
        
        # Eliminar usuario
        db.session.delete(user_to_delete)
        db.session.commit()
        
        print(f"\n✅ Usuario '{user_to_delete.username}' eliminado exitosamente")
        
        if vehicles_count > 0 or monthly_count > 0:
            print(f"\n📝 IMPORTANTE:")
            print(f"   Los registros de vehículos y clientes mensuales SE MANTIENEN")
            print(f"   con '{user_to_delete.username}' como operador (para historial)")
            print(f"   El usuario ya no podrá iniciar sesión, pero su nombre queda registrado")
        
    except ValueError:
        print("❌ Debe ingresar un número")
    except Exception as e:
        db.session.rollback()
        print(f"\n❌ Error al eliminar usuario: {e}")

def cambiar_contrasena():
    """Cambia la contraseña de un usuario"""
    print("\n" + "="*80)
    print("🔑 CAMBIAR CONTRASEÑA")
    print("="*80)
    
    users = User.query.order_by(User.role.desc(), User.username).all()
    
    if not users:
        print("\n⚠️  No hay usuarios en el sistema")
        return
    
    print("\nSeleccione el usuario:")
    
    for idx, user in enumerate(users, 1):
        role_badge = "🔐 ADMIN" if user.role == 'admin' else "👤 OPER"
        print(f"   {idx}. [{role_badge}] {user.username:15} | {user.name}")
    
    print(f"   0. Cancelar")
    
    try:
        opcion = int(input("\nOpción: ").strip())
        
        if opcion == 0:
            print("❌ Operación cancelada")
            return
        
        if opcion < 1 or opcion > len(users):
            print("❌ Opción inválida")
            return
        
        user = users[opcion - 1]
        
        print(f"\n" + "="*80)
        print(f"Usuario seleccionado: {user.username} ({user.name})")
        print(f"Rol: {'ADMINISTRADOR' if user.role == 'admin' else 'OPERADOR'}")
        print("="*80)
        
        nueva_password = input("\nNueva contraseña: ").strip()
        
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
        print(f"   {user.username} puede iniciar sesión con: {nueva_password}")
        
    except ValueError:
        print("❌ Debe ingresar un número")
    except Exception as e:
        db.session.rollback()
        print(f"\n❌ Error al cambiar contraseña: {e}")

def cambiar_rol():
    """Cambia el rol de un usuario (operador ↔ admin)"""
    print("\n" + "="*80)
    print("🔄 CAMBIAR ROL DE USUARIO")
    print("="*80)
    
    users = User.query.order_by(User.role.desc(), User.username).all()
    
    if not users:
        print("\n⚠️  No hay usuarios en el sistema")
        return
    
    print("\nSeleccione el usuario:")
    
    for idx, user in enumerate(users, 1):
        role_badge = "🔐 ADMIN" if user.role == 'admin' else "👤 OPER"
        print(f"   {idx}. [{role_badge}] {user.username:15} | {user.name}")
    
    print(f"   0. Cancelar")
    
    try:
        opcion = int(input("\nOpción: ").strip())
        
        if opcion == 0:
            print("❌ Operación cancelada")
            return
        
        if opcion < 1 or opcion > len(users):
            print("❌ Opción inválida")
            return
        
        user = users[opcion - 1]
        
        # Verificar si es el último admin y quiere convertirlo a operador
        if user.role == 'admin':
            total_admins = User.query.filter_by(role='admin').count()
            if total_admins <= 1:
                print("\n❌ ERROR: No se puede cambiar el rol del único administrador")
                print("   Cree otro administrador primero")
                return
        
        current_role = "ADMINISTRADOR" if user.role == 'admin' else "OPERADOR"
        new_role = "operador" if user.role == 'admin' else "admin"
        new_role_text = "OPERADOR" if user.role == 'admin' else "ADMINISTRADOR"
        
        print(f"\n" + "="*80)
        print(f"Usuario: {user.username} ({user.name})")
        print(f"Rol actual: {current_role}")
        print(f"Nuevo rol:  {new_role_text}")
        print("="*80)
        
        confirmar = input(f"\n¿Cambiar rol? (SI/no): ").strip().upper()
        
        if confirmar not in ['SI', 'S', '']:
            print("❌ Operación cancelada")
            return
        
        # Cambiar rol
        user.role = new_role
        db.session.commit()
        
        print(f"\n✅ Rol cambiado exitosamente")
        print(f"   {user.username} ahora es: {new_role_text}")
        
    except ValueError:
        print("❌ Debe ingresar un número")
    except Exception as e:
        db.session.rollback()
        print(f"\n❌ Error al cambiar rol: {e}")

def mostrar_estadisticas():
    """Muestra estadísticas de los usuarios"""
    print("\n" + "="*80)
    print("📊 ESTADÍSTICAS DE USUARIOS")
    print("="*80)
    
    total_users = User.query.count()
    total_admins = User.query.filter_by(role='admin').count()
    total_operators = User.query.filter_by(role='operador').count()
    
    print(f"\n👥 RESUMEN GENERAL:")
    print(f"   Total de usuarios:      {total_users}")
    print(f"   Administradores:        {total_admins}")
    print(f"   Operadores:             {total_operators}")
    
    if total_admins == 0:
        print("\n⚠️  ADVERTENCIA: No hay administradores en el sistema!")
    
    # Estadísticas de actividad
    print(f"\n📈 ACTIVIDAD:")
    
    for user in User.query.all():
        vehicles = Vehicle.query.filter(
            (Vehicle.operator_name == user.username) | 
            (Vehicle.exit_operator_name == user.username)
        ).count()
        
        monthly = MonthlyClient.query.filter_by(
            registered_by=user.username
        ).count()
        
        attendance = Attendance.query.filter_by(
            user_id=user.id
        ).count()
        
        role_badge = "🔐" if user.role == 'admin' else "👤"
        
        if vehicles > 0 or monthly > 0 or attendance > 0:
            print(f"\n   {role_badge} {user.username} ({user.name}):")
            if vehicles > 0:
                print(f"      🚗 {vehicles} registros de vehículos")
            if monthly > 0:
                print(f"      💳 {monthly} clientes mensuales")
            if attendance > 0:
                print(f"      ⏰ {attendance} registros de asistencia")
    
    print("\n" + "="*80)

def mostrar_menu():
    """Muestra el menú principal"""
    print("\n" + "="*80)
    print("🔧 GESTOR DE USUARIOS")
    print("="*80)
    print("\n1. Listar todos los usuarios")
    print("2. Agregar nuevo ADMINISTRADOR")
    print("3. Eliminar usuario")
    print("4. Cambiar contraseña")
    print("5. Cambiar rol (operador ↔ admin)")
    print("6. Ver estadísticas")
    print("0. Salir")
    print("\n💡 Nota: Para gestionar operadores usa: python manage_users.py")
    print()

def main():
    """Función principal"""
    app = create_app()
    
    with app.app_context():
        print("\n" + "="*80)
        print("👥 GESTOR COMPLETO DE USUARIOS DEL SISTEMA")
        print("="*80)
        
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
                    agregar_usuario()
                    input("\nPresione ENTER para continuar...")
                
                elif opcion == '3':
                    eliminar_usuario()
                    input("\nPresione ENTER para continuar...")
                
                elif opcion == '4':
                    cambiar_contrasena()
                    input("\nPresione ENTER para continuar...")
                
                elif opcion == '5':
                    cambiar_rol()
                    input("\nPresione ENTER para continuar...")
                
                elif opcion == '6':
                    mostrar_estadisticas()
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
    main()