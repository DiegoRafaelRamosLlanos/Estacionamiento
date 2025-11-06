"""
Script para agregar el campo owner_name a la tabla MonthlyClient
Ejecutar: python migrate_add_owner.py
"""

import sqlite3
import os
from datetime import datetime

def migrate_database():
    # Ruta de la base de datos
    db_path = 'app.db'
    
    if not os.path.exists(db_path):
        print("❌ Error: No se encuentra la base de datos app.db")
        print("   Ejecute primero: python init_db.py")
        return
    
    # Hacer backup antes de modificar
    backup_path = f'app_backup_{datetime.now().strftime("%Y%m%d_%H%M%S")}.db'
    import shutil
    shutil.copy2(db_path, backup_path)
    print(f"✅ Backup creado: {backup_path}")
    
    # Conectar a la base de datos
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    try:
        # Verificar si la columna ya existe
        cursor.execute("PRAGMA table_info(monthly_client)")
        columns = [col[1] for col in cursor.fetchall()]
        
        if 'owner_name' in columns:
            print("✅ La columna 'owner_name' ya existe en la tabla")
        else:
            print("📝 Agregando columna 'owner_name' a la tabla monthly_client...")
            
            # Agregar la columna
            cursor.execute("""
                ALTER TABLE monthly_client 
                ADD COLUMN owner_name VARCHAR(100) DEFAULT 'Sin especificar'
            """)
            
            print("✅ Columna 'owner_name' agregada exitosamente")
        
        # Actualizar registros existentes sin titular
        cursor.execute("""
            UPDATE monthly_client 
            SET owner_name = 'Cliente - ' || plate 
            WHERE owner_name IS NULL OR owner_name = '' OR owner_name = 'Sin especificar'
        """)
        
        updated = cursor.rowcount
        if updated > 0:
            print(f"✅ Se actualizaron {updated} registros con nombre de titular por defecto")
        
        # Guardar cambios
        conn.commit()
        
        # Mostrar clientes actuales
        print("\n" + "="*70)
        print("📋 CLIENTES MENSUALES ACTUALES")
        print("="*70)
        
        cursor.execute("""
            SELECT plate, owner_name, model, phone, vehicle_type 
            FROM monthly_client 
            ORDER BY plate
        """)
        
        clients = cursor.fetchall()
        
        if clients:
            print(f"\nTotal: {len(clients)} cliente(s)")
            print("-" * 70)
            for client in clients:
                print(f"Patente: {client[0]:10} | Titular: {client[1]:25} | Modelo: {client[2]}")
        else:
            print("\nNo hay clientes mensuales registrados")
        
        print("\n" + "="*70)
        print("✅ MIGRACIÓN COMPLETADA EXITOSAMENTE")
        print("="*70)
        print("\n💡 Ahora puedes:")
        print("   1. Reemplazar el archivo app/models/models.py con el nuevo código")
        print("   2. Reiniciar la aplicación: python run.py")
        print("   3. El formulario de registro ahora incluirá el campo 'Titular'")
        print("\n")
        
    except Exception as e:
        print(f"\n❌ Error durante la migración: {e}")
        conn.rollback()
        print(f"💡 Puedes restaurar desde el backup: {backup_path}")
    finally:
        conn.close()

if __name__ == '__main__':
    print("\n" + "="*70)
    print("🔄 MIGRACIÓN: AGREGAR CAMPO 'TITULAR' A CLIENTES MENSUALES")
    print("="*70 + "\n")
    
    respuesta = input("¿Desea continuar con la migración? (s/n): ")
    
    if respuesta.lower() == 's':
        migrate_database()
    else:
        print("\n❌ Migración cancelada")