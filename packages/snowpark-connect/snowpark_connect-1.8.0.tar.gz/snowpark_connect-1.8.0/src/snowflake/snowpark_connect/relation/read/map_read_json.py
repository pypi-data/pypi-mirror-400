#
# Copyright (c) 2012-2025 Snowflake Computing Inc. All rights reserved.
#

import concurrent.futures
import copy
import json
import os
import typing
import uuid
from contextlib import suppress
from datetime import datetime

import pyspark.sql.connect.proto.relations_pb2 as relation_proto

from snowflake import snowpark
from snowflake.snowpark._internal.analyzer.analyzer_utils import unquote_if_quoted
from snowflake.snowpark._internal.utils import is_in_stored_procedure
from snowflake.snowpark.row import Row
from snowflake.snowpark.types import (
    ArrayType,
    DataType,
    DateType,
    MapType,
    NullType,
    StringType,
    StructField,
    StructType,
    TimestampType,
)
from snowflake.snowpark_connect.dataframe_container import DataFrameContainer
from snowflake.snowpark_connect.error.error_codes import ErrorCodes
from snowflake.snowpark_connect.error.error_utils import attach_custom_error_code
from snowflake.snowpark_connect.relation.read.map_read import JsonReaderConfig
from snowflake.snowpark_connect.relation.read.metadata_utils import (
    add_filename_metadata_to_reader,
)
from snowflake.snowpark_connect.relation.read.utils import (
    apply_metadata_exclusion_pattern,
    get_spark_column_names_from_snowpark_columns,
    rename_columns_as_snowflake_standard,
)
from snowflake.snowpark_connect.type_mapping import (
    cast_to_match_snowpark_type,
    map_simple_types,
    merge_different_types,
)
from snowflake.snowpark_connect.type_support import emulate_integral_types
from snowflake.snowpark_connect.utils.snowpark_connect_logging import logger
from snowflake.snowpark_connect.utils.telemetry import (
    SnowparkConnectNotImplementedError,
)


def _append_node_in_trace_stack(trace_stack: str, node: str) -> str:
    return f"{trace_stack}:{node}"


def map_read_json(
    rel: relation_proto.Relation,
    schema: StructType | None,
    session: snowpark.Session,
    paths: list[str],
    options: JsonReaderConfig,
) -> DataFrameContainer:
    """
    Read a JSON file into a Snowpark DataFrame.

    [JSON lines](http://jsonlines.org/) file format is supported.

    We leverage the stage that is already created in the map_read function that
    calls this.
    """

    if rel.read.is_streaming is True:
        # TODO: Structured streaming implementation.
        exception = SnowparkConnectNotImplementedError(
            "Streaming is not supported for JSON files."
        )
        attach_custom_error_code(exception, ErrorCodes.UNSUPPORTED_OPERATION)
        raise exception
    else:
        snowpark_options = options.convert_to_snowpark_args()
        raw_options = rel.read.data_source.options
        snowpark_options["infer_schema"] = True

        rows_to_infer_schema = snowpark_options.pop("rowstoinferschema", 1000)
        dropFieldIfAllNull = snowpark_options.pop("dropfieldifallnull", False)
        batch_size = snowpark_options.pop("batchsize", 1000)

        apply_metadata_exclusion_pattern(snowpark_options)

        reader = add_filename_metadata_to_reader(
            session.read.options(snowpark_options), raw_options
        )

        df = reader.json(paths[0])
        if len(paths) > 1:
            # TODO: figure out if this is what Spark does.
            for p in paths[1:]:
                df = df.union_all(
                    add_filename_metadata_to_reader(
                        session.read.options(snowpark_options), raw_options
                    ).json(p)
                )

        if schema is None:
            schema = copy.deepcopy(df.schema)
            infer_row_counts = 0

            columns_with_valid_contents = set()
            string_nodes_finalized = set[str]()
            for row in df.to_local_iterator():
                infer_row_counts += 1
                if (
                    rows_to_infer_schema != -1
                    and infer_row_counts > rows_to_infer_schema
                ):
                    break
                schema = merge_row_schema(
                    schema,
                    row,
                    columns_with_valid_contents,
                    string_nodes_finalized,
                    dropFieldIfAllNull,
                )

            if dropFieldIfAllNull:
                schema.fields = [
                    sf
                    for sf in schema.fields
                    if unquote_if_quoted(sf.name) in columns_with_valid_contents
                ]

        new_schema, fields_changed = validate_and_update_schema(schema)
        if fields_changed:
            schema = new_schema

        df = construct_dataframe_by_schema(
            schema, df.to_local_iterator(), session, snowpark_options, batch_size
        )

        spark_column_names = get_spark_column_names_from_snowpark_columns(df.columns)

        renamed_df, snowpark_column_names = rename_columns_as_snowflake_standard(
            df, rel.common.plan_id
        )
        return DataFrameContainer.create_with_column_mapping(
            dataframe=renamed_df,
            spark_column_names=spark_column_names,
            snowpark_column_names=snowpark_column_names,
            snowpark_column_types=[
                emulate_integral_types(f.datatype) for f in df.schema.fields
            ],
        )


def should_drop_field(field: StructField) -> bool:
    if isinstance(field.datatype, StructType):
        # "a" : {} => drop the field
        if len(field.datatype.fields) == 0:
            return True
    elif (
        isinstance(field.datatype, ArrayType)
        and field.datatype.element_type is not None
        and isinstance(field.datatype.element_type, StructType)
    ):
        if len(field.datatype.element_type.fields) == 0:
            # "a" : [{}] => drop the field
            return True
    return False


# Validate the schema to ensure it is valid for Snowflake
# Handles these cases:
#   1. Drops StructField([])
#   2. Drops ArrayType(StructType([]))
#   3. ArrayType() -> ArrayType(StringType())
def validate_and_update_schema(schema: StructType | None) -> (StructType | None, bool):
    if not isinstance(schema, StructType):
        return schema, False
    new_fields = []
    fields_changed = False
    for sf in schema.fields:
        if should_drop_field(sf):
            fields_changed = True
            continue
        if isinstance(sf.datatype, StructType):
            # If the schema is a struct, validate the child schema
            if len(sf.datatype.fields) == 0:
                # No fields in the struct, drop the field
                fields_changed = True
                continue
            child_field = StructField(sf.name, sf.datatype, sf.nullable)
            # Recursively validate the child schema
            child_field.datatype, child_field_changes = validate_and_update_schema(
                sf.datatype
            )
            if should_drop_field(child_field):
                fields_changed = True
                continue
            new_fields.append(child_field)
            fields_changed = fields_changed or child_field_changes
        elif isinstance(sf.datatype, ArrayType):
            # If the schema is an array, validate the element schema
            if sf.datatype.element_type is not None and isinstance(
                sf.datatype.element_type, StructType
            ):
                # If the element schema is a struct, validate the element schema
                if len(sf.datatype.element_type.fields) == 0:
                    # No fields in the struct, drop the field
                    fields_changed = True
                    continue
                else:
                    # Recursively validate the element schema
                    element_schema, element_field_changes = validate_and_update_schema(
                        sf.datatype.element_type
                    )
                    if element_field_changes:
                        sf.datatype.element_type = element_schema
                        fields_changed = True
                    if should_drop_field(sf):
                        fields_changed = True
                        continue
            elif sf.datatype.element_type is None:
                fields_changed = True
                sf.datatype.element_type = StringType()
            new_fields.append(sf)
        else:
            new_fields.append(sf)
    if fields_changed:
        schema.fields = new_fields
    return schema, fields_changed


def merge_json_schema(
    content: typing.Any,
    schema: StructType | None,
    trace_stack: str,
    string_nodes_finalized: set[str],
    dropFieldIfAllNull: bool = False,
) -> DataType:
    """
    Merge the JSON content's schema into an existing schema structure.

    This function recursively processes JSON content (dict, list, or primitive values) and merges
    its inferred schema with an existing schema if provided. It handles nested structures like
    objects (StructType) and arrays (ArrayType), and can optionally drop fields that are always null.

    Args:
        content: The JSON content to infer schema from. Can be a dict, list, primitive value, or None.
        schema: The existing schema to merge with, or None if inferring from scratch.
        trace_stack: A string representing the current position in the schema hierarchy,
                          used for tracking/debugging nested structures.
        string_nodes_finalized: A set of strings representing the nodes that have been finalized as strings.
        dropFieldIfAllNull: If True, fields that only contain null values will be excluded
                          from the resulting schema. Defaults to False.

    Returns:
        The merged schema as a DataType. Returns NullType if content is None and no existing
        schema is provided. For dicts, returns StructType; for lists, returns ArrayType;
        for primitives, returns the appropriate primitive type (StringType, IntegerType, etc.).
    """
    if content is None:
        if schema is not None:
            return schema
        return NullType()

    if trace_stack in string_nodes_finalized:
        return StringType()

    if isinstance(content, dict):
        additional_schemas = list[StructField]()

        existed_schema = {}
        if schema is not None:
            if schema.type_name() == "struct":
                for sf in schema.fields:
                    existed_schema[sf.name] = sf.datatype
            else:
                string_nodes_finalized.add(trace_stack)
                return StringType()

        for k, v in content.items():
            col_name = f'"{unquote_if_quoted(k)}"'
            existed_data_type = existed_schema.get(col_name, None)
            next_level_schema = merge_json_schema(
                v,
                existed_data_type,
                _append_node_in_trace_stack(trace_stack, col_name),
                string_nodes_finalized,
                dropFieldIfAllNull,
            )

            if not dropFieldIfAllNull or not isinstance(next_level_schema, NullType):
                # Drop field if it's always null
                if col_name in existed_schema:
                    existed_schema[col_name] = next_level_schema
                else:
                    additional_schemas.append(StructField(col_name, next_level_schema))

        current_schema = StructType()
        if schema is not None and schema.type_name() == "struct":
            # Keep the order of columns in the schema
            for sf in schema.fields:
                col_name = f'"{unquote_if_quoted(sf.name)}"'
                if (
                    not dropFieldIfAllNull
                    or existed_schema.get(col_name, NullType()) != NullType()
                ):
                    current_schema.add(
                        StructField(col_name, existed_schema.get(col_name, NullType()))
                    )

        for additional_schema in additional_schemas:
            current_schema.add(additional_schema)

    elif isinstance(content, list):
        # ArrayType(*) need to have element schema inside, it would be NullType() as placeholder and keep updating while enumerating
        inner_schema = NullType()
        next_level_trace_stack = _append_node_in_trace_stack(trace_stack, "$array")

        if schema is not None:
            if schema.type_name() in ("list", "array"):
                inner_schema = schema.element_type
            else:
                string_nodes_finalized.add(trace_stack)
                return StringType()

        if next_level_trace_stack in string_nodes_finalized:
            inner_schema = StringType()
        else:
            if len(content) > 0:
                for v in content:
                    inner_schema = merge_json_schema(
                        v,
                        inner_schema,
                        next_level_trace_stack,
                        string_nodes_finalized,
                        dropFieldIfAllNull,
                    )
                    if isinstance(inner_schema, StringType):
                        string_nodes_finalized.add(next_level_trace_stack)
                        break
            if isinstance(inner_schema, NullType) and dropFieldIfAllNull:
                return NullType()
        current_schema = ArrayType(inner_schema)
    else:
        current_schema = map_simple_types(type(content).__name__)

    if (
        schema is not None
        and schema != NullType()
        and current_schema is not None
        and current_schema != NullType()
        and schema.type_name() != current_schema.type_name()
    ):
        current_schema = merge_different_types(schema, current_schema)

    if isinstance(current_schema, StructType) or isinstance(current_schema, ArrayType):
        current_schema.structured = True

    if isinstance(current_schema, StringType):
        string_nodes_finalized.add(trace_stack)
    return current_schema


def merge_row_schema(
    schema: StructType | None,
    row: Row,
    columns_with_valid_contents: set[str],
    string_nodes_finalized: set[str],
    dropFieldIfAllNull: bool = False,
) -> StructType | NullType:
    """
    Merge the schema inferred from a single row with the existing schema.

    This function updates the schema by examining each row of data and merging
    type information. It handles nested structures (StructType, MapType, ArrayType)
    and attempts to parse JSON strings to infer deeper schema structures.

    Args:
        schema: The current schema to merge with
        row: A single row of data to examine
        columns_with_valid_contents: Set to track columns that have non-null values
        string_nodes_finalized: Set to track nodes that have been finalized as strings
        dropFieldIfAllNull: If True, fields that are always null will be dropped

    Returns:
        The merged schema as a StructType, or NullType if the row is None and no schema exists
    """

    if row is None:
        if schema is not None:
            return schema
        return NullType()

    new_schema = StructType()

    for sf in schema.fields:
        col_name = unquote_if_quoted(sf.name)
        if col_name in string_nodes_finalized:
            columns_with_valid_contents.add(col_name)
        elif isinstance(sf.datatype, (StructType, MapType, StringType)):
            next_level_content = row[col_name]
            next_level_trace_stack = _append_node_in_trace_stack(col_name, col_name)
            if next_level_content is not None:
                with suppress(json.JSONDecodeError):
                    if isinstance(next_level_content, datetime):
                        next_level_content = str(next_level_content)
                    next_level_content = json.loads(next_level_content)
                if isinstance(next_level_content, dict):
                    sf.datatype = merge_json_schema(
                        next_level_content,
                        None
                        if not isinstance(sf.datatype, StructType)
                        else sf.datatype,
                        next_level_trace_stack,
                        string_nodes_finalized,
                        dropFieldIfAllNull,
                    )
                else:
                    sf.datatype = StringType()
                    string_nodes_finalized.add(col_name)
                columns_with_valid_contents.add(col_name)

        elif isinstance(sf.datatype, ArrayType):
            content = row[col_name]
            if content is not None:
                with suppress(Exception):
                    decoded_content = json.loads(content)
                    if isinstance(decoded_content, list):
                        content = decoded_content
                if not isinstance(content, list) or col_name in string_nodes_finalized:
                    sf.datatype = StringType()
                    string_nodes_finalized.add(col_name)
                else:
                    next_level_trace_stack = _append_node_in_trace_stack(
                        col_name, "array"
                    )
                    if next_level_trace_stack in string_nodes_finalized:
                        sf.datatype.element_type = StringType()
                    else:
                        inner_schema = sf.datatype.element_type
                        for v in content:
                            if v is not None:
                                columns_with_valid_contents.add(col_name)
                            inner_schema = merge_json_schema(
                                v,
                                inner_schema,
                                next_level_trace_stack,
                                string_nodes_finalized,
                                dropFieldIfAllNull,
                            )
                            if isinstance(inner_schema, StringType):
                                string_nodes_finalized.add(next_level_trace_stack)
                                break
                        sf.datatype.element_type = inner_schema
        elif isinstance(sf.datatype, TimestampType):
            sf.datatype = StringType()
            columns_with_valid_contents.add(col_name)
            string_nodes_finalized.add(col_name)
        elif row[col_name] is not None:
            columns_with_valid_contents.add(col_name)

        if isinstance(sf.datatype, StructType) or isinstance(sf.datatype, ArrayType):
            sf.datatype.structured = True
        new_schema.add(sf)

    return new_schema


def insert_data_chunk(
    session: snowpark.Session,
    data: list[Row],
    schema: StructType,
    table_name: str,
) -> None:
    df = session.create_dataframe(
        data=data,
        schema=schema,
    )

    df.write.mode("append").save_as_table(
        table_name, table_type="temp", table_exists=True
    )


def construct_dataframe_by_schema(
    schema: StructType,
    rows: typing.Iterator[Row],
    session: snowpark.Session,
    snowpark_options: dict,
    batch_size: int = 1000,
) -> snowpark.DataFrame:
    table_name = "__sas_json_read_temp_" + uuid.uuid4().hex

    # We can have more workers than CPU count, this is an IO-intensive task
    max_workers = min(16, os.cpu_count() * 2)

    current_data = []
    progress = 0

    # Initialize the temp table
    session.create_dataframe([], schema=schema).write.mode("append").save_as_table(
        table_name, table_type="temp", table_exists=False
    )

    is_running_in_stored_proc = is_in_stored_procedure()

    # We are having issues in which the read is not giving correct number of rows
    # in storedprocs when the number of workers are more than 1
    # as a temporary fix we will make max_workers to 1
    if is_running_in_stored_proc:
        max_workers = 1

    with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as exc:
        for row in rows:
            current_data.append(construct_row_by_schema(row, schema, snowpark_options))
            if len(current_data) >= batch_size:
                progress += len(current_data)
                exc.submit(
                    insert_data_chunk,
                    session,
                    copy.deepcopy(current_data),
                    schema,
                    table_name,
                )

                logger.info(f"JSON reader: finished processing {progress} rows")
                current_data.clear()

        if len(current_data) > 0:
            progress += len(current_data)
            exc.submit(
                insert_data_chunk,
                session,
                copy.deepcopy(current_data),
                schema,
                table_name,
            )
            logger.info(f"JSON reader: finished processing {progress} rows")

    return session.table(table_name)


def construct_row_by_schema(
    content: typing.Any, schema: DataType, snowpark_options: dict
) -> None | DataType:
    if content is None:
        return None
    elif isinstance(schema, StructType):
        result = {}
        if isinstance(content, (dict, Row)):
            for sf in schema.fields:
                col_name = unquote_if_quoted(sf.name)
                quoted_col_name = (
                    f'"{col_name}"' if isinstance(content, Row) else col_name
                )
                result[quoted_col_name] = construct_row_by_schema(
                    (content.as_dict() if isinstance(content, Row) else content).get(
                        col_name, None
                    ),
                    sf.datatype,
                    snowpark_options,
                )
        elif isinstance(content, str):
            with suppress(json.JSONDecodeError):
                decoded_content = json.loads(content)
                if isinstance(decoded_content, dict):
                    content = decoded_content
            for sf in schema.fields:
                col_name = unquote_if_quoted(sf.name)
                result[col_name] = construct_row_by_schema(
                    content.get(col_name, None), sf.datatype, snowpark_options
                )
        else:
            exception = SnowparkConnectNotImplementedError(
                f"JSON construct {str(content)} to StructType failed"
            )
            attach_custom_error_code(exception, ErrorCodes.TYPE_MISMATCH)
            raise exception
        return result
    elif isinstance(schema, ArrayType):
        result = []
        inner_schema = schema.element_type
        if isinstance(content, str):
            content = json.loads(content)
        if inner_schema is not None:
            for ele in content:
                result.append(
                    construct_row_by_schema(ele, inner_schema, snowpark_options)
                )
        return result
    elif isinstance(schema, DateType):
        return cast_to_match_snowpark_type(
            schema, content, snowpark_options.get("DATE_FORMAT")
        )

    return cast_to_match_snowpark_type(schema, content)
