"""
Repositorio para operaciones de clientes mensuales
"""

from datetime import datetime
from typing import List, Optional
from app.models.models import MonthlyClient
from app.repositories.base_repository import BaseRepository


class MonthlyClientRepository(BaseRepository[MonthlyClient]):
    """Repositorio para operaciones específicas de clientes mensuales"""
    
    def __init__(self):
        super().__init__(MonthlyClient)
    
    def find_by_plate(self, plate: str) -> Optional[MonthlyClient]:
        """
        Busca un cliente mensual por patente
        
        Args:
            plate: Patente del cliente
            
        Returns:
            Cliente mensual o None
        """
        return MonthlyClient.query.filter_by(plate=plate).first()
    
    def exists_by_plate(self, plate: str) -> bool:
        """
        Verifica si existe un cliente con la patente dada
        
        Args:
            plate: Patente a verificar
            
        Returns:
            True si existe, False en caso contrario
        """
        return self.find_by_plate(plate) is not None
    
    def get_active_clients(self) -> List[MonthlyClient]:
        """
        Obtiene todos los clientes con abono activo (no vencido)
        
        Returns:
            Lista de clientes activos
        """
        all_clients = self.get_all()
        return [client for client in all_clients if not client.is_expired()]
    
    def get_expired_clients(self) -> List[MonthlyClient]:
        """
        Obtiene todos los clientes con abono vencido
        
        Returns:
            Lista de clientes vencidos
        """
        all_clients = self.get_all()
        return [client for client in all_clients if client.is_expired()]
    
    def get_expiring_soon(self, days: int = 7) -> List[MonthlyClient]:
        """
        Obtiene clientes cuyo abono vence en los próximos X días
        
        Args:
            days: Número de días de anticipación
            
        Returns:
            Lista de clientes próximos a vencer
        """
        all_clients = self.get_all()
        expiring_clients = []
        
        for client in all_clients:
            if not client.is_expired():
                days_remaining = client.days_remaining()
                if 0 < days_remaining <= days:
                    expiring_clients.append(client)
        
        return expiring_clients
    
    def get_by_operator(self, operator_name: str) -> List[MonthlyClient]:
        """
        Obtiene clientes registrados por un operador específico
        
        Args:
            operator_name: Nombre del operador
            
        Returns:
            Lista de clientes
        """
        return MonthlyClient.query.filter_by(registered_by=operator_name).all()
    
    def get_by_vehicle_type(self, vehicle_type: str) -> List[MonthlyClient]:
        """
        Obtiene clientes por tipo de vehículo
        
        Args:
            vehicle_type: Tipo de vehículo ('auto' o 'moto')
            
        Returns:
            Lista de clientes
        """
        return MonthlyClient.query.filter_by(vehicle_type=vehicle_type).all()
    
    def search(self, query: str) -> List[MonthlyClient]:
        """
        Búsqueda de clientes por patente u owner
        
        Args:
            query: Texto de búsqueda
            
        Returns:
            Lista de clientes que coinciden
        """
        search_pattern = f'%{query}%'
        return MonthlyClient.query.filter(
            (MonthlyClient.plate.like(search_pattern)) |
            (MonthlyClient.owner_name.like(search_pattern))
        ).all()


# Instancia global del repositorio
monthly_client_repository = MonthlyClientRepository()
