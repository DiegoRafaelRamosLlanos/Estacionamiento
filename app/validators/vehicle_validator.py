"""
Validador de datos de vehículos
"""

import re
from app.constants.vehicle_types import VehicleType
from app.exceptions import ValidationException


class VehicleValidator:
    """Valida datos relacionados con vehículos"""
    
    # Patrón para patentes (ej: ABC123, AB123CD)
    PLATE_PATTERN = re.compile(r'^[A-Z0-9]{3,7}$')
    
    @staticmethod
    def validate_plate(plate: str) -> str:
        """
        Valida y normaliza una patente
        
        Args:
            plate: Patente a validar
            
        Returns:
            Patente normalizada (uppercase, sin espacios)
            
        Raises:
            ValidationException: Si la patente es inválida
        """
        if not plate:
            raise ValidationException('plate', 'La patente es obligatoria')
        
        # Normalizar: uppercase y sin espacios
        normalized_plate = plate.upper().strip().replace(' ', '')
        
        # Validar formato
        if not VehicleValidator.PLATE_PATTERN.match(normalized_plate):
            raise ValidationException(
                'plate',
                'Formato de patente inválido. Use solo letras y números (3-7 caracteres)'
            )
        
        return normalized_plate
    
    @staticmethod
    def validate_vehicle_type(vehicle_type: str) -> str:
        """
        Valida el tipo de vehículo
        
        Args:
            vehicle_type: Tipo de vehículo
            
        Returns:
            Tipo de vehículo validado
            
        Raises:
            ValidationException: Si el tipo es inválido
        """
        if not vehicle_type:
            raise ValidationException('type', 'El tipo de vehículo es obligatorio')
        
        if not VehicleType.is_valid(vehicle_type):
            valid_types = ', '.join(VehicleType.get_all_values())
            raise ValidationException(
                'type',
                f'Tipo de vehículo inválido. Valores permitidos: {valid_types}'
            )
        
        return vehicle_type
    
    @staticmethod
    def validate_vehicle_entry(data: dict) -> dict:
        """
        Valida datos completos para entrada de vehículo
        
        Args:
            data: Dict con datos del vehículo (plate, type)
            
        Returns:
            Dict con datos validados
            
        Raises:
            ValidationException: Si algún dato es inválido
        """
        validated = {}
        
        # Validar patente
        plate = data.get('plate')
        validated['plate'] = VehicleValidator.validate_plate(plate)
        
        # Validar tipo
        vehicle_type = data.get('type')
        validated['type'] = VehicleValidator.validate_vehicle_type(vehicle_type)
        
        return validated
    
    @staticmethod
    def validate_vehicle_id(vehicle_id: any) -> int:
        """
        Valida un ID de vehículo
        
        Args:
            vehicle_id: ID a validar
            
        Returns:
            ID como entero
            
        Raises:
            ValidationException: Si el ID es inválido
        """
        if not vehicle_id:
            raise ValidationException('vehicle_id', 'El ID del vehículo es obligatorio')
        
        try:
            return int(vehicle_id)
        except (ValueError, TypeError):
            raise ValidationException('vehicle_id', 'El ID del vehículo debe ser un número')
