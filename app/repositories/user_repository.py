"""
Repositorio para operaciones de usuarios
"""

from typing import List, Optional
from app.models.models import User
from app.repositories.base_repository import BaseRepository


class UserRepository(BaseRepository[User]):
    """Repositorio para operaciones específicas de usuarios"""
    
    def __init__(self):
        super().__init__(User)
    
    def find_by_username(self, username: str) -> Optional[User]:
        """
        Busca un usuario por nombre de usuario
        
        Args:
            username: Nombre de usuario
            
        Returns:
            Usuario o None
        """
        return User.query.filter_by(username=username).first()
    
    def exists_by_username(self, username: str) -> bool:
        """
        Verifica si existe un usuario con el username dado
        
        Args:
            username: Username a verificar
            
        Returns:
            True si existe, False en caso contrario
        """
        return self.find_by_username(username) is not None
    
    def get_by_role(self, role: str) -> List[User]:
        """
        Obtiene todos los usuarios con un rol específico
        
        Args:
            role: Rol a filtrar ('admin' o 'operador')
            
        Returns:
            Lista de usuarios con ese rol
        """
        return User.query.filter_by(role=role).all()
    
    def get_admins(self) -> List[User]:
        """
        Obtiene todos los administradores
        
        Returns:
            Lista de administradores
        """
        return self.get_by_role('admin')
    
    def get_operators(self) -> List[User]:
        """
        Obtiene todos los operadores
        
        Returns:
            Lista de operadores
        """
        return self.get_by_role('operador')
    
    def count_by_role(self, role: str) -> int:
        """
        Cuenta los usuarios con un rol específico
        
        Args:
            role: Rol a contar
            
        Returns:
            Número de usuarios con ese rol
        """
        return User.query.filter_by(role=role).count()


# Instancia global del repositorio
user_repository = UserRepository()
