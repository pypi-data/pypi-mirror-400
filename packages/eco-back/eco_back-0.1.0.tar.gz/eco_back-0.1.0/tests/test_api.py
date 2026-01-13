"""
Tests para el módulo API
"""
import pytest
from eco_back.api import APIConfig, APIClient, Consecutivo


class TestAPIConfig:
    """Tests para APIConfig"""
    
    def test_create_config(self):
        """Test de creación de configuración"""
        config = APIConfig(
            base_url="https://api.example.com",
            timeout=30
        )
        
        assert config.base_url == "https://api.example.com"
        assert config.timeout == 30
        assert config.verify_ssl is True
        assert config.headers == {}
    
    def test_config_removes_trailing_slash(self):
        """Test que la URL base no termine con /"""
        config = APIConfig(base_url="https://api.example.com/")
        assert config.base_url == "https://api.example.com"
    
    def test_from_dict(self):
        """Test de creación desde diccionario"""
        config_dict = {
            "base_url": "https://api.example.com",
            "timeout": 60,
            "headers": {"Authorization": "Bearer token"},
            "verify_ssl": False
        }
        
        config = APIConfig.from_dict(config_dict)
        
        assert config.base_url == "https://api.example.com"
        assert config.timeout == 60
        assert config.verify_ssl is False
        assert "Authorization" in config.headers
    
    def test_to_dict(self):
        """Test de conversión a diccionario"""
        config = APIConfig(
            base_url="https://api.example.com",
            timeout=45
        )
        
        config_dict = config.to_dict()
        
        assert isinstance(config_dict, dict)
        assert config_dict["base_url"] == "https://api.example.com"
        assert config_dict["timeout"] == 45


class TestAPIClient:
    """Tests para APIClient"""
    
    def test_client_creation(self):
        """Test de creación del cliente"""
        config = APIConfig(base_url="https://api.example.com")
        client = APIClient(config)
        
        assert client.config == config
        assert client.session is not None
    
    def test_build_url(self):
        """Test de construcción de URL"""
        config = APIConfig(base_url="https://api.example.com")
        client = APIClient(config)
        
        # Con / al inicio
        url1 = client._build_url("/users/1")
        assert url1 == "https://api.example.com/users/1"
        
        # Sin / al inicio
        url2 = client._build_url("users/1")
        assert url2 == "https://api.example.com/users/1"
    
    def test_context_manager(self):
        """Test de uso como context manager"""
        config = APIConfig(base_url="https://api.example.com")
        
        with APIClient(config) as client:
            assert client.session is not None
        
        # La sesión debería estar cerrada después del bloque


class TestConsecutivo:
    """Tests para Consecutivo"""
    
    def test_consecutivo_creation(self):
        """Test de creación del cliente de Consecutivos"""
        client = Consecutivo(base_url="https://api.unp.example.com")
        
        assert client.client is not None
        assert client.client.config.base_url == "https://api.unp.example.com"
    
    def test_consecutivo_custom_timeout(self):
        """Test con timeout personalizado"""
        client = Consecutivo(
            base_url="https://api.unp.example.com",
            timeout=60
        )
        
        assert client.client.config.timeout == 60
    
    # Nota: Para tests completos de peticiones HTTP necesitarías:
    # - pytest-mock o responses para mockear las peticiones
    # - O un servidor de prueba
    
    # Ejemplo de test con mock (requiere pytest-mock):
    # def test_obtener_success(self, mocker):
    #     """Test de obtención exitosa de consecutivo"""
    #     client = Consecutivo(base_url="https://api.unp.example.com")
    #     
    #     mock_get = mocker.patch.object(
    #         client.client,
    #         'get',
    #         return_value={'consecutivo': 12345}
    #     )
    #     
    #     consecutivo = client.obtener_consecutivo(origen=1)
    #     
    #     assert consecutivo == 12345
    #     mock_get.assert_called_once()


# Tests de integración (requieren conexión a internet)
@pytest.mark.integration
class TestAPIIntegration:
    """Tests de integración con API real"""
    
    def test_get_request_jsonplaceholder(self):
        """Test de GET request con API pública"""
        config = APIConfig(base_url="https://jsonplaceholder.typicode.com")
        
        with APIClient(config) as client:
            user = client.get("/users/1")
            
            assert user is not None
            assert 'name' in user
            assert 'email' in user
    
    def test_post_request_jsonplaceholder(self):
        """Test de POST request con API pública"""
        config = APIConfig(base_url="https://jsonplaceholder.typicode.com")
        
        with APIClient(config) as client:
            new_post = client.post(
                "/posts",
                json={
                    "title": "Test",
                    "body": "Test body",
                    "userId": 1
                }
            )
            
            assert new_post is not None
            assert 'id' in new_post
