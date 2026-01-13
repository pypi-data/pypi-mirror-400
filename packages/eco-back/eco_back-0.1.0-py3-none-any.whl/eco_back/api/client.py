"""
Cliente HTTP para consumir APIs
"""
from typing import Optional, Dict, Any, Union
import logging

try:
    import requests
    from requests.exceptions import RequestException, Timeout, HTTPError
    REQUESTS_AVAILABLE = True
except ImportError:
    REQUESTS_AVAILABLE = False

from .config import APIConfig

logger = logging.getLogger(__name__)


class APIClient:
    """
    Cliente HTTP genérico para consumir APIs REST
    
    Ejemplo:
        >>> from eco_back.api import APIConfig, APIClient
        >>> 
        >>> config = APIConfig(base_url="https://api.ejemplo.com")
        >>> client = APIClient(config)
        >>> 
        >>> # GET request
        >>> data = client.get("/users/1")
        >>> 
        >>> # POST request
        >>> response = client.post("/users", data={"name": "Juan"})
    """
    
    def __init__(self, config: APIConfig):
        """
        Inicializa el cliente API
        
        Args:
            config: Configuración del API
            
        Raises:
            ImportError: Si requests no está instalado
        """
        if not REQUESTS_AVAILABLE:
            raise ImportError(
                "requests no está instalado. Instálalo con: pip install requests"
            )
        
        self.config = config
        self.session = requests.Session()
        
        # Configurar headers por defecto
        if self.config.headers:
            self.session.headers.update(self.config.headers)
    
    def _build_url(self, endpoint: str) -> str:
        """
        Construye la URL completa
        
        Args:
            endpoint: Endpoint del API
            
        Returns:
            URL completa
        """
        # Asegurar que el endpoint empiece con /
        if not endpoint.startswith('/'):
            endpoint = f'/{endpoint}'
        
        return f'{self.config.base_url}{endpoint}'
    
    def _handle_response(
        self,
        response: requests.Response,
        raise_for_status: bool = True
    ) -> Optional[Union[Dict[str, Any], list, str]]:
        """
        Procesa la respuesta HTTP
        
        Args:
            response: Respuesta HTTP
            raise_for_status: Si debe lanzar excepción en errores HTTP
            
        Returns:
            Datos parseados de la respuesta o None
        """
        if raise_for_status:
            try:
                response.raise_for_status()
            except HTTPError as e:
                logger.error(f"Error HTTP {response.status_code}: {e}")
                raise
        
        if response.status_code == 204:  # No Content
            return None
        
        try:
            return response.json()
        except ValueError:
            # Si no es JSON, retornar el texto
            return response.text
    
    def get(
        self,
        endpoint: str,
        params: Optional[Dict[str, Any]] = None,
        headers: Optional[Dict[str, str]] = None,
        timeout: Optional[int] = None,
        raise_for_status: bool = True
    ) -> Optional[Union[Dict[str, Any], list, str]]:
        """
        Realiza una petición GET
        
        Args:
            endpoint: Endpoint del API
            params: Parámetros query string
            headers: Headers adicionales
            timeout: Tiempo de espera (usa el default si no se especifica)
            raise_for_status: Si debe lanzar excepción en errores HTTP
            
        Returns:
            Respuesta parseada
            
        Raises:
            RequestException: Si hay error en la petición
        """
        url = self._build_url(endpoint)
        timeout = timeout or self.config.timeout
        
        try:
            logger.debug(f"GET {url}")
            response = self.session.get(
                url,
                params=params,
                headers=headers,
                timeout=timeout,
                verify=self.config.verify_ssl
            )
            return self._handle_response(response, raise_for_status)
        except Timeout:
            logger.error(f"Timeout al hacer GET a {url}")
            raise
        except RequestException as e:
            logger.error(f"Error en GET {url}: {e}")
            raise
    
    def post(
        self,
        endpoint: str,
        data: Optional[Dict[str, Any]] = None,
        json: Optional[Dict[str, Any]] = None,
        headers: Optional[Dict[str, str]] = None,
        timeout: Optional[int] = None,
        raise_for_status: bool = True
    ) -> Optional[Union[Dict[str, Any], list, str]]:
        """
        Realiza una petición POST
        
        Args:
            endpoint: Endpoint del API
            data: Datos form-encoded
            json: Datos JSON
            headers: Headers adicionales
            timeout: Tiempo de espera
            raise_for_status: Si debe lanzar excepción en errores HTTP
            
        Returns:
            Respuesta parseada
        """
        url = self._build_url(endpoint)
        timeout = timeout or self.config.timeout
        
        try:
            logger.debug(f"POST {url}")
            response = self.session.post(
                url,
                data=data,
                json=json,
                headers=headers,
                timeout=timeout,
                verify=self.config.verify_ssl
            )
            return self._handle_response(response, raise_for_status)
        except RequestException as e:
            logger.error(f"Error en POST {url}: {e}")
            raise
    
    def put(
        self,
        endpoint: str,
        data: Optional[Dict[str, Any]] = None,
        json: Optional[Dict[str, Any]] = None,
        headers: Optional[Dict[str, str]] = None,
        timeout: Optional[int] = None,
        raise_for_status: bool = True
    ) -> Optional[Union[Dict[str, Any], list, str]]:
        """
        Realiza una petición PUT
        
        Args:
            endpoint: Endpoint del API
            data: Datos form-encoded
            json: Datos JSON
            headers: Headers adicionales
            timeout: Tiempo de espera
            raise_for_status: Si debe lanzar excepción en errores HTTP
            
        Returns:
            Respuesta parseada
        """
        url = self._build_url(endpoint)
        timeout = timeout or self.config.timeout
        
        try:
            logger.debug(f"PUT {url}")
            response = self.session.put(
                url,
                data=data,
                json=json,
                headers=headers,
                timeout=timeout,
                verify=self.config.verify_ssl
            )
            return self._handle_response(response, raise_for_status)
        except RequestException as e:
            logger.error(f"Error en PUT {url}: {e}")
            raise
    
    def delete(
        self,
        endpoint: str,
        headers: Optional[Dict[str, str]] = None,
        timeout: Optional[int] = None,
        raise_for_status: bool = True
    ) -> Optional[Union[Dict[str, Any], list, str]]:
        """
        Realiza una petición DELETE
        
        Args:
            endpoint: Endpoint del API
            headers: Headers adicionales
            timeout: Tiempo de espera
            raise_for_status: Si debe lanzar excepción en errores HTTP
            
        Returns:
            Respuesta parseada
        """
        url = self._build_url(endpoint)
        timeout = timeout or self.config.timeout
        
        try:
            logger.debug(f"DELETE {url}")
            response = self.session.delete(
                url,
                headers=headers,
                timeout=timeout,
                verify=self.config.verify_ssl
            )
            return self._handle_response(response, raise_for_status)
        except RequestException as e:
            logger.error(f"Error en DELETE {url}: {e}")
            raise
    
    def close(self):
        """Cierra la sesión"""
        if self.session:
            self.session.close()
    
    def __enter__(self):
        """Context manager entry"""
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit"""
        self.close()
        return False
