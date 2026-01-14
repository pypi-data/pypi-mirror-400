#
# Copyright (c) 2012-2025 Snowflake Computing Inc. All rights reserved.
#

import hashlib
from dataclasses import dataclass

from pyspark.sql.connect.proto.expressions_pb2 import CommonInlineUserDefinedFunction

from snowflake.snowpark.types import ArrayType, MapType, VariantType
from snowflake.snowpark_connect.resources_initializer import (
    ensure_scala_udf_jars_uploaded,
)
from snowflake.snowpark_connect.type_mapping import (
    map_type_to_snowflake_type,
    proto_to_snowpark_type,
)
from snowflake.snowpark_connect.utils.jvm_udf_utils import (
    NullHandling,
    Param,
    ReturnType,
    Signature,
    build_jvm_udxf_imports,
    map_type_to_java_type,
)
from snowflake.snowpark_connect.utils.session import get_or_create_snowpark_session

JAVA_UDTF_PREFIX = "__SC_JAVA_UDTF_"

SCALA_INPUT_VARIANT = """
Object mappedInput = com.snowflake.sas.scala.UdfPacketUtils$.MODULE$.fromVariant(udfPacket, input, 0);

java.util.Iterator<Object> javaInput = Arrays.asList(mappedInput).iterator();
scala.collection.Iterator<Object> scalaInput = new scala.collection.AbstractIterator<Object>() {
    public boolean hasNext() { return javaInput.hasNext(); }
    public Object next() { return javaInput.next(); }
};
"""

SCALA_INPUT_SIMPLE_TYPE = """
java.util.Iterator<__iterator_type__> javaInput = Arrays.asList(input).iterator();
scala.collection.Iterator<__iterator_type__> scalaInput = new scala.collection.AbstractIterator<__iterator_type__>() {
    public boolean hasNext() { return javaInput.hasNext(); }
    public __iterator_type__ next() { return javaInput.next(); }
};
"""

UDTF_TEMPLATE = """
import org.apache.spark.sql.connect.common.UdfPacket;

import java.io.IOException;
import java.io.InputStream;
import java.io.ObjectInputStream;
import java.io.Serializable;
import java.nio.file.Files;
import java.nio.file.Paths;

import java.util.*;
import java.lang.*;
import java.util.stream.Collectors;
import com.snowflake.snowpark_java.types.*;
import java.util.stream.Stream;
import java.util.stream.StreamSupport;

public class OutputRow {
  public Variant __java_udtf_prefix__C1;
  public OutputRow(Variant __java_udtf_prefix__C1) {
    this.__java_udtf_prefix__C1 = __java_udtf_prefix__C1;
  }
}

public class JavaUdtfHandler {
    private final static String OPERATION_FILE = "__operation_file__";
    private static scala.Function1<scala.collection.Iterator<__iterator_type__>, scala.collection.Iterator<Object>> operation = null;
    private static UdfPacket udfPacket = null;

  public static Class getOutputClass() { return OutputRow.class; }

    private static void loadOperation() throws IOException, ClassNotFoundException {
        if (operation != null) {
            return; // Already loaded
        }

        udfPacket = com.snowflake.sas.scala.Utils$.MODULE$.deserializeUdfPacket(OPERATION_FILE);
        operation = (scala.Function1<scala.collection.Iterator<__iterator_type__>, scala.collection.Iterator<Object>>) udfPacket.function();
    }

  public Stream<OutputRow> process(__input_type__ input) throws IOException, ClassNotFoundException {
        loadOperation();

        __scala_input__

        scala.collection.Iterator<Object> scalaResult = operation.apply(scalaInput);

        java.util.Iterator<Variant> javaResult = new java.util.Iterator<Variant>() {
            public boolean hasNext() { return scalaResult.hasNext(); }
            public Variant next() {
                return com.snowflake.sas.scala.Utils$.MODULE$.toVariant(scalaResult.next(), udfPacket);
            }
        };

        return StreamSupport.stream(Spliterators.spliteratorUnknownSize(javaResult, Spliterator.ORDERED), false)
                .map(i -> new OutputRow(i));
  }

  public Stream<OutputRow> endPartition() {
    return Stream.empty();
  }
}
"""


@dataclass(frozen=True)
class JavaUDTFDef:
    """
    Complete definition for creating a Java UDTF in Snowflake.

    Contains all the information needed to generate the CREATE FUNCTION SQL statement
    and the Java code body for the UDTF.

    Attributes:
        name: UDTF name
        signature: SQL signature (for Snowflake function definition)
        java_signature: Java signature (for Java code generation)
        imports: List of JAR files to import
        null_handling: Null handling behavior (defaults to RETURNS_NULL_ON_NULL_INPUT)
    """

    name: str
    signature: Signature
    java_signature: Signature
    imports: list[str]
    null_handling: NullHandling = NullHandling.RETURNS_NULL_ON_NULL_INPUT

    def _gen_body_java(self) -> str:
        returns_variant = self.signature.returns.data_type == "VARIANT"
        return_type = (
            "Variant" if returns_variant else self.java_signature.returns.data_type
        )

        is_variant_input = self.java_signature.params[0].data_type.lower() == "variant"

        scala_input_template = (
            SCALA_INPUT_VARIANT if is_variant_input else SCALA_INPUT_SIMPLE_TYPE
        )

        iterator_type = (
            "Object" if is_variant_input else self.java_signature.params[0].data_type
        )

        return (
            UDTF_TEMPLATE.replace("__operation_file__", self.imports[0].split("/")[-1])
            .replace("__scala_input__", scala_input_template)
            .replace("__iterator_type__", iterator_type)
            .replace("__input_type__", self.java_signature.params[0].data_type)
            .replace("__return_type__", return_type)
            .replace("__java_udtf_prefix__", JAVA_UDTF_PREFIX)
        )

    def to_create_function_sql(self) -> str:
        args = ", ".join(
            [f"{param.name} {param.data_type}" for param in self.signature.params]
        )

        def quote_single(s: str) -> str:
            """Helper function to wrap strings in single quotes for SQL."""
            return "'" + s + "'"

        # Handler and imports
        imports_sql = f"IMPORTS = ({', '.join(quote_single(x) for x in self.imports)})"

        return f"""
create or replace function {self.name}({args})
returns table ({JAVA_UDTF_PREFIX}C1 VARIANT)
language java
runtime_version = 17
PACKAGES = ('com.snowflake:snowpark:latest')
{imports_sql}
handler='JavaUdtfHandler'
as
$$
{self._gen_body_java()}
$$;"""


def create_java_udtf_for_scala_flatmap_handling(
    udf_proto: CommonInlineUserDefinedFunction,
) -> str:
    ensure_scala_udf_jars_uploaded()

    return_type = proto_to_snowpark_type(udf_proto.scalar_scala_udf.outputType)

    session = get_or_create_snowpark_session()

    return_type_java = map_type_to_java_type(return_type)
    sql_return_type = map_type_to_snowflake_type(return_type)

    java_input_params: list[Param] = []
    sql_input_params: list[Param] = []
    for i, input_type_proto in enumerate(udf_proto.scalar_scala_udf.inputTypes):
        input_type = proto_to_snowpark_type(input_type_proto)

        param_name = "arg" + str(i)

        if isinstance(input_type, (ArrayType, MapType, VariantType)):
            java_type = "Variant"
            snowflake_type = "Variant"
        else:
            java_type = map_type_to_java_type(input_type)
            snowflake_type = map_type_to_snowflake_type(input_type)

        java_input_params.append(Param(param_name, java_type))
        sql_input_params.append(Param(param_name, snowflake_type))

    udtf_name = (
        JAVA_UDTF_PREFIX + hashlib.md5(udf_proto.scalar_scala_udf.payload).hexdigest()
    )

    imports = build_jvm_udxf_imports(
        session,
        udf_proto.scalar_scala_udf.payload,
        udtf_name,
    )

    udtf = JavaUDTFDef(
        name=udtf_name,
        signature=Signature(
            params=sql_input_params, returns=ReturnType(sql_return_type)
        ),
        imports=imports,
        java_signature=Signature(
            params=java_input_params, returns=ReturnType(return_type_java)
        ),
    )

    sql = udtf.to_create_function_sql()
    session.sql(sql).collect()

    return udtf_name
