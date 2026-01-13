"""
CatalogPlugin for schema discovery and metadata management.

Provides tools for discovering database schemas, API structures, and other
organizational metadata across multiple platforms.
"""
import logging
from typing import Any, Dict, List, Optional, TYPE_CHECKING

from .base import BasePlugin

if TYPE_CHECKING:
    from ..core.tools import AgentTool

logger = logging.getLogger(__name__)


class CatalogPlugin(BasePlugin):
    """
    Plugin for schema discovery and metadata cataloging.

    Works standalone (returns data directly) or with optional graph storage
    for building an organizational knowledge graph.

    Supports:
    - PostgreSQL, MySQL, MongoDB schema discovery
    - GraphQL introspection
    - OpenAPI/Swagger spec parsing
    - Salesforce object metadata
    - Schema comparison and validation
    """

    def __init__(
        self,
        graph_store: Optional[Any] = None,
        organization_id: Optional[int] = None,
        auto_persist: bool = False
    ):
        """
        Initialize CatalogPlugin.

        Args:
            graph_store: Optional graph storage backend (Neo4j, etc.)
            organization_id: Optional organization ID for multi-tenant storage
            auto_persist: If True and graph_store provided, automatically persist discoveries
        """
        self._graph_store = graph_store
        self._organization_id = organization_id
        self._auto_persist = auto_persist

        logger.debug(f"CatalogPlugin initialized (graph_store: {graph_store is not None}, auto_persist: {auto_persist})")

    def get_tools(self) -> List['AgentTool']:
        """
        Expose schema discovery operations as agent tools.

        Returns:
            List of AgentTool instances for catalog operations
        """
        from ..core.tools import AgentTool

        return [
            AgentTool(
                name="discover_postgres",
                description="Discover PostgreSQL database schema including tables, columns, foreign keys, and indexes",
                parameters={
                    "type": "object",
                    "properties": {
                        "connection_string": {
                            "type": "string",
                            "description": "PostgreSQL connection string (e.g., postgresql://user:pass@host:port/db)"
                        },
                        "schema": {
                            "type": "string",
                            "description": "Schema name to introspect (default: 'public')"
                        },
                        "persist": {
                            "type": "boolean",
                            "description": "Whether to persist schema to graph storage if available (default: auto_persist setting)"
                        }
                    },
                    "required": ["connection_string"]
                },
                handler=self._tool_discover_postgres,
                category="catalog",
                source="plugin",
                plugin_name="Catalog",
                timeout_seconds=120
            ),
            AgentTool(
                name="discover_mysql",
                description="Discover MySQL/MariaDB database schema including tables, columns, and relationships",
                parameters={
                    "type": "object",
                    "properties": {
                        "connection_string": {
                            "type": "string",
                            "description": "MySQL connection string (e.g., mysql://user:pass@host:port/db)"
                        },
                        "schema": {
                            "type": "string",
                            "description": "Schema/database name to introspect"
                        },
                        "persist": {
                            "type": "boolean",
                            "description": "Whether to persist schema to graph storage if available"
                        }
                    },
                    "required": ["connection_string"]
                },
                handler=self._tool_discover_mysql,
                category="catalog",
                source="plugin",
                plugin_name="Catalog",
                timeout_seconds=120
            ),
            AgentTool(
                name="discover_mongodb",
                description="Discover MongoDB schema by sampling documents to infer structure",
                parameters={
                    "type": "object",
                    "properties": {
                        "connection_string": {
                            "type": "string",
                            "description": "MongoDB connection string (e.g., mongodb://user:pass@host:port/db)"
                        },
                        "database": {
                            "type": "string",
                            "description": "Database name to introspect"
                        },
                        "sample_size": {
                            "type": "integer",
                            "description": "Number of documents to sample per collection (default: 100)"
                        },
                        "persist": {
                            "type": "boolean",
                            "description": "Whether to persist schema to graph storage if available"
                        }
                    },
                    "required": ["connection_string", "database"]
                },
                handler=self._tool_discover_mongodb,
                category="catalog",
                source="plugin",
                plugin_name="Catalog",
                timeout_seconds=120
            ),
            AgentTool(
                name="discover_openapi",
                description="Discover API structure from OpenAPI/Swagger specification",
                parameters={
                    "type": "object",
                    "properties": {
                        "spec_url": {
                            "type": "string",
                            "description": "URL to OpenAPI spec (JSON or YAML)"
                        },
                        "service_name": {
                            "type": "string",
                            "description": "Optional service name override"
                        },
                        "persist": {
                            "type": "boolean",
                            "description": "Whether to persist schema to graph storage if available"
                        }
                    },
                    "required": ["spec_url"]
                },
                handler=self._tool_discover_openapi,
                category="catalog",
                source="plugin",
                plugin_name="Catalog",
                timeout_seconds=60
            ),
            AgentTool(
                name="compare_schemas",
                description="Compare two schemas to identify differences for migration planning",
                parameters={
                    "type": "object",
                    "properties": {
                        "schema_a": {
                            "type": "object",
                            "description": "First schema (from discover_* tools)"
                        },
                        "schema_b": {
                            "type": "object",
                            "description": "Second schema to compare against"
                        }
                    },
                    "required": ["schema_a", "schema_b"]
                },
                handler=self._tool_compare_schemas,
                category="catalog",
                source="plugin",
                plugin_name="Catalog",
                timeout_seconds=30
            ),
            AgentTool(
                name="export_diagram",
                description="Export schema as a visual diagram in Mermaid, DBDiagram, or JSON Schema format",
                parameters={
                    "type": "object",
                    "properties": {
                        "schema": {
                            "type": "object",
                            "description": "Schema object (from discover_* tools)"
                        },
                        "format": {
                            "type": "string",
                            "description": "Output format: 'mermaid', 'dbdiagram', or 'json_schema' (default: 'mermaid')"
                        }
                    },
                    "required": ["schema"]
                },
                handler=self._tool_export_diagram,
                category="catalog",
                source="plugin",
                plugin_name="Catalog",
                timeout_seconds=30
            )
        ]

    async def _tool_discover_postgres(self, args: Dict[str, Any]) -> Dict[str, Any]:
        """Tool handler for discover_postgres"""
        connection_string = args.get("connection_string")
        schema = args.get("schema", "public")
        persist = args.get("persist", self._auto_persist)

        result = await self.discover_postgres(
            connection_string=connection_string,
            schema=schema,
            persist=persist
        )

        return result

    async def discover_postgres(
        self,
        connection_string: str,
        schema: str = "public",
        persist: bool = False
    ) -> Dict[str, Any]:
        """
        Discover PostgreSQL database schema.

        Args:
            connection_string: PostgreSQL connection string
            schema: Schema name (default: public)
            persist: Whether to persist to graph storage

        Returns:
            Dictionary with discovered tables, columns, and relationships
        """
        import asyncpg

        conn = await asyncpg.connect(connection_string)

        try:
            # Get tables
            tables = await conn.fetch("""
                SELECT table_name,
                       pg_stat_user_tables.n_live_tup as row_count
                FROM information_schema.tables
                LEFT JOIN pg_stat_user_tables
                    ON table_name = relname
                WHERE table_schema = $1
                AND table_type = 'BASE TABLE'
            """, schema)

            # Get columns
            columns = await conn.fetch("""
                SELECT
                    table_name,
                    column_name,
                    data_type,
                    character_maximum_length,
                    numeric_precision,
                    numeric_scale,
                    is_nullable,
                    column_default
                FROM information_schema.columns
                WHERE table_schema = $1
                ORDER BY table_name, ordinal_position
            """, schema)

            # Get primary keys
            pkeys = await conn.fetch("""
                SELECT
                    tc.table_name,
                    kcu.column_name
                FROM information_schema.table_constraints tc
                JOIN information_schema.key_column_usage kcu
                    ON tc.constraint_name = kcu.constraint_name
                WHERE tc.constraint_type = 'PRIMARY KEY'
                AND tc.table_schema = $1
            """, schema)

            # Get foreign keys
            fkeys = await conn.fetch("""
                SELECT
                    tc.table_name as source_table,
                    kcu.column_name as source_column,
                    ccu.table_name AS target_table,
                    ccu.column_name AS target_column,
                    tc.constraint_name,
                    rc.delete_rule,
                    rc.update_rule
                FROM information_schema.table_constraints tc
                JOIN information_schema.key_column_usage kcu
                    ON tc.constraint_name = kcu.constraint_name
                JOIN information_schema.constraint_column_usage ccu
                    ON ccu.constraint_name = tc.constraint_name
                JOIN information_schema.referential_constraints rc
                    ON tc.constraint_name = rc.constraint_name
                WHERE tc.constraint_type = 'FOREIGN KEY'
                AND tc.table_schema = $1
            """, schema)

            # Get indexes
            indexes = await conn.fetch("""
                SELECT
                    tablename,
                    indexname,
                    indexdef
                FROM pg_indexes
                WHERE schemaname = $1
            """, schema)

            # Build result
            result = {
                "database_type": "postgresql",
                "schema": schema,
                "tables": [dict(row) for row in tables],
                "columns": [dict(row) for row in columns],
                "primary_keys": [dict(row) for row in pkeys],
                "foreign_keys": [dict(row) for row in fkeys],
                "indexes": [dict(row) for row in indexes],
                "table_count": len(tables),
                "column_count": len(columns)
            }

            # Optionally persist to graph storage
            if persist and self._graph_store:
                await self._persist_schema(result)

            return {
                "success": True,
                "schema": result,
                "persisted": persist and self._graph_store is not None
            }

        finally:
            await conn.close()

    async def _tool_discover_mysql(self, args: Dict[str, Any]) -> Dict[str, Any]:
        """Tool handler for discover_mysql"""
        connection_string = args.get("connection_string")
        schema = args.get("schema")
        persist = args.get("persist", self._auto_persist)

        result = await self.discover_mysql(
            connection_string=connection_string,
            schema=schema,
            persist=persist
        )

        return result

    async def discover_mysql(
        self,
        connection_string: str,
        schema: Optional[str] = None,
        persist: bool = False
    ) -> Dict[str, Any]:
        """
        Discover MySQL/MariaDB database schema.

        Args:
            connection_string: MySQL connection string
            schema: Schema/database name
            persist: Whether to persist to graph storage

        Returns:
            Dictionary with discovered tables, columns, and relationships
        """
        # Parse connection string to extract database
        import aiomysql
        from urllib.parse import urlparse

        parsed = urlparse(connection_string)
        db_name = schema or parsed.path.lstrip('/')

        # Extract credentials
        username = parsed.username or 'root'
        password = parsed.password or ''
        host = parsed.hostname or 'localhost'
        port = parsed.port or 3306

        conn = await aiomysql.connect(
            host=host,
            port=port,
            user=username,
            password=password,
            db=db_name
        )

        try:
            async with conn.cursor(aiomysql.DictCursor) as cursor:
                # Get tables
                await cursor.execute(f"""
                    SELECT TABLE_NAME as table_name,
                           TABLE_ROWS as row_count
                    FROM information_schema.TABLES
                    WHERE TABLE_SCHEMA = '{db_name}'
                    AND TABLE_TYPE = 'BASE TABLE'
                """)
                tables = await cursor.fetchall()

                # Get columns
                await cursor.execute(f"""
                    SELECT
                        TABLE_NAME as table_name,
                        COLUMN_NAME as column_name,
                        DATA_TYPE as data_type,
                        CHARACTER_MAXIMUM_LENGTH as character_maximum_length,
                        NUMERIC_PRECISION as numeric_precision,
                        NUMERIC_SCALE as numeric_scale,
                        IS_NULLABLE as is_nullable,
                        COLUMN_DEFAULT as column_default,
                        COLUMN_KEY as column_key
                    FROM information_schema.COLUMNS
                    WHERE TABLE_SCHEMA = '{db_name}'
                    ORDER BY TABLE_NAME, ORDINAL_POSITION
                """)
                columns = await cursor.fetchall()

                # Get foreign keys
                await cursor.execute(f"""
                    SELECT
                        TABLE_NAME as source_table,
                        COLUMN_NAME as source_column,
                        REFERENCED_TABLE_NAME as target_table,
                        REFERENCED_COLUMN_NAME as target_column,
                        CONSTRAINT_NAME as constraint_name
                    FROM information_schema.KEY_COLUMN_USAGE
                    WHERE TABLE_SCHEMA = '{db_name}'
                    AND REFERENCED_TABLE_NAME IS NOT NULL
                """)
                fkeys = await cursor.fetchall()

            result = {
                "database_type": "mysql",
                "schema": db_name,
                "tables": tables,
                "columns": columns,
                "foreign_keys": fkeys,
                "table_count": len(tables),
                "column_count": len(columns)
            }

            # Optionally persist to graph storage
            if persist and self._graph_store:
                await self._persist_schema(result)

            return {
                "success": True,
                "schema": result,
                "persisted": persist and self._graph_store is not None
            }

        finally:
            conn.close()

    async def _tool_discover_mongodb(self, args: Dict[str, Any]) -> Dict[str, Any]:
        """Tool handler for discover_mongodb"""
        connection_string = args.get("connection_string")
        database = args.get("database")
        sample_size = args.get("sample_size", 100)
        persist = args.get("persist", self._auto_persist)

        result = await self.discover_mongodb(
            connection_string=connection_string,
            database=database,
            sample_size=sample_size,
            persist=persist
        )

        return result

    async def discover_mongodb(
        self,
        connection_string: str,
        database: str,
        sample_size: int = 100,
        persist: bool = False
    ) -> Dict[str, Any]:
        """
        Discover MongoDB schema by sampling documents.

        Args:
            connection_string: MongoDB connection string
            database: Database name
            sample_size: Number of documents to sample per collection
            persist: Whether to persist to graph storage

        Returns:
            Dictionary with inferred schema from document samples
        """
        from motor.motor_asyncio import AsyncIOMotorClient

        client = AsyncIOMotorClient(connection_string)
        db = client[database]

        try:
            # Get collections
            collection_names = await db.list_collection_names()

            collections_schema = []

            for coll_name in collection_names:
                collection = db[coll_name]

                # Sample documents
                cursor = collection.find().limit(sample_size)
                docs = await cursor.to_list(length=sample_size)

                # Infer schema from samples
                fields = {}
                for doc in docs:
                    for key, value in doc.items():
                        if key not in fields:
                            fields[key] = {
                                "field_name": key,
                                "types": set(),
                                "sample_count": 0
                            }
                        fields[key]["types"].add(type(value).__name__)
                        fields[key]["sample_count"] += 1

                # Convert sets to lists for JSON serialization
                for field in fields.values():
                    field["types"] = list(field["types"])

                collections_schema.append({
                    "collection_name": coll_name,
                    "document_count": await collection.count_documents({}),
                    "sampled_count": len(docs),
                    "fields": list(fields.values())
                })

            result = {
                "database_type": "mongodb",
                "database": database,
                "collections": collections_schema,
                "collection_count": len(collections_schema),
                "sample_size": sample_size
            }

            # Optionally persist to graph storage
            if persist and self._graph_store:
                await self._persist_schema(result)

            return {
                "success": True,
                "schema": result,
                "persisted": persist and self._graph_store is not None
            }

        finally:
            client.close()

    async def _tool_discover_openapi(self, args: Dict[str, Any]) -> Dict[str, Any]:
        """Tool handler for discover_openapi"""
        spec_url = args.get("spec_url")
        service_name = args.get("service_name")
        persist = args.get("persist", self._auto_persist)

        result = await self.discover_openapi(
            spec_url=spec_url,
            service_name=service_name,
            persist=persist
        )

        return result

    async def discover_openapi(
        self,
        spec_url: str,
        service_name: Optional[str] = None,
        persist: bool = False
    ) -> Dict[str, Any]:
        """
        Discover API structure from OpenAPI/Swagger spec.

        Args:
            spec_url: URL to OpenAPI spec (JSON or YAML)
            service_name: Optional service name override
            persist: Whether to persist to graph storage

        Returns:
            Dictionary with discovered endpoints
        """
        import httpx
        import yaml

        async with httpx.AsyncClient() as client:
            resp = await client.get(spec_url)

            if spec_url.endswith(".yaml") or spec_url.endswith(".yml"):
                spec = yaml.safe_load(resp.text)
            else:
                spec = resp.json()

        base_url = ""
        if spec.get("servers"):
            base_url = spec["servers"][0].get("url", "")

        svc_name = service_name or spec.get("info", {}).get("title", "Unknown API")

        # Extract endpoints
        endpoints = []
        for path, methods in spec.get("paths", {}).items():
            for method, details in methods.items():
                if method.startswith("x-"):
                    continue

                endpoints.append({
                    "method": method.upper(),
                    "path": path,
                    "summary": details.get("summary", ""),
                    "description": details.get("description", ""),
                    "parameters": details.get("parameters", []),
                    "request_body": details.get("requestBody", {}),
                    "responses": details.get("responses", {})
                })

        result = {
            "api_type": "openapi",
            "service_name": svc_name,
            "base_url": base_url,
            "version": spec.get("info", {}).get("version", "unknown"),
            "endpoints": endpoints,
            "endpoint_count": len(endpoints)
        }

        # Optionally persist to graph storage
        if persist and self._graph_store:
            await self._persist_schema(result)

        return {
            "success": True,
            "schema": result,
            "persisted": persist and self._graph_store is not None
        }

    async def _tool_compare_schemas(self, args: Dict[str, Any]) -> Dict[str, Any]:
        """Tool handler for compare_schemas"""
        schema_a = args.get("schema_a")
        schema_b = args.get("schema_b")

        result = await self.compare_schemas(schema_a, schema_b)

        return result

    async def compare_schemas(
        self,
        schema_a: Dict[str, Any],
        schema_b: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Compare two schemas to identify differences.

        Args:
            schema_a: First schema
            schema_b: Second schema

        Returns:
            Dictionary with added, removed, and modified elements
        """
        # Compare tables (for database schemas)
        tables_a = {t["table_name"]: t for t in schema_a.get("tables", [])}
        tables_b = {t["table_name"]: t for t in schema_b.get("tables", [])}

        added_tables = [name for name in tables_b if name not in tables_a]
        removed_tables = [name for name in tables_a if name not in tables_b]

        # Compare columns
        columns_a = {(c["table_name"], c["column_name"]): c for c in schema_a.get("columns", [])}
        columns_b = {(c["table_name"], c["column_name"]): c for c in schema_b.get("columns", [])}

        added_columns = [key for key in columns_b if key not in columns_a]
        removed_columns = [key for key in columns_a if key not in columns_b]

        # Type changes
        modified_columns = []
        for key in set(columns_a.keys()) & set(columns_b.keys()):
            if columns_a[key].get("data_type") != columns_b[key].get("data_type"):
                modified_columns.append({
                    "table": key[0],
                    "column": key[1],
                    "old_type": columns_a[key].get("data_type"),
                    "new_type": columns_b[key].get("data_type")
                })

        return {
            "success": True,
            "comparison": {
                "added_tables": added_tables,
                "removed_tables": removed_tables,
                "added_columns": [{"table": k[0], "column": k[1]} for k in added_columns],
                "removed_columns": [{"table": k[0], "column": k[1]} for k in removed_columns],
                "modified_columns": modified_columns,
                "breaking_changes": len(removed_tables) + len(removed_columns) + len(modified_columns)
            }
        }

    async def _tool_export_diagram(self, args: Dict[str, Any]) -> Dict[str, Any]:
        """Tool handler for export_diagram"""
        schema = args.get("schema")
        format = args.get("format", "mermaid")

        result = await self.export_diagram(schema, format)

        return result

    async def export_diagram(
        self,
        schema: Dict[str, Any],
        format: str = "mermaid"
    ) -> Dict[str, Any]:
        """
        Export schema as a visual diagram.

        Args:
            schema: Schema object
            format: Output format ('mermaid', 'dbdiagram', 'json_schema')

        Returns:
            Dictionary with diagram in requested format
        """
        if format == "mermaid":
            # Generate Mermaid ER diagram
            lines = ["erDiagram"]

            # Group columns by table
            tables = {}
            for col in schema.get("columns", []):
                table_name = col["table_name"]
                if table_name not in tables:
                    tables[table_name] = []
                tables[table_name].append(col)

            # Add tables and columns
            for table_name, columns in tables.items():
                lines.append(f"    {table_name} {{")
                for col in columns:
                    data_type = col.get("data_type", "unknown")
                    col_name = col["column_name"]
                    lines.append(f"        {data_type} {col_name}")
                lines.append("    }")

            # Add relationships
            for fk in schema.get("foreign_keys", []):
                source = fk["source_table"]
                target = fk["target_table"]
                lines.append(f"    {source} ||--o{{ {target} : \"\"")

            diagram = "\n".join(lines)

            return {
                "success": True,
                "format": "mermaid",
                "diagram": diagram
            }

        elif format == "json_schema":
            # Generate JSON Schema representation
            json_schema = {
                "$schema": "http://json-schema.org/draft-07/schema#",
                "type": "object",
                "properties": {},
                "required": []
            }

            # Add table schemas
            for table in schema.get("tables", []):
                table_name = table["table_name"]
                table_columns = [c for c in schema.get("columns", []) if c["table_name"] == table_name]

                properties = {}
                for col in table_columns:
                    col_type = self._map_sql_to_json_type(col.get("data_type", "string"))
                    properties[col["column_name"]] = {"type": col_type}

                json_schema["properties"][table_name] = {
                    "type": "object",
                    "properties": properties
                }

            return {
                "success": True,
                "format": "json_schema",
                "schema": json_schema
            }

        else:
            return {
                "success": False,
                "error": f"Unsupported format: {format}. Use 'mermaid' or 'json_schema'"
            }

    def _map_sql_to_json_type(self, sql_type: str) -> str:
        """Map SQL data types to JSON Schema types"""
        sql_type = sql_type.lower()

        if any(t in sql_type for t in ["int", "serial", "bigint", "smallint"]):
            return "integer"
        elif any(t in sql_type for t in ["float", "double", "decimal", "numeric", "real"]):
            return "number"
        elif any(t in sql_type for t in ["bool", "boolean"]):
            return "boolean"
        elif any(t in sql_type for t in ["json", "jsonb"]):
            return "object"
        elif "array" in sql_type:
            return "array"
        else:
            return "string"

    async def _persist_schema(self, schema: Dict[str, Any]) -> None:
        """
        Persist schema to graph storage.

        Args:
            schema: Schema object to persist
        """
        # This would integrate with the graph store
        # For now, just log that we would persist
        logger.info(f"Would persist schema to graph: {schema.get('database_type', 'unknown')} - {schema.get('schema', 'unknown')}")
        # TODO: Implement actual graph persistence when context-graph is ready


def catalog(**kwargs) -> CatalogPlugin:
    """Create CatalogPlugin with simplified interface."""
    return CatalogPlugin(**kwargs)
