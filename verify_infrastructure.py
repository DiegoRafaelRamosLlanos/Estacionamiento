"""
Script de verificación para la nueva arquitectura refactorizada
Verifica que todas las capas se importen correctamente
"""

import sys

def test_constants():
    """Test de importación de constantes"""
    print("✓ Verificando constantes...")
    from app.constants import VehicleType, UserRole, PricingConfig
    
    # Verificar VehicleType
    assert VehicleType.AUTO.value == 'auto'
    assert VehicleType.MOTO.value == 'moto'
    assert VehicleType.is_valid('auto') == True
    
    # Verificar UserRole
    assert UserRole.ADMIN.value == 'admin'
    assert UserRole.OPERADOR.value == 'operador'
    assert UserRole.ADMIN.has_permission('manage_users') == True
    
    # Verificar PricingConfig
    assert PricingConfig.AUTO_FIRST_HOUR == 500
    assert PricingConfig.MOTO_FIRST_HOUR == 300
    
    print("   ✅ Constantes: OK")

def test_exceptions():
    """Test de importación de excepciones"""
    print("✓ Verificando excepciones...")
    from app.exceptions import (
        BusinessException,
        VehicleNotFoundException,
        ValidationException
    )
    
    # Verificar que se puedan crear
    try:
        raise VehicleNotFoundException(vehicle_id=123)
    except BusinessException as e:
        assert 'no encontrado' in str(e).lower()
    
    print("   ✅ Excepciones: OK")

def test_validators():
    """Test de importación de validadores"""
    print("✓ Verificando validadores...")
    from app.validators import VehicleValidator, MonthlyClientValidator, UserValidator
    
    # Test validación de patente
    plate = VehicleValidator.validate_plate('abc123')
    assert plate == 'ABC123'
    
    # Test validación de tipo
    vehicle_type = VehicleValidator.validate_vehicle_type('auto')
    assert vehicle_type == 'auto'
    
    print("   ✅ Validadores: OK")

def test_repositories():
    """Test de importación de repositorios"""
    print("✓ Verificando repositorios...")
    from app.repositories import (
        VehicleRepository,
        MonthlyClientRepository,
        UserRepository,
        AttendanceRepository
    )
    
    # Verificar instanciación
    vehicle_repo = VehicleRepository()
    monthly_repo = MonthlyClientRepository()
    user_repo = UserRepository()
    attendance_repo = AttendanceRepository()
    
    print("   ✅ Repositorios: OK")

def test_services():
    """Test de importación de servicios"""
    print("✓ Verificando servicios...")
    from app.services import (
        VehicleService,
        PricingService,
        QRService,
        MonthlyClientService
    )
    
    # Verificar instancias globales
    from app.services.vehicle_service import vehicle_service
    from app.services.pricing_service import pricing_service
    from app.services.qr_service import qr_service
    from app.services.monthly_service import monthly_client_service
    
    assert vehicle_service is not None
    assert pricing_service is not None
    assert qr_service is not None
    assert monthly_client_service is not None
    
    print("   ✅ Servicios: OK")

def test_utils():
    """Test de importación de utilidades"""
    print("✓ Verificando utilidades...")
    from app.utils import DateUtils, ResponseUtils
    from datetime import datetime
    
    # Test DateUtils
    dt = datetime.now()
    formatted = DateUtils.format_datetime(dt, 'datetime')
    assert formatted is not None
    
    # Test ResponseUtils
    response, code = ResponseUtils.success(message="Test")
    assert code == 200
    
    print("   ✅ Utilidades: OK")

def main():
    """Función principal"""
    print("\n" + "="*70)
    print("🧪 VERIFICACIÓN DE ARQUITECTURA REFACTORIZADA")
    print("="*70 + "\n")
    
    try:
        test_constants()
        test_exceptions()
        test_validators()
        test_repositories()
        test_services()
        test_utils()
        
        print("\n" + "="*70)
        print("✅ TODAS LAS VERIFICACIONES PASARON")
        print("="*70)
        print("\n✨ La arquitectura refactorizada está correctamente implementada!")
        print("📦 Capas creadas:")
        print("   • constants/   - Constantes y enums")
        print("   • exceptions/  - Excepciones personalizadas")
        print("   • validators/  - Validación de datos")
        print("   • repositories/ - Acceso a datos")
        print("   • services/    - Lógica de negocio")
        print("   • utils/       - Utilidades")
        print("\n💡 Siguiente paso: Crear los blueprints con las rutas refactorizadas")
        print()
        
        return 0
        
    except Exception as e:
        print("\n" + "="*70)
        print(f"❌ ERROR: {type(e).__name__}")
        print("="*70)
        print(f"   {str(e)}")
        print()
        import traceback
        traceback.print_exc()
        return 1

if __name__ == '__main__':
    from app import create_app
    
    app = create_app()
    with app.app_context():
        sys.exit(main())
