import json
import logging
from typing import Any, Dict, Iterable, List, Optional, Union

from sfn_db_query_builder import fetch_column_name_datatype
from sqlalchemy import inspect, text
from sqlalchemy.exc import SQLAlchemyError
from .context_helper import fetch_data_central_db

logger = logging.getLogger(__name__)

class ContextManager:
    """
    A context manager class to provide and manage context/metadata for agents.
    It handles the lifecycle of context data, ensuring proper setup and teardown.
    """

    def __init__(self, config: Optional[Dict[str, Any]] = None, **kwargs):
        """
        Initializes the ContextManager.

        Args:
            config (Optional[Dict[str, Any]]): Configuration dictionary for context management.
            **kwargs: Additional parameters for context initialization (e.g., user_id, session_id).
        """
        self.config = config if config is not None else {}
        self.context_data: Dict[str, Any] = {}
        self.session_id = kwargs.get("session_id")
        self.user_id = kwargs.get("user_id")
        logger.info(f"ContextManager initialized for session_id: {self.session_id}, user_id: {self.user_id}")

    def __enter__(self):
        """
        Enters the runtime context related to this object.
        Performs setup operations like loading initial context data or establishing connections.
        """
        logger.info(f"Entering ContextManager for session_id: {self.session_id}")
        # Placeholder for actual context loading/connection establishment
        self._load_initial_context()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """
        Exits the runtime context related to this object.
        Performs cleanup operations like closing connections or saving state.
        """
        logger.info(f"Exiting ContextManager for session_id: {self.session_id}")
        # Placeholder for actual context cleanup/state saving
        self._cleanup_context()
        if exc_type:
            logger.error(f"ContextManager exited with an exception: {exc_val}", exc_info=True)
        return False # Propagate exceptions

    def _load_initial_context(self):
        """
        Internal method to load initial context data.
        This would typically involve fetching common data like global settings,
        or user-specific preferences based on session_id/user_id.
        """
        logger.debug("Loading initial context data...")
        # Example: self.context_data["global_settings"] = self._fetch_global_settings()
        # Example: self.context_data["user_preferences"] = self._fetch_user_preferences(self.user_id)
        pass

    def _cleanup_context(self):
        """
        Internal method to clean up context resources.
        This would typically involve closing database connections,
        saving transient state, or releasing locks.
        """
        logger.debug("Cleaning up context resources...")
        # Example: self._close_database_connection()
        # Example: self._save_session_state(self.session_id, self.context_data)
        pass


    def format_domain_info(self, domain_desc: Dict[str, Any]) -> str:
        """
        Formats domain information into a readable string.
        """
        formatted_domain_desc = "## Domain\n"
        if domain_desc:
            formatted_domain_desc += (
                f"- {domain_desc['name']}: {domain_desc['description']}\n"
            )
        return formatted_domain_desc

    def format_node_info(self, node_desc: List[Dict[str, Any]]) -> str:
        """
        Formats node information into a readable string.
        """
        formatted_node_desc = "## Categories\n"
        for node in node_desc:
            formatted_node_desc += f"- {node['name']}: {node['description']}\n"
        return formatted_node_desc

    @staticmethod
    def _quote_identifier(identifier: str) -> str:
        """
        Safely quote SQL identifiers (schema, table, column names).
        """
        if identifier is None:
            raise ValueError("Identifier cannot be None.")
        return '"' + str(identifier).replace('"', '""') + '"'


    @staticmethod
    def _escape_literal(value: Any) -> str:
        """
        Safely escape literal values for SQL string interpolation.
        """
        if value is None:
            return "NULL"
        return "'" + str(value).replace("'", "''") + "'"


    @staticmethod
    def _parse_use_case_pack(use_case_pack: Any) -> Dict[str, Any]:
        """
        Ensure the use_case_pack field is returned as a dictionary.
        """
        if not use_case_pack:
            return {}
        if isinstance(use_case_pack, dict):
            return use_case_pack
        if isinstance(use_case_pack, str):
            try:
                return json.loads(use_case_pack)
            except json.JSONDecodeError:
                logger.warning("Unable to decode use_case_pack JSON.")
        return {}

    def get_domain_metadata(
        self,
        domain_id: Union[int, str],
        use_case: Optional[str] = None,
        include_methodology: bool = True,
    ) -> Dict[str, Any]:
        """
        Fetch enriched domain metadata, including optional methodology details.
        """
        sanitized_domain_id = self._escape_literal(domain_id)
        query = f"""
        SELECT
            name,
            description,
            industry_name,
            use_case_pack
        FROM sfnge.public.domains
        WHERE id = {sanitized_domain_id}
        """
        logger.debug("Fetching domain metadata with query: %s", query.strip())
        result = fetch_data_central_db(query, fetch="one", mappings=True)
        if not result:
            logger.warning("Domain metadata not found for id=%s", domain_id)
            return {}

        metadata: Dict[str, Any] = {
            "id": domain_id,
            "name": result.get("name"),
            "description": result.get("description"),
            "industry_name": result.get("industry_name"),
        }

        use_case_pack = self._parse_use_case_pack(result.get("use_case_pack"))
        metadata["use_case_pack"] = use_case_pack

        modelling_approach = None
        if include_methodology and use_case:
            use_case_collection = use_case_pack.get("use_case") if isinstance(use_case_pack, dict) else {}
            use_case_entry = {}
            if isinstance(use_case_collection, dict):
                use_case_entry = use_case_collection.get(use_case, {})
            if isinstance(use_case_entry, dict):
                modelling_approach = (
                    use_case_entry.get("methodology")
                    or use_case_entry.get("modelling_approach")
                )

        if include_methodology:
            metadata["modelling_approach"] = modelling_approach

        return metadata

    def format_domain_metadata(self, domain_metadata: Optional[Dict[str, Any]]) -> str:
        """
        Render domain metadata into a prompt-friendly string.
        """
        if not domain_metadata:
            return "## Domain\n- No domain metadata available.\n"

        lines = ["## Domain"]

        name = domain_metadata.get("name")
        industry = domain_metadata.get("industry_name")
        description = domain_metadata.get("description")
        modelling_approach = domain_metadata.get("modelling_approach")

        summary_parts: List[str] = []
        if name:
            summary_parts.append(name)
        if industry:
            summary_parts.append(f"Industry: {industry}")
        if summary_parts:
            lines.append(f"- {' | '.join(summary_parts)}")

        if description:
            lines.append(f"- Description: {description}")

        if modelling_approach:
            lines.append(f"- Modelling Approach: {modelling_approach}")

        return "\n".join(lines) + "\n"

    def get_domain_entities(
        self,
        domain_id: Union[int, str],
        include_descriptions: bool = True,
        status: bool = False,
    ) -> List[Dict[str, Any]]:
        """
        Fetch all entities for a given domain.

        Args:
            domain_id: The domain ID
            include_descriptions: Whether to include entity descriptions
            status: Optional status filter (e.g., 'APPROVED')
        """
        columns = "name, description" if include_descriptions else "name"
        query = f"""
        SELECT {columns}
        FROM sfnge.public.domain_nodes
        WHERE domain_id = {domain_id}
        """

        if status:
            query += " AND status = 'APPROVED'"

        query += " ORDER BY name"

        logger.debug("Fetching domain entities with query: %s", query.strip())
        results = fetch_data_central_db(query, fetch="all", mappings=True)
        if not results:
            return []

        return results

    def get_entity_description(
        self,
        domain_id: Union[int, str],
        entity_name: str,
    ) -> Optional[str]:
        """
        Fetch a single entity description belonging to a domain.
        """
        sanitized_domain_id = self._escape_literal(domain_id)
        sanitized_entity_name = self._escape_literal(entity_name)

        query = f"""
        SELECT description
        FROM sfnge.public.domain_nodes
        WHERE domain_id = {sanitized_domain_id}
            AND name = {sanitized_entity_name}
        """

        logger.debug(
            "Fetching entity description with query: %s", query.replace("\n", " ").strip()
        )
        result = fetch_data_central_db(query, fetch="one", mappings=True)
        if not result:
            return None
        return result.get("description")

    def get_node_attributes(
        self,
        node_id: Optional[Union[int, str]] = None,
        domain_id: Optional[Union[int, str]] = None,
        entity_name: Optional[str] = None,
    ) -> List[Dict[str, Any]]:
        """
        Fetches canonical fields/attributes for a node.

        Either node_id must be provided, or both domain_id and entity_name.

        Args:
            node_id: Direct node ID to fetch attributes for.
            domain_id: Domain ID (required if node_id not provided).
            entity_name: Entity name (required if node_id not provided).

        Returns:
            List of dictionaries containing name, data_type, and description for approved node attributes.
        """
        if node_id is None and (domain_id is None or entity_name is None):
            raise ValueError(
                "Either node_id must be provided, or both domain_id and entity_name must be provided"
            )

        logger.debug(
            f"Fetching node attributes for node_id={node_id}, domain_id={domain_id}, entity_name={entity_name}"
        )

        if node_id is not None:
            query = f"""
                SELECT name,
                    data_type,
                    description
                FROM sfnge.public.node_attributes
                WHERE node_id = '{node_id}'
                    AND is_approved = TRUE
            """
        else:
            query = f"""
                SELECT name,
                    data_type,
                    description
                FROM sfnge.public.node_attributes
                WHERE node_id IN (
                        SELECT id
                        FROM sfnge.public.domain_nodes
                        WHERE domain_id = '{domain_id}'
                            AND name = '{entity_name}'
                    )
                    AND is_approved = TRUE
            """
        canonical_fields = fetch_data_central_db(query, fetch="all", mappings=True)

        if not canonical_fields:
            logger.warning(
                f"No canonical fields found for node_id={node_id}, "
                f"domain_id={domain_id}, entity_name={entity_name}"
            )
            return []

        return canonical_fields

    def get_entity_mapping(
        self,
        entity_name: str,
        schema_name: str,
        db_session,
        domain_id: Optional[Union[int, str]] = None,
    ) -> List[str]:
        """
        Fetches the table mapping for a given entity.
        """
        logger.debug(
            f"Fetching entity mapping for entity '{entity_name}'"
            f"{f' for domain {domain_id}' if domain_id else ''}."
        )

        try:
            base_query = f"SELECT table_name FROM {schema_name}.entity_table_mapping WHERE entity_name = '{entity_name}'"

            if domain_id is not None:
                base_query += f" AND domain_id = {domain_id}"

            entity_mapping_row = db_session.execute(text(base_query)).mappings().first()

            if not entity_mapping_row or not entity_mapping_row.get("table_name"):
                logger.warning(
                    f"No entity mapping found for entity '{entity_name}'"
                    f"{f' for domain {domain_id}' if domain_id else ''}."
                )
                return []

            return json.loads(entity_mapping_row["table_name"])

        except json.JSONDecodeError as e:
            logger.exception(f"Error decoding entity mapping JSON for '{entity_name}': {e}")
            raise Exception(f"Error decoding entity mapping for '{entity_name}': {str(e)}") from e
        except Exception as e:
            logger.exception(f"An error occurred while fetching entity mapping for '{entity_name}': {e}")
            raise e

    def get_mappings(self, entity_name: str, schema_name: str, table_name: str, db_session: Any) -> Dict[str, List[Any]]:
        """
        Fetches mappings for a given table and entity.
        """
        logger.debug(f"Fetching mappings for table '{table_name}' in schema '{schema_name}' for entity '{entity_name}'.")
        try:
            
            query = text(f"""
                SELECT
                    column_name,
                    client_column_name,
                    data_type
                FROM
                    {schema_name}.category_schema_mapping
                WHERE
                    table_name = :table_name
                    AND client_column_name IS NOT NULL
                    AND client_column_name != ''
                    AND category_name = :entity_name
            """)

            mappings_rows = db_session.execute(
                query,
                {"table_name": table_name, "entity_name": entity_name}
            ).mappings().all()

            if not mappings_rows:
                logger.warning(f"Mapping for table {table_name} is not present for entity {entity_name}.")
                return {}

            result = {}
            for mapping in mappings_rows:
                std_column_name = mapping['column_name']
                client_column_name = mapping['client_column_name']
                data_type = mapping['data_type']
                result[std_column_name] = [client_column_name.lower(), data_type]

            return result
        except SQLAlchemyError as e:
            logger.exception(f"Error fetching mappings for table {table_name}: {e}")
            raise Exception(f"Error fetching mappings for table {table_name}: {str(e)}") from e

    def get_use_case_details(
        self,
        project_name: str,
        db_session,
        additional_columns: Optional[List[str]] = None,
    ) -> Dict[str, Any]:
        """
        Retrieve the configured use case for a project, including narrative context.

        Args:
            project_name: The project name
            db_session: Database session
            additional_columns: Optional list of additional column names to fetch

        Returns:
            Dictionary containing use case details including name, description, raw_labels,
            and any additional columns requested
        """
        if not db_session:
            raise ValueError("db_session is required to fetch use case details.")

        # Build SELECT clause
        select_columns = ["labels", "target_logic"]
        if additional_columns:
            select_columns.extend(additional_columns)

        select_clause = ", ".join(select_columns)

        query = text(
            f"""
            SELECT {select_clause}
            FROM {project_name}.dataset_labels
            """
        )

        try:
            row = db_session.execute(query).mappings().first()
        except SQLAlchemyError as exc:
            logger.exception("Failed to fetch use case details: %s", exc)
            return {}

        if not row:
            return {}

        labels_payload = row.get("labels")
        parsed_labels: Any = labels_payload
        if isinstance(labels_payload, str):
            try:
                parsed_labels = json.loads(labels_payload)
            except json.JSONDecodeError:
                logger.warning("Invalid JSON in dataset_labels.labels for project %s.", project_name)
        use_case_name = None
        if isinstance(parsed_labels, list) and parsed_labels:
            first_entry = parsed_labels[0]
            if isinstance(first_entry, dict):
                use_case_name = first_entry.get("use_case") or first_entry.get("name")

        result = {
            "name": use_case_name,
            "description": row.get("target_logic"),
            "raw_labels": parsed_labels,
        }

        # Add additional columns to result if requested
        if additional_columns:
            for col in additional_columns:
                result[col] = row.get(col)

        return result

    def get_primary_entity_info(
        self,
        project_name: str,
        domain_id: Optional[Union[int, str]],
        db_session,
    ) -> Dict[str, Any]:
        """
        Determine the primary entity/category and its backing table for a project.
        """
        if not db_session:
            raise ValueError("db_session is required to derive primary entity metadata.")

        final_mapping_query = text(
            f"""
            SELECT category_name
            FROM {project_name}.final_dataset_mapping
            WHERE sfn_column_name = 'primary_category'
            """
        )

        try:
            primary_mapping = db_session.execute(final_mapping_query).mappings().first()
        except SQLAlchemyError as exc:
            logger.exception("Failed to fetch primary category: %s", exc)
            return {}

        if not primary_mapping:
            return {}

        primary_category = primary_mapping.get("category_name")
        if not primary_category:
            return {}

        schema_name = f"{project_name}_operations"
        category_literal = json.dumps([primary_category])

        lineage_query = text(
            f"""
            SELECT tablename
            FROM {schema_name}.lineage
            WHERE category = :category_literal
                AND COALESCE(level, 0) = 0
            ORDER BY updated_at DESC
            LIMIT 1
            """
        )

        try:
            lineage_row = db_session.execute(
                lineage_query,
                {"category_literal": category_literal},
            ).mappings().first()
        except SQLAlchemyError as exc:
            logger.exception("Failed to fetch primary entity table: %s", exc)
            lineage_row = None

        metadata = {
            "primary_category": primary_category,
            "primary_entity_table": lineage_row.get("tablename") if lineage_row else None,
            "schema_name": schema_name,
        }

        if domain_id is not None:
            metadata["domain_metadata"] = self.get_domain_metadata(domain_id)

        return metadata

    def resolve_operation_table(
        self,
        project_name: str,
        table_name: str,
        db_session,
        exclude_operation_types: Optional[Iterable[str]] = None,
    ) -> Optional[str]:
        """
        Resolve the latest operation table backing a logical table.
        """
        if not db_session:
            raise ValueError("db_session is required to resolve operation tables.")

        schema_name = f"{project_name}_operations"
        exclusions = tuple(exclude_operation_types) if exclude_operation_types else ("join",)
        exclusion_clause = ", ".join(self._escape_literal(item) for item in exclusions)

        query = text(
            f"""
            SELECT operation_id
            FROM {schema_name}.operation_details
            WHERE tablename = :table_name
            AND operation_type NOT IN ({exclusion_clause})
            ORDER BY sequence DESC
            LIMIT 1
            """
        )

        try:
            record = db_session.execute(query, {"table_name": table_name}).mappings().first()
        except SQLAlchemyError as exc:
            logger.exception("Failed to resolve operation table: %s", exc)
            record = None

        if record and record.get("operation_id"):
            return f"_{record['operation_id']}"

        return None

    def get_tables_from_lineage(
        self,
        schema_name: str,
        db_session,
        depth_filter: Optional[int] = 0,
    ) -> List[str]:
        """
        Fetch lineage tables for a project, optionally filtered by depth/level.
        """
        if not db_session:
            raise ValueError("db_session is required to fetch table list.")

        base_query = f"""
            SELECT tablename
            FROM {schema_name}.lineage
        """

        params: Dict[str, Any] = {}
        if depth_filter is not None:
            base_query += " WHERE COALESCE(level, 0) = :depth"
            params["depth"] = depth_filter

        base_query += " ORDER BY tablename"

        query = text(base_query)

        try:
            rows = db_session.execute(query, params).fetchall()
        except SQLAlchemyError as exc:
            logger.exception("Failed to fetch table list: %s", exc)
            return []

        return [row[0] if isinstance(row, tuple) else row.tablename for row in rows if row]

    def get_table_descriptions(
        self,
        schema_name: str,
        db_session,
        table_names: Optional[Iterable[str]] = None,
    ) -> Dict[str, str]:
        """
        Fetch descriptions for the supplied tables from table_description.
        """
        if not db_session:
            raise ValueError("db_session is required to fetch table descriptions.")

        base_query = f"""
            SELECT table_name, description
            FROM {schema_name}.table_description
        """
        params: Dict[str, Any] = {}

        if table_names:
            table_names = list(table_names)
            if not table_names:
                return {}

            placeholders = ", ".join(f":table_{idx}" for idx, _ in enumerate(table_names))
            base_query += f" WHERE table_name IN ({placeholders})"
            params = {f"table_{idx}": name for idx, name in enumerate(table_names)}

        query = text(base_query)

        try:
            rows = db_session.execute(query, params).mappings().all()
        except SQLAlchemyError as exc:
            logger.exception("Failed to fetch table descriptions: %s", exc)
            return {}

        return {
            row.get("table_name"): row.get("description") or ""
            for row in rows
            if row and row.get("table_name")
        }

    def get_sample_rows(
        self,
        schema_name: str,
        table_name: str,
        db_session,
        limit: int = 10,
        columns: Optional[Iterable[str]] = None,
        strategy: str = "head",
    ) -> List[Dict[str, Any]]:
        """
        Fetch a representative sample of rows from a table.
        """
        if not db_session:
            raise ValueError("db_session is required to fetch table samples.")

        qualified_table = f"{schema_name}.{table_name}"

        projected_columns = "*"
        if columns:
            projected_columns = ", ".join(columns)

        order_clause = ""

        if strategy == "random":
            order_clause = " ORDER BY RANDOM()"

        elif strategy == "non-null":

            if not columns:
                # fetch all columns for the table
                col_query = text("""
                    SELECT column_name
                    FROM information_schema.columns
                    WHERE table_schema = :schema_name
                    AND table_name = :table_name
                    ORDER BY ordinal_position
                """)

                result = db_session.execute(col_query, {
                    "schema_name": schema_name.upper(),
                    "table_name": table_name.upper()
                }).fetchall()

                columns = [row[0] for row in result]

                if not columns:
                    raise ValueError(f"Could not fetch columns for {qualified_table}")

                projected_columns = ", ".join(columns)

            case_expr = " + ".join(
                [f"CASE WHEN {col} IS NOT NULL THEN 1 ELSE 0 END" for col in columns]
            )

            order_clause = f" ORDER BY {case_expr} DESC"

        query = text(
            f"""
            SELECT {projected_columns}
            FROM {qualified_table}
            {order_clause}
            LIMIT :limit
            """
        )

        try:
            rows = db_session.execute(query, {"limit": limit}).mappings().all()
        except SQLAlchemyError as exc:
            logger.exception("Failed to fetch table samples: %s", exc)
            return []

        return [dict(row) for row in rows if row]

    def get_column_datatypes(
        self,
        schema_name: str,
        table_name: str,
        db_session,
    ) -> Dict[str, str]:
        """
        Retrieve column data types using INFORMATION_SCHEMA.
        """
        if not db_session:
            raise ValueError("db_session is required to fetch column data types.")

        query = text(
            """
            SELECT
                COLUMN_NAME,
                DATA_TYPE,
                CHARACTER_MAXIMUM_LENGTH,
                NUMERIC_PRECISION,
                NUMERIC_SCALE
            FROM INFORMATION_SCHEMA.COLUMNS
            WHERE TABLE_SCHEMA = :schema_name
                AND TABLE_NAME = :table_name
            ORDER BY ORDINAL_POSITION
            """
        )

        try:
            rows = db_session.execute(
                query,
                {
                    "schema_name": schema_name.upper(),
                    "table_name": table_name.upper(),
                },
            ).fetchall()
        except SQLAlchemyError as exc:
            logger.exception("Failed to fetch column data types: %s", exc)
            return {}

        column_types: Dict[str, str] = {}
        for row in rows:
            column_name = row[0]
            data_type = row[1]
            char_length = row[2]
            numeric_precision = row[3]
            numeric_scale = row[4]

            if char_length and data_type and data_type.upper() in {"VARCHAR", "CHAR", "STRING", "TEXT"}:
                formatted = f"{data_type}({char_length})"
            elif numeric_precision and data_type and data_type.upper() in {"NUMBER", "DECIMAL", "NUMERIC"}:
                if numeric_scale and numeric_scale > 0:
                    formatted = f"{data_type}({numeric_precision},{numeric_scale})"
                else:
                    formatted = f"{data_type}({numeric_precision})"
            else:
                formatted = data_type

            column_types[column_name] = formatted

        return column_types

    def get_column_descriptions(
        self,
        project_name: str,
        table_name: str,
        schema_name: Optional[str] = None,
        db_session=None,
        additional_columns: Optional[List[str]] = None,
    ) -> Dict[str, Any]:
        """
        Fetch column descriptions from column_descriptions table.

        Args:
            project_name: The project name
            table_name: The table name
            schema_name: Optional schema name filter
            db_session: Database session
            additional_columns: Optional list of additional columns to fetch (will be converted to lowercase)

        Returns:
            If additional_columns is None: Dict[str, str] mapping column_name -> description
            If additional_columns is provided: Dict[str, Dict[str, Any]] mapping column_name -> {description, ...additional_columns}
        """
        if not db_session:
            raise ValueError("db_session is required to fetch column descriptions.")

        # Build SELECT clause
        select_columns = "column_name, description"
        if additional_columns:
            additional_cols_lower = [col.lower() for col in additional_columns]
            select_columns += ", " + ", ".join(additional_cols_lower)

        base_query = f"""
            SELECT {select_columns}
            FROM {project_name}.column_descriptions
            WHERE table_name = :table_name
        """

        params = {"table_name": table_name}

        if schema_name is not None:
            base_query += " AND schema_name = :schema_name"
            params["schema_name"] = schema_name

        query = text(base_query)

        try:
            rows = db_session.execute(query, params).mappings().all()
        except SQLAlchemyError as exc:
            logger.exception("Failed to fetch column descriptions: %s", exc)
            return {}

        # Return format depends on whether additional_columns were requested
        if not additional_columns:
            # Backward compatible: return simple column_name -> description mapping
            return {
                row.get("column_name"): row.get("description") or ""
                for row in rows
                if row and row.get("column_name")
            }
        else:
            # Return column_name -> {description, ...additional fields} mapping
            result = {}
            for row in rows:
                if row and row.get("column_name"):
                    column_data = {"description": row.get("description") or ""}
                    for col in additional_columns:
                        column_data[col.lower()] = row.get(col.lower())
                    result[row.get("column_name")] = column_data
            return result

    def get_column_statistics(
        self,
        schema_name: str,
        table_name: str,
        db_session,
        columns: Optional[List[str]] = None,
        metrics: Optional[List[str]] = None,
        column_data_types: Optional[List[Dict[str, str]]] = None,
        top_k: int = 5,
    ) -> Dict[str, Any]:
        """
        Compute comprehensive column statistics in an optimized manner.

        Args:
            schema_name: Schema name
            table_name: Table name
            db_session: Database session
            columns: List of column names to analyze. If None, analyze all columns
            metrics: List of metrics to compute. If None, compute all available metrics.
                Available metrics: 'row_count', 'null_count', 'null_fraction', 'null_percentage',
                'distinct_count', 'min_value', 'max_value', 'mean', 'std', 'top_values'
            column_data_types: Optional pre-fetched column types (list of {'column_name': str, 'data_type': str})
            top_k: Number of top values to return for frequency analysis (default: 5)

        Returns:
            Dictionary with structure:
            {
                "row_count": int,
                "columns": {
                    "column_name": {
                        "data_type": str,
                        "null_count": int,
                        "null_fraction": float,
                        "null_percentage": float,
                        "distinct_count": int,
                        "min_value": Any,
                        "max_value": Any,
                        "mean": float (numeric only),
                        "std": float (numeric only),
                        "top_values": [{"value": Any, "count": int}, ...]
                    },
                    ...
                }
            }
        """
        if not db_session:
            raise ValueError("db_session is required to compute column statistics.")

        qualified_table = f"{schema_name}.{table_name}"

        # Define all possible metrics
        all_metrics = {
            'row_count', 'null_count', 'null_fraction', 'null_percentage',
            'distinct_count', 'min_value', 'max_value', 'mean', 'std', 'top_values'
        }

        # If metrics not specified, compute all except top_values (expensive)
        if metrics is None:
            metrics = ['null_count', 'null_fraction', 'null_percentage', 'distinct_count',
                      'min_value', 'max_value', 'mean', 'std']

        # Validate metrics
        invalid_metrics = set(metrics) - all_metrics
        if invalid_metrics:
            logger.warning(f"Invalid metrics requested: {invalid_metrics}. Ignoring them.")
            metrics = [m for m in metrics if m in all_metrics]

        # Get table row count if needed
        row_count_query = text(f"SELECT COUNT(*) AS row_count FROM {qualified_table}")
        try:
            row = db_session.execute(row_count_query).first()
            total_rows = row[0] if row else 0
        except SQLAlchemyError as exc:
            logger.exception("Failed to compute row count: %s", exc)
            return {"row_count": 0, "columns": {}}

        # Get column data types
        if column_data_types is None:
            if columns is None:
                column_types_dict = self.get_column_datatypes(schema_name, table_name, db_session)
                column_data_types = [
                    {"column_name": col_name, "data_type": col_type}
                    for col_name, col_type in column_types_dict.items()
                ]
            else:
                # Fetch only for specified columns
                column_types_dict = self.get_column_datatypes(schema_name, table_name, db_session)
                column_data_types = [
                    {"column_name": col_name, "data_type": column_types_dict.get(col_name, "UNKNOWN")}
                    for col_name in columns
                    if col_name in column_types_dict
                ]

        # Filter by requested columns if specified
        if columns is not None:
            column_data_types = [
                col_info for col_info in column_data_types
                if col_info["column_name"] in columns
            ]

        if not column_data_types or total_rows == 0:
            return {"row_count": total_rows, "columns": {}}

        # Define numeric types for mean/std computation
        NUMERICAL_TYPES = {
            "number", "decimal", "numeric", "float", "double", "real",
            "int", "integer", "bigint", "smallint", "tinyint"
        }

        # Build unified query for basic metrics using UNION ALL
        queries = []
        for col_info in column_data_types:
            column_name = col_info["column_name"]
            data_type = col_info["data_type"]
            base_type = data_type.split("(")[0].strip().lower()
            is_numeric = base_type in NUMERICAL_TYPES

            # Build SELECT clause based on requested metrics
            select_parts = [f"'{column_name}' AS column_name"]

            if 'null_count' in metrics or 'null_fraction' in metrics or 'null_percentage' in metrics:
                select_parts.append(
                    f"SUM(CASE WHEN {column_name} IS NULL THEN 1 ELSE 0 END) AS null_count"
                )

            if 'distinct_count' in metrics:
                select_parts.append(f"COUNT(DISTINCT {column_name}) AS distinct_count")

            if 'mean' in metrics:
                if is_numeric:
                    select_parts.append(f"AVG(CAST({column_name} AS FLOAT)) AS mean")
                else:
                    select_parts.append("NULL AS mean")

            if 'std' in metrics:
                if is_numeric:
                    select_parts.append(f"STDDEV(CAST({column_name} AS FLOAT)) AS std")
                else:
                    select_parts.append("NULL AS std")

            if 'min_value' in metrics:
                select_parts.append(f"CAST(MIN({column_name}) AS TEXT) AS min_val")

            if 'max_value' in metrics:
                select_parts.append(f"CAST(MAX({column_name}) AS TEXT) AS max_val")

            query = f"SELECT {', '.join(select_parts)} FROM {qualified_table}"
            queries.append(f"({query})")

        # Execute unified query
        final_query = " UNION ALL ".join(queries)

        try:
            result = db_session.execute(text(final_query)).fetchall()
        except SQLAlchemyError as exc:
            logger.exception("Failed to compute column statistics: %s", exc)
            return {"row_count": total_rows, "columns": {}}

        # Parse results into dictionary
        stats: Dict[str, Any] = {
            "row_count": total_rows,
            "columns": {}
        }

        # Map column data types for quick lookup
        col_type_map = {
            col_info["column_name"]: col_info["data_type"]
            for col_info in column_data_types
        }

        for row in result:
            col_name = row[0]
            col_stats = {"data_type": col_type_map.get(col_name, "UNKNOWN")}

            idx = 1
            if 'null_count' in metrics or 'null_fraction' in metrics or 'null_percentage' in metrics:
                null_count = row[idx] or 0
                col_stats["null_count"] = int(null_count)
                if 'null_fraction' in metrics:
                    col_stats["null_fraction"] = round(null_count / total_rows, 4) if total_rows else 0.0
                if 'null_percentage' in metrics:
                    col_stats["null_percentage"] = round((null_count / total_rows) * 100, 2) if total_rows else 0.0
                idx += 1

            if 'distinct_count' in metrics:
                col_stats["distinct_count"] = int(row[idx] or 0)
                idx += 1

            if 'mean' in metrics:
                mean_val = row[idx]
                col_stats["mean"] = round(mean_val, 3) if mean_val is not None else None
                idx += 1

            if 'std' in metrics:
                std_val = row[idx]
                col_stats["std"] = round(std_val, 3) if std_val is not None else None
                idx += 1

            if 'min_value' in metrics:
                col_stats["min_value"] = row[idx]
                idx += 1

            if 'max_value' in metrics:
                col_stats["max_value"] = row[idx]
                idx += 1

            stats["columns"][col_name] = col_stats

        # Compute top_values separately if requested (cannot be efficiently combined with UNION ALL)
        if 'top_values' in metrics:
            for col_name in stats["columns"].keys():
                top_values_query = text(
                    f"""
                    SELECT
                        {col_name} AS value,
                        COUNT(*) AS frequency
                    FROM {qualified_table}
                    GROUP BY {col_name}
                    ORDER BY frequency DESC
                    LIMIT :top_k
                    """
                )

                try:
                    top_rows = db_session.execute(top_values_query, {"top_k": top_k}).fetchall()
                    top_values = [
                        {"value": row[0], "count": row[1]}
                        for row in top_rows
                        if row is not None
                    ]
                    stats["columns"][col_name]["top_values"] = top_values
                except SQLAlchemyError as exc:
                    logger.exception("Failed to fetch top values for %s: %s", col_name, exc)
                    stats["columns"][col_name]["top_values"] = []

        return stats

    def find_identical_column_pairs(
        self,
        schema_name: str,
        table_name: str,
        db_session,
    ) -> List[tuple]:
        """
        Find column pairs that have identical data (including NULL handling).

        Args:
            schema_name: Schema name
            table_name: Table name
            db_session: Database session

        Returns:
            List of tuples representing identical column pairs: [('col1', 'col2'), ...]
        """
        if not db_session:
            raise ValueError("db_session is required to find identical column pairs.")

        try:
            engine = db_session.get_bind()
            inspector = inspect(engine)
            columns_info = inspector.get_columns(table_name=table_name, schema=schema_name)
            columns = [
                (col["name"], str(col["type"]).split("(")[0].strip().upper())
                for col in columns_info
            ]

            def are_types_compatible(t1, t2):
                """Check if two data types are compatible for comparison."""
                numeric_types = {
                    "INTEGER", "BIGINT", "SMALLINT", "NUMERIC", "DECIMAL",
                    "FLOAT", "DOUBLE", "REAL", "NUMBER"
                }
                text_types = {"VARCHAR", "TEXT", "CHAR", "STRING"}
                date_types = {
                    "DATE", "TIMESTAMP", "TIMESTAMPTZ", "TIMESTAMP_NTZ",
                    "TIMESTAMP_LTZ", "TIMESTAMP_TZ", "DATETIME"
                }
                excluded = {"VARIANT", "OBJECT", "ARRAY", "GEOGRAPHY", "GEOMETRY"}

                if t1 in excluded or t2 in excluded:
                    return False
                elif t1 in numeric_types and t2 in numeric_types:
                    return True
                elif t1 in text_types and t2 in text_types:
                    return True
                elif t1 in date_types and t2 in date_types:
                    return True
                return False

            # Find candidate pairs (same or compatible types)
            candidate_pairs = [
                (c1[0], c2[0])
                for i, c1 in enumerate(columns)
                for j, c2 in enumerate(columns)
                if i < j and are_types_compatible(c1[1], c2[1])
            ]

            if not candidate_pairs:
                logger.info("No compatible column pairs found for comparison.")
                return []

            # Detect database dialect
            dialect = engine.dialect.name  # "postgresql" or "snowflake"
            full_table_name = f"{schema_name}.{table_name}"

            # Build query to check if columns are identical
            exists_checks = []
            for col1, col2 in candidate_pairs:
                if dialect == "snowflake":
                    condition = f"EQUAL_NULL({col1}, {col2})"
                else:  # postgres & others
                    condition = f"({col1} = {col2} OR ({col1} IS NULL AND {col2} IS NULL))"

                exists_checks.append(
                    f"""
                    CASE WHEN EXISTS (
                        SELECT 1
                        FROM {full_table_name}
                        WHERE NOT {condition}
                    )
                    THEN 0 ELSE 1 END AS "{col1}__{col2}"
                """
                )

            final_query = f"SELECT {', '.join(exists_checks)};"

            with engine.connect() as conn:
                result = conn.execute(text(final_query)).mappings().first()

            # Extract identical pairs
            identical_pairs = [
                tuple(col.split("__"))
                for col, val in result.items()
                if val == 1
            ]

            logger.info(f"Found {len(identical_pairs)} identical column pairs in {schema_name}.{table_name}")
            return identical_pairs

        except Exception as e:
            logger.exception(f"Error finding identical column pairs: {e}")
            return []

    def format_table_metadata(self, table_metadata: Dict[str, Any]) -> str:
        """
        Convert table metadata dictionaries into structured prompt snippets.
        """
        if not table_metadata:
            return "## Table Metadata\n- No metadata available.\n"

        lines = ["## Table Metadata"]

        row_count = table_metadata.get("table_info", {}).get("row_count") or table_metadata.get("row_count")
        if row_count is not None:
            lines.append(f"- Rows: {row_count}")

        columns_metadata = table_metadata.get("columns") or table_metadata.get("table_columns_info")
        if columns_metadata:
            lines.append("- Columns:")
            for column, metadata in columns_metadata.items():
                column_line = f"  - {column}"
                data_type = metadata.get("data_type")
                if data_type:
                    column_line += f" ({data_type})"
                null_percentage = metadata.get("null_percentage")
                if null_percentage is not None:
                    column_line += f" – Nulls: {null_percentage}%"
                lines.append(column_line)

        return "\n".join(lines) + "\n"


    def get_column_name_datatype(self, data_store: Any, db_session: Any, schema_name: str, table_name: str, filter_val: Optional[str] = None) -> Optional[List[Dict[str, str]]]:
        """
        Fetches column names and their data types for a given table.

        Args:
            data_store (Any): The data store object/type.
            db_session (Any): The database session object.
            schema_name (str): The name of the schema.
            table_name (str): The name of the table.
            filter_val (Optional[str]): Optional filter value for the data types.

        Returns:
            Optional[List[Dict[str, str]]]: A list of dictionaries mapping column names to their data types,
                                     or None if an error occurs.
        """
        logger.debug(f"Fetching column name and datatype for table '{table_name}' in schema '{schema_name}'.")
        try:
            if filter_val is not None:
                return fetch_column_name_datatype(
                    data_store,
                    db_session,
                    schema_name,
                    table_name,
                    filter_val=filter_val
                )
            else:
                return fetch_column_name_datatype(
                    data_store,
                    db_session,
                    schema_name,
                    table_name
                )
        except Exception as e:
            logger.exception(f"An error occurred while fetching column name and datatype: {e}")
            return None

    def get_session_data(self, key: Optional[str] = None) -> Any:
        """
        Retrieves data specific to the current session.
        If key is provided, returns the value for that key; otherwise, returns all session data.
        """
        logger.debug(f"Fetching session data for key: {key if key else 'all'}")
        if key:
            return self.context_data.get(f"session_{key}")
        return {k.replace("session_", ""): v for k, v in self.context_data.items() if k.startswith("session_")}

    def format_use_case(self, use_case_details: Dict[str, Any]) -> str:
        """
        Convert use case dictionaries into a compact prompt segment.
        """
        if not use_case_details:
            return "## Use Case\n- No use case details available.\n"

        name = use_case_details.get("name") or "Unknown"
        description = use_case_details.get("description") or "No description provided."

        lines = [
            "## Use Case",
            f"- Name: {name}",
            f"- Description: {description}",
        ]

        modelling_approach = use_case_details.get("modelling_approach")
        if modelling_approach:
            lines.append(f"- Modelling Approach: {modelling_approach}")

        return "\n".join(lines) + "\n"

    def get_table_row_count(self, schema_name: str, table_name: str, db_session: Any) -> int:
        """Gets the total row count of a table."""
        logger.debug(f"Fetching row count for {schema_name}.{table_name}")
        try:
            query = text(f"SELECT COUNT(*) FROM {schema_name}.{table_name}")
            result = db_session.execute(query).scalar()
            return result if result is not None else 0
        except SQLAlchemyError as e:
            logger.exception(f"Error fetching row count for {schema_name}.{table_name}: {e}")
            return 0

    def get_distinct_column_counts(self, schema_name: str, table_name: str, columns: List[Dict[str, str]], db_session: Any, limit: int = 10) -> Dict[str, int]:
        """Gets distinct counts for categorical columns."""
        logger.debug(f"Fetching distinct column counts for {schema_name}.{table_name}")
        distinct_counts = {}
        if not columns:
            return distinct_counts

        for column in list(columns)[:limit]:
            column_name = column['column_name']
            data_type = column['data_type']
            if any(text_type in data_type.upper() for text_type in ["VARCHAR", "TEXT", "STRING", "CHAR"]):
                try:
                    query = text(f"SELECT COUNT(DISTINCT {column_name}) FROM {schema_name}.{table_name}")
                    result = db_session.execute(query).scalar()
                    distinct_counts[column_name] = result if result is not None else 0
                except SQLAlchemyError as e:
                    logger.exception(f"Error fetching distinct count for column {column_name}: {e}")
        return distinct_counts

    def get_table_type(self, schema_name: str, table_name: str, db_session: Any) -> str:
        """Checks if the object is a table or a view."""
        logger.debug(f"Fetching table type for {schema_name}.{table_name}")
        try:
            query = text("""
                SELECT table_type
                FROM information_schema.tables
                WHERE table_schema = :schema_name AND table_name = :table_name
            """)
            result = db_session.execute(query, {"schema_name": schema_name.upper(), "table_name": table_name.upper()}).scalar()
            return result if result else "TABLE"
        except SQLAlchemyError as e:
            logger.exception(f"Error fetching table type for {schema_name}.{table_name}: {e}")
            return "TABLE" # Default fallback

    def get_operation_details(self, schema_name: str, table_name: str, db_session: Any, is_final_dataset: bool = False) -> List[Dict]:
        """Fetches operation details for a table."""
        logger.debug(f"Fetching operation details for {table_name}")
        try:

            query = text(f"""
                SELECT operation_type, sequence, main_query
                FROM {schema_name}.operation_details
                WHERE tablename = :table_name
                ORDER BY sequence
            """)
            
            operations = db_session.execute(query, {"table_name": table_name}).mappings().all()
            return [dict(op) for op in operations]
        except SQLAlchemyError as e:
            logger.exception(f"Could not fetch operation details for table {table_name}: {e}")
            return []

    def format_operation_details(self, operations: List[Dict]) -> str:
        """Formats operation details into a readable string."""
        if not operations:
            return "No operation details available."

        operations_info_list = []
        for op in operations:
            operations_info_list.append(
                f"- Operation: {op.get('operation_type')} (Sequence: {op.get('sequence')})\\n"
                f"  Query: {op.get('main_query')}"
            )
        return "\\n".join(operations_info_list)

    def get_group_by_fields(
        self,
        schema_name: str,
        table_names: List[str],
        db_session: Any,
    ) -> Dict[str, List[str]]:
        """
        Fetch group_by fields for given table names from operation_details.

        Args:
            schema_name: The schema name (typically {project_name}_operations)
            table_names: List of table names to fetch group_by fields for
            db_session: Database session

        Returns:
            Dictionary mapping table_name -> list of group_by column names
        """
        if not db_session:
            raise ValueError("db_session is required to fetch group_by fields.")

        if not table_names:
            logger.warning("No table names provided to fetch group_by fields.")
            return {}

        logger.debug(f"Fetching group_by fields for tables: {table_names} in schema: {schema_name}")

        try:
            # Create placeholders for the IN clause
            placeholders = ", ".join(f":table_{idx}" for idx, _ in enumerate(table_names))
            params = {f"table_{idx}": name for idx, name in enumerate(table_names)}

            query = text(f"""
                SELECT tablename, fields
                FROM {schema_name}.operation_details
                WHERE tablename IN ({placeholders})
                    AND operation_type = 'group_by'
            """)

            results = db_session.execute(query, params).mappings().all()

            group_by_fields = {}
            for row in results:
                tablename = row.get("tablename")
                fields_json = row.get("fields")

                if tablename and fields_json:
                    try:
                        fields = json.loads(fields_json) if isinstance(fields_json, str) else fields_json
                        columns = fields.get("columns", [])
                        group_by_fields[tablename] = columns
                    except json.JSONDecodeError as e:
                        logger.exception(f"Error decoding fields JSON for table {tablename}: {e}")
                        continue

            return group_by_fields

        except SQLAlchemyError as e:
            logger.exception(f"Error fetching group_by fields: {e}")
            return {}
        
    def get_final_dataset_mapping(
        self,
        project_name: str,
        db_session,
        exclude_columns: Optional[List[str]] = None,
    ) -> Dict[str, str]:
        """
        Fetch column mappings from FINAL_DATASET_MAPPING table.

        Args:
            project_name: The project name
            db_session: Database session
            exclude_columns: Optional list of column names to exclude from the mapping

        Returns:
            Dictionary mapping sfn_column_name to client_column_name
        """
        if not db_session:
            raise ValueError("db_session is required to fetch final dataset mapping.")

        logger.debug(f"Fetching final dataset mapping for project '{project_name}'.")

        try:
            # Default exclude list
            if exclude_columns is None:
                exclude_columns = ['primary_category', 'categories_present']

            # Build exclusion clause
            if exclude_columns:
                exclusion_placeholders = ", ".join(f":excl_{idx}" for idx, _ in enumerate(exclude_columns))
                exclusion_clause = f"WHERE sfn_column_name NOT IN ({exclusion_placeholders})"
                params = {f"excl_{idx}": col for idx, col in enumerate(exclude_columns)}
            else:
                exclusion_clause = ""
                params = {}

            query = text(f"""
                SELECT
                    sfn_column_name,
                    client_column_name
                FROM
                    {project_name}.FINAL_DATASET_MAPPING
                {exclusion_clause}
            """)

            mappings_rows = db_session.execute(query, params).mappings().all()

            # Convert to dictionary
            mappings = {
                mapping["sfn_column_name"]: mapping["client_column_name"]
                for mapping in mappings_rows
            }

            logger.debug(f"Retrieved {len(mappings)} column mappings for project '{project_name}'.")
            return mappings

        except SQLAlchemyError as e:
            logger.exception(f"Error fetching final dataset mapping for project {project_name}: {e}")
            raise Exception(f"Error fetching final dataset mapping: {str(e)}") from e

    def _get_feature_dtype_dict_from_columns(self, column_data_types):
        """
        Create feature data type dictionary from column data types (SQL types).

        Args:
            column_data_types: List of dicts with 'column_name' and 'data_type'

        Returns:
            Dictionary mapping column names to feature data types (TEXT, NUMERICAL, DATETIME, BOOLEAN, OTHER)
        """
        feature_dtype_dict = {}

        # Define type mappings
        NUMERICAL_TYPES = {
            "number", "decimal", "numeric", "float", "double", "real",
            "int", "integer", "bigint", "smallint", "tinyint"
        }
        TEXT_TYPES = {
            "varchar", "char", "text", "string", "clob", "nvarchar", "nchar"
        }
        DATETIME_TYPES = {
            "date", "datetime", "timestamp", "time", "timestamp_ntz", "timestamp_ltz", "timestamp_tz"
        }
        BOOLEAN_TYPES = {"boolean", "bool"}

        for col in column_data_types:
            column_name = col["column_name"]
            data_type = col["data_type"]

            # Extract base type (remove precision/scale like VARCHAR(255) -> VARCHAR)
            base_type = data_type.split("(")[0].strip().lower()

            if base_type in NUMERICAL_TYPES:
                feature_dtype_dict[column_name] = "NUMERICAL"
            elif base_type in TEXT_TYPES:
                feature_dtype_dict[column_name] = "TEXT"
            elif base_type in DATETIME_TYPES:
                feature_dtype_dict[column_name] = "DATETIME"
            elif base_type in BOOLEAN_TYPES:
                feature_dtype_dict[column_name] = "BOOLEAN"
            else:
                feature_dtype_dict[column_name] = "OTHER"

        return feature_dtype_dict

    def get_pool_tables_count(self, schema_name: str, db_session: Any) -> int:
        """
        Get the count of tables in the lineage pool.

        Args:
            schema_name: The schema name (typically {project_name}_operations)
            db_session: Database session

        Returns:
            Count of tables in the lineage
        """
        logger.debug(f"Fetching pool tables count for schema '{schema_name}'")
        try:
            query = text(f"SELECT COUNT(*) FROM {schema_name}.LINEAGE")
            result = db_session.execute(query).fetchone()
            return result[0] if result else 0
        except SQLAlchemyError as e:
            logger.exception(f"Error fetching pool tables count: {e}")
            return 0

    def get_entity_last_state(
        self,
        project_name: str,
        schema_name: str,
        db_session: Any,
    ) -> List[Dict[str, Any]]:
        """
        Get the last state of entities from golden lineage.

        Args:
            project_name: The project name
            schema_name: The operations schema name (typically {project_name}_operations)
            db_session: Database session

        Returns:
            List of dictionaries containing entity state information
        """
        logger.debug(f"Fetching entity last state for project '{project_name}'")
        try:
            query = text(f"""
            WITH a AS (
                SELECT CATEGORY_NAME AS ENTITY_NAME,
                    CASE
                        WHEN COUNT(CLIENT_COLUMN_NAME) >= 1 THEN 'mapped'
                        ELSE 'Unmapped'
                    END AS LAST_STATE,
                    CASE
                        WHEN max(MAPPED_DATE) IS NOT NULL THEN max(MAPPED_DATE)
                        ELSE NULL
                    END AS LAST_UPDATE_AT
                FROM {project_name}.CATEGORY_SCHEMA_MAPPING
                GROUP BY CATEGORY_NAME
            ),
            b AS (
                SELECT REGEXP_SUBSTR(CATEGORY, '"(.*?)"', 1, 1, 'e', 1) AS ENTITY_NAME,
                    OPERATION_STATUS,
                    TABLENAME AS TABLENAME,
                    IS_FINAL_TABLE as IS_FINAL_TABLE,
                    LAST_STATE,
                    UPDATED_AT AS last_update_at
                FROM {schema_name}.LINEAGE
                WHERE CATEGORY IS NOT NULL
            )
            SELECT a.ENTITY_NAME,
                b.TABLENAME,
                b.IS_FINAL_TABLE,
                b.OPERATION_STATUS,
                COALESCE(b.LAST_STATE, a.LAST_STATE) AS LAST_STATE,
                COALESCE(b.last_update_at, a.last_update_at) AS last_update_at
            FROM a
                LEFT JOIN b ON a.ENTITY_NAME = b.ENTITY_NAME
            """)

            rows = db_session.execute(query).fetchall()
            return [dict(row._mapping) for row in rows]
        except SQLAlchemyError as e:
            logger.exception(f"Error fetching entity last state: {e}")
            return []

    def get_entity_table_mapping_all(
        self,
        schema_name: str,
        db_session: Any,
    ) -> List[Dict[str, Any]]:
        """
        Get entity to table mappings for all entities.

        Args:
            schema_name: The operations schema name (typically {project_name}_operations)
            db_session: Database session

        Returns:
            List of dictionaries containing entity-table mapping information
        """
        logger.debug(f"Fetching entity table mappings for schema '{schema_name}'")
        try:
            query = text(f"""
            SELECT ENTITY_NAME,
                TABLE_NAME,
                UPDATED_AT
            FROM  {schema_name}.ENTITY_TABLE_MAPPING
            WHERE TABLE_NAME IS NOT NULL
                OR TABLE_NAME NOT LIKE '[]'
            """)

            rows = db_session.execute(query).fetchall()
            return [dict(row._mapping) for row in rows]
        except SQLAlchemyError as e:
            logger.exception(f"Error fetching entity table mappings: {e}")
            return []

    def get_domain_usecase_info_by_customer(
        self,
        customer_id: Union[int, str],
    ) -> List[Dict[str, Any]]:
        """
        Get domain and usecase information for a customer.

        Args:
            customer_id: The customer ID

        Returns:
            List of dictionaries containing domain and usecase information
        """
        logger.debug(f"Fetching domain usecase info for customer_id '{customer_id}'")
        sanitized_customer_id = self._escape_literal(customer_id)

        query = f"""
        SELECT name as domain_name,
            use_case_pack
        FROM public.domains
        where id in (
                Select domain_id
                FROM public.customer_domain
                where customer_id = {sanitized_customer_id}
            )
            and status = 'Completed'
        """

        domain_usecase_info = fetch_data_central_db(query, fetch="all", mappings=True)
        parsed_output = []

        for row in domain_usecase_info:
            domain_name = row["domain_name"]

            use_case_dict = (
                row.get("use_case_pack", {}).get("use_case", {})
                if isinstance(row.get("use_case_pack", {}), dict)
                else {}
            )

            if not isinstance(use_case_dict, dict):
                continue

            usecase_list = []

            for use_case_name, use_case_data in use_case_dict.items():
                if not isinstance(use_case_data, dict):
                    continue

                mappings = use_case_data.get("mappings", {})

                if not isinstance(mappings, dict):
                    mappings = {}

                primary_category = mappings.get("primary_category", None)
                selected_categories = mappings.get("selected_categories", [])

                if not isinstance(selected_categories, list):
                    selected_categories = (
                        [selected_categories] if selected_categories is not None else []
                    )

                usecase_list.append(
                    {
                        "usecase_name": use_case_name,
                        "primary_category": primary_category,
                        "selected_categories": selected_categories,
                    }
                )

            parsed_output.append({"domain_name": domain_name, "usecases": usecase_list})

        return parsed_output

    def get_background_process_status(
        self,
        schema_name: str,
        db_session: Any,
    ) -> Dict[str, Any]:
        """
        Get the background process status for both pre-mapping and post-mapping processes.

        Args:
            schema_name: The operations schema name (typically {project_name}_operations)
            db_session: Database session

        Returns:
            Dictionary containing pre_mapping and post_mapping process status information
        """
        logger.debug(f"Fetching background process status for schema '{schema_name}'")

        # Get post-mapping background processes (from GOLDEN_DATASET_OPERATIONS.LINEAGE)
        query = text("""
        SELECT REGEXP_SUBSTR(CATEGORY, '"(.*?)"', 1, 1, 'e', 1) AS ENTITY_NAME,
            TABLENAME AS TABLENAME,
            OPERATION_STATUS,
            ERROR_MSG,
            LAST_STATE,
            UPDATED_AT
        FROM GOLDEN_DATASET_OPERATIONS.LINEAGE
        WHERE OPERATION_STATUS NOT IN ('Completed')
        """)

        try:
            rows = db_session.execute(query).fetchall()
            result = [dict(row._mapping) for row in rows]
        except SQLAlchemyError as e:
            logger.exception(f"Error fetching post-mapping background processes: {e}")
            result = []

        state_to_action = {
            "aggregate": "Aggregation",
            "clean": "Cleaning",
            "join": "Joining",
        }

        post_mapping_background_processes_running = set()
        post_mapping_background_processes_failed = set()

        for row in result:
            from datetime import datetime
            operation_status = row["operation_status"]

            if operation_status.lower() == "running":
                action = state_to_action.get(row.get("last_state"), row.get("last_state"))

                # Build message
                if action:
                    message_parts = [f"{action} is in progress"]
                else:
                    message_parts = ["Operations are running in background"]

                if row.get("tablename"):
                    message_parts.append(f"on table '{row['tablename']}'")
                if row.get("entity_name"):
                    message_parts.append(f"for entity '{row['entity_name']}'")

                timestamp = row.get("updated_at", "")

                if isinstance(timestamp, datetime):
                    time_str = timestamp.strftime("%Y-%m-%d %H:%M:%S")
                    message = " ".join(message_parts) + f" (Last update at: {time_str})"
                else:
                    message = " ".join(message_parts)

                post_mapping_background_processes_running.add(message)

            if operation_status.lower() == "failed":
                action = state_to_action.get(row.get("last_state"), row.get("last_state"))

                # Build message
                if action:
                    message_parts = [f"{action} operation failed"]
                else:
                    message_parts = ["Operation failed in background"]

                if row.get("tablename"):
                    message_parts.append(f"on table '{row['tablename']}'")
                if row.get("entity_name"):
                    message_parts.append(f"for entity '{row['entity_name']}'")
                if row.get("error_msg"):
                    message_parts.append(f"\nerror_msg -\n'{row['error_msg']}'")

                timestamp = row.get("updated_at", "")

                if isinstance(timestamp, datetime):
                    time_str = timestamp.strftime("%Y-%m-%d %H:%M:%S")
                    message = " ".join(message_parts) + f" (Last update at: {time_str})"
                else:
                    message = " ".join(message_parts)

                post_mapping_background_processes_failed.add(message)

        # Handle no processes case for post-mapping
        if not post_mapping_background_processes_running:
            post_mapping_background_processes_status = False
            post_mapping_background_processes_details = {
                "No background processes are in progress post mapping"
            }
        else:
            post_mapping_background_processes_status = True
            post_mapping_background_processes_details = post_mapping_background_processes_running

        if not post_mapping_background_processes_failed:
            post_mapping_background_processes_failed_status = False
            post_mapping_background_processes_failed_details = {
                "No background processes are in failed state post mapping"
            }
        else:
            post_mapping_background_processes_failed_status = True
            post_mapping_background_processes_failed_details = (
                post_mapping_background_processes_failed
            )

        post_map_background_process = {
            "Running": {
                "status": post_mapping_background_processes_status,
                "details": post_mapping_background_processes_details,
            },
            "Failed": {
                "status": post_mapping_background_processes_failed_status,
                "details": post_mapping_background_processes_failed_details,
            },
        }

        # Get pre-mapping background processes (from ENTITY_STATUS)
        query = text(f"""
        WITH running_processes AS (
            SELECT process_status,
                process_name,
                ARRAY_AGG(entity_name) AS entities,
                NULL AS error_log,
                MAX(updated_at) AS updated_at
            FROM {schema_name}.ENTITY_STATUS
            WHERE process_status = 'running'
            GROUP BY process_status,
                process_name
        ),
        failed_processes AS (
            SELECT process_status,
                process_name,
                ARRAY_CONSTRUCT(entity_name) AS entities,
                error_log,
                updated_at
            FROM {schema_name}.ENTITY_STATUS
            WHERE process_status = 'failed'
        )
        SELECT *
        FROM running_processes
        UNION ALL
        SELECT *
        FROM failed_processes
        ORDER BY process_status,
            process_name
        """)

        try:
            background_process_result = db_session.execute(query).fetchall()
            background_process_result = [dict(row._mapping) for row in background_process_result]
        except SQLAlchemyError as e:
            logger.exception(f"Error fetching pre-mapping background processes: {e}")
            background_process_result = []

        result = {"Running_processes": {}, "Failed_processes": {}}

        for row in background_process_result:
            status = row["process_status"]
            process_name = row["process_name"]

            # Parse entities JSON string back into list
            try:
                entities = json.loads(row["entities"])
            except Exception:
                entities = [row["entities"]] if row["entities"] else []

            if status == "running":
                # For running process, aggregate under process name
                result["Running_processes"][process_name] = {
                    "entities": entities,
                    "last_updated_at": row["updated_at"],
                }
            elif status == "failed":
                # For failed process, append per-entity record
                if process_name not in result["Failed_processes"]:
                    result["Failed_processes"][process_name] = []

                for entity in entities:
                    result["Failed_processes"][process_name].append(
                        {
                            "entity": entity,
                            "error_log": row["error_log"],
                            "updated_at": row["updated_at"],
                        }
                    )

        running_statements = []
        failed_statements = []

        for process, details in result.get("Running_processes", {}).items():
            # entities can be stored as string representation of list, so we parse safely
            import ast
            entities_list = []

            for entity in details.get("entities", []):
                try:
                    parsed = ast.literal_eval(entity)  # convert string list to python list

                    if isinstance(parsed, list):
                        entities_list.extend(parsed)
                    else:
                        entities_list.append(str(parsed))
                except Exception:
                    entities_list.append(entity)

            entities_str = ", ".join(entities_list) if entities_list else "Entities"
            last_updated = details.get("last_updated_at", "")

            running_statements.append(
                f"{process} is running in background for entities [{entities_str}] "
                f"(last update at: {last_updated})"
            )

        # Failed processes
        for process, failures in result.get("Failed_processes", {}).items():
            import ast
            for failure in failures:
                try:
                    entity_list = ast.literal_eval(failure.get("entity", "[]"))

                    if isinstance(entity_list, list):
                        entities_str = ", ".join(entity_list)
                    else:
                        entities_str = str(entity_list)
                except Exception:
                    entities_str = failure.get("entity", "Entity")

                updated_at = failure.get("updated_at", "")
                error_log = failure.get("error_log", "")

                failed_statements.append(
                    f"{process} got failed for entity [{entities_str}] at {updated_at} with error "
                    f"-\n{error_log}"
                )

        if not running_statements:
            running_statements_status = False
            running_statements = {"No background processes are in progress post mapping"}
        else:
            running_statements_status = True

        if not failed_statements:
            failed_statements_status = False
            failed_statements = {"No background processes are in progress post mapping"}
        else:
            failed_statements_status = True

        pre_mapping_background_processes = {
            "Running": {
                "status": running_statements_status,
                "details": running_statements,
            },
            "Failed": {
                "status": failed_statements_status,
                "details": failed_statements,
            },
        }

        background_process_result = {
            "pre_mapping": pre_mapping_background_processes,
            "post_mapping": post_map_background_process,
        }

        return background_process_result
