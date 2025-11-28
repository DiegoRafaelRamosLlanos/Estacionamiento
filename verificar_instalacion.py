#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Script de verificación de instalación
Verifica que todas las dependencias estén correctamente instaladas
"""

import sys

def verificar_dependencias():
    """Verificar que todas las dependencias estén instaladas"""
    
    dependencias = {
        'Flask': 'flask',
        'SQLAlchemy': 'sqlalchemy',
        'Flask-Login': 'flask_login',
        'Flask-WTF': 'flask_wtf',
        'Bootstrap-Flask': 'flask_bootstrap',
        'python-dotenv': 'dotenv',
        'python-barcode': 'barcode',
        'Pillow': 'PIL',
        'python-escpos': 'escpos',
        'reportlab': 'reportlab',
        'python-dateutil': 'dateutil',
        'Werkzeug': 'werkzeug',
        'qrcode': 'qrcode',
    }
    
    print("=" * 60)
    print("VERIFICACIÓN DE DEPENDENCIAS - Sistema de Estacionamiento")
    print("=" * 60)
    print()
    
    errores = []
    exitosos = []
    
    for nombre, modulo in dependencias.items():
        try:
            __import__(modulo)
            exitosos.append(nombre)
            print(f"✓ {nombre:<25} INSTALADO")
        except ImportError as e:
            errores.append(nombre)
            print(f"✗ {nombre:<25} FALTA - Error: {str(e)}")
    
    print()
    print("=" * 60)
    print(f"Total: {len(exitosos)}/{len(dependencias)} dependencias instaladas")
    print("=" * 60)
    
    if errores:
        print()
        print("⚠️  DEPENDENCIAS FALTANTES:")
        for dep in errores:
            print(f"   - {dep}")
        print()
        print("Para instalar las dependencias faltantes, ejecuta:")
        print("   pip install -r requirements.txt")
        return False
    else:
        print()
        print("✅ Todas las dependencias están instaladas correctamente")
        print()
        verificar_configuracion()
        return True

def verificar_configuracion():
    """Verificar archivos de configuración"""
    import os
    
    print()
    print("=" * 60)
    print("VERIFICACIÓN DE CONFIGURACIÓN")
    print("=" * 60)
    print()
    
    archivos_requeridos = [
        'config.py',
        'run.py',
        'app/__init__.py',
        'app/routes.py',
        'app/models/models.py',
        'app/services/barcode_service.py',
        'app/services/vehicle_service.py',
    ]
    
    for archivo in archivos_requeridos:
        if os.path.exists(archivo):
            print(f"✓ {archivo:<40} EXISTE")
        else:
            print(f"✗ {archivo:<40} FALTA")
    
    print()
    
    # Verificar base de datos
    if os.path.exists('app.db'):
        print("✓ Base de datos (app.db) encontrada")
    else:
        print("⚠️  Base de datos no encontrada")
        print("   Ejecuta: python -c \"from app import app, db; app.app_context().push(); db.create_all()\"")
    
    print()

def verificar_python_version():
    """Verificar versión de Python"""
    version = sys.version_info
    print()
    print(f"Python {version.major}.{version.minor}.{version.micro}")
    
    if version.major >= 3 and version.minor >= 8:
        print("✓ Versión de Python compatible")
        return True
    else:
        print("✗ Se requiere Python 3.8 o superior")
        return False

if __name__ == "__main__":
    print()
    if not verificar_python_version():
        sys.exit(1)
    
    print()
    if not verificar_dependencias():
        sys.exit(1)
    
    print()
    print("=" * 60)
    print("✅ SISTEMA LISTO PARA EJECUTARSE")
    print("=" * 60)
    print()
    print("Para iniciar el servidor, ejecuta:")
    print("   python run.py")
    print()
