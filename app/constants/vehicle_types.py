"""
Tipos de vehículos y configuraciones relacionadas
"""

from enum import Enum


class VehicleType(str, Enum):
    """Tipos de vehículos soportados por el sistema"""
    AUTO = 'auto'
    MOTO = 'moto'
    
    @property
    def display_name(self) -> str:
        """Nombre para mostrar al usuario"""
        names = {
            self.AUTO: 'Auto',
            self.MOTO: 'Moto'
        }
        return names.get(self, self.value)
    
    @property
    def icon(self) -> str:
        """Icono o emoji representativo"""
        icons = {
            self.AUTO: '🚗',
            self.MOTO: '🏍️'
        }
        return icons.get(self, '🚙')
    
    @classmethod
    def is_valid(cls, value: str) -> bool:
        """Verifica si un valor es un tipo de vehículo válido"""
        try:
            cls(value)
            return True
        except ValueError:
            return False
    
    @classmethod
    def get_all_values(cls) -> list:
        """Retorna lista de todos los valores válidos"""
        return [vtype.value for vtype in cls]
