"""
Excepciones de negocio personalizadas

Estas excepciones permiten manejar errores de forma más específica
y proporcionar mensajes de error más claros al usuario.
"""


class BusinessException(Exception):
    """Excepción base para errores de lógica de negocio"""
    
    def __init__(self, message: str, code: str = None):
        self.message = message
        self.code = code or 'BUSINESS_ERROR'
        super().__init__(self.message)
    
    def to_dict(self) -> dict:
        """Convierte la excepción a un diccionario para respuestas JSON"""
        return {
            'error': self.code,
            'message': self.message
        }


class VehicleNotFoundException(BusinessException):
    """Excepción cuando no se encuentra un vehículo"""
    
    def __init__(self, vehicle_id: int = None, plate: str = None):
        if vehicle_id:
            message = f'Vehículo con ID {vehicle_id} no encontrado'
        elif plate:
            message = f'Vehículo con patente {plate} no encontrado'
        else:
            message = 'Vehículo no encontrado'
        
        super().__init__(message, 'VEHICLE_NOT_FOUND')
        self.vehicle_id = vehicle_id
        self.plate = plate


class VehicleAlreadyExitedException(BusinessException):
    """Excepción cuando se intenta registrar salida de un vehículo que ya salió"""
    
    def __init__(self, vehicle_id: int, exit_time: str = None):
        message = f'El vehículo con ID {vehicle_id} ya ha salido'
        if exit_time:
            message += f' a las {exit_time}'
        
        super().__init__(message, 'VEHICLE_ALREADY_EXITED')
        self.vehicle_id = vehicle_id
        self.exit_time = exit_time


class MonthlyClientExpiredException(BusinessException):
    """Excepción cuando el abono mensual de un cliente está vencido"""
    
    def __init__(self, plate: str, expiration_date: str = None):
        message = f'El abono mensual de la patente {plate} ha vencido'
        if expiration_date:
            message += f' desde {expiration_date}'
        message += '. Por favor, renovar.'
        
        super().__init__(message, 'MONTHLY_CLIENT_EXPIRED')
        self.plate = plate
        self.expiration_date = expiration_date


class MonthlyClientDuplicatedException(BusinessException):
    """Excepción cuando se intenta registrar un cliente mensual que ya existe"""
    
    def __init__(self, plate: str):
        message = f'Ya existe un cliente mensual con la patente {plate}'
        super().__init__(message, 'MONTHLY_CLIENT_DUPLICATED')
        self.plate = plate


class MonthlyClientNotFoundException(BusinessException):
    """Excepción cuando no se encuentra un cliente mensual"""
    
    def __init__(self, client_id: int = None, plate: str = None):
        if client_id:
            message = f'Cliente mensual con ID {client_id} no encontrado'
        elif plate:
            message = f'Cliente mensual con patente {plate} no encontrado'
        else:
            message = 'Cliente mensual no encontrado'
        
        super().__init__(message, 'MONTHLY_CLIENT_NOT_FOUND')
        self.client_id = client_id
        self.plate = plate


class ValidationException(BusinessException):
    """Excepción para errores de validación de datos"""
    
    def __init__(self, field: str, message: str):
        full_message = f'Error de validación en {field}: {message}'
        super().__init__(full_message, 'VALIDATION_ERROR')
        self.field = field
        self.validation_message = message
    
    def to_dict(self) -> dict:
        """Incluye el campo en la respuesta"""
        result = super().to_dict()
        result['field'] = self.field
        return result


class AuthorizationException(BusinessException):
    """Excepción cuando un usuario no tiene permisos para una operación"""
    
    def __init__(self, required_permission: str = None):
        if required_permission:
            message = f'No tiene permisos para: {required_permission}'
        else:
            message = 'Acceso denegado. No tiene permisos suficientes.'
        
        super().__init__(message, 'AUTHORIZATION_ERROR')
        self.required_permission = required_permission
