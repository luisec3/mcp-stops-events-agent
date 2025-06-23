from mcp.server.fastmcp import FastMCP
import sqlite3

DB_PATH = 'db/stops.db'
TABLE_NAME = 'stops'

# Create the server
server = FastMCP("SQL Server")

# Define the sql query tool
@server.tool(name="query_tool", description="Executes a query and returns the result")
def query_tool(query: str) -> dict:
    # Validate the query is a SELECT
    if not query.strip().lower().startswith("select"):
        return {"error": "Only Select queries are allowed"}
    try:
        # Execute the query
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute(query)
        columns = [col[0] for col in cursor.description]
        rows = cursor.fetchall()
        results = [dict(zip(columns, row)) for row in rows]

        return {"results": results}
    except Exception as e:
        return {"error": str(e)}
    finally:
        conn.close()


# Run the server over stdio
if __name__ == "__main__":
    server.run()
