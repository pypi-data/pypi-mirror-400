"""
Ejemplo de tests para eco-back
"""
import pytest
from eco_back import __version__


def test_version():
    """Test que verifica la versión de la librería"""
    assert __version__ == "0.1.0"


# Agrega tus tests aquí
# def test_mi_funcion():
#     assert mi_funcion() == resultado_esperado
