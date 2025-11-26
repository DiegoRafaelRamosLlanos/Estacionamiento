"""
Servicio para cálculo de tarifas
"""

from datetime import datetime
from app.constants.pricing import PricingConfig
from app.models.models import Vehicle


class PricingService:
    """
    Servicio centralizado para cálculo de tarifas
    
    Encapsula toda la lógica de cálculo de precios,
    facilitando cambios futuros en las tarifas.
    """
    
    @staticmethod
    def calculate_cost(vehicle: Vehicle) -> float:
        """
        Calcula el costo de estacionamiento para un vehículo
        
        Args:
            vehicle: Vehículo con entry_time y exit_time
            
        Returns:
            Costo total en pesos
        """
        # Si es cliente mensual, no hay costo
        if vehicle.is_monthly:
            return 0.0
        
        # Si no ha salido todavía, calcular hasta ahora
        exit_time = vehicle.exit_time or datetime.now()
        
        # Calcular diferencia de tiempo
        time_diff = exit_time - vehicle.entry_time
        total_minutes = time_diff.total_seconds() / 60
        
        # Obtener tarifas según tipo de vehículo
        first_hour_rate = PricingConfig.get_first_hour_rate(vehicle.type)
        fraction_rate = PricingConfig.get_fraction_rate(vehicle.type)
        
        # Calcular costo
        if total_minutes <= PricingConfig.FIRST_HOUR_MINUTES:
            # Primera hora completa
            cost = first_hour_rate
        else:
            # Primera hora + fracciones adicionales
            cost = first_hour_rate
            remaining_minutes = total_minutes - PricingConfig.FIRST_HOUR_MINUTES
            
            # Calcular cuartos de hora (redondear hacia arriba)
            quarter_hours = int(remaining_minutes / PricingConfig.FRACTION_MINUTES)
            if remaining_minutes % PricingConfig.FRACTION_MINUTES > 0:
                quarter_hours += 1
            
            cost += quarter_hours * fraction_rate
        
        return float(cost)
    
    @staticmethod
    def estimate_cost(vehicle_type: str, minutes: int) -> float:
        """
        Estima el costo para un tiempo determinado
        
        Args:
            vehicle_type: Tipo de vehículo ('auto' o 'moto')
            minutes: Minutos de estacionamiento
            
        Returns:
            Costo estimado
        """
        first_hour_rate = PricingConfig.get_first_hour_rate(vehicle_type)
        fraction_rate = PricingConfig.get_fraction_rate(vehicle_type)
        
        if minutes <= PricingConfig.FIRST_HOUR_MINUTES:
            return float(first_hour_rate)
        
        cost = first_hour_rate
        remaining_minutes = minutes - PricingConfig.FIRST_HOUR_MINUTES
        quarter_hours = int(remaining_minutes / PricingConfig.FRACTION_MINUTES)
        
        if remaining_minutes % PricingConfig.FRACTION_MINUTES > 0:
            quarter_hours += 1
        
        cost += quarter_hours * fraction_rate
        
        return float(cost)
    
    @staticmethod
    def get_pricing_info(vehicle_type: str) -> dict:
        """
        Obtiene información de precios para mostrar al usuario
        
        Args:
            vehicle_type: Tipo de vehículo
            
        Returns:
            Dict con información de precios
        """
        return PricingConfig.get_pricing_info(vehicle_type)
    
    @staticmethod
    def format_pricing_text(vehicle_type: str) -> str:
        """
        Formatea el texto de tarifas para tickets
        
        Args:
            vehicle_type: Tipo de vehículo
            
        Returns:
            Texto formateado
        """
        return PricingConfig.format_pricing_text(vehicle_type)


# Instancia global del servicio
pricing_service = PricingService()
