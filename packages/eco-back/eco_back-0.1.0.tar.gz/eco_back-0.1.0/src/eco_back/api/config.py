"""
Configuración para clientes API
"""
from dataclasses import dataclass
from typing import Optional, Dict


@dataclass
class APIConfig:
    """
    Configuración para el cliente API
    
    Args:
        base_url: URL base del API
        timeout: Tiempo de espera para las peticiones en segundos
        headers: Headers personalizados para las peticiones
        verify_ssl: Verificar certificados SSL
    """
    base_url: str
    timeout: int = 30
    headers: Optional[Dict[str, str]] = None
    verify_ssl: bool = True
    
    def __post_init__(self):
        """Inicialización después de crear la instancia"""
        if self.headers is None:
            self.headers = {}
        
        # Asegurar que la URL base no termine con /
        if self.base_url.endswith('/'):
            self.base_url = self.base_url[:-1]
    
    @classmethod
    def from_dict(cls, config: dict) -> "APIConfig":
        """
        Crea una instancia de APIConfig desde un diccionario
        
        Args:
            config: Diccionario con la configuración
            
        Returns:
            Instancia de APIConfig
        """
        return cls(**config)
    
    def to_dict(self) -> dict:
        """
        Convierte la configuración a diccionario
        
        Returns:
            Diccionario con la configuración
        """
        return {
            "base_url": self.base_url,
            "timeout": self.timeout,
            "headers": self.headers,
            "verify_ssl": self.verify_ssl,
        }
