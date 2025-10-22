from app import create_app, db
from app.models.models import User, Vehicle, MonthlyClient
import socket

app = create_app()

# Crear todas las tablas de la base de datos
with app.app_context():
    db.create_all()

def get_local_ip():
    """Obtiene la IP local de la máquina"""
    try:
        # Crear un socket UDP
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        # No necesita conectarse realmente
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
        s.close()
        return ip
    except Exception:
        return "127.0.0.1"

if __name__ == '__main__':
    PORT = 8080
    local_ip = get_local_ip()
    
    print("\n" + "="*70)
    print("🚀 SERVIDOR DE ESTACIONAMIENTO INICIADO")
    print("="*70)
    print(f"\n📍 Acceso LOCAL (desde esta PC):")
    print(f"   http://127.0.0.1:{PORT}")
    print(f"   http://localhost:{PORT}")
    print(f"\n📱 Acceso desde CELULAR/TABLET (misma red WiFi):")
    print(f"   http://{local_ip}:{PORT}")
    print(f"\n🔍 IP ACTUAL DETECTADA: {local_ip}")
    print(f"\n💡 IMPORTANTE:")
    print(f"   - Si cambias de red, la IP cambiará")
    print(f"   - WiFi casa: IP será tipo 192.168.0.X o 192.168.1.X")
    print(f"   - Hotspot celular: IP será tipo 192.168.43.1 o 192.168.18.X")
    print(f"\n👤 Usuarios: operador1, operador2, operador3, operador4")
    print(f"🔑 Contraseña: 1234")
    print("\n" + "="*70 + "\n")
    
    # Iniciar servidor
    # host='0.0.0.0' permite conexiones desde cualquier dispositivo en la red
    app.run(host='0.0.0.0', port=PORT, debug=True)