import json
import argparse
from typing import Dict, Any, Optional, Union, List

from SPARQLWrapper import SPARQLWrapper, JSON, SPARQLExceptions
from mcp.server.fastmcp import FastMCP


class SPARQLServer:
    def __init__(self, endpoint_url: str):
        self.endpoint_url = endpoint_url
        self.sparql = SPARQLWrapper(endpoint_url)
        self.sparql.setReturnFormat(JSON)
    
    def query(self, query_string: str) -> Dict[str, Any]:
        """Execute a SPARQL query and return the results"""
        try:
            self.sparql.setQuery(query_string)
            results = self.sparql.query().convert()
            return results
        except SPARQLExceptions.EndPointNotFound:
            return {"error": f"SPARQL endpoint not found: {self.endpoint_url}"}
        except Exception as e:
            return {"error": f"Query error: {str(e)}"}


def parse_args():
    parser = argparse.ArgumentParser(description="MCP SPARQL Query Server")
    parser.add_argument(
        "--endpoint", 
        required=False,
        default="https://dbpedia.org/sparql",
        help="SPARQL endpoint URL (e.g., http://dbpedia.org/sparql)"
    )
    return parser.parse_args()


def main():
    args = parse_args()
    
    # Initialize the SPARQL server with the endpoint URL
    sparql_server = SPARQLServer(endpoint_url=args.endpoint)
    
    # Create the MCP server
    mcp = FastMCP("SPARQL Query Server")
    
    query_doc = f"""
Execute a SPARQL query against the endpoint {sparql_server.endpoint_url}.
        
Args:
    query_string: A valid SPARQL query string
    
Returns:
    The query results in JSON format
"""

    @mcp.tool(description=query_doc)
    def query(query_string: str) -> Union[Dict[str, Any], List[Dict[str, Any]]]:
        return sparql_server.query(query_string)
    
    # Run the MCP server
    mcp.run(transport="stdio")


if __name__ == "__main__":
    main()
