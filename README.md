# AI-Powered Agent for Analyzing Machine Stop Events via MCP Server

## Instrucciones de Instalación
### 1. Clonar el repositorio
```sh
git clone 
cd mcp-stop-events-agent
```

### 2. Creación de un Entorno Virtual
```sh
python -m venv venv
source venv/bin/activate  # o venv\Scripts\activate en Windows
```

### 3. Instalación de dependencias
```sh
pip install -r requirements.txt
```

### 4. Creación de la base de datos y carga de datos
```sh
python src/create_db.py
```

### 5. Autenticación de cliente de Claude
Insertar en auth/anthropic_key.txt la API key

### 6. Iniciar el cliente del servidor MCP
```sh
python src/client.py
```

### 7. Realizar consultas en lenguaje natural:
#### Ejemplos
1. **Conteo**: "¿Cuántas paradas ocurrieron el 1 de enero?"
2. **Filtrado**: "Lista todas las paradas causadas por 'Die Head Cleaning'"
3. **Agregación**: "¿Cuál es la duración promedio de cada tipo de parada?"
4. **Tendencias**: "¿Qué hora del día tuvo la mayor duración total de paradas?"
5. **Consulta compleja**: "¿Cuáles son los 3 tipos de parada más frecuentes en el último mes?"