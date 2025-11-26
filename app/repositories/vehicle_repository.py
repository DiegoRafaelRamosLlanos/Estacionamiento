"""
Repositorio para operaciones de vehículos
"""

from datetime import datetime
from typing import List, Optional
from app.models.models import Vehicle
from app.repositories.base_repository import BaseRepository
from app import db


class VehicleRepository(BaseRepository[Vehicle]):
    """Repositorio para operaciones específicas de vehículos"""
    
    def __init__(self):
        super().__init__(Vehicle)
    
    def find_active_by_plate(self, plate: str) -> Optional[Vehicle]:
        """
        Busca un vehículo activo (sin salida) por patente
        
        Args:
            plate: Patente del vehículo
            
        Returns:
            Vehículo activo o None
        """
        return Vehicle.query.filter_by(
            plate=plate,
            exit_time=None
        ).first()
    
    def find_by_plate(self, plate: str) -> List[Vehicle]:
        """
        Busca todos los vehículos con una patente
        
        Args:
            plate: Patente del vehículo
            
        Returns:
            Lista de vehículos
        """
        return Vehicle.query.filter_by(plate=plate).all()
    
    def get_active_vehicles(self) -> List[Vehicle]:
        """
        Obtiene todos los vehículos activos (sin salida)
        
        Returns:
            Lista de vehículos activos
        """
        return Vehicle.query.filter_by(exit_time=None).all()
    
    def get_today_vehicles(self) -> List[Vehicle]:
        """
        Obtiene todos los vehículos que ingresaron hoy
        
        Returns:
            Lista de vehículos del día
        """
        today = datetime.now().date()
        return Vehicle.query.filter(
            db.func.date(Vehicle.entry_time) == today
        ).all()
    
    def get_vehicles_by_date_range(
        self,
        start_date: datetime,
        end_date: datetime = None
    ) -> List[Vehicle]:
        """
        Obtiene vehículos en un rango de fechas
        
        Args:
            start_date: Fecha inicial
            end_date: Fecha final (opcional, default: ahora)
            
        Returns:
            Lista de vehículos en el rango
        """
        query = Vehicle.query.filter(Vehicle.entry_time >= start_date)
        
        if end_date:
            query = query.filter(Vehicle.entry_time < end_date)
        
        return query.all()
    
    def get_vehicles_by_operator(self, operator_name: str) -> List[Vehicle]:
        """
        Obtiene vehículos registrados por un operador específico
        
        Args:
            operator_name: Nombre del operador
            
        Returns:
            Lista de vehículos
        """
        return Vehicle.query.filter(
            (Vehicle.operator_name == operator_name) |
            (Vehicle.exit_operator_name == operator_name)
        ).all()
    
    def get_monthly_vehicles_today(self) -> List[Vehicle]:
        """
        Obtiene vehículos de clientes mensuales que ingresaron hoy
        
        Returns:
            Lista de vehículos mensuales
        """
        today = datetime.now().date()
        return Vehicle.query.filter(
            db.func.date(Vehicle.entry_time) == today,
            Vehicle.is_monthly == True
        ).all()
    
    def search(
        self,
        plate: str = None,
        operator: str = None,
        start_date: datetime = None,
        end_date: datetime = None,
        limit: int = 100
    ) -> List[Vehicle]:
        """
        Búsqueda avanzada de vehículos con múltiples filtros
        
        Args:
            plate: Filtrar por patente (búsqueda parcial)
            operator: Filtrar por operador
            start_date: Fecha inicial
            end_date: Fecha final
            limit: Límite de resultados
            
        Returns:
            Lista de vehículos que coinciden con los filtros
        """
        query = Vehicle.query
        
        if plate:
            query = query.filter(Vehicle.plate.like(f'%{plate}%'))
        
        if operator:
            query = query.filter(
                (Vehicle.operator_name.like(f'%{operator}%')) |
                (Vehicle.exit_operator_name.like(f'%{operator}%'))
            )
        
        if start_date:
            query = query.filter(Vehicle.entry_time >= start_date)
        
        if end_date:
            query = query.filter(Vehicle.entry_time < end_date)
        
        return query.order_by(Vehicle.entry_time.desc()).limit(limit).all()


# Instancia global del repositorio
vehicle_repository = VehicleRepository()
