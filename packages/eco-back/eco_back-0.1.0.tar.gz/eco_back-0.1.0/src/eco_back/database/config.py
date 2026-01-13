"""
Configuración de base de datos
"""
from dataclasses import dataclass
from typing import Optional


@dataclass
class DatabaseConfig:
    """
    Configuración para la conexión a la base de datos
    
    Args:
        host: Dirección del servidor de base de datos
        port: Puerto de conexión
        database: Nombre de la base de datos
        user: Usuario de la base de datos
        password: Contraseña del usuario
        charset: Conjunto de caracteres (default: utf8mb4)
        connect_timeout: Tiempo de espera para la conexión en segundos
    """
    host: str
    port: int
    database: str
    user: str
    password: str
    charset: str = "utf8mb4"
    connect_timeout: int = 10
    
    @classmethod
    def from_dict(cls, config: dict) -> "DatabaseConfig":
        """
        Crea una instancia de DatabaseConfig desde un diccionario
        
        Args:
            config: Diccionario con la configuración
            
        Returns:
            Instancia de DatabaseConfig
        """
        return cls(**config)
    
    def to_dict(self) -> dict:
        """
        Convierte la configuración a diccionario
        
        Returns:
            Diccionario con la configuración
        """
        return {
            "host": self.host,
            "port": self.port,
            "database": self.database,
            "user": self.user,
            "password": self.password,
            "charset": self.charset,
            "connect_timeout": self.connect_timeout,
        }
