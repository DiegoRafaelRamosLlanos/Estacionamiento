"""
Configuración de tarifas y precios del estacionamiento
Centraliza todas las tarifas para facilitar futuras actualizaciones
"""

from app.constants.vehicle_types import VehicleType


class PricingConfig:
    """Configuración centralizada de tarifas"""
    
    # Tiempo de fraccionamiento (en minutos)
    FRACTION_MINUTES = 15  # Cada 15 minutos
    FIRST_HOUR_MINUTES = 60  # Primera hora
    
    # Tarifas para AUTOS
    AUTO_FIRST_HOUR = 500  # Primera hora
    AUTO_FRACTION = 125    # Cada 15 minutos adicionales ($500 / 4)
    
    # Tarifas para MOTOS
    MOTO_FIRST_HOUR = 300  # Primera hora
    MOTO_FRACTION = 75     # Cada 15 minutos adicionales ($300 / 4)
    
    @classmethod
    def get_first_hour_rate(cls, vehicle_type: str) -> int:
        """
        Obtiene la tarifa de la primera hora según tipo de vehículo
        
        Args:
            vehicle_type: Tipo de vehículo ('auto' o 'moto')
            
        Returns:
            Tarifa de primera hora
        """
        rates = {
            VehicleType.AUTO.value: cls.AUTO_FIRST_HOUR,
            VehicleType.MOTO.value: cls.MOTO_FIRST_HOUR
        }
        return rates.get(vehicle_type, cls.AUTO_FIRST_HOUR)
    
    @classmethod
    def get_fraction_rate(cls, vehicle_type: str) -> int:
        """
        Obtiene la tarifa por fracción según tipo de vehículo
        
        Args:
            vehicle_type: Tipo de vehículo ('auto' o 'moto')
            
        Returns:
            Tarifa por cada 15 minutos
        """
        rates = {
            VehicleType.AUTO.value: cls.AUTO_FRACTION,
            VehicleType.MOTO.value: cls.MOTO_FRACTION
        }
        return rates.get(vehicle_type, cls.AUTO_FRACTION)
    
    @classmethod
    def get_pricing_info(cls, vehicle_type: str) -> dict:
        """
        Obtiene toda la información de precios para un tipo de vehículo
        
        Args:
            vehicle_type: Tipo de vehículo
            
        Returns:
            Dict con información de precios
        """
        return {
            'first_hour': cls.get_first_hour_rate(vehicle_type),
            'fraction': cls.get_fraction_rate(vehicle_type),
            'fraction_minutes': cls.FRACTION_MINUTES,
            'vehicle_type': vehicle_type
        }
    
    @classmethod
    def format_pricing_text(cls, vehicle_type: str) -> str:
        """
        Formatea el texto de tarifas para mostrar al usuario
        
        Args:
            vehicle_type: Tipo de vehículo
            
        Returns:
            Texto formateado con las tarifas
        """
        first_hour = cls.get_first_hour_rate(vehicle_type)
        fraction = cls.get_fraction_rate(vehicle_type)
        
        return (
            f"1ra hora: ${first_hour}\n"
            f"c/{cls.FRACTION_MINUTES} min: ${fraction}"
        )
