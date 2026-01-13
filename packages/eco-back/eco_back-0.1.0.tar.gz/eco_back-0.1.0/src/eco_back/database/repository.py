"""
Repositorio base para operaciones CRUD
"""
from typing import Generic, TypeVar, List, Optional, Dict, Any
from abc import ABC, abstractmethod

from .connection import DatabaseConnection
from .models import BaseModel

T = TypeVar('T', bound=BaseModel)


class BaseRepository(ABC, Generic[T]):
    """
    Clase base para repositorios de base de datos
    
    Implementa el patrón Repository para separar la lógica de acceso a datos
    """
    
    def __init__(self, db_connection: DatabaseConnection):
        """
        Inicializa el repositorio
        
        Args:
            db_connection: Conexión a la base de datos
        """
        self.db = db_connection
    
    @property
    @abstractmethod
    def table_name(self) -> str:
        """Nombre de la tabla en la base de datos"""
        pass
    
    @abstractmethod
    def _row_to_model(self, row: Dict[str, Any]) -> T:
        """
        Convierte una fila de la base de datos a un modelo
        
        Args:
            row: Fila de la base de datos
            
        Returns:
            Instancia del modelo
        """
        pass
    
    def find_by_id(self, id: int) -> Optional[T]:
        """
        Busca un registro por su ID
        
        Args:
            id: ID del registro
            
        Returns:
            Instancia del modelo o None si no se encuentra
        """
        query = f"SELECT * FROM {self.table_name} WHERE id = %s"
        results = self.db.execute_query(query, (id,))
        
        if results:
            return self._row_to_model(results[0])
        return None
    
    def find_all(self, limit: Optional[int] = None, offset: int = 0) -> List[T]:
        """
        Obtiene todos los registros
        
        Args:
            limit: Número máximo de registros a retornar
            offset: Número de registros a saltar
            
        Returns:
            Lista de instancias del modelo
        """
        query = f"SELECT * FROM {self.table_name}"
        
        if limit:
            query += f" LIMIT {limit} OFFSET {offset}"
        
        results = self.db.execute_query(query)
        return [self._row_to_model(row) for row in results]
    
    def find_where(self, conditions: Dict[str, Any]) -> List[T]:
        """
        Busca registros que cumplan ciertas condiciones
        
        Args:
            conditions: Diccionario con las condiciones (campo: valor)
            
        Returns:
            Lista de instancias del modelo
        """
        where_clauses = [f"{field} = %s" for field in conditions.keys()]
        where_sql = " AND ".join(where_clauses)
        
        query = f"SELECT * FROM {self.table_name} WHERE {where_sql}"
        results = self.db.execute_query(query, tuple(conditions.values()))
        
        return [self._row_to_model(row) for row in results]
    
    @abstractmethod
    def create(self, model: T) -> T:
        """
        Crea un nuevo registro
        
        Args:
            model: Instancia del modelo a crear
            
        Returns:
            Instancia del modelo creado con su ID
        """
        pass
    
    @abstractmethod
    def update(self, id: int, model: T) -> Optional[T]:
        """
        Actualiza un registro existente
        
        Args:
            id: ID del registro a actualizar
            model: Instancia del modelo con los nuevos datos
            
        Returns:
            Instancia del modelo actualizado o None si no se encuentra
        """
        pass
    
    def delete(self, id: int) -> bool:
        """
        Elimina un registro por su ID
        
        Args:
            id: ID del registro a eliminar
            
        Returns:
            True si se eliminó, False si no se encontró
        """
        query = f"DELETE FROM {self.table_name} WHERE id = %s"
        affected_rows = self.db.execute_update(query, (id,))
        return affected_rows > 0
    
    def count(self) -> int:
        """
        Cuenta el número total de registros
        
        Returns:
            Número de registros en la tabla
        """
        query = f"SELECT COUNT(*) as total FROM {self.table_name}"
        result = self.db.execute_query(query)
        return result[0]['total'] if result else 0
