"""
Repositorio base con operaciones CRUD genéricas
"""

from typing import TypeVar, Generic, List, Optional
from app import db

T = TypeVar('T')


class BaseRepository(Generic[T]):
    """
    Repositorio base con operaciones CRUD comunes
    
    Esta clase proporciona una interfaz genérica para operaciones
    básicas de base de datos, reduciendo la duplicación de código.
    """
    
    def __init__(self, model_class: type):
        """
        Inicializa el repositorio con un modelo específico
        
        Args:
            model_class: Clase del modelo SQLAlchemy
        """
        self.model_class = model_class
    
    def get_by_id(self, entity_id: int) -> Optional[T]:
        """
        Obtiene una entidad por su ID
        
        Args:
            entity_id: ID de la entidad
            
        Returns:
            Entidad o None si no existe
        """
        return self.model_class.query.get(entity_id)
    
    def get_all(self) -> List[T]:
        """
        Obtiene todas las entidades
        
        Returns:
            Lista de entidades
        """
        return self.model_class.query.all()
    
    def create(self, entity: T) -> T:
        """
        Crea una nueva entidad
        
        Args:
            entity: Entidad a crear
            
        Returns:
            Entidad creada
        """
        db.session.add(entity)
        return entity
    
    def update(self, entity: T) -> T:
        """
        Actualiza una entidad existente
        
        Args:
            entity: Entidad a actualizar
            
        Returns:
            Entidad actualizada
        """
        # SQLAlchemy rastrea automáticamente los cambios
        return entity
    
    def delete(self, entity: T) -> None:
        """
        Elimina una entidad
        
        Args:
            entity: Entidad a eliminar
        """
        db.session.delete(entity)
    
    def save(self) -> None:
        """
        Guarda los cambios en la base de datos (commit)
        """
        db.session.commit()
    
    def rollback(self) -> None:
        """
        Deshace los cambios pendientes (rollback)
        """
        db.session.rollback()
    
    def exists_by_id(self, entity_id: int) -> bool:
        """
        Verifica si existe una entidad con el ID dado
        
        Args:
            entity_id: ID a verificar
            
        Returns:
            True si existe, False en caso contrario
        """
        return self.get_by_id(entity_id) is not None
    
    def count(self) -> int:
        """
        Cuenta el total de entidades
        
        Returns:
            Número total de entidades
        """
        return self.model_class.query.count()
