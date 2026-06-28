# Verity MCP server — stdio MCP server (for Glama checks & containerized runs)
FROM python:3.12-slim
WORKDIR /app
COPY . /app
RUN pip install --no-cache-dir .
# Starts the stdio MCP server; responds to MCP introspection (tools/list) with no network needed.
ENTRYPOINT ["verity-mcp"]
