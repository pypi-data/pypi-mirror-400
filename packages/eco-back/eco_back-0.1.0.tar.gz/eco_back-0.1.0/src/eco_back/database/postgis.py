"""
Utilidades para trabajar con PostGIS en PostgreSQL
"""
from typing import Optional, Dict, Any, List, Tuple, Union
import logging

from .connection import DatabaseConnection

logger = logging.getLogger(__name__)

try:
    from shapely.geometry import Point, LineString, Polygon, MultiPoint, MultiLineString, MultiPolygon
    from shapely import wkt, wkb
    SHAPELY_AVAILABLE = True
except ImportError:
    SHAPELY_AVAILABLE = False


class PostGISHelper:
    """
    Clase helper para operaciones con PostGIS
    """
    
    def __init__(self, db_connection: DatabaseConnection):
        """
        Inicializa el helper de PostGIS
        
        Args:
            db_connection: Conexión a la base de datos PostgreSQL
        """
        self.db = db_connection
    
    def enable_postgis(self) -> bool:
        """
        Habilita la extensión PostGIS en la base de datos
        
        Returns:
            True si se habilitó correctamente
            
        Raises:
            Exception: Si hay un error al habilitar PostGIS
        """
        try:
            self.db.execute_update("CREATE EXTENSION IF NOT EXISTS postgis")
            logger.info("Extensión PostGIS habilitada")
            return True
        except Exception as e:
            logger.error(f"Error al habilitar PostGIS: {e}")
            raise
    
    def get_postgis_version(self) -> str:
        """
        Obtiene la versión de PostGIS instalada
        
        Returns:
            Versión de PostGIS
        """
        result = self.db.execute_query("SELECT PostGIS_Version()")
        return result[0]['postgis_version'] if result else "No disponible"
    
    def create_spatial_index(self, table_name: str, column_name: str = "geom") -> bool:
        """
        Crea un índice espacial en una columna de geometría
        
        Args:
            table_name: Nombre de la tabla
            column_name: Nombre de la columna de geometría
            
        Returns:
            True si se creó correctamente
        """
        try:
            index_name = f"idx_{table_name}_{column_name}"
            query = f"""
                CREATE INDEX IF NOT EXISTS {index_name}
                ON {table_name} USING GIST ({column_name})
            """
            self.db.execute_update(query)
            logger.info(f"Índice espacial creado: {index_name}")
            return True
        except Exception as e:
            logger.error(f"Error al crear índice espacial: {e}")
            raise
    
    def point_to_geometry(self, lat: float, lon: float, srid: int = 4326) -> str:
        """
        Convierte coordenadas lat/lon a geometría PostGIS
        
        Args:
            lat: Latitud
            lon: Longitud
            srid: Sistema de referencia espacial (default: 4326 - WGS84)
            
        Returns:
            String de geometría PostGIS
        """
        return f"ST_SetSRID(ST_MakePoint({lon}, {lat}), {srid})"
    
    def insert_point(
        self,
        table_name: str,
        lat: float,
        lon: float,
        data: Optional[Dict[str, Any]] = None,
        geom_column: str = "geom",
        srid: int = 4326
    ) -> int:
        """
        Inserta un punto geográfico en una tabla
        
        Args:
            table_name: Nombre de la tabla
            lat: Latitud
            lon: Longitud
            data: Datos adicionales a insertar
            geom_column: Nombre de la columna de geometría
            srid: Sistema de referencia espacial
            
        Returns:
            ID del registro insertado
        """
        data = data or {}
        columns = list(data.keys()) + [geom_column]
        placeholders = [f"%s" for _ in data] + [f"ST_SetSRID(ST_MakePoint(%s, %s), {srid})"]
        values = list(data.values()) + [lon, lat]
        
        query = f"""
            INSERT INTO {table_name} ({', '.join(columns)})
            VALUES ({', '.join(placeholders)})
            RETURNING id
        """
        
        result = self.db.execute_query(query, tuple(values))
        return result[0]['id'] if result else None
    
    def find_within_distance(
        self,
        table_name: str,
        lat: float,
        lon: float,
        distance_meters: float,
        geom_column: str = "geom",
        srid: int = 4326
    ) -> List[Dict[str, Any]]:
        """
        Busca puntos dentro de una distancia específica
        
        Args:
            table_name: Nombre de la tabla
            lat: Latitud del punto central
            lon: Longitud del punto central
            distance_meters: Distancia en metros
            geom_column: Nombre de la columna de geometría
            srid: Sistema de referencia espacial
            
        Returns:
            Lista de registros encontrados
        """
        query = f"""
            SELECT *,
                   ST_Distance(
                       {geom_column}::geography,
                       ST_SetSRID(ST_MakePoint(%s, %s), {srid})::geography
                   ) as distance
            FROM {table_name}
            WHERE ST_DWithin(
                {geom_column}::geography,
                ST_SetSRID(ST_MakePoint(%s, %s), {srid})::geography,
                %s
            )
            ORDER BY distance
        """
        
        return self.db.execute_query(
            query,
            (lon, lat, lon, lat, distance_meters)
        )
    
    def find_within_bbox(
        self,
        table_name: str,
        min_lat: float,
        min_lon: float,
        max_lat: float,
        max_lon: float,
        geom_column: str = "geom",
        srid: int = 4326
    ) -> List[Dict[str, Any]]:
        """
        Busca puntos dentro de un bounding box
        
        Args:
            table_name: Nombre de la tabla
            min_lat: Latitud mínima
            min_lon: Longitud mínima
            max_lat: Latitud máxima
            max_lon: Longitud máxima
            geom_column: Nombre de la columna de geometría
            srid: Sistema de referencia espacial
            
        Returns:
            Lista de registros encontrados
        """
        query = f"""
            SELECT *
            FROM {table_name}
            WHERE {geom_column} && ST_MakeEnvelope(%s, %s, %s, %s, {srid})
        """
        
        return self.db.execute_query(
            query,
            (min_lon, min_lat, max_lon, max_lat)
        )
    
    def get_coordinates(
        self,
        table_name: str,
        id: int,
        geom_column: str = "geom"
    ) -> Optional[Tuple[float, float]]:
        """
        Obtiene las coordenadas lat/lon de un registro
        
        Args:
            table_name: Nombre de la tabla
            id: ID del registro
            geom_column: Nombre de la columna de geometría
            
        Returns:
            Tupla (latitud, longitud) o None
        """
        query = f"""
            SELECT ST_Y({geom_column}) as lat, ST_X({geom_column}) as lon
            FROM {table_name}
            WHERE id = %s
        """
        
        result = self.db.execute_query(query, (id,))
        if result:
            return (result[0]['lat'], result[0]['lon'])
        return None
    
    def calculate_distance(
        self,
        lat1: float,
        lon1: float,
        lat2: float,
        lon2: float,
        srid: int = 4326
    ) -> float:
        """
        Calcula la distancia entre dos puntos en metros
        
        Args:
            lat1: Latitud del punto 1
            lon1: Longitud del punto 1
            lat2: Latitud del punto 2
            lon2: Longitud del punto 2
            srid: Sistema de referencia espacial
            
        Returns:
            Distancia en metros
        """
        query = """
            SELECT ST_Distance(
                ST_SetSRID(ST_MakePoint(%s, %s), %s)::geography,
                ST_SetSRID(ST_MakePoint(%s, %s), %s)::geography
            ) as distance
        """
        
        result = self.db.execute_query(
            query,
            (lon1, lat1, srid, lon2, lat2, srid)
        )
        
        return result[0]['distance'] if result else 0.0
    
    def insert_polygon(
        self,
        table_name: str,
        coordinates: List[Tuple[float, float]],
        data: Optional[Dict[str, Any]] = None,
        geom_column: str = "geom",
        srid: int = 4326
    ) -> int:
        """
        Inserta un polígono en la base de datos
        
        Args:
            table_name: Nombre de la tabla
            coordinates: Lista de tuplas (lat, lon) que forman el polígono
            data: Datos adicionales a insertar
            geom_column: Nombre de la columna de geometría
            srid: Sistema de referencia espacial
            
        Returns:
            ID del registro insertado
        """
        data = data or {}
        
        # Convertir coordenadas a formato WKT
        points = ", ".join([f"{lon} {lat}" for lat, lon in coordinates])
        # Cerrar el polígono si no está cerrado
        if coordinates[0] != coordinates[-1]:
            points += f", {coordinates[0][1]} {coordinates[0][0]}"
        
        columns = list(data.keys()) + [geom_column]
        placeholders = ["%s" for _ in data] + [f"ST_GeomFromText('POLYGON(({points}))', {srid})"]
        values = list(data.values())
        
        query = f"""
            INSERT INTO {table_name} ({', '.join(columns)})
            VALUES ({', '.join(placeholders)})
            RETURNING id
        """
        
        result = self.db.execute_query(query, tuple(values) if values else None)
        return result[0]['id'] if result else None
    
    def point_in_polygon(
        self,
        table_name: str,
        lat: float,
        lon: float,
        geom_column: str = "geom",
        srid: int = 4326
    ) -> List[Dict[str, Any]]:
        """
        Encuentra polígonos que contienen un punto específico
        
        Args:
            table_name: Nombre de la tabla con polígonos
            lat: Latitud del punto
            lon: Longitud del punto
            geom_column: Nombre de la columna de geometría
            srid: Sistema de referencia espacial
            
        Returns:
            Lista de polígonos que contienen el punto
        """
        query = f"""
            SELECT *
            FROM {table_name}
            WHERE ST_Contains(
                {geom_column},
                ST_SetSRID(ST_MakePoint(%s, %s), {srid})
            )
        """
        
        return self.db.execute_query(query, (lon, lat))
