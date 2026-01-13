import logging
from typing import TypedDict

import boto3
from mcp.server.fastmcp import FastMCP
from pyiceberg.catalog import Catalog
from pyiceberg.catalog.glue import GlueCatalog

from iceberg_mcp import iceberg_config

logger = logging.getLogger("iceberg-mcp")

# Initialize FastMCP server
mcp = FastMCP("iceberg-mcp", "Iceberg MCP Server", version="0.1.0")


class SchemaField(TypedDict):
    id: int
    name: str
    type: str
    required: bool
    doc: str | None


@mcp.tool()
def get_namespaces() -> str:
    """Provides a list of namespaces from the Iceberg catalog."""
    catalog = get_catalog()
    namespaces = catalog.list_namespaces()
    return "\n".join(ns[0] for ns in namespaces)


@mcp.tool()
def get_iceberg_tables(namespace: str) -> str:
    """Provides a list of iceberg tables from the Iceberg catalog for a given namespace"""
    catalog = get_catalog()
    tables = catalog.list_tables(namespace)
    return "\n".join(t[1] for t in tables)


@mcp.tool()
def get_table_schema(
    namespace: str,
    table_name: str
) -> list[SchemaField]:
    """Provides the schema for a given Iceberg table""" 
    catalog: Catalog = get_catalog()
    table_obj = catalog.load_table((namespace, table_name))
    schema = table_obj.schema()

    fields = []
    for field in schema.fields:
        fields.append(
            {
                "id": field.field_id,
                "name": field.name,
                "type": str(field.field_type),
                "required": field.required,
                "doc": field.doc if field.doc else None,
            }
        )

    return fields


@mcp.tool()
def get_table_properties(
        namespace: str,
        table_name: str
) -> dict:
    catalog: Catalog = get_catalog()
    table_obj = catalog.load_table((namespace, table_name))
    partition_specs = [p.dict() for p in table_obj.metadata.partition_specs]
    sort_orders = [s.dict() for s in table_obj.metadata.sort_orders]
    current_snapshot = table_obj.current_snapshot()
    if not current_snapshot or not current_snapshot.summary:
        return {}
    return {
        "total_size_in_bytes": current_snapshot.summary["total-files-size"],
        "total_records": current_snapshot.summary["total-records"],
        "partition_specs": partition_specs,
        "sort_orders": sort_orders,
        **table_obj.properties
    }


@mcp.tool()
def get_table_partitions(
        namespace: str,
        table_name: str
) -> list[dict[str, int]]:
    """Provides the partitions for a given Iceberg table""" 
    catalog: Catalog = get_catalog()
    table_obj = catalog.load_table((namespace, table_name))
    partitions = table_obj.inspect.partitions().to_pylist()

    result = []
    for p in partitions:
        result.append(
            {
                "partition": p['partition'],
                "record_count": p['record_count'],
                "size_in_bytes": p['total_data_file_size_in_bytes'],
            }
        )
    return result

def get_catalog() -> GlueCatalog:
    try:
        session = boto3.Session(profile_name=iceberg_config.profile_name)
        credentials = session.get_credentials().get_frozen_credentials()

        catalog = GlueCatalog(
            "glue",
            **{
                "client.access-key-id": credentials.access_key,
                "client.secret-access-key": credentials.secret_key,
                "client.session-token": credentials.token,
                "client.region": iceberg_config.region,
            },
        )
    except Exception as e:
        logger.error(f"Error creating AWS connection: {str(e)}")
        raise
    return catalog


def main() -> None:
    mcp.run(transport="stdio")


if __name__ == "__main__":
    main()
