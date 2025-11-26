"""
Sistema de Backup Automático para Estacionamiento
Ejecutar diariamente con: python backup_manager.py
O configurar con cron/Task Scheduler
"""

import os
import shutil
import sqlite3
from datetime import datetime, timedelta
import json
import csv

class BackupManager:
    def __init__(self):
        self.base_dir = os.path.dirname(os.path.abspath(__file__))
        self.db_path = os.path.join(self.base_dir, 'app.db')
        self.backup_dir = os.path.join(self.base_dir, 'backups')
        self.reports_dir = os.path.join(self.base_dir, 'reportes_diarios')
        
        # Crear directorios si no existen
        os.makedirs(self.backup_dir, exist_ok=True)
        os.makedirs(self.reports_dir, exist_ok=True)
        
        # Subdirectorios por año y mes
        today = datetime.now()
        self.year_dir = os.path.join(self.backup_dir, str(today.year))
        self.month_dir = os.path.join(self.year_dir, f"{today.month:02d}_{today.strftime('%B')}")
        
        os.makedirs(self.year_dir, exist_ok=True)
        os.makedirs(self.month_dir, exist_ok=True)

    def backup_database(self):
        """Respaldar la base de datos completa"""
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        backup_filename = f"estacionamiento_backup_{timestamp}.db"
        backup_path = os.path.join(self.month_dir, backup_filename)
        
        try:
            shutil.copy2(self.db_path, backup_path)
            print(f"✅ Backup creado: {backup_path}")
            return backup_path
        except Exception as e:
            print(f"❌ Error al crear backup: {e}")
            return None

    def generate_daily_report(self):
        """Generar reporte diario en múltiples formatos"""
        today = datetime.now().date()
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Obtener vehículos que:
            # 1. Ingresaron hoy, O
            # 2. Salieron hoy, O
            # 3. Están activos (sin importar cuándo ingresaron)
            cursor.execute("""
                SELECT id, plate, type, entry_time, exit_time, 
                       total_cost, is_monthly, operator_name, exit_operator_name
                FROM vehicle
                WHERE DATE(entry_time) = ?
                   OR DATE(exit_time) = ?
                   OR exit_time IS NULL
                ORDER BY entry_time DESC
            """, (today, today))
            
            vehicles = cursor.fetchall()
            
            # Calcular estadísticas precisas del día
            vehicles_entered_today = [v for v in vehicles if v[3] and v[3].startswith(str(today))]
            vehicles_exited_today = [v for v in vehicles if v[4] and v[4].startswith(str(today))]
            active_vehicles = [v for v in vehicles if not v[4]]
            
            # Total de vehículos únicos del día (ingresaron O salieron hoy)
            unique_today_ids = set()
            for v in vehicles:
                if (v[3] and v[3].startswith(str(today))) or (v[4] and v[4].startswith(str(today))):
                    unique_today_ids.add(v[0])
            
            total_vehicles = len(unique_today_ids)
            total_earnings = sum(v[5] for v in vehicles_exited_today if v[5])
            active_vehicles_count = len(active_vehicles)
            monthly_clients = sum(1 for v in vehicles_entered_today if v[6])
            
            # Reporte TXT legible
            txt_filename = f"reporte_{today}__{timestamp}.txt"
            txt_path = os.path.join(self.reports_dir, txt_filename)
            
            with open(txt_path, 'w', encoding='utf-8') as f:
                f.write("=" * 80 + "\n")
                f.write(f"REPORTE DIARIO DE ESTACIONAMIENTO - {today.strftime('%d/%m/%Y')}\n")
                f.write("=" * 80 + "\n\n")
                
                f.write("RESUMEN DEL DÍA:\n")
                f.write("-" * 80 + "\n")
                f.write(f"Total de vehículos:      {total_vehicles}\n")
                f.write(f"Recaudación total:       ${total_earnings:,.2f}\n")
                f.write(f"Vehículos activos:       {active_vehicles_count}\n")
                f.write(f"Clientes mensuales:      {monthly_clients}\n")
                f.write("\n")
                
                f.write("DETALLE DE MOVIMIENTOS:\n")
                f.write("-" * 80 + "\n\n")
                
                for v in vehicles:
                    f.write(f"ID: {v[0]} | Patente: {v[1]} | Tipo: {v[2]}\n")
                    f.write(f"  Ingreso:  {v[3]}\n")
                    f.write(f"  Salida:   {v[4] if v[4] else 'AÚN ESTACIONADO'}\n")
                    f.write(f"  Costo:    ${v[5]:,.2f}" if v[5] else "  Costo:    N/A (Mensual)\n")
                    f.write(f"  Operador: {v[7]}" + (f" / {v[8]}" if v[8] else "") + "\n")
                    f.write("-" * 80 + "\n")
            
            print(f"✅ Reporte TXT creado: {txt_path}")
            
            conn.close()
            
            return txt_path
            
        except Exception as e:
            print(f"❌ Error al generar reportes: {e}")
            return None

    def clean_old_backups(self, days_to_keep=90):
        """Eliminar backups antiguos (por defecto mantiene 90 días)"""
        cutoff_date = datetime.now() - timedelta(days=days_to_keep)
        deleted_count = 0
        
        try:
            for root, dirs, files in os.walk(self.backup_dir):
                for file in files:
                    if file.endswith('.db'):
                        file_path = os.path.join(root, file)
                        file_time = datetime.fromtimestamp(os.path.getctime(file_path))
                        
                        if file_time < cutoff_date:
                            os.remove(file_path)
                            deleted_count += 1
                            print(f"🗑️  Eliminado backup antiguo: {file}")
            
            print(f"✅ Limpieza completada: {deleted_count} archivos eliminados")
            
        except Exception as e:
            print(f"❌ Error al limpiar backups: {e}")



    def run_full_backup(self):
        """Ejecutar backup completo"""
        print("\n" + "=" * 80)
        print("🔄 INICIANDO BACKUP DEL SISTEMA DE ESTACIONAMIENTO")
        print("=" * 80 + "\n")
        
        # 1. Backup de base de datos
        print("📦 1. Respaldando base de datos...")
        self.backup_database()
        
        # 2. Reporte diario
        print("\n📊 2. Generando reportes diarios...")
        self.generate_daily_report()

        
        # 3. Limpiar backups antiguos
        print("\n🧹 3. Limpiando backups antiguos...")
        self.clean_old_backups(days_to_keep=90)
        
        print("\n" + "=" * 80)
        print("✅ BACKUP COMPLETADO EXITOSAMENTE")
        print("=" * 80 + "\n")


if __name__ == '__main__':
    manager = BackupManager()
    manager.run_full_backup()