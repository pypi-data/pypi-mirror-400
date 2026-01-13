from __future__ import annotations

import re
from dataclasses import dataclass
from typing import List, Dict, Tuple, Any, Set

from clickzetta_ingestion.bulkload.bulkload_conf import BulkLoadConf
from clickzetta_ingestion.bulkload.bulkload_context import FieldSchema


class IGSTableType:
    NORMAL = "NORMAL"
    ACID = "ACID"


@dataclass
class TableMetadata:
    """
    Raw table structure from database (cacheable, immutable).
    Contains complete schema without any filtering.
    """
    table_type: str
    schema_name: str
    table_name: str

    # Complete column definitions (unfiltered)
    complete_field_schemas: List[FieldSchema]
    complete_name_to_id_map: Dict[str, int]

    # Original indices (based on complete schema)
    primary_key_indices: List[int]
    partition_key_indices: List[int]

    generated_columns: List[FieldSchema]
    identity_columns: Set[str]

    def __post_init__(self):
        """Make the structure immutable by converting to tuples"""
        # Convert lists to tuples for immutability
        self.complete_field_schemas = tuple(self.complete_field_schemas)
        self.primary_key_indices = tuple(self.primary_key_indices)
        self.partition_key_indices = tuple(self.partition_key_indices)
        self.generated_columns = tuple(self.generated_columns)
        # Set is already immutable enough for our purposes


@dataclass
class BulkLoadTable:
    """Bulkload table information."""
    table_type: str
    schema_name: str
    table_name: str
    field_schemas: List[FieldSchema]
    primary_key_indices: List[int]
    partition_key_indices: List[int]
    partition_spec_values: List[object]
    partial_update_column_indices: List[int]
    generated_columns: List[FieldSchema]
    identity_columns: set = None

    def __post_init__(self):
        self.column_names = [field.name for field in self.field_schemas]
        self.column_names_map = {field.name: i for i, field in enumerate(self.field_schemas)}
        self.column_types_map = {field.name: field.type for field in self.field_schemas}
        self.primary_key_names = [self.field_schemas[i].name for i in self.primary_key_indices]
        self.partition_key_names = [self.field_schemas[i].name for i in self.partition_key_indices]
        self.partial_update_column_names = [self.field_schemas[i].name for i in self.partial_update_column_indices]
        self.special_column_names = {field.name: BulkLoadTable.make_compatible_name(field.name) for field in
                                     self.field_schemas}
        if self.identity_columns is None:
            self.identity_columns = set()

    def get_table_type(self) -> str:
        return self.table_type

    def get_igs_table_type(self) -> str:
        return self.table_type

    def get_schema_name(self) -> str:
        return self.schema_name

    def get_table_name(self) -> str:
        return self.table_name

    def get_table_schema(self) -> List[FieldSchema]:
        return self.field_schemas

    def get_primary_key_indices(self) -> List[int]:
        return self.primary_key_indices

    def get_partition_key_indices(self) -> List[int]:
        return self.partition_key_indices

    def get_partition_spec_values(self) -> List[object]:
        return self.partition_spec_values

    def get_partition_static_value(self) -> List[object]:
        return self.partition_spec_values

    def get_partial_update_column_indices(self) -> List[int]:
        return self.partial_update_column_indices

    def get_generated_columns(self) -> List[FieldSchema]:
        return self.generated_columns

    def get_column_names(self) -> List[str]:
        return self.column_names

    def get_column_names_map(self) -> Dict[str, int]:
        return self.column_names_map

    def get_column_types_map(self) -> Dict[str, str]:
        return self.column_types_map

    def get_primary_key_names(self) -> List[str]:
        return self.primary_key_names

    def get_partition_key_names(self) -> List[str]:
        return self.partition_key_names

    def get_partial_update_columns(self) -> List[str]:
        return self.partial_update_column_names

    def get_special_column_names(self) -> Dict[str, str]:
        return self.special_column_names

    def get_identity_columns(self) -> set:
        return self.identity_columns

    @staticmethod
    def make_compatible_name(name: str) -> str:
        """Convert any string to a valid Avro name with optimal performance."""
        return name
        # if not name or (not name[0].isalpha() and name[0] != '_'):
        #     needs_sanitization = True
        # else:
        #     needs_sanitization = False
        #     for char in name[1:]:
        #         if not (char.isalnum() or char == '_'):
        #             needs_sanitization = True
        #             break
        #
        # if not needs_sanitization:
        #     return name
        #
        # def sanitize_char(c: str) -> str:
        #     if c.isalpha() or c == '_':
        #         return c
        #     return f"_{c}" if c.isdigit() else f"_x{ord(c):X}"
        #
        # result = [sanitize_char(name[0]) if not name[0].isalpha() and name[0] != '_' else name[0]]
        #
        # for char in name[1:]:
        #     if char.isalnum() or char == '_':
        #         result.append(char)
        #     else:
        #         result.append(sanitize_char(char))
        #
        # return ''.join(result)


class TableParser:
    """Parser for table schema information."""

    def __init__(self):
        self._generated_column_pattern = re.compile(r'^\s*`?(\w+)`?.+?GENERATED\s+ALWAYS\s+AS', re.IGNORECASE)
        self._identity_column_pattern = re.compile(r'^\s*`?(\w+)`?.+?IDENTITY', re.IGNORECASE)

    def parse_table_metadata(self, describe_extended_result: List[Tuple[Any, ...]], show_create_table_result: str) -> \
            Tuple[str, List[Any], Dict[Any, Any], List[Any], List[Any], List[Any], Set[Any]]:
        """
        Parses the output of Hive's DESCRIBE EXTENDED and SHOW CREATE TABLE commands to extract table metadata.

        Args:
            describe_extended_result: A list of rows from the DESCRIBE EXTENDED query result.
                                      Each row is expected to be a sequence (e.g., tuple, list) with at least two elements.
            show_create_table_result: The full string output from the SHOW CREATE TABLE command.

        Returns:
            A tuple containing the parsed metadata:
            - table_type: The type of the table (e.g., IGSTableType.NORMAL, IGSTableType.ACID).
            - field_schemas: A list of FieldSchema objects representing the table columns.
            - name_to_id_map: A dictionary mapping lowercase column names to their index in field_schemas.
            - primary_key: A list of indices representing the primary key columns in field_schemas.
            - partition_key: A list of indices representing the partition key columns in field_schemas.
            - partial_update_columns: A placeholder list
            - generated_columns: A list of FieldSchema objects that are generated columns.
            - identity_columns: A set of column names that are IDENTITY columns.
        """

        # Initialize the results as specified
        table_type = IGSTableType.NORMAL
        field_schemas = []
        name_to_id_map = {}
        primary_key_indices = []
        partition_key_indices = []
        generated_columns = []
        identity_columns = set()

        # Lists to hold the parsed keys and values from DESCRIBE EXTENDED
        key_list = []
        value_list = []

        # Extract the first two columns from the DESCRIBE EXTENDED result
        for row in describe_extended_result:
            if len(row) >= 2:
                key_list.append(str(row[0]) if row[0] is not None else None)
                value_list.append(str(row[1]) if row[1] is not None else None)

        # Parser state
        name_list = []
        data_type_list = []
        find_all_column_names = True
        pos = 0

        while pos < len(key_list):
            key = key_list[pos]
            value = value_list[pos]

            # Section 1: Parse regular column definitions
            # Stop when we hit the partition information or an empty/null key
            if find_all_column_names and (
                    key is None or key == '' or (key and key.strip().lower() == '# partition information')):
                # Convert parsed names and types into FieldSchema objects
                for name, data_type_with_nullable in zip(name_list, data_type_list):
                    if name and data_type_with_nullable:  # Ensure they are not None or empty
                        # Parse nullability from type string
                        data_type_str = data_type_with_nullable.strip()
                        
                        # Check for NOT NULL keyword (case insensitive)
                        not_null_match = re.search(r'\s+(NOT\s+)?NULL\s*$', data_type_str, re.IGNORECASE)
                        if not_null_match:
                            # If we found NULL/NOT NULL keywords
                            nullable = not ('NOT' in not_null_match.group(0).upper())
                            # Remove the nullability keywords from type
                            clean_type = re.sub(r'\s+(NOT\s+)?NULL\s*$', '', data_type_str, flags=re.IGNORECASE).strip()
                        else:
                            # Default to nullable if no explicit nullability specified
                            nullable = True
                            clean_type = data_type_str
                        
                        # Create FieldSchema object
                        field_schema = FieldSchema(
                            name=name.strip(),
                            field_type=clean_type,
                            nullable=nullable
                        )
                        field_schemas.append(field_schema)

                # Create the name-to-id map
                for index, field_schema in enumerate(field_schemas):
                    name_to_id_map[field_schema.name.lower()] = index

                find_all_column_names = False

            # If we are still in the column definition section, collect the name and type
            if find_all_column_names:
                if key and value:
                    name_list.append(key)
                    data_type_list.append(value.strip())  # Keep original type with nullability info
            else:
                # Section 2: Parse partition keys
                # Look for the partition information section and collect partition column names
                if key and key.strip().lower() == '# partition information':
                    pos += 1
                    while pos < len(key_list):
                        partition_column_name = key_list[pos]
                        if partition_column_name and partition_column_name.strip() != '':
                            partition_column_name = partition_column_name.strip()
                            if partition_column_name.lower() in name_to_id_map:
                                partition_key_indices.append(name_to_id_map[partition_column_name.lower()])
                            pos += 1
                        else:
                            break
                    continue  # Skip the pos increment at the end of the loop

                # Section 3: Parse primary key
                # Look for a property key 'primary_key' and extract column names from its value
                elif key and key.strip().lower() == 'primary_key':
                    # Use regex to find content within parentheses
                    pattern = re.compile(r"\(([^)]+)\)")
                    matcher = pattern.search(value)
                    if matcher:
                        group = matcher.group(1)
                        # Split the string on comma, accounting for potential spaces
                        parts = [part.strip() for part in group.split(',')]
                        for part in parts:
                            part_lower = part.lower()
                            if part_lower in name_to_id_map:
                                primary_key_indices.append(name_to_id_map[part_lower])
                        table_type = IGSTableType.ACID

            pos += 1  # Move to the next row

        # Section 4: Identify generated columns and identity columns using SHOW CREATE TABLE
        # Split the DDL into lines and check each field against a regex pattern
        col_str_lines = [line.strip() for line in show_create_table_result.split('\n')]
        generated_column_names = set()

        # First pass: identify identity columns and generated columns from DDL (avoid nested loops)
        identity_column_names_from_ddl = set()
        generated_column_names_from_ddl = set()

        for line in col_str_lines:
            # Check for IDENTITY columns
            identity_match = self._identity_column_pattern.match(line)
            if identity_match:
                identity_column_names_from_ddl.add(identity_match.group(1))
                continue

            # Check for generated columns (separate check, not elif)
            generated_match = self._generated_column_pattern.match(line)
            if generated_match:
                generated_column_names_from_ddl.add(generated_match.group(1))

        # Second pass: update field schemas based on identified columns
        for field_schema in field_schemas:
            # Mark IDENTITY columns as nullable
            if field_schema.name in identity_column_names_from_ddl:
                identity_columns.add(field_schema.name)
                field_schema.nullable = True
                continue

            # Mark generated columns
            if field_schema.name in generated_column_names_from_ddl:
                generated_column_names.add(field_schema.name)
                generated_columns.append(field_schema)

        # Store original field_schemas for index mapping
        original_field_schemas = field_schemas[:]

        # Then, create new lists excluding generated columns
        filtered_field_schemas = []
        new_name_to_id_map = {}

        for field_schema in field_schemas:
            # Exclude generated columns. The identity columns will not include parquet schema and merge sql.
            if field_schema.name not in generated_column_names:
                # Add to filtered list
                new_index = len(filtered_field_schemas)
                filtered_field_schemas.append(field_schema)
                new_name_to_id_map[field_schema.name.lower()] = new_index
        
        # Update primary key and partition key indices to match the new field_schemas indices
        updated_primary_key_indices = []
        for old_index in primary_key_indices:
            # Find the field name from the original field schema list
            if old_index < len(original_field_schemas):
                field_name = original_field_schemas[old_index].name
                if field_name.lower() in new_name_to_id_map:
                    updated_primary_key_indices.append(new_name_to_id_map[field_name.lower()])
        
        updated_partition_key_indices = []
        for old_index in partition_key_indices:
            # Find the field name from the original field schema list
            if old_index < len(original_field_schemas):
                field_name = original_field_schemas[old_index].name
                if field_name.lower() in new_name_to_id_map:
                    updated_partition_key_indices.append(new_name_to_id_map[field_name.lower()])
        
        # Update the field_schemas and name_to_id_map
        name_to_id_map = new_name_to_id_map

        # Return all the collected results
        return (table_type, filtered_field_schemas, name_to_id_map, updated_primary_key_indices, updated_partition_key_indices,
                generated_columns, identity_columns)


class BulkLoadTableFactory:
    """
    Factory to build BulkLoadTable from TableMetadata and BulkLoadConf.
    Encapsulates the filtering and index remapping logic.
    """

    @staticmethod
    def build(raw_structure: TableMetadata, conf: 'BulkLoadConf') -> BulkLoadTable:
        """
        Build BulkLoadTable from raw structure and configuration.

        Args:
            raw_structure: Complete table structure from database
            conf: Bulk load configuration

        Returns:
            BulkLoadTable with filtered schema and remapped indices
        """
        from clickzetta_ingestion.bulkload.bulkload_conf import BulkLoadOperation

        # Copy data from raw_structure
        field_schemas = list(raw_structure.complete_field_schemas)
        name_to_id_map = dict(raw_structure.complete_name_to_id_map)
        primary_key_indices = list(raw_structure.primary_key_indices)
        partition_key_indices = list(raw_structure.partition_key_indices)
        table_type = raw_structure.table_type
        partial_update_columns = []

        # Handle UPSERT operation special logic
        if conf.get_operation() == BulkLoadOperation.UPSERT:
            # Handle record_keys
            record_keys = conf.get_record_keys()
            if record_keys and len(record_keys) > 0:
                primary_key_indices = BulkLoadTableFactory._resolve_record_keys(
                    record_keys, name_to_id_map
                )
                table_type = IGSTableType.ACID

            # Handle partial_update_columns (core: filter field_schemas)
            partial_update_column_names = conf.get_partial_update_columns()
            if partial_update_column_names and len(partial_update_column_names) > 0:
                (field_schemas, name_to_id_map, primary_key_indices,
                 partition_key_indices, partial_update_columns) = \
                    BulkLoadTableFactory._apply_partial_update_filter(
                        field_schemas, name_to_id_map, primary_key_indices,
                        partition_key_indices, partial_update_column_names
                    )

        # Parse partition_spec_values
        partition_spec_values = []
        if conf.get_partition_specs():
            partition_spec_values = BulkLoadTableFactory._parse_partition_specs(
                field_schemas, partition_key_indices, conf.get_partition_specs()
            )

        # Set primary key columns as non-nullable
        for idx in primary_key_indices:
            if 0 <= idx < len(field_schemas):
                field_schemas[idx].nullable = False

        return BulkLoadTable(
            table_type=table_type,
            schema_name=raw_structure.schema_name,
            table_name=raw_structure.table_name,
            field_schemas=field_schemas,
            primary_key_indices=primary_key_indices,
            partition_key_indices=partition_key_indices,
            partition_spec_values=partition_spec_values,
            partial_update_column_indices=partial_update_columns,
            generated_columns=list(raw_structure.generated_columns),
            identity_columns=raw_structure.identity_columns
        )

    @staticmethod
    def _resolve_record_keys(
        record_keys: List[str],
        name_to_id_map: Dict[str, int]
    ) -> List[int]:
        """
        Resolve record keys to indices.

        Args:
            record_keys: List of record key column names
            name_to_id_map: Mapping from column name to index

        Returns:
            List of indices for record keys

        Raises:
            RuntimeError: If a record key does not exist in the schema
        """
        primary_key_indices = []
        for record_key in record_keys:
            record_key_lower = record_key.lower()
            if record_key_lower not in name_to_id_map:
                raise RuntimeError(f"recordKey [{record_key}] not exists in table schema.")
            primary_key_indices.append(name_to_id_map[record_key_lower])
        return primary_key_indices

    @staticmethod
    def _apply_partial_update_filter(
        field_schemas: List[FieldSchema],
        name_to_id_map: Dict[str, int],
        primary_key_indices: List[int],
        partition_key_indices: List[int],
        partial_update_column_names: List[str]
    ) -> Tuple[List[FieldSchema], Dict[str, int], List[int], List[int], List[int]]:
        """
        Filter field_schemas to only include required columns.
        This implements the logic from lines 413-455 in default_bulkload_handler.py.

        Args:
            field_schemas: Complete list of field schemas
            name_to_id_map: Mapping from column name to index
            primary_key_indices: Primary key indices
            partition_key_indices: Partition key indices
            partial_update_column_names: Partial update column names

        Returns:
            Tuple of (filtered_field_schemas, new_name_to_id_map, new_primary_key_indices,
                      new_partition_key_indices, partial_update_indices)

        Raises:
            RuntimeError: If a partial update column does not exist in the schema
        """
        # Validate partial_update_columns exist
        sub_partial_update_columns = []
        for col in partial_update_column_names:
            col_lower = col.lower()
            if col_lower not in name_to_id_map:
                raise RuntimeError(f"partialUpdateColumn [{col}] not exists in table schema.")
            if col_lower not in sub_partial_update_columns:
                sub_partial_update_columns.append(col_lower)

        # Build required columns set
        sub_primary_key = [field_schemas[i].name.lower() for i in primary_key_indices]
        sub_partition_key = [field_schemas[i].name.lower() for i in partition_key_indices]

        required_columns = set()
        required_columns.update(sub_primary_key)
        required_columns.update(sub_partition_key)
        required_columns.update(sub_partial_update_columns)

        # Filter field_schemas
        filtered_field_schemas = [fs for fs in field_schemas
                                  if fs.name.lower() in required_columns]

        # Rebuild mapping and indices
        new_name_to_id_map = {fs.name.lower(): i for i, fs in enumerate(filtered_field_schemas)}
        new_primary_key_indices = [new_name_to_id_map[key] for key in sub_primary_key]
        new_partition_key_indices = [new_name_to_id_map[key] for key in sub_partition_key]
        new_partial_update_indices = [new_name_to_id_map[col] for col in sub_partial_update_columns]

        return (filtered_field_schemas, new_name_to_id_map, new_primary_key_indices,
                new_partition_key_indices, new_partial_update_indices)

    @staticmethod
    def _parse_partition_specs(
        field_schemas: List[FieldSchema],
        partition_key_indices: List[int],
        partition_specs: str
    ) -> List[object]:
        """
        Parse partition specs string into values.

        Args:
            field_schemas: List of field schemas
            partition_key_indices: Indices of partition key columns
            partition_specs: Partition specs string (e.g., "pt=a,dt=20231201")

        Returns:
            List of partition spec values

        Raises:
            RuntimeError: If partition specs cannot be parsed
        """
        try:
            partition_spec_dict = BulkLoadTableFactory._parse_partition_spec_dict(
                field_schemas, partition_specs
            )
            return [partition_spec_dict.get(field_schemas[idx].name.lower())
                    for idx in partition_key_indices]
        except Exception:
            # Return empty list on error
            return []

    @staticmethod
    def _parse_partition_spec_dict(
        field_schemas: List[FieldSchema],
        partition_spec: str
    ) -> Dict[str, object]:
        """
        Parse partition specification string into a dictionary.

        Args:
            field_schemas: List of field schemas
            partition_spec: Partition spec string (e.g., "pt=a,dt=20231201")

        Returns:
            Dictionary mapping partition column names to values

        Raises:
            RuntimeError: If parsing fails
        """
        result = {}

        try:
            if '=' in partition_spec:
                # Remove common SQL keywords and clean up
                cleaned_spec = partition_spec.replace('PARTITION', '').replace('(', '').replace(')', '').strip()

                pairs = []
                current_pair = ""
                in_quotes = False
                quote_char = None

                # Parse while respecting quotes
                for char in cleaned_spec:
                    if char in ['"', "'"] and not in_quotes:
                        in_quotes = True
                        quote_char = char
                        current_pair += char
                    elif char == quote_char and in_quotes:
                        in_quotes = False
                        quote_char = None
                        current_pair += char
                    elif char == ',' and not in_quotes:
                        pairs.append(current_pair.strip())
                        current_pair = ""
                    else:
                        current_pair += char

                if current_pair.strip():
                    pairs.append(current_pair.strip())

                # Process each key=value pair
                for pair in pairs:
                    if '=' in pair:
                        key, value = pair.split('=', 1)
                        key = key.strip()
                        value = value.strip()

                        # Remove quotes from value
                        if (value.startswith('"') and value.endswith('"')) or \
                                (value.startswith("'") and value.endswith("'")):
                            value = value[1:-1]

                        # Find the field schema for this partition column
                        field = None
                        for field_schema in field_schemas:
                            if field_schema.name.lower() == key.lower():
                                field = field_schema
                                break

                        if not field:
                            raise RuntimeError(f"Partition column '{key}' not found in table schema.")

                        # Convert value using type-aware conversion
                        from clickzetta_ingestion.rpc import arrow_utils
                        converted_value = arrow_utils.convert_to_field_type(field.type, value)
                        result[key.lower()] = converted_value

        except Exception as e:
            raise RuntimeError(f"Error parsing partition spec '{partition_spec}': {e}")

        return result
