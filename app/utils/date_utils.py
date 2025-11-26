"""
Utilidades para manejo de fechas y tiempos
"""

from datetime import datetime, timedelta
from typing import Tuple


class DateUtils:
    """Helper para operaciones comunes con fechas"""
    
    # Formatos comunes
    FORMAT_DATETIME = '%Y-%m-%d %H:%M:%S'
    FORMAT_DATE = '%Y-%m-%d'
    FORMAT_TIME = '%H:%M:%S'
    FORMAT_DISPLAY_DATETIME = '%d/%m/%Y %H:%M:%S'
    FORMAT_DISPLAY_DATE = '%d/%m/%Y'
    
    @staticmethod
    def format_datetime(dt: datetime, format_type: str = 'datetime') -> str:
        """
        Formatea una fecha/hora de forma consistente
        
        Args:
            dt: Objeto datetime a formatear
            format_type: Tipo de formato ('datetime', 'date', 'time', 'display_datetime', 'display_date')
            
        Returns:
            String con fecha formateada
        """
        if not dt:
            return ''
        
        formats = {
            'datetime': DateUtils.FORMAT_DATETIME,
            'date': DateUtils.FORMAT_DATE,
            'time': DateUtils.FORMAT_TIME,
            'display_datetime': DateUtils.FORMAT_DISPLAY_DATETIME,
            'display_date': DateUtils.FORMAT_DISPLAY_DATE
        }
        
        fmt = formats.get(format_type, DateUtils.FORMAT_DATETIME)
        return dt.strftime(fmt)
    
    @staticmethod
    def calculate_time_difference(start: datetime, end: datetime = None) -> dict:
        """
        Calcula la diferencia entre dos fechas
        
        Args:
            start: Fecha inicial
            end: Fecha final (si es None, usa datetime.now())
            
        Returns:
            Dict con total_minutes, hours, minutes, hours_decimal
        """
        if not end:
            end = datetime.now()
        
        time_diff = end - start
        total_minutes = int(time_diff.total_seconds() / 60)
        hours = total_minutes // 60
        minutes = total_minutes % 60
        hours_decimal = total_minutes / 60
        
        return {
            'total_minutes': total_minutes,
            'hours': hours,
            'minutes': minutes,
            'hours_decimal': round(hours_decimal, 2),
            'total_seconds': int(time_diff.total_seconds())
        }
    
    @staticmethod
    def format_duration(total_minutes: int) -> str:
        """
        Formatea una duración en minutos a texto legible
        
        Args:
            total_minutes: Total de minutos
            
        Returns:
            String formateado (ej: "2h 30min")
        """
        hours = total_minutes // 60
        minutes = total_minutes % 60
        
        if hours > 0:
            return f"{hours}h {minutes}min"
        else:
            return f"{minutes}min"
    
    @staticmethod
    def get_today_range() -> Tuple[datetime, datetime]:
        """
        Obtiene el rango de inicio y fin del día actual
        
        Returns:
            Tupla (start_of_day, end_of_day)
        """
        today = datetime.now().date()
        start_of_day = datetime.combine(today, datetime.min.time())
        end_of_day = datetime.combine(today, datetime.max.time())
        
        return start_of_day, end_of_day
    
    @staticmethod
    def parse_date(date_string: str, format_type: str = 'date') -> datetime:
        """
        Parsea un string a datetime
        
        Args:
            date_string: String con la fecha
            format_type: Tipo de formato esperado
            
        Returns:
            Objeto datetime
        """
        formats = {
            'datetime': DateUtils.FORMAT_DATETIME,
            'date': DateUtils.FORMAT_DATE,
            'time': DateUtils.FORMAT_TIME
        }
        
        fmt = formats.get(format_type, DateUtils.FORMAT_DATE)
        return datetime.strptime(date_string, fmt)
    
    @staticmethod
    def add_months(dt: datetime, months: int) -> datetime:
        """
        Suma meses a una fecha (aproximado: 30 días por mes)
        
        Args:
            dt: Fecha base
            months: Número de meses a sumar
            
        Returns:
            Nueva fecha
        """
        days = 30 * months
        return dt + timedelta(days=days)
    
    @staticmethod
    def is_same_day(dt1: datetime, dt2: datetime) -> bool:
        """
        Verifica si dos fechas son del mismo día
        
        Args:
            dt1: Primera fecha
            dt2: Segunda fecha
            
        Returns:
            True si son del mismo día
        """
        return dt1.date() == dt2.date()
