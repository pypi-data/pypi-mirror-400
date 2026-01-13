"""
Cliente para operaciones de registro y consecutivos UNP
"""
from typing import Optional
import logging

from .client import APIClient
from .config import APIConfig

logger = logging.getLogger(__name__)


class Consecutivo:
    """
    Cliente para obtener consecutivos de la API UNP
    
    Maneja operaciones relacionadas con la obtención de consecutivos.
    
    Ejemplo:
        >>> from eco_back.api import Consecutivo
        >>> 
        >>> client = Consecutivo(base_url="https://api.unp.com")
        >>> numero = client.obtener(origen=1)
        >>> print(numero)
    """
    
    def __init__(self, base_url: str, timeout: int = 30, verify_ssl: bool = True):
        """
        Inicializa el cliente de Consecutivos
        
        Args:
            base_url: URL base del API UNP
            timeout: Tiempo de espera para las peticiones
            verify_ssl: Verificar certificados SSL
        """
        config = APIConfig(
            base_url=base_url,
            timeout=timeout,
            verify_ssl=verify_ssl
        )
        self.client = APIClient(config)
    
    def obtener(self, origen: int = 1) -> Optional[int]:
        """
        Obtiene un consecutivo desde la API UNP
        
        Args:
            origen: Identificador del origen (default: 1)
            
        Returns:
            Número consecutivo o None si hay error
            
        Example:
            >>> client = Consecutivo(base_url="https://api.unp.com")
            >>> numero = client.obtener(origen=1)
            >>> if numero:
            ...     print(f"Consecutivo obtenido: {numero}")
        """
        try:
            endpoint = f'api-auth/users/consecutivos/{origen}/'
            response = self.client.get(endpoint, raise_for_status=False)
            
            if response and isinstance(response, dict):
                consecutivo = response.get('consecutivo')
                logger.info(f"Consecutivo obtenido: {consecutivo} para origen {origen}")
                return consecutivo
            else:
                logger.warning(f"No se pudo obtener consecutivo para origen {origen}")
                return None
                
        except Exception as e:
            logger.error(f"Error al obtener consecutivo: {e}")
            return None
    
    # Alias para compatibilidad
    def obtener_consecutivo(self, origen: int = 1) -> Optional[int]:
        """Alias de obtener() para compatibilidad"""
        return self.obtener(origen)
    
    def close(self):
        """Cierra el cliente"""
        self.client.close()
    
    def __enter__(self):
        """Context manager entry"""
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit"""
        self.close()
        return False
