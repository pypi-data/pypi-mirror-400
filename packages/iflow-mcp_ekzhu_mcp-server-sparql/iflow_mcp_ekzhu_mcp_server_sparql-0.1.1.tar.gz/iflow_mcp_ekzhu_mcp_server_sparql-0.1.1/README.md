# MCP Server SPARQL

A Model Context Protocol (MCP) server that provides tools for querying SPARQL endpoints.

## Usage

Example usage for querying the Wikidata SPARQL endpoint.

### uvx

```json
"mcpServers": {
  "mcp-server-sparql": {
    "command": "uvx",
    "args": ["mcp-server-sparql", "--endpoint", "https://query.wikidata.org/sparql"],
  }
}
```

### Tool: `query`

Execute a SPARQL query against the configured endpoint.

**Parameters:**

- `query_string`: A valid SPARQL query string

**Returns:**

- The query results in JSON format
