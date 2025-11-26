"""
Repositorios para acceso a datos
"""

from app.repositories.base_repository import BaseRepository
from app.repositories.vehicle_repository import VehicleRepository
from app.repositories.monthly_repository import MonthlyClientRepository
from app.repositories.user_repository import UserRepository
from app.repositories.attendance_repository import AttendanceRepository

__all__ = [
    'BaseRepository',
    'VehicleRepository',
    'MonthlyClientRepository',
    'UserRepository',
    'AttendanceRepository'
]
