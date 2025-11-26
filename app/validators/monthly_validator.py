"""
Validador de datos de clientes mensuales
"""

from datetime import datetime
from app.constants.vehicle_types import VehicleType
from app.exceptions import ValidationException
from app.validators.vehicle_validator import VehicleValidator


class MonthlyClientValidator:
    """Valida datos relacionados con clientes mensuales"""
    
    # Duraciones válidas en meses
    VALID_DURATIONS = [1, 3, 6, 12]
    
    @staticmethod
    def validate_owner_name(owner_name: str) -> str:
        """
        Valida el nombre del titular
        
        Args:
            owner_name: Nombre a validar
            
        Returns:
            Nombre normalizado
            
        Raises:
            ValidationException: Si el nombre es inválido
        """
        if not owner_name or not owner_name.strip():
            raise ValidationException('owner_name', 'El nombre del titular es obligatorio')
        
        normalized = owner_name.strip()
        
        if len(normalized) < 3:
            raise ValidationException(
                'owner_name',
                'El nombre del titular debe tener al menos 3 caracteres'
            )
        
        return normalized
    
    @staticmethod
    def validate_phone(phone: str, required: bool = False) -> str:
        """
        Valida el número de teléfono
        
        Args:
            phone: Teléfono a validar
            required: Si es obligatorio
            
        Returns:
            Teléfono normalizado
            
        Raises:
            ValidationException: Si el teléfono es inválido
        """
        if not phone or not phone.strip():
            if required:
                raise ValidationException('phone', 'El teléfono es obligatorio')
            return ''
        
        # Remover espacios y caracteres comunes
        normalized = phone.strip().replace(' ', '').replace('-', '').replace('(', '').replace(')', '')
        
        # Verificar que solo contenga dígitos y posiblemente un +
        if not normalized.replace('+', '').isdigit():
            raise ValidationException('phone', 'El teléfono debe contener solo números')
        
        return normalized
    
    @staticmethod
    def validate_duration(duration_months: any) -> int:
        """
        Valida la duración del abono
        
        Args:
            duration_months: Duración en meses
            
        Returns:
            Duración como entero
            
        Raises:
            ValidationException: Si la duración es inválida
        """
        if not duration_months:
            raise ValidationException('duration_months', 'La duración del abono es obligatoria')
        
        try:
            duration = int(duration_months)
        except (ValueError, TypeError):
            raise ValidationException('duration_months', 'La duración debe ser un número')
        
        if duration not in MonthlyClientValidator.VALID_DURATIONS:
            valid = ', '.join(map(str, MonthlyClientValidator.VALID_DURATIONS))
            raise ValidationException(
                'duration_months',
                f'Duración inválida. Valores permitidos: {valid} meses'
            )
        
        return duration
    
    @staticmethod
    def validate_start_date(date_string: str) -> datetime:
        """
        Valida la fecha de inicio
        
        Args:
            date_string: Fecha en formato YYYY-MM-DD
            
        Returns:
            Objeto datetime
            
        Raises:
            ValidationException: Si la fecha es inválida
        """
        if not date_string:
            raise ValidationException('start_date', 'La fecha de inicio es obligatoria')
        
        try:
            return datetime.strptime(date_string, '%Y-%m-%d')
        except ValueError:
            raise ValidationException(
                'start_date',
                'Formato de fecha inválido. Use YYYY-MM-DD'
            )
    
    @staticmethod
    def validate_monthly_client(data: dict) -> dict:
        """
        Valida datos completos para cliente mensual
        
        Args:
            data: Dict con datos del cliente
            
        Returns:
            Dict con datos validados
            
        Raises:
            ValidationException: Si algún dato es inválido
        """
        validated = {}
        
        # Validar patente (reutilizar validador de vehículos)
        plate = data.get('plate')
        validated['plate'] = VehicleValidator.validate_plate(plate)
        
        # Validar tipo de vehículo
        vehicle_type = data.get('type') or data.get('vehicle_type')
        validated['vehicle_type'] = VehicleValidator.validate_vehicle_type(vehicle_type)
        
        # Validar nombre del titular
        owner_name = data.get('owner_name')
        validated['owner_name'] = MonthlyClientValidator.validate_owner_name(owner_name)
        
        # Validar teléfono (opcional)
        phone = data.get('phone', '')
        validated['phone'] = MonthlyClientValidator.validate_phone(phone, required=False)
        
        # Validar modelo (opcional)
        model = data.get('model', '').strip()
        validated['model'] = model
        
        # Validar fecha de inicio
        start_date = data.get('start_date')
        validated['start_date'] = MonthlyClientValidator.validate_start_date(start_date)
        
        # Validar duración
        duration_months = data.get('duration_months')
        validated['duration_months'] = MonthlyClientValidator.validate_duration(duration_months)
        
        return validated
