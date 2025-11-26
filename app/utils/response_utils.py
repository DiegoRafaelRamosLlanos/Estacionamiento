"""
Utilidades para generar respuestas HTTP estandarizadas
"""

from flask import jsonify
from typing import Any, Dict


class ResponseUtils:
    """Helper para crear respuestas JSON consistentes"""
    
    @staticmethod
    def success(data: Any = None, message: str = None, status_code: int = 200) -> tuple:
        """
        Crea una respuesta de éxito estandarizada
        
        Args:
            data: Datos a incluir en la respuesta
            message: Mensaje opcional de éxito
            status_code: Código HTTP (default: 200)
            
        Returns:
            Tupla (response, status_code) para Flask
        """
        response_data = {
            'success': True
        }
        
        if message:
            response_data['message'] = message
        
        if data is not None:
            # Si data es un dict, fusionarlo con response_data
            if isinstance(data, dict):
                response_data.update(data)
            else:
                response_data['data'] = data
        
        return jsonify(response_data), status_code
    
    @staticmethod
    def error(message: str, code: str = None, status_code: int = 400, **kwargs) -> tuple:
        """
        Crea una respuesta de error estandarizada
        
        Args:
            message: Mensaje de error
            code: Código de error opcional
            status_code: Código HTTP (default: 400)
            **kwargs: Datos adicionales a incluir
            
        Returns:
            Tupla (response, status_code) para Flask
        """
        response_data = {
            'success': False,
            'message': message
        }
        
        if code:
            response_data['error'] = code
        
        # Agregar cualquier dato adicional
        response_data.update(kwargs)
        
        return jsonify(response_data), status_code
    
    @staticmethod
    def validation_error(field: str, message: str, status_code: int = 400) -> tuple:
        """
        Crea una respuesta de error de validación
        
        Args:
            field: Campo que falló la validación
            message: Mensaje de error
            status_code: Código HTTP (default: 400)
            
        Returns:
            Tupla (response, status_code) para Flask
        """
        return ResponseUtils.error(
            message=message,
            code='VALIDATION_ERROR',
            status_code=status_code,
            field=field
        )
    
    @staticmethod
    def not_found(resource: str = 'Recurso', status_code: int = 404) -> tuple:
        """
        Crea una respuesta de recurso no encontrado
        
        Args:
            resource: Nombre del recurso no encontrado
            status_code: Código HTTP (default: 404)
            
        Returns:
            Tupla (response, status_code) para Flask
        """
        return ResponseUtils.error(
            message=f'{resource} no encontrado',
            code='NOT_FOUND',
            status_code=status_code
        )
    
    @staticmethod
    def unauthorized(message: str = None, status_code: int = 403) -> tuple:
        """
        Crea una respuesta de acceso no autorizado
        
        Args:
            message: Mensaje opcional
            status_code: Código HTTP (default: 403)
            
        Returns:
            Tupla (response, status_code) para Flask
        """
        default_message = 'No tiene permisos para realizar esta operación'
        return ResponseUtils.error(
            message=message or default_message,
            code='UNAUTHORIZED',
            status_code=status_code
        )
    
    @staticmethod
    def from_exception(exception: Exception, status_code: int = 500) -> tuple:
        """
        Crea una respuesta de error desde una excepción
        
        Args:
            exception: Excepción a convertir
            status_code: Código HTTP (default: 500)
            
        Returns:
            Tupla (response, status_code) para Flask
        """
        # Si la excepción tiene método to_dict, usarlo
        if hasattr(exception, 'to_dict'):
            error_data = exception.to_dict()
            return jsonify({
                'success': False,
                **error_data
            }), status_code
        
        # Si la excepción tiene código, usarlo
        code = getattr(exception, 'code', 'INTERNAL_ERROR')
        message = str(exception)
        
        return ResponseUtils.error(
            message=message,
            code=code,
            status_code=status_code
        )
