"""
Script para agregar el campo 'registered_by' a MonthlyClient
Ejecutar: python migrate_add_operator.py
"""

import sqlite3
import os
from datetime import datetime

def migrate_database():
    db_path = 'app.db'
    
    if not os.path.exists(db_path):
        print("❌ Error: No se encuentra la base de datos app.db")
        return
    
    # Hacer backup
    backup_path = f'app_backup_{datetime.now().strftime("%Y%m%d_%H%M%S")}.db'
    import shutil
    shutil.copy2(db_path, backup_path)
    print(f"✅ Backup creado: {backup_path}")
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    try:
        # Verificar si la columna ya existe
        cursor.execute("PRAGMA table_info(monthly_client)")
        columns = [col[1] for col in cursor.fetchall()]
        
        if 'registered_by' in columns:
            print("✅ La columna 'registered_by' ya existe")
        else:
            print("📝 Agregando columna 'registered_by'...")
            
            # Agregar columna
            cursor.execute("""
                ALTER TABLE monthly_client 
                ADD COLUMN registered_by VARCHAR(64)
            """)
            
            # Actualizar registros existentes
            cursor.execute("""
                UPDATE monthly_client 
                SET registered_by = 'Sistema'
                WHERE registered_by IS NULL OR registered_by = ''
            """)
            
            print("✅ Columna 'registered_by' agregada exitosamente")
        
        conn.commit()
        
        # Mostrar clientes actuales
        print("\n" + "="*80)
        print("📋 CLIENTES MENSUALES - CON INFORMACIÓN DE REGISTRO")
        print("="*80)
        
        cursor.execute("""
            SELECT plate, owner_name, model, registered_by, 
                   datetime(created_at, 'localtime') as fecha_registro
            FROM monthly_client 
            ORDER BY created_at DESC
        """)
        
        clients = cursor.fetchall()
        
        if clients:
            print(f"\nTotal: {len(clients)} cliente(s)\n")
            for client in clients:
                print(f"Patente: {client[0]:10} | Titular: {client[1]:25}")
                print(f"  Modelo: {client[2]}")
                print(f"  Registrado por: {client[3]:15} | Fecha: {client[4]}")
                print("-" * 80)
        else:
            print("\nNo hay clientes mensuales registrados")
        
        print("\n✅ MIGRACIÓN COMPLETADA")
        print("\n💡 Próximos pasos:")
        print("   1. Actualizar app/models/models.py")
        print("   2. Actualizar app/routes.py")
        print("   3. Actualizar app/templates/monthly.html")
        print("   4. Reiniciar: python run.py\n")
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        conn.rollback()
    finally:
        conn.close()

if __name__ == '__main__':
    print("\n" + "="*80)
    print("🔄 MIGRACIÓN: AGREGAR RASTREO DE OPERADOR EN CLIENTES MENSUALES")
    print("="*80 + "\n")
    
    respuesta = input("¿Continuar? (s/n): ")
    if respuesta.lower() == 's':
        migrate_database()
    else:
        print("\n❌ Migración cancelada")