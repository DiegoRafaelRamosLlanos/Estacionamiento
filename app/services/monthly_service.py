"""
Servicio para lógica de negocio de clientes mensuales
"""

from datetime import datetime
from typing import Optional, List
from app.models.models import MonthlyClient
from app.repositories.monthly_repository import monthly_client_repository
from app.validators.monthly_validator import MonthlyClientValidator
from app.exceptions import (
    MonthlyClientDuplicatedException,
    MonthlyClientNotFoundException
)
from app.utils.date_utils import DateUtils


class MonthlyClientService:
    """
    Servicio para gestión de clientes mensuales
    
    Encapsula la lógica de negocio de abonos mensuales
    """
    
    def __init__(self):
        self.monthly_repo = monthly_client_repository
    
    def register_client(
        self,
        plate: str,
        owner_name: str,
        vehicle_type: str,
        start_date: str,
        duration_months: int,
        model: str = '',
        phone: str = '',
        registered_by: str = None
    ) -> MonthlyClient:
        """
        Registra un nuevo cliente mensual
        
        Args:
            plate: Patente del vehículo
            owner_name: Nombre del titular
            vehicle_type: Tipo de vehículo
            start_date: Fecha de inicio (YYYY-MM-DD)
            duration_months: Duración en meses
            model: Modelo del vehículo (opcional)
            phone: Teléfono del titular (opcional)
            registered_by: Username del operador que registra
            
        Returns:
            Cliente mensual creado
            
        Raises:
            ValidationException: Si los datos son inválidos
            MonthlyClientDuplicatedException: Si ya existe la patente
        """
        # Validar datos
        validated_data = MonthlyClientValidator.validate_monthly_client({
            'plate': plate,
            'owner_name': owner_name,
            'type': vehicle_type,
            'start_date': start_date,
            'duration_months': duration_months,
            'model': model,
            'phone': phone
        })
        
        # Verificar duplicados
        if self.monthly_repo.exists_by_plate(validated_data['plate']):
            raise MonthlyClientDuplicatedException(plate=validated_data['plate'])
        
        # Crear cliente
        client = MonthlyClient(
            plate=validated_data['plate'],
            owner_name=validated_data['owner_name'],
            vehicle_type=validated_data['vehicle_type'],
            start_date=validated_data['start_date'],
            duration_months=validated_data['duration_months'],
            model=validated_data.get('model', ''),
            phone=validated_data.get('phone', ''),
            registered_by=registered_by,
            created_at=datetime.now()
        )
        
        # Guardar
        self.monthly_repo.create(client)
        self.monthly_repo.save()
        
        return client
    
    def renew_or_extend(
        self,
        client_id: int,
        duration_months: int
    ) -> tuple:
        """
        Renueva (si está vencido) o extiende (si está activo) un abono
        
        Args:
            client_id: ID del cliente
            duration_months: Meses a agregar/renovar
            
        Returns:
            Tupla (cliente_actualizado, tipo_operacion)
            donde tipo_operacion es 'RENOVADO' o 'EXTENDIDO'
            
        Raises:
            MonthlyClientNotFoundException: Si no existe el cliente
            ValidationException: Si la duración es inválida
        """
        # Validar duración
        duration_months = MonthlyClientValidator.validate_duration(duration_months)
        
        # Buscar cliente
        client = self.monthly_repo.get_by_id(client_id)
        if not client:
            raise MonthlyClientNotFoundException(client_id=client_id)
        
        if client.is_expired():
            # RENOVAR: Cliente vencido, reiniciar desde hoy
            client.start_date = datetime.now()
            client.duration_months = duration_months
            operation_type = 'RENOVADO'
        else:
            # EXTENDER: Cliente activo, sumar duración
            client.duration_months += duration_months
            operation_type = 'EXTENDIDO'
        
        # Guardar
        self.monthly_repo.save()
        
        return client, operation_type
    
    def update_client(
        self,
        client_id: int,
        plate: str = None,
        owner_name: str = None,
        vehicle_type: str = None,
        model: str = None,
        phone: str = None
    ) -> MonthlyClient:
        """
        Actualiza los datos de un cliente mensual
        
        Args:
            client_id: ID del cliente
            plate: Nueva patente (opcional)
            owner_name: Nuevo nombre (opcional)
            vehicle_type: Nuevo tipo (opcional)
            model: Nuevo modelo (opcional)
            phone: Nuevo teléfono (opcional)
            
        Returns:
            Cliente actualizado
            
        Raises:
            MonthlyClientNotFoundException: Si no existe el cliente
            MonthlyClientDuplicatedException: Si la nueva patente ya existe
        """
        # Buscar cliente
        client = self.monthly_repo.get_by_id(client_id)
        if not client:
            raise MonthlyClientNotFoundException(client_id=client_id)
        
        # Actualizar campos proporcionados
        if plate is not None:
            validated_plate = VehicleValidator.validate_plate(plate)
            # Verificar si la nueva patente ya existe (y no es el mismo cliente)
            if validated_plate != client.plate:
                if self.monthly_repo.exists_by_plate(validated_plate):
                    raise MonthlyClientDuplicatedException(plate=validated_plate)
            client.plate = validated_plate
        
        if owner_name is not None:
            client.owner_name = MonthlyClientValidator.validate_owner_name(owner_name)
        
        if vehicle_type is not None:
            from app.validators.vehicle_validator import VehicleValidator
            client.vehicle_type = VehicleValidator.validate_vehicle_type(vehicle_type)
        
        if model is not None:
            client.model = model.strip()
        
        if phone is not None:
            client.phone = MonthlyClientValidator.validate_phone(phone)
        
        # Guardar
        self.monthly_repo.save()
        
        return client
    
    def delete_client(self, client_id: int) -> None:
        """
        Elimina un cliente mensual
        
        Args:
            client_id: ID del cliente
            
        Raises:
            MonthlyClientNotFoundException: Si no existe el cliente
        """
        client = self.monthly_repo.get_by_id(client_id)
        if not client:
            raise MonthlyClientNotFoundException(client_id=client_id)
        
        self.monthly_repo.delete(client)
        self.monthly_repo.save()
    
    def get_all_clients(self) -> List[MonthlyClient]:
        """Obtiene todos los clientes mensuales"""
        return self.monthly_repo.get_all()
    
    def get_active_clients(self) -> List[MonthlyClient]:
        """Obtiene solo los clientes con abono activo"""
        return self.monthly_repo.get_active_clients()
    
    def get_expired_clients(self) -> List[MonthlyClient]:
        """Obtiene solo los clientes con abono vencido"""
        return self.monthly_repo.get_expired_clients()
    
    def get_expiring_soon(self, days: int = 7) -> List[MonthlyClient]:
        """Obtiene clientes que vencen en los próximos X días"""
        return self.monthly_repo.get_expiring_soon(days)
    
    def check_monthly_status(self, plate: str) -> Optional[dict]:
        """
        Verifica el estado de un cliente mensual por patente
        
        Args:
            plate: Patente a verificar
            
        Returns:
            Dict con información del cliente o None si no existe
        """
        from app.validators.vehicle_validator import VehicleValidator
        validated_plate = VehicleValidator.validate_plate(plate)
        
        client = self.monthly_repo.find_by_plate(validated_plate)
        if not client:
            return None
        
        return {
            'exists': True,
            'is_expired': client.is_expired(),
            'expiration_date': client.get_expiration_date(),
            'days_remaining': client.days_remaining(),
            'client': client
        }


# Instancia global del servicio
monthly_client_service = MonthlyClientService()
