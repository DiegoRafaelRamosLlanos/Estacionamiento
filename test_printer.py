"""
Script de prueba para la impresora térmica
Ejecutar este script para verificar la conexión y funcionalidad de la impresora
"""

import sys
import os

# Agregar el directorio raíz al path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.printer_service import printer_service, test_printer_connection

def main():
    print("=" * 50)
    print("PRUEBA DE IMPRESORA TÉRMICA TP85K")
    print("=" * 50)
    print()
    
    # Test 1: Verificar configuración
    print("1. Verificando configuración...")
    print(f"   - Impresora habilitada: {printer_service.enabled}")
    print(f"   - Tipo: {printer_service.printer_type}")
    print(f"   - IP: {printer_service.printer_ip}")
    print(f"   - Puerto: {printer_service.printer_port}")
    print(f"   - Timeout: {printer_service.timeout}s")
    print()
    
    # Test 2: Probar conexión
    print("2. Probando conexión con la impresora...")
    print("   (Esto imprimirá un ticket de prueba)")
    success = test_printer_connection()
    print()
    
    if success:
        print("✓ PRUEBA EXITOSA")
        print("  La impresora está conectada y funcionando correctamente.")
        print("  Deberías ver un ticket de prueba impreso.")
    else:
        print("✗ PRUEBA FALLIDA")
        print("  Verifica:")
        print("  - La impresora está encendida")
        print("  - La IP 192.168.1.13 es correcta y accesible")
        print("  - El puerto 9100 está abierto")
        print("  - Hay papel en la impresora")
    
    print()
    print("=" * 50)

if __name__ == "__main__":
    main()
