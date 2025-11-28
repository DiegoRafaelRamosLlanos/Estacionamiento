"""
Servicio para lógica de negocio de vehículos
"""

from datetime import datetime
from app.models.models import Vehicle
from app.repositories.vehicle_repository import vehicle_repository
from app.repositories.monthly_repository import monthly_client_repository
from app.services.barcode_service import barcode_service
from app.services.pricing_service import pricing_service
from app.validators.vehicle_validator import VehicleValidator
from app.exceptions import (
    VehicleNotFoundException,
    VehicleAlreadyExitedException,
    MonthlyClientExpiredException
)
from app.printer_service import printer_service


class VehicleService:
    """
    Servicio para gestión de vehículos
    
    Encapsula toda la lógica de negocio relacionada con
    entrada y salida de vehículos.
    """
    
    def __init__(self):
        self.vehicle_repo = vehicle_repository
        self.monthly_repo = monthly_client_repository
        self.barcode_service = barcode_service
        self.pricing_service = pricing_service
        self.printer = printer_service
    
    def register_entry(self, plate: str, vehicle_type: str, operator_name: str) -> dict:
        """
        Registra la entrada de un vehículo
        
        Args:
            plate: Patente del vehículo
            vehicle_type: Tipo de vehículo ('auto' o 'moto')
            operator_name: Nombre del operador que registra
            
        Returns:
            Dict con información del registro y resultado de impresión
            
        Raises:
            ValidationException: Si los datos son inválidos
            MonthlyClientExpiredException: Si es cliente mensual vencido
        """
        # Validar datos
        validated = VehicleValidator.validate_vehicle_entry({
            'plate': plate,
            'type': vehicle_type
        })
        
        # Verificar si es cliente mensual
        monthly_client = self.monthly_repo.find_by_plate(validated['plate'])
        is_monthly = False
        
        if monthly_client:
            # Verificar si está vencido
            if monthly_client.is_expired():
                raise MonthlyClientExpiredException(
                    plate=validated['plate'],
                    expiration_date=monthly_client.get_expiration_date().strftime('%d/%m/%Y')
                )
            is_monthly = True
        
        # Crear vehículo
        vehicle = Vehicle(
            plate=validated['plate'],
            type=validated['type'],
            is_monthly=is_monthly,
            operator_name=operator_name,
            entry_time=datetime.now()
        )
        
        # Guardar en BD
        self.vehicle_repo.create(vehicle)
        self.vehicle_repo.save()
        
        # Generar código de barras
        barcode_code = self.barcode_service.generate_barcode_base64(str(vehicle.id))
        vehicle.qr_code = barcode_code  # Mantenemos el nombre de columna para compatibilidad
        self.vehicle_repo.save()
        
        # Intentar imprimir ticket
        print_success = False
        print_message = ""
        try:
            print_success, print_message = self.printer.print_entry_ticket(vehicle)
        except Exception as e:
            print_message = f"Error al imprimir: {str(e)}"
        
        return {
            'vehicle_id': vehicle.id,
            'plate': vehicle.plate,
            'type': vehicle.type,
            'entry_time': vehicle.entry_time,
            'qr_code': barcode_code,  # Mantenemos el nombre para compatibilidad con frontend
            'is_monthly': is_monthly,
            'operator': operator_name,
            'printed': print_success,
            'print_message': print_message
        }
    
    def register_exit(
        self,
        vehicle_id: int = None,
        plate: str = None,
        operator_name: str = None
    ) -> dict:
        """
        Registra la salida de un vehículo
        
        Args:
            vehicle_id: ID del vehículo (opcional si se provee plate)
            plate: Patente del vehículo (opcional si se provee vehicle_id)
            operator_name: Nombre del operador que registra
            
        Returns:
            Dict con información de la salida y costos
            
        Raises:
            VehicleNotFoundException: Si no se encuentra el vehículo
            VehicleAlreadyExitedException: Si el vehículo ya salió
        """
        # Buscar vehículo
        if vehicle_id:
            vehicle = self.vehicle_repo.get_by_id(vehicle_id)
        elif plate:
            validated_plate = VehicleValidator.validate_plate(plate)
            vehicle = self.vehicle_repo.find_active_by_plate(validated_plate)
        else:
            raise VehicleNotFoundException()
        
        if not vehicle:
            if vehicle_id:
                raise VehicleNotFoundException(vehicle_id=vehicle_id)
            else:
                raise VehicleNotFoundException(plate=plate)
        
        # Verificar si ya salió
        if vehicle.exit_time:
            raise VehicleAlreadyExitedException(
                vehicle_id=vehicle.id,
                exit_time=vehicle.exit_time.strftime('%d/%m/%Y %H:%M:%S')
            )
        
        # Registrar salida
        vehicle.exit_time = datetime.now()
        vehicle.exit_operator_name = operator_name
        
        # Calcular costo
        cost = self.pricing_service.calculate_cost(vehicle)
        vehicle.total_cost = cost
        
        # Guardar
        self.vehicle_repo.save()
        
        # Calcular tiempo de permanencia
        time_diff = vehicle.exit_time - vehicle.entry_time
        total_minutes = int(time_diff.total_seconds() / 60)
        hours = total_minutes // 60
        minutes = total_minutes % 60
        hours_decimal = total_minutes / 60
        
        # Intentar imprimir ticket de salida
        print_success = False
        print_message = ""
        try:
            print_success, print_message = self.printer.print_exit_ticket(vehicle)
        except Exception as e:
            print_message = f"Error al imprimir: {str(e)}"
        
        return {
            'vehicle_id': vehicle.id,
            'plate': vehicle.plate,
            'type': vehicle.type,
            'entry_time': vehicle.entry_time,
            'exit_time': vehicle.exit_time,
            'total_minutes': total_minutes,
            'hours': hours,
            'minutes': minutes,
            'hours_decimal': round(hours_decimal, 2),
            'cost': cost,
            'is_monthly': vehicle.is_monthly,
            'operator': vehicle.operator_name,
            'exit_operator': operator_name,
            'printed': print_success,
            'print_message': print_message
        }
    
    def get_active_vehicles(self) -> list:
        """
        Obtiene todos los vehículos activos
        
        Returns:
            Lista de vehículos sin salida
        """
        return self.vehicle_repo.get_active_vehicles()
    
    def get_vehicle_by_id(self, vehicle_id: int) -> Vehicle:
        """
        Obtiene un vehículo por ID
        
        Args:
            vehicle_id: ID del vehículo
            
        Returns:
            Vehículo
            
        Raises:
            VehicleNotFoundException: Si no existe
        """
        vehicle = self.vehicle_repo.get_by_id(vehicle_id)
        if not vehicle:
            raise VehicleNotFoundException(vehicle_id=vehicle_id)
        return vehicle


# Instancia global del servicio
vehicle_service = VehicleService()
