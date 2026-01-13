"""Base PostgreSQL service for generic CRUD operations."""
import json
from datetime import datetime, timezone
from typing import Dict, Any, List, Optional, Tuple
from optikka_design_data_layer import logger
from optikka_design_data_layer.db.postgres_client import postgres_client


class BasePostgresService:
    """Generic CRUD service for PostgreSQL tables."""

    def __init__(self, table_name: str, id_column: str = "id"):
        # Quote table name for PostgreSQL case sensitivity
        self.table_name = f'"{table_name}"' if not table_name.startswith('"') else table_name
        self.id_column = id_column

    def _convert_value_for_sql(self, value: Any, column_name: Optional[str] = None) -> Any:
        """Convert Python values to SQL-compatible formats."""
        # JSONB columns that should convert booleans/None to JSON
        jsonb_columns = {"qaRequired", "inputParameters"}
        
        if isinstance(value, dict):
            return json.dumps(value)
        elif isinstance(value, list):
            if value and isinstance(value[0], (dict, list)):
                return json.dumps(value)
            return value
        elif column_name and column_name in jsonb_columns:
            # For JSONB columns, convert booleans and None to JSON
            if isinstance(value, bool) or value is None:
                return json.dumps(value)
        elif hasattr(value, 'value'):
            # Handle enum types (e.g., BatchStatusEnum) - get the string value
            return value.value if hasattr(value, 'value') else str(value)
        elif hasattr(value, 'name'):
            # Handle enum types without value attribute - use name
            return value.name
        return value

    def _build_where_clause(self, filters: Dict[str, Any]) -> Tuple[str, List[Any]]:
        """Build WHERE clause from filters."""
        if not filters:
            return "", []

        conditions = []
        params = []

        for key, value in filters.items():
            if value is None:
                conditions.append(f'"{key}" IS NULL')
            elif isinstance(value, list) and len(value) > 0:
                # IN clause for lists
                placeholders = ",".join(["%s"] * len(value))
                conditions.append(f'"{key}" IN ({placeholders})')
                params.extend(value)
            elif isinstance(value, dict):
                # Handle operators like {"$ne": value}, {"$gt": value}, etc.
                for op, op_value in value.items():
                    if op == "$ne":
                        conditions.append(f'"{key}" != %s')
                        params.append(self._convert_value_for_sql(op_value))
                    elif op == "$gt":
                        conditions.append(f'"{key}" > %s')
                        params.append(self._convert_value_for_sql(op_value))
                    elif op == "$lt":
                        conditions.append(f'"{key}" < %s')
                        params.append(self._convert_value_for_sql(op_value))
                    elif op == "$gte":
                        conditions.append(f'"{key}" >= %s')
                        params.append(self._convert_value_for_sql(op_value))
                    elif op == "$lte":
                        conditions.append(f'"{key}" <= %s')
                        params.append(self._convert_value_for_sql(op_value))
                    elif op == "$like":
                        conditions.append(f'"{key}" LIKE %s')
                        params.append(op_value)
            else:
                conditions.append(f'"{key}" = %s')
                params.append(self._convert_value_for_sql(value))

        return " AND ".join(conditions), params

    def find_by_id(self, record_id: str, include_deleted: bool = False) -> Optional[Dict[str, Any]]:
        """Find record by ID."""
        try:
            with postgres_client.get_connection() as conn:
                with conn.cursor() as cur:
                    query = f'SELECT * FROM {self.table_name} WHERE "{self.id_column}" = %s'
                    params = [record_id]
                    if not include_deleted:
                        query += " AND deleted = false"
                    query += " LIMIT 1"
                    cur.execute(query, params)
                    row = cur.fetchone()
                    if row:
                        colnames = [desc[0] for desc in cur.description]
                        return dict(zip(colnames, row))
                    return None
        except Exception as e:
            logger.error(f"Error finding {self.table_name} by ID {record_id}: {e}", exc_info=True)
            return None

    def find_one(self, filters: Dict[str, Any], include_deleted: bool = False) -> Optional[Dict[str, Any]]:
        """Find single record matching filters."""
        try:
            with postgres_client.get_connection() as conn:
                with conn.cursor() as cur:
                    where_clause, params = self._build_where_clause(filters)
                    query = f"SELECT * FROM {self.table_name}"
                    if where_clause:
                        query += f" WHERE {where_clause}"
                    if not include_deleted:
                        query += " AND deleted = false" if where_clause else " WHERE deleted = false"
                    query += " LIMIT 1"
                    cur.execute(query, params)
                    row = cur.fetchone()
                    if row:
                        colnames = [desc[0] for desc in cur.description]
                        return dict(zip(colnames, row))
                    return None
        except Exception as e:
            logger.error(f"Error finding {self.table_name}: {e}", exc_info=True)
            return None

    def find_all(
        self,
        filters: Optional[Dict[str, Any]] = None,
        include_deleted: bool = False,
        limit: Optional[int] = None,
        offset: Optional[int] = None,
        order_by: Optional[str] = None,
        order_direction: str = "ASC",
    ) -> Tuple[List[Dict[str, Any]], int]:
        """Find all records with optional filtering, pagination, and ordering."""
        try:
            with postgres_client.get_connection() as conn:
                with conn.cursor() as cur:
                    where_clause, params = self._build_where_clause(filters or {})
                    query_where = f"WHERE {where_clause}" if where_clause else ""
                    if not include_deleted:
                        query_where += " AND deleted = false" if query_where else "WHERE deleted = false"
                    order_clause = f'ORDER BY "{order_by}" {order_direction}' if order_by else ""
                    limit_clause = f"LIMIT {limit}" + (f" OFFSET {offset}" if offset is not None else "") if limit is not None else ""
                    count_query = f"SELECT COUNT(*) as count FROM {self.table_name} {query_where}"
                    cur.execute(count_query, params)
                    total_count = cur.fetchone()[0] or 0
                    query = f"SELECT * FROM {self.table_name} {query_where} {order_clause} {limit_clause}"
                    cur.execute(query, params)
                    rows = cur.fetchall()
                    if rows:
                        colnames = [desc[0] for desc in cur.description]
                        return [dict(zip(colnames, row)) for row in rows], total_count
                    return [], total_count
        except Exception as e:
            logger.error(f"Error finding all {self.table_name}: {e}", exc_info=True)
            return [], 0

    def create(self, data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Create new record."""
        try:
            with postgres_client.get_connection() as conn:
                with conn.cursor() as cur:
                    columns = list(data.keys())
                    values = [self._convert_value_for_sql(data[col], col) for col in columns]
                    quoted_columns = [f'"{col}"' for col in columns]
                    placeholders = ",".join(["%s"] * len(columns))
                    query = f'INSERT INTO {self.table_name} ({",".join(quoted_columns)}) VALUES ({placeholders}) RETURNING *'
                    cur.execute(query, values)
                    row = cur.fetchone()
                    conn.commit()
                    if row:
                        colnames = [desc[0] for desc in cur.description]
                        record = dict(zip(colnames, row))
                        logger.debug(f"Created {self.table_name} {record.get(self.id_column)}")
                        return record
                    return None
        except Exception as e:
            logger.error(f"Error creating {self.table_name}: {e}", exc_info=True)
            return None

    def update(self, record_id: str, data: Dict[str, Any], include_deleted: bool = False) -> Optional[Dict[str, Any]]:
        """Update existing record."""
        try:
            if not data:
                return None
            with postgres_client.get_connection() as conn:
                with conn.cursor() as cur:
                    if "updatedAt" not in data:
                        data["updatedAt"] = datetime.now(timezone.utc)
                    set_clauses = [f'"{key}" = %s' for key in data.keys()]
                    values = [self._convert_value_for_sql(v, key) for key, v in data.items()] + [record_id]
                    where_clause = f'"{self.id_column}" = %s'
                    if not include_deleted:
                        where_clause += " AND deleted = false"
                    query = f'UPDATE {self.table_name} SET {",".join(set_clauses)} WHERE {where_clause} RETURNING *'
                    cur.execute(query, values)
                    row = cur.fetchone()
                    conn.commit()
                    if row:
                        colnames = [desc[0] for desc in cur.description]
                        return dict(zip(colnames, row))
                    return None
        except Exception as e:
            logger.error(f"Error updating {self.table_name} {record_id}: {e}", exc_info=True)
            return None

    def delete(self, record_id: str, soft_delete: bool = True) -> bool:
        """Delete record (soft delete by default)."""
        try:
            with postgres_client.get_connection() as conn:
                with conn.cursor() as cur:
                    if soft_delete:
                        query = f'UPDATE {self.table_name} SET deleted = true, "updatedAt" = %s WHERE "{self.id_column}" = %s AND deleted = false'
                        cur.execute(query, [datetime.now(timezone.utc), record_id])
                    else:
                        query = f'DELETE FROM {self.table_name} WHERE "{self.id_column}" = %s'
                        cur.execute(query, [record_id])
                    conn.commit()
                    return cur.rowcount > 0
        except Exception as e:
            logger.error(f"Error deleting {self.table_name} {record_id}: {e}", exc_info=True)
            return False
