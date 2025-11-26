"""
Repositorio para operaciones de asistencias
"""

from datetime import datetime
from typing import List, Optional
from app.models.models import Attendance
from app.repositories.base_repository import BaseRepository
from app import db


class AttendanceRepository(BaseRepository[Attendance]):
    """Repositorio para operaciones específicas de asistencias"""
    
    def __init__(self):
        super().__init__(Attendance)
    
    def get_today_attendances(self) -> List[Attendance]:
        """
        Obtiene todas las asistencias del día actual
        
        Returns:
            Lista de asistencias de hoy
        """
        today = datetime.now().date()
        return Attendance.query.filter(
            db.func.date(Attendance.login_time) == today
        ).order_by(Attendance.login_time.desc()).all()
    
    def get_active_attendances(self) -> List[Attendance]:
        """
        Obtiene asistencias activas (usuarios actualmente trabajando)
        
        Returns:
            Lista de asistencias sin logout
        """
        return Attendance.query.filter_by(logout_time=None).all()
    
    def get_by_user(self, user_id: int) -> List[Attendance]:
        """
        Obtiene todas las asistencias de un usuario
        
        Args:
            user_id: ID del usuario
            
        Returns:
            Lista de asistencias del usuario
        """
        return Attendance.query.filter_by(user_id=user_id).order_by(
            Attendance.login_time.desc()
        ).all()
    
    def get_by_user_and_date_range(
        self,
        user_id: int,
        start_date: datetime,
        end_date: datetime = None
    ) -> List[Attendance]:
        """
        Obtiene asistencias de un usuario en un rango de fechas
        
        Args:
            user_id: ID del usuario
            start_date: Fecha inicial
            end_date: Fecha final (opcional)
            
        Returns:
            Lista de asistencias en el rango
        """
        query = Attendance.query.filter_by(user_id=user_id)
        query = query.filter(Attendance.login_time >= start_date)
        
        if end_date:
            query = query.filter(Attendance.login_time < end_date)
        
        return query.order_by(Attendance.login_time.desc()).all()
    
    def get_by_date_range(
        self,
        start_date: datetime,
        end_date: datetime = None
    ) -> List[Attendance]:
        """
        Obtiene todas las asistencias en un rango de fechas
        
        Args:
            start_date: Fecha inicial
            end_date: Fecha final (opcional)
            
        Returns:
            Lista de asistencias en el rango
        """
        query = Attendance.query.filter(Attendance.login_time >= start_date)
        
        if end_date:
            query = query.filter(Attendance.login_time < end_date)
        
        return query.order_by(Attendance.login_time.desc()).all()
    
    def get_active_by_user(self, user_id: int) -> Optional[Attendance]:
        """
        Obtiene la asistencia activa de un usuario específico
        
        Args:
            user_id: ID del usuario
            
        Returns:
            Asistencia activa o None
        """
        return Attendance.query.filter_by(
            user_id=user_id,
            logout_time=None
        ).first()


# Instancia global del repositorio
attendance_repository = AttendanceRepository()
