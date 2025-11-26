"""
Roles de usuario y permisos del sistema
"""

from enum import Enum


class UserRole(str, Enum):
    """Roles de usuario en el sistema"""
    ADMIN = 'admin'
    OPERADOR = 'operador'
    
    @property
    def display_name(self) -> str:
        """Nombre para mostrar al usuario"""
        names = {
            self.ADMIN: 'Administrador',
            self.OPERADOR: 'Operador'
        }
        return names.get(self, self.value)
    
    @property
    def icon(self) -> str:
        """Icono o emoji representativo"""
        icons = {
            self.ADMIN: '🔐',
            self.OPERADOR: '👤'
        }
        return icons.get(self, '👤')
    
    @property
    def permissions(self) -> set:
        """Permisos asociados al rol"""
        perms = {
            self.ADMIN: {
                'view_reports',
                'view_audit',
                'manage_users',
                'manage_monthly_clients',
                'edit_monthly_clients',
                'view_attendance',
                'export_data',
                'manage_backups'
            },
            self.OPERADOR: {
                'register_entry',
                'register_exit',
                'view_status',
                'view_monthly_clients'
            }
        }
        return perms.get(self, set())
    
    def has_permission(self, permission: str) -> bool:
        """Verifica si el rol tiene un permiso específico"""
        return permission in self.permissions
    
    @classmethod
    def is_valid(cls, value: str) -> bool:
        """Verifica si un valor es un rol válido"""
        try:
            cls(value)
            return True
        except ValueError:
            return False
    
    @classmethod
    def get_all_values(cls) -> list:
        """Retorna lista de todos los valores válidos"""
        return [role.value for role in cls]
