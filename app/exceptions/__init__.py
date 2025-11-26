"""
Excepciones personalizadas del sistema
"""

from app.exceptions.business_exceptions import (
    BusinessException,
    VehicleNotFoundException,
    VehicleAlreadyExitedException,
    MonthlyClientExpiredException,
    MonthlyClientDuplicatedException,
    MonthlyClientNotFoundException,
    ValidationException,
    AuthorizationException
)

__all__ = [
    'BusinessException',
    'VehicleNotFoundException',
    'VehicleAlreadyExitedException',
    'MonthlyClientExpiredException',
    'MonthlyClientDuplicatedException',
    'MonthlyClientNotFoundException',
    'ValidationException',
    'AuthorizationException'
]
