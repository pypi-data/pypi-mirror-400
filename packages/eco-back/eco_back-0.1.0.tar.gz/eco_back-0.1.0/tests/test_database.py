"""
Tests para el módulo de base de datos
"""
import pytest
from eco_back.database import DatabaseConfig, DatabaseConnection


class TestDatabaseConfig:
    """Tests para DatabaseConfig"""
    
    def test_create_config(self):
        """Test de creación de configuración"""
        config = DatabaseConfig(
            host="localhost",
            port=3306,
            database="test_db",
            user="test_user",
            password="test_pass"
        )
        
        assert config.host == "localhost"
        assert config.port == 3306
        assert config.database == "test_db"
        assert config.user == "test_user"
        assert config.password == "test_pass"
        assert config.charset == "utf8mb4"  # valor por defecto
        assert config.connect_timeout == 10  # valor por defecto
    
    def test_from_dict(self):
        """Test de creación desde diccionario"""
        config_dict = {
            "host": "localhost",
            "port": 3306,
            "database": "test_db",
            "user": "test_user",
            "password": "test_pass",
            "charset": "utf8",
            "connect_timeout": 5
        }
        
        config = DatabaseConfig.from_dict(config_dict)
        
        assert config.host == "localhost"
        assert config.charset == "utf8"
        assert config.connect_timeout == 5
    
    def test_to_dict(self):
        """Test de conversión a diccionario"""
        config = DatabaseConfig(
            host="localhost",
            port=3306,
            database="test_db",
            user="test_user",
            password="test_pass"
        )
        
        config_dict = config.to_dict()
        
        assert isinstance(config_dict, dict)
        assert config_dict["host"] == "localhost"
        assert config_dict["port"] == 3306
        assert "password" in config_dict


class TestDatabaseConnection:
    """Tests para DatabaseConnection"""
    
    def test_connection_creation(self):
        """Test de creación de conexión"""
        config = DatabaseConfig(
            host="localhost",
            port=3306,
            database="test_db",
            user="test_user",
            password="test_pass"
        )
        
        db = DatabaseConnection(config)
        
        assert db.config == config
        assert db.connection is None
        assert db.cursor is None
    
    # Nota: Para tests completos de conexión necesitarías:
    # - Una base de datos de prueba
    # - Mock de la conexión
    # - pytest-mock o unittest.mock
    
    # Ejemplo de test con mock (requiere pytest-mock):
    # def test_connect_success(self, mocker):
    #     """Test de conexión exitosa"""
    #     config = DatabaseConfig(...)
    #     db = DatabaseConnection(config)
    #     
    #     mock_connection = mocker.patch('mysql.connector.connect')
    #     db.connect()
    #     
    #     mock_connection.assert_called_once()
