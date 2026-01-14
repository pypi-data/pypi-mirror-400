#
# Copyright (c) 2012-2025 Snowflake Computing Inc. All rights reserved.
#

import pyspark.sql.connect.proto.relations_pb2 as relation_proto
from pyspark.sql.connect.proto.expressions_pb2 import CommonInlineUserDefinedFunction

import snowflake.snowpark.functions as snowpark_fn
from snowflake import snowpark
from snowflake.snowpark.types import StructType
from snowflake.snowpark_connect.column_name_handler import make_unique_snowpark_name
from snowflake.snowpark_connect.constants import MAP_IN_ARROW_EVAL_TYPE
from snowflake.snowpark_connect.dataframe_container import DataFrameContainer
from snowflake.snowpark_connect.expression.map_unresolved_star import (
    map_unresolved_star_as_single_column,
)
from snowflake.snowpark_connect.expression.typer import ExpressionTyper
from snowflake.snowpark_connect.relation.map_relation import map_relation
from snowflake.snowpark_connect.type_mapping import proto_to_snowpark_type
from snowflake.snowpark_connect.utils.java_udtf_utils import (
    JAVA_UDTF_PREFIX,
    create_java_udtf_for_scala_flatmap_handling,
)
from snowflake.snowpark_connect.utils.pandas_udtf_utils import (
    create_pandas_udtf,
    create_pandas_udtf_with_arrow,
)
from snowflake.snowpark_connect.utils.udf_helper import udf_check
from snowflake.snowpark_connect.utils.udtf_helper import (
    create_pandas_udtf_in_sproc,
    require_creating_udtf_in_sproc,
)


def map_map_partitions(
    rel: relation_proto.Relation,
) -> DataFrameContainer:
    """
    Map a function over the partitions of the input DataFrame.

    This is a simple wrapper around the `mapInPandas` method in Snowpark.
    """
    input_container = map_relation(rel.map_partitions.input)
    udf_proto = rel.map_partitions.func
    udf_check(udf_proto)

    return _map_with_pandas_udtf(input_container, udf_proto)


def _call_udtf(
    udtf_name: str, input_df: snowpark.DataFrame, return_type: StructType | None = None
) -> snowpark.DataFrame:
    # Add a dummy column with random 1-10 values for partitioning
    input_df_with_dummy = input_df.withColumn(
        "_DUMMY_PARTITION_KEY",
        (
            snowpark_fn.uniform(
                snowpark_fn.lit(1), snowpark_fn.lit(10), snowpark_fn.random()
            )
            * 10
        ).cast("int"),
    )

    udtf_columns = [f"snowflake_jtf_{column}" for column in input_df.columns] + [
        "_DUMMY_PARTITION_KEY"
    ]

    tfc = snowpark_fn.call_table_function(udtf_name, *udtf_columns).over(
        partition_by=[snowpark_fn.col("_DUMMY_PARTITION_KEY")]
    )

    # Overwrite the input_df columns to prevent name conflicts with UDTF output columns
    result_df_with_dummy = input_df_with_dummy.to_df(udtf_columns).join_table_function(
        tfc
    )

    output_cols = [field.name for field in return_type.fields]

    # Only return the output columns.
    result_df = result_df_with_dummy.select(*output_cols)

    return DataFrameContainer.create_with_column_mapping(
        dataframe=result_df,
        spark_column_names=output_cols,
        snowpark_column_names=output_cols,
        snowpark_column_types=[field.datatype for field in return_type.fields],
    )


def _map_with_pandas_udtf(
    input_df_container: DataFrameContainer,
    udf_proto: CommonInlineUserDefinedFunction,
) -> snowpark.DataFrame:
    """
    Handle mapInArrow using pandas_udtf for partition-level Arrow processing.
    """
    input_df = input_df_container.dataframe
    input_schema = input_df.schema
    spark_column_names = input_df_container.column_map.get_spark_columns()
    return_type = proto_to_snowpark_type(
        udf_proto.python_udf.output_type
        if udf_proto.WhichOneof("function") == "python_udf"
        else udf_proto.scalar_scala_udf.outputType
    )

    if udf_proto.WhichOneof("function") == "scalar_scala_udf":
        assert (
            len(udf_proto.scalar_scala_udf.inputTypes) == 1
        ), "len(inputTypes) should be 1 for map and flatMap operations"

        udtf_name = create_java_udtf_for_scala_flatmap_handling(udf_proto)

        if udf_proto.scalar_scala_udf.inputTypes[0].WhichOneof("kind") == "struct":
            spark_col_name, typed_col = map_unresolved_star_as_single_column(
                udf_proto.arguments[0],
                input_df_container.column_map,
                ExpressionTyper(input_df),
            )

            udtf_arg_column = typed_col.col
        else:
            udtf_arg_column = snowpark_fn.col(
                input_df_container.column_map.get_snowpark_columns()[0]
            )
            spark_col_name = input_df_container.column_map.get_spark_columns()[0]

        if udf_proto.scalar_scala_udf.inputTypes[0].WhichOneof("kind") in (
            "map",
            "array",
        ):
            udtf_arg_column = snowpark_fn.to_variant(udtf_arg_column)

        new_snowpark_col_name = make_unique_snowpark_name(spark_col_name)

        df = input_df.join_table_function(
            snowpark_fn.call_table_function(udtf_name, udtf_arg_column)
        )

        df = df.select(
            snowpark_fn.cast(
                snowpark_fn.col(JAVA_UDTF_PREFIX + "C1"), return_type
            ).alias(new_snowpark_col_name)
        )

        if udf_proto.scalar_scala_udf.outputType.WhichOneof("kind") == "struct":
            spark_names = [field.name for field in return_type.fields]
            output_snowpark_names = [
                make_unique_snowpark_name(name) for name in spark_names
            ]
            output_types = [field.datatype for field in return_type.fields]

            cols = [
                snowpark_fn.get(
                    snowpark_fn.col(new_snowpark_col_name), snowpark_fn.lit(spark_name)
                ).alias(snowpark_name)
                for spark_name, snowpark_name in zip(spark_names, output_snowpark_names)
            ]

            if cols:
                df = df.select(*cols)
        else:
            output_types = [return_type]
            output_snowpark_names = [new_snowpark_col_name]
            spark_names = [spark_col_name]

        return DataFrameContainer.create_with_column_mapping(
            dataframe=df,
            spark_column_names=spark_names,
            snowpark_column_names=output_snowpark_names,
            snowpark_column_types=output_types,
        )

    # Check if this is mapInArrow (eval_type == 207)
    map_in_arrow = (
        udf_proto.WhichOneof("function") == "python_udf"
        and udf_proto.python_udf.eval_type == MAP_IN_ARROW_EVAL_TYPE
    )
    if require_creating_udtf_in_sproc(udf_proto):
        udtf_name = create_pandas_udtf_in_sproc(
            udf_proto, spark_column_names, input_schema, return_type
        )
    else:
        if map_in_arrow:
            map_udtf = create_pandas_udtf_with_arrow(
                udf_proto, spark_column_names, input_schema, return_type
            )
        else:
            map_udtf = create_pandas_udtf(
                udf_proto, spark_column_names, input_schema, return_type
            )
        udtf_name = map_udtf.name
    return _call_udtf(udtf_name, input_df, return_type)
