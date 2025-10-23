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
            
            # Obtener todos los movimientos del día
            cursor.execute("""
                SELECT id, plate, type, entry_time, exit_time, 
                       total_cost, is_monthly, operator_name, exit_operator_name
                FROM vehicle
                WHERE DATE(entry_time) = ?
                ORDER BY entry_time DESC
            """, (today,))
            
            vehicles = cursor.fetchall()
            
            # Calcular estadísticas
            total_vehicles = len(vehicles)
            total_earnings = sum(v[5] for v in vehicles if v[5])
            active_vehicles = sum(1 for v in vehicles if not v[4])
            monthly_clients = sum(1 for v in vehicles if v[6])
            
            # 1. Reporte JSON (para procesamiento automático)
            json_data = {
                'fecha': str(today),
                'timestamp': timestamp,
                'resumen': {
                    'total_vehiculos': total_vehicles,
                    'recaudacion_total': total_earnings,
                    'vehiculos_activos': active_vehicles,
                    'clientes_mensuales': monthly_clients
                },
                'movimientos': [
                    {
                        'id': v[0],
                        'patente': v[1],
                        'tipo': v[2],
                        'ingreso': v[3],
                        'salida': v[4],
                        'costo': v[5],
                        'es_mensual': v[6],
                        'operador_ingreso': v[7],
                        'operador_salida': v[8]
                    } for v in vehicles
                ]
            }
            
            json_filename = f"reporte_{today}__{timestamp}.json"
            json_path = os.path.join(self.reports_dir, json_filename)
            
            with open(json_path, 'w', encoding='utf-8') as f:
                json.dump(json_data, f, indent=2, ensure_ascii=False)
            
            print(f"✅ Reporte JSON creado: {json_path}")
            
            # 2. Reporte CSV (para Excel)
            csv_filename = f"reporte_{today}__{timestamp}.csv"
            csv_path = os.path.join(self.reports_dir, csv_filename)
            
            with open(csv_path, 'w', newline='', encoding='utf-8-sig') as f:
                writer = csv.writer(f)
                writer.writerow(['ID', 'Patente', 'Tipo', 'Ingreso', 'Salida', 
                               'Costo', 'Es Mensual', 'Operador Ingreso', 'Operador Salida'])
                writer.writerows(vehicles)
            
            print(f"✅ Reporte CSV creado: {csv_path}")
            
            # 3. Reporte TXT legible
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
                f.write(f"Vehículos activos:       {active_vehicles}\n")
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
            
            return {
                'json': json_path,
                'csv': csv_path,
                'txt': txt_path
            }
            
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

    def export_monthly_summary(self):
        """Exportar resumen mensual"""
        today = datetime.now()
        first_day = today.replace(day=1)
        
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT 
                    DATE(entry_time) as fecha,
                    COUNT(*) as total_vehiculos,
                    SUM(CASE WHEN exit_time IS NOT NULL THEN total_cost ELSE 0 END) as recaudacion,
                    SUM(CASE WHEN exit_time IS NULL THEN 1 ELSE 0 END) as activos
                FROM vehicle
                WHERE entry_time >= ?
                GROUP BY DATE(entry_time)
                ORDER BY fecha
            """, (first_day,))
            
            monthly_data = cursor.fetchall()
            
            filename = f"resumen_mensual_{today.strftime('%Y_%m')}.csv"
            filepath = os.path.join(self.reports_dir, filename)
            
            with open(filepath, 'w', newline='', encoding='utf-8-sig') as f:
                writer = csv.writer(f)
                writer.writerow(['Fecha', 'Total Vehículos', 'Recaudación', 'Activos'])
                writer.writerows(monthly_data)
            
            print(f"✅ Resumen mensual creado: {filepath}")
            conn.close()
            
            return filepath
            
        except Exception as e:
            print(f"❌ Error al generar resumen mensual: {e}")
            return None

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
        
        # 3. Resumen mensual (solo el día 1 del mes o si no existe)
        if datetime.now().day == 1 or not os.path.exists(
            os.path.join(self.reports_dir, 
                        f"resumen_mensual_{datetime.now().strftime('%Y_%m')}.csv")
        ):
            print("\n📈 3. Generando resumen mensual...")
            self.export_monthly_summary()
        
        # 4. Limpiar backups antiguos
        print("\n🧹 4. Limpiando backups antiguos...")
        self.clean_old_backups(days_to_keep=90)
        
        print("\n" + "=" * 80)
        print("✅ BACKUP COMPLETADO EXITOSAMENTE")
        print("=" * 80 + "\n")


if __name__ == '__main__':
    manager = BackupManager()
    manager.run_full_backup()