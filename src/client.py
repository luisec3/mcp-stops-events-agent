from datetime import date
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client
import anthropic
import asyncio

# Define server parameters to run the sql server
server_params = StdioServerParameters(
    command="python",
    args=["src/sql_server.py"],
    env=None
)

KEY_PATH = "auth/anthropic_key.txt"


async def run(user_query):
    # Start the server as a subprocess and get stdio read/write functions
    async with stdio_client(server_params) as (read, write):
        # Create a client session to communicate to the server
        async with ClientSession(read, write) as session:
            # Initialize the connection to the server
            await session.initialize()

            # Define the query_tool
            tools_for_claude = [
                {
                    "name": "query_tool",
                    "description": "Executes a sql query to the stops table and returns the result",
                    "input_schema": {
                        "type": "object",
                        "properties": {
                            "query": {
                                "type": "string",
                                "description": "Consulta SQL a ejecutar"
                            }
                        },
                        "required": ["query"]
                    }
                }
            ]

            user_query = f"""Eres un asistente que ayuda a consultar una base de datos con SQL a partir de lenguaje natural.
Trabajas sobre una base de datos SQLite que contiene la siguiente tabla:

Tabla: stops
- stop_id (UUID)
- stop_type_id (UUID)
- stop_type_name (TEXT)
- start_at (TEXT, formato ISO)
- ends_at (TEXT, formato ISO)
- duration_minutes (REAL)

Pregunta: ¿Cuántas paradas hubo por día?
SQL: SELECT DATE(start_at) AS fecha, COUNT(*) AS total FROM stops GROUP BY fecha ORDER BY fecha;

Pregunta: ¿Cuál es la duración promedio por tipo?
SQL: SELECT stop_type_name, AVG(duration_minutes) AS duracion_promedio FROM stops GROUP BY stop_type_name;

Pregunta: ¿Cuál fue la primera parada?
SQL: SELECT * FROM stops ORDER BY start_at LIMIT 1;

Para consultas con tiempo relativo (por ejemplo: dame los registros del ultimo mes), asume la fecha actual como: {date.today()}

Proporciona los resultados de manera estructurada unicamente con la información que fue solicitada
En caso de retornar paradas hazlo en estructura de clave: valor, con el nombre de campo como clave.

Por último, no ejecutes consultas que requieran eliminar o modificar los datos de la base de datos.

Contesta la siguiente consulta proporcionada por el usuario: """ + user_query

            # Set up Anthropic client
            with open(KEY_PATH, 'r') as f:
                api_key = f.read().strip()

            anthropic_client = anthropic.Anthropic(api_key=api_key)

            # Send initial message to Claude with the user’s query and tools
            response = anthropic_client.messages.create(
                model="claude-3-5-sonnet-20241022",
                max_tokens=1000,
                messages=[{"role": "user", "content": user_query}],
                tools=tools_for_claude,
            )

            # Check if Claude wants to use a tool
            if response.stop_reason == "tool_use":
                tool_call = next((block for block in response.content if block.type == "tool_use"), None)
                if tool_call:
                    tool_name = tool_call.name
                    tool_input = tool_call.input
                    # Call the tool via MCP
                    try:
                        result = await session.call_tool(tool_name, arguments=tool_input)
                        # Create tool result message for Claude
                        tool_result_message = {
                            "role": "user",
                            "content": [
                                {
                                    "type": "tool_result",
                                    "tool_use_id": tool_call.id,
                                    "content": str(result),
                                }
                            ],
                        }
                        # Send follow-up message to Claude with the tool result
                        follow_up_response = anthropic_client.messages.create(
                            model="claude-3-5-sonnet-20241022",
                            max_tokens=1000,
                            messages=[
                                {"role": "user", "content": user_query},
                                {"role": "assistant", "content": response.content},
                                tool_result_message,
                            ],
                        )
                        final_answer = follow_up_response.content[0].text
                    except Exception as e:
                        final_answer = f"Error calling tool: {e}"
                else:
                    final_answer = "Claude tried to use a tool, but no tool_use block was found."
            else:
                final_answer = response.content[0].text
  
            # Print the assistant response
            print("\n============================")
            print(final_answer)
            print("============================\n")

if __name__ == "__main__":
    WELCOME_MESSAGE = """
🚦 Bienvenido al Asistente de Análisis de Paradas 🚦

Puedes hacer consultas en lenguaje natural como:

1️⃣  "¿Cuántas paradas hubo por día?"
2️⃣  "¿Cuál es la duración promedio por tipo?"
3️⃣  "Filtra las paradas por tipo de parada"
4️⃣  "Muéstrame la tendencia de duración de paradas por tipo"

Escribe 'salir' para cerrar el programa.
"""

    print(WELCOME_MESSAGE)

    while True:
        # Get a question from the user
        user_query = input("Escribe tu consulta: ")

        if user_query.strip().lower() in ["salir", "exit", "quit"]:
            print("👋 ¡Hasta luego!")
            break

        # Run the async function
        asyncio.run(run(user_query))
