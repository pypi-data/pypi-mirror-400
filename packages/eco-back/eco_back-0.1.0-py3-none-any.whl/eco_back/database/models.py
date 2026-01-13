"""
Modelos base para la base de datos
"""
from abc import ABC, abstractmethod
from typing import Dict, Any, Optional, List


class BaseModel(ABC):
    """
    Clase base para modelos de base de datos
    """
    
    @abstractmethod
    def to_dict(self) -> Dict[str, Any]:
        """
        Convierte el modelo a diccionario
        
        Returns:
            Diccionario con los datos del modelo
        """
        pass
    
    @classmethod
    @abstractmethod
    def from_dict(cls, data: Dict[str, Any]) -> "BaseModel":
        """
        Crea una instancia del modelo desde un diccionario
        
        Args:
            data: Diccionario con los datos
            
        Returns:
            Instancia del modelo
        """
        pass
    
    @classmethod
    @abstractmethod
    def from_db_row(cls, row: Dict[str, Any]) -> "BaseModel":
        """
        Crea una instancia del modelo desde una fila de la base de datos
        
        Args:
            row: Diccionario con los datos de la fila
            
        Returns:
            Instancia del modelo
        """
        pass
