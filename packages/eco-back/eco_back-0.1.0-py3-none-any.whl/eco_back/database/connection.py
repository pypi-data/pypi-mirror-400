"""
Gestión de conexiones a base de datos
"""
from typing import Optional, Any, Dict, List, Union
from contextlib import contextmanager
import logging

try:
    import psycopg2
    from psycopg2 import sql
    from psycopg2.extras import RealDictCursor
    PSYCOPG2_AVAILABLE = True
except ImportError:
    PSYCOPG2_AVAILABLE = False

from .config import DatabaseConfig

logger = logging.getLogger(__name__)


class DatabaseConnection:
    """
    Clase para gestionar conexiones a base de datos
    
    Ejemplo:
        >>> config = DatabaseConfig(
        ...     host="localhost",
        ...     port=3306,
        ...     database="mi_db",
        ...     user="usuario",
        ...     password="password"
        ... )
        >>> db = DatabaseConnection(config)
        >>> db.connect()
        >>> resultado = db.execute_query("SELECT * FROM tabla")
        >>> db.close()
        
    O usando context manager:
        >>> with DatabaseConnection(config) as db:
        ...     resultado = db.execute_query("SELECT * FROM tabla")
    """
    
    def __init__(self, config: DatabaseConfig):
        """
        Inicializa la conexión a la base de datos
        
        Args:
            config: Configuración de la base de datos
        """
        self.config = config
        self.connection: Optional[Any] = None
        self.cursor: Optional[Any] = None
        
    def connect(self) -> None:
        """
        Establece la conexión a PostgreSQL
        
        Raises:
            ImportError: Si psycopg2 no está instalado
            Exception: Si no se puede establecer la conexión
        """
        if not PSYCOPG2_AVAILABLE:
            raise ImportError(
                "psycopg2 no está instalado. Instálalo con: pip install psycopg2-binary"
            )
        
        try:
            self.connection = psycopg2.connect(
                host=self.config.host,
                port=self.config.port,
                dbname=self.config.database,
                user=self.config.user,
                password=self.config.password,
                connect_timeout=self.config.connect_timeout,
                options=f"-c client_encoding={self.config.charset}"
            )
            self.connection.autocommit = False
            
            logger.info(f"Conectado a PostgreSQL: {self.config.database}")
        except Exception as e:
            logger.error(f"Error al conectar a PostgreSQL: {e}")
            raise
    
    def close(self) -> None:
        """
        Cierra la conexión a la base de datos
        """
        if self.cursor:
            self.cursor.close()
            self.cursor = None
        
        if self.connection:
            self.connection.close()
            self.connection = None
            logger.info("Conexión cerrada")
    
    def execute_query(self, query: str, params: Optional[Union[tuple, dict]] = None) -> List[Dict[str, Any]]:
        """
        Ejecuta una consulta SELECT y retorna los resultados
        
        Args:
            query: Consulta SQL a ejecutar
            params: Parámetros para la consulta (opcional)
            
        Returns:
            Lista de diccionarios con los resultados
            
        Raises:
            Exception: Si hay un error en la consulta
        """
        if not self.connection:
            raise Exception("No hay conexión a la base de datos")
        
        try:
            cursor = self.connection.cursor(cursor_factory=RealDictCursor)
            
            if params:
                cursor.execute(query, params)
            else:
                cursor.execute(query)
            
            results = cursor.fetchall()
            # Convertir RealDictRow a dict normal
            results = [dict(row) for row in results]
            cursor.close()
            
            logger.debug(f"Consulta ejecutada: {query}")
            return results
        except Exception as e:
            logger.error(f"Error al ejecutar consulta: {e}")
            raise
    
    def execute_update(self, query: str, params: Optional[Union[tuple, dict]] = None) -> int:
        """
        Ejecuta una consulta INSERT, UPDATE o DELETE
        
        Args:
            query: Consulta SQL a ejecutar
            params: Parámetros para la consulta (opcional)
            
        Returns:
            Número de filas afectadas
            
        Raises:
            Exception: Si hay un error en la consulta
        """
        if not self.connection:
            raise Exception("No hay conexión a la base de datos")
        
        try:
            cursor = self.connection.cursor()
            
            if params:
                cursor.execute(query, params)
            else:
                cursor.execute(query)
            
            self.connection.commit()
            affected_rows = cursor.rowcount
            cursor.close()
            
            logger.debug(f"Actualización ejecutada: {query}, filas afectadas: {affected_rows}")
            return affected_rows
        except Exception as e:
            self.connection.rollback()
            logger.error(f"Error al ejecutar actualización: {e}")
            raise
    
    @contextmanager
    def transaction(self):
        """
        Context manager para transacciones
        
        Ejemplo:
            >>> with db.transaction():
            ...     db.execute_update("INSERT INTO tabla VALUES (...)")
            ...     db.execute_update("UPDATE tabla SET ...")
        """
        try:
            yield self
            if self.connection:
                self.connection.commit()
                logger.debug("Transacción confirmada")
        except Exception as e:
            if self.connection:
                self.connection.rollback()
                logger.error(f"Transacción revertida: {e}")
            raise
    
    def __enter__(self):
        """Context manager entry"""
        self.connect()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit"""
        self.close()
        return False
