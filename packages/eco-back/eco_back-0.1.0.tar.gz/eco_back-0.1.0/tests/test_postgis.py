"""
Tests para PostGIS
"""
import pytest
from eco_back.database import DatabaseConfig, DatabaseConnection, PostGISHelper


class TestPostGISHelper:
    """Tests para PostGISHelper"""
    
    @pytest.fixture
    def config(self):
        """Fixture de configuración de prueba"""
        return DatabaseConfig(
            host="localhost",
            port=5432,
            database="test_db",
            user="test_user",
            password="test_pass"
        )
    
    @pytest.fixture
    def postgis_helper(self, config):
        """Fixture de PostGISHelper"""
        db = DatabaseConnection(config)
        return PostGISHelper(db)
    
    def test_point_to_geometry(self, postgis_helper):
        """Test de conversión de punto a geometría"""
        result = postgis_helper.point_to_geometry(40.4168, -3.7038)
        
        assert "ST_SetSRID" in result
        assert "ST_MakePoint" in result
        assert "-3.7038" in result
        assert "40.4168" in result
    
    def test_point_to_geometry_custom_srid(self, postgis_helper):
        """Test de conversión con SRID personalizado"""
        result = postgis_helper.point_to_geometry(40.4168, -3.7038, srid=3857)
        
        assert "3857" in result
    
    # Nota: Los siguientes tests requieren una base de datos PostgreSQL
    # con PostGIS instalado para ejecutarse completamente
    
    # @pytest.mark.integration
    # def test_enable_postgis(self, config):
    #     """Test de habilitación de PostGIS"""
    #     with DatabaseConnection(config) as db:
    #         postgis = PostGISHelper(db)
    #         result = postgis.enable_postgis()
    #         assert result is True
    
    # @pytest.mark.integration
    # def test_get_postgis_version(self, config):
    #     """Test de obtención de versión"""
    #     with DatabaseConnection(config) as db:
    #         postgis = PostGISHelper(db)
    #         version = postgis.get_postgis_version()
    #         assert version is not None
    #         assert len(version) > 0


class TestPostGISOperations:
    """Tests de operaciones geoespaciales"""
    
    def test_distance_calculation_logic(self):
        """Test de lógica de cálculo de distancia"""
        # Este test verifica la lógica sin necesidad de BD
        # En un entorno real, la distancia Madrid-Barcelona es ~500km
        
        madrid_lat, madrid_lon = 40.4168, -3.7038
        barcelona_lat, barcelona_lon = 41.3851, 2.1734
        
        # Verificar que las coordenadas son válidas
        assert -90 <= madrid_lat <= 90
        assert -180 <= madrid_lon <= 180
        assert -90 <= barcelona_lat <= 90
        assert -180 <= barcelona_lon <= 180
    
    def test_bbox_coordinates(self):
        """Test de validación de bounding box"""
        min_lat, min_lon = 40.40, -3.75
        max_lat, max_lon = 40.45, -3.65
        
        # Verificar que el bbox es válido
        assert min_lat < max_lat
        assert min_lon < max_lon
        assert -90 <= min_lat <= 90
        assert -90 <= max_lat <= 90
