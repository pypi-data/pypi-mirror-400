# eco-back

Librería Python para backend con soporte para PostgreSQL/PostGIS y clientes API

## Características

- ✅ **Base de datos**: Conexión y operaciones con PostgreSQL
- ✅ **PostGIS**: Operaciones geoespaciales (puntos, polígonos, búsquedas por proximidad)
- ✅ **Cliente API**: Cliente HTTP genérico y cliente específico UNP
- ✅ **Patrón Repository**: Implementación de patrones de diseño para acceso a datos

## Descripción

eco-back es una librería modular que facilita el desarrollo de aplicaciones backend, proporcionando abstracciones para bases de datos geoespaciales y consumo de APIs REST.

## Instalación

### Desde el código fuente

```bash
pip install -e .
```

### Para desarrollo

```bash
pip install -e ".[dev]"
```

## Uso

### Cliente de Consecutivos (UNP)

```python
from eco_back.api import Consecutivo

# Crear cliente
client = Consecutivo(base_url="https://api.unp.example.com")

# Obtener consecutivo
consecutivo = client.obtener(origen=1)
if consecutivo:
    print(f"Consecutivo: {consecutivo}")

client.close()

# Forma recomendada: usar context manager
with Consecutivo(base_url="https://api.unp.example.com") as client:
    consecutivo = client.obtener(origen=1)
    # Usar el consecutivo...
```

### Cliente API Genérico

```python
from eco_back.api import APIConfig, APIClient

config = APIConfig(
    base_url="https://api.example.com",
    timeout=30,
    headers={"Authorization": "Bearer token"}
)

with APIClient(config) as client:
    # GET request
    data = client.get("/endpoint")
    
    # POST request
    result = client.post("/endpoint", json={"key": "value"})
```

### Conexión básica a PostgreSQL

```python
from eco_back.database import DatabaseConfig, DatabaseConnection

config = DatabaseConfig(
    host="localhost",
    port=5432,
    database="mi_base_datos",
    user="usuario",
    password="password"
)

with DatabaseConnection(config) as db:
    resultados = db.execute_query("SELECT * FROM tabla")
    for row in resultados:
        print(row)
```

### Uso de PostGIS

```python
from eco_back.database import DatabaseConfig, DatabaseConnection, PostGISHelper

config = DatabaseConfig(
    host="localhost",
    port=5432,
    database="mi_db_geo",
    user="postgres",
    password="password"
)

with DatabaseConnection(config) as db:
    postgis = PostGISHelper(db)
    
    # Habilitar PostGIS
    postgis.enable_postgis()
    
    # Insertar un punto geográfico
    punto_id = postgis.insert_point(
        table_name="ubicaciones",
        lat=40.4168,
        lon=-3.7038,
        data={"nombre": "Madrid", "tipo": "ciudad"}
    )
    
    # Buscar puntos cercanos (5km)
    cercanos = postgis.find_within_distance(
        table_name="ubicaciones",
        lat=40.4168,
        lon=-3.7038,
        distance_meters=5000
    )
```

## Desarrollo

### Ejecutar tests

```bash
pytest
```

### Formatear código

```bash
black src/ tests/
```

### Linting

```bash
flake8 src/ tests/
```

### Type checking

```bash
mypy src/
```

## Licencia

MIT
