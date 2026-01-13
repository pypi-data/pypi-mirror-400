"""
Tests for HoloTable class in Holo Search SDK.

This module contains comprehensive tests for the HoloTable table class.
"""

from unittest.mock import Mock, patch

import pytest

from holo_search_sdk.backend import HoloTable
from holo_search_sdk.backend.connection import HoloConnect
from holo_search_sdk.backend.query import QueryBuilder
from holo_search_sdk.exceptions import SqlError


class TestHoloTable:
    """Test cases for the HoloTable class."""

    def test_holo_table_initialization(self):
        """Test HoloTable initialization."""
        mock_connection = Mock(spec=HoloConnect)
        table_name = "test_table"

        table = HoloTable(mock_connection, table_name)

        assert table._db is mock_connection
        assert table._name == table_name
        assert table._column_distance_methods == {}

    def test_get_name(self):
        """Test get_name method."""
        mock_connection = Mock(spec=HoloConnect)
        table_name = "test_table"

        table = HoloTable(mock_connection, table_name)

        assert table.get_name() == table_name

    def test_holo_table_initialization_with_alias(self):
        """Test HoloTable initialization with alias."""
        mock_connection = Mock(spec=HoloConnect)
        table_name = "test_table"
        table_alias = "tt"

        table = HoloTable(mock_connection, table_name, table_alias)

        assert table._db is mock_connection
        assert table._name == table_name
        assert table._alias == table_alias
        assert table._column_distance_methods == {}

    def test_get_alias(self):
        """Test get_alias method."""
        mock_connection = Mock(spec=HoloConnect)
        table_name = "test_table"
        table_alias = "tt"

        table = HoloTable(mock_connection, table_name, table_alias)

        assert table.get_alias() == table_alias

    def test_get_alias_none(self):
        """Test get_alias method when no alias is set."""
        mock_connection = Mock(spec=HoloConnect)
        table_name = "test_table"

        table = HoloTable(mock_connection, table_name)

        assert table.get_alias() is None

    def test_vacuum(self):
        """Test vacuum method."""
        mock_connection = Mock(spec=HoloConnect)
        table_name = "test_table"

        table = HoloTable(mock_connection, table_name)
        result = table.vacuum()

        assert result is table  # Method chaining
        mock_connection.execute.assert_called_once()
        call_args = mock_connection.execute.call_args
        sql_str = call_args[0][0].as_string()
        assert sql_str == 'VACUUM "test_table";'
        assert call_args[1]["use_transaction"] is False

    def test_insert_multi_without_column_names(self):
        """Test insert_multi method without column names."""
        mock_connection = Mock(spec=HoloConnect)
        table_name = "test_table"
        values = [
            [1, "test1", [0.1, 0.2]],
            [2, "test2", [0.3, 0.4]],
            [3, "test3", [0.5, 0.6]],
        ]

        table = HoloTable(mock_connection, table_name)
        result = table.insert_multi(values)

        assert result is table  # Method chaining
        mock_connection.execute.assert_called_once()
        call_args = mock_connection.execute.call_args[0]
        sql_str = call_args[0].as_string()
        assert 'INSERT INTO "test_table"' in sql_str
        assert "VALUES" in sql_str

    def test_insert_multi_with_column_names(self):
        """Test insert_multi method with column names."""
        mock_connection = Mock(spec=HoloConnect)
        table_name = "test_table"
        values = [
            [1, "test1", [0.1, 0.2]],
            [2, "test2", [0.3, 0.4]],
        ]
        column_names = ["id", "name", "vector"]

        table = HoloTable(mock_connection, table_name)
        result = table.insert_multi(values, column_names)

        assert result is table  # Method chaining
        mock_connection.execute.assert_called_once()
        call_args = mock_connection.execute.call_args[0]
        sql_str = call_args[0].as_string()
        assert 'INSERT INTO "test_table"' in sql_str
        assert "id" in sql_str
        assert "name" in sql_str
        assert "vector" in sql_str

    def test_set_vector_index_default_params(self):
        """Test set_vector_index method with default parameters."""
        mock_connection = Mock(spec=HoloConnect)
        table_name = "test_table"
        column = "vector"
        distance_method = "Cosine"
        base_quantization_type = "rabitq"

        table = HoloTable(mock_connection, table_name)
        result = table.set_vector_index(column, distance_method, base_quantization_type)

        assert result is table  # Method chaining
        assert table._column_distance_methods[column] == distance_method
        mock_connection.execute.assert_called_once()
        call_args = mock_connection.execute.call_args[0]
        sql_str = call_args[0].as_string()
        assert "set_table_property" in sql_str
        assert "vectors" in sql_str
        assert "HGraph" in sql_str

    def test_set_vector_index_custom_params(self):
        """Test set_vector_index method with custom parameters."""
        mock_connection = Mock(spec=HoloConnect)
        table_name = "test_table"
        column = "embedding"
        distance_method = "Euclidean"
        base_quantization_type = "fp16"

        table = HoloTable(mock_connection, table_name)
        result = table.set_vector_index(
            column,
            distance_method,
            base_quantization_type,
            max_degree=32,
            ef_construction=200,
            use_reorder=True,
            precise_quantization_type="fp16",
            precise_io_type="reader_io",
            max_total_size_to_merge_mb=2048,
            build_thread_count=8,
        )

        assert result is table  # Method chaining
        assert table._column_distance_methods[column] == distance_method
        mock_connection.execute.assert_called_once()

    def test_set_vector_indexes_single_column(self):
        """Test set_vector_indexes method with single column."""
        mock_connection = Mock(spec=HoloConnect)
        table_name = "test_table"
        column_configs = {
            "vector": {
                "distance_method": "Cosine",
                "base_quantization_type": "rabitq",
                "max_degree": 64,
                "ef_construction": 400,
            }
        }

        table = HoloTable(mock_connection, table_name)
        result = table.set_vector_indexes(column_configs)

        assert result is table  # Method chaining
        # After setting indexes, _column_distance_methods should have the distance method
        assert len(table._column_distance_methods) == 1
        mock_connection.execute.assert_called_once()
        call_args = mock_connection.execute.call_args[0]
        sql_str = call_args[0].as_string()
        assert "set_table_property" in sql_str
        assert "vectors" in sql_str

    def test_set_vector_indexes_multiple_columns(self):
        """Test set_vector_indexes method with multiple columns."""
        mock_connection = Mock(spec=HoloConnect)
        table_name = "test_table"
        column_configs = {
            "vector1": {
                "distance_method": "Cosine",
                "base_quantization_type": "rabitq",
            },
            "vector2": {
                "distance_method": "Euclidean",
                "base_quantization_type": "fp32",
                "max_degree": 32,
            },
        }

        table = HoloTable(mock_connection, table_name)
        result = table.set_vector_indexes(column_configs)

        assert result is table  # Method chaining
        mock_connection.execute.assert_called_once()
        call_args = mock_connection.execute.call_args[0]
        sql_str = call_args[0].as_string()
        assert "set_table_property" in sql_str
        assert "vector1" in sql_str
        assert "vector2" in sql_str

    @patch("holo_search_sdk.backend.table.QueryBuilder")
    def test_get_by_key_with_return_columns(self, mock_query_builder_class):
        """Test get_by_key method with specific return columns."""
        mock_connection = Mock(spec=HoloConnect)
        mock_query_builder = Mock(spec=QueryBuilder)
        mock_query_builder.select.return_value = mock_query_builder
        mock_query_builder.where.return_value = mock_query_builder
        mock_query_builder_class.return_value = mock_query_builder

        table = HoloTable(mock_connection, "test_table")
        return_columns = ["id", "name", "vector"]

        result = table.get_by_key("id", 123, return_columns)

        assert result is mock_query_builder
        mock_query_builder_class.assert_called_once_with(
            mock_connection, "test_table", None
        )
        mock_query_builder.select.assert_called_once_with(return_columns)
        mock_query_builder.where.assert_called_once()

    @patch("holo_search_sdk.backend.table.QueryBuilder")
    def test_get_by_key_without_return_columns(self, mock_query_builder_class):
        """Test get_by_key method without specific return columns (select all)."""
        mock_connection = Mock(spec=HoloConnect)
        mock_query_builder = Mock(spec=QueryBuilder)
        mock_query_builder.select.return_value = mock_query_builder
        mock_query_builder.where.return_value = mock_query_builder
        mock_query_builder_class.return_value = mock_query_builder

        table = HoloTable(mock_connection, "test_table")

        result = table.get_by_key("id", 123)

        assert result is mock_query_builder
        mock_query_builder_class.assert_called_once_with(
            mock_connection, "test_table", None
        )
        mock_query_builder.select.assert_called_once_with("*")
        mock_query_builder.where.assert_called_once()

    @patch("holo_search_sdk.backend.table.QueryBuilder")
    def test_get_by_key_string_value(self, mock_query_builder_class):
        """Test get_by_key method with string key value."""
        mock_connection = Mock(spec=HoloConnect)
        mock_query_builder = Mock(spec=QueryBuilder)
        mock_query_builder.select.return_value = mock_query_builder
        mock_query_builder.where.return_value = mock_query_builder
        mock_query_builder_class.return_value = mock_query_builder

        table = HoloTable(mock_connection, "test_table")

        result = table.get_by_key("username", "test_user", ["id", "username"])

        assert result is mock_query_builder
        mock_query_builder.select.assert_called_once_with(["id", "username"])
        mock_query_builder.where.assert_called_once()

    @patch("holo_search_sdk.backend.table.QueryBuilder")
    def test_get_multi_by_keys_with_return_columns(self, mock_query_builder_class):
        """Test get_multi_by_keys method with specific return columns."""
        mock_connection = Mock(spec=HoloConnect)
        mock_query_builder = Mock(spec=QueryBuilder)
        mock_query_builder.select.return_value = mock_query_builder
        mock_query_builder.where.return_value = mock_query_builder
        mock_query_builder_class.return_value = mock_query_builder

        table = HoloTable(mock_connection, "test_table")
        key_values = [1, 2, 3, 4]
        return_columns = ["id", "name", "vector"]

        result = table.get_multi_by_keys("id", key_values, return_columns)

        assert result is mock_query_builder
        mock_query_builder_class.assert_called_once_with(
            mock_connection, "test_table", None
        )
        mock_query_builder.select.assert_called_once_with(return_columns)
        mock_query_builder.where.assert_called_once()

    @patch("holo_search_sdk.backend.table.QueryBuilder")
    def test_get_multi_by_keys_without_return_columns(self, mock_query_builder_class):
        """Test get_multi_by_keys method without specific return columns (select all)."""
        mock_connection = Mock(spec=HoloConnect)
        mock_query_builder = Mock(spec=QueryBuilder)
        mock_query_builder.select.return_value = mock_query_builder
        mock_query_builder.where.return_value = mock_query_builder
        mock_query_builder_class.return_value = mock_query_builder

        table = HoloTable(mock_connection, "test_table")
        key_values = [1, 2, 3]

        result = table.get_multi_by_keys("id", key_values)

        assert result is mock_query_builder
        mock_query_builder_class.assert_called_once_with(
            mock_connection, "test_table", None
        )
        mock_query_builder.select.assert_called_once_with("*")
        mock_query_builder.where.assert_called_once()

    @patch("holo_search_sdk.backend.table.QueryBuilder")
    def test_get_multi_by_keys_empty_list(self, mock_query_builder_class):
        """Test get_multi_by_keys method with empty key values list."""
        mock_connection = Mock(spec=HoloConnect)
        mock_query_builder = Mock(spec=QueryBuilder)
        mock_query_builder.select.return_value = mock_query_builder
        mock_query_builder.where.return_value = mock_query_builder
        mock_query_builder_class.return_value = mock_query_builder

        table = HoloTable(mock_connection, "test_table")
        key_values = []

        result = table.get_multi_by_keys("id", key_values)

        assert result is mock_query_builder
        mock_query_builder.select.assert_called_once_with("*")
        mock_query_builder.where.assert_called_once()

    def test_insert_one_with_column_names(self):
        """Test inserting one record with column names."""
        mock_connection = Mock(spec=HoloConnect)
        table = HoloTable(mock_connection, "test_table")

        values = [1, "test", [0.1, 0.2, 0.3]]
        column_names = ["id", "content", "vector"]

        result = table.insert_one(values, column_names)

        assert result is table
        mock_connection.execute.assert_called_once()
        call_args = mock_connection.execute.call_args
        sql_str = call_args[0][0].as_string()
        assert (
            sql_str
            == 'INSERT INTO "test_table" ("id", "content", "vector") VALUES (%s, %s, %s);'
        )
        assert call_args[0][1] == tuple(values)

    def test_insert_one_without_column_names(self):
        """Test inserting one record without column names."""
        mock_connection = Mock(spec=HoloConnect)
        table = HoloTable(mock_connection, "test_table")

        values = [1, "test"]

        result = table.insert_one(values)

        assert result is table
        mock_connection.execute.assert_called_once()
        call_args = mock_connection.execute.call_args
        sql_str = call_args[0][0].as_string()
        assert sql_str == 'INSERT INTO "test_table" VALUES (%s, %s);'
        assert call_args[0][1] == tuple(values)

    def test_insert_multi_with_data(self):
        """Test inserting multiple records."""
        mock_connection = Mock(spec=HoloConnect)
        table = HoloTable(mock_connection, "test_table")

        values = [[1, "test1"], [2, "test2"], [3, "test3"]]
        column_names = ["id", "content"]

        result = table.insert_multi(values, column_names)

        assert result is table
        mock_connection.execute.assert_called_once()
        call_args = mock_connection.execute.call_args
        sql_str = call_args[0][0].as_string()
        assert (
            sql_str
            == 'INSERT INTO "test_table" ("id", "content") VALUES (%s, %s), (%s, %s), (%s, %s);'
        )
        # Check that all values are flattened in the tuple
        expected_params = (1, "test1", 2, "test2", 3, "test3")
        assert call_args[0][1] == expected_params

    def test_insert_multi_empty_values(self):
        """Test inserting empty list returns table without executing."""
        mock_connection = Mock(spec=HoloConnect)
        table = HoloTable(mock_connection, "test_table")

        result = table.insert_multi([])

        assert result is table
        mock_connection.execute.assert_not_called()

    def test_set_vector_index(self):
        """Test setting a vector index."""
        mock_connection = Mock(spec=HoloConnect)
        table = HoloTable(mock_connection, "test_table")

        result = table.set_vector_index(
            column="vector_col",
            distance_method="Euclidean",
            base_quantization_type="rabitq",
            max_degree=64,
            ef_construction=400,
        )

        assert result is table
        assert table._column_distance_methods["vector_col"] == "Euclidean"
        mock_connection.execute.assert_called_once()
        call_args = mock_connection.execute.call_args
        sql_str = call_args[0][0].as_string()
        expected_str = """CALL set_table_property('test_table', 'vectors', '{"vector_col": {"algorithm": "HGraph", "distance_method": "Euclidean", "builder_params": {"max_degree": 64, "ef_construction": 400, "base_quantization_type": "rabitq", "use_reorder": false, "precise_quantization_type": "fp32", "precise_io_type": "block_memory_io", "max_total_size_to_merge_mb": 4096, "build_thread_count": 16}}}');"""
        assert sql_str == expected_str

    def test_set_vector_indexes(self):
        """Test setting multiple vector indexes."""
        mock_connection = Mock(spec=HoloConnect)
        table = HoloTable(mock_connection, "test_table")

        column_configs = {
            "vector1": {
                "distance_method": "Euclidean",
                "base_quantization_type": "rabitq",
                "max_degree": 32,
            },
            "vector2": {
                "distance_method": "Cosine",
                "base_quantization_type": "rabitq",
                "ef_construction": 300,
            },
        }

        result = table.set_vector_indexes(column_configs)

        assert result is table
        assert table._column_distance_methods["vector1"] == "Euclidean"
        assert table._column_distance_methods["vector2"] == "Cosine"
        mock_connection.execute.assert_called_once()
        call_args = mock_connection.execute.call_args
        sql_str = call_args[0][0].as_string()
        expected_str = """
            CALL set_table_property(
                'test_table',
                'vectors',
                '{"vector1": {"algorithm": "HGraph", "distance_method": "Euclidean", "builder_params": {"max_degree": 32, "ef_construction": 400, "base_quantization_type": "rabitq", "use_reorder": false, "precise_quantization_type": "fp32", "precise_io_type": "block_memory_io", "max_total_size_to_merge_mb": 4096, "build_thread_count": 16}}, "vector2": {"algorithm": "HGraph", "distance_method": "Cosine", "builder_params": {"max_degree": 64, "ef_construction": 300, "base_quantization_type": "rabitq", "use_reorder": false, "precise_quantization_type": "fp32", "precise_io_type": "block_memory_io", "max_total_size_to_merge_mb": 4096, "build_thread_count": 16}}}');
            """
        assert sql_str == expected_str

    def test_delete_vector_indexes(self):
        """Test deleting all vector indexes."""
        mock_connection = Mock(spec=HoloConnect)
        table = HoloTable(mock_connection, "test_table")
        table._column_distance_methods = {"vector1": "Euclidean", "vector2": "Cosine"}

        result = table.delete_vector_indexes()

        assert result is table
        assert table._column_distance_methods == {}
        mock_connection.execute.assert_called_once()
        call_args = mock_connection.execute.call_args
        sql_str = call_args[0][0].as_string()
        expected_str = """
        CALL set_table_property(
            'test_table',
            'vectors',
            '{}');
        """
        assert sql_str == expected_str

    @patch("holo_search_sdk.backend.table.QueryBuilder")
    def test_search_vector_with_distance_method(self, mock_query_builder_class):
        """Test vector search with explicit distance method."""
        mock_connection = Mock(spec=HoloConnect)
        mock_query_builder = Mock(spec=QueryBuilder)
        mock_query_builder.select.return_value = mock_query_builder
        mock_query_builder.set_distance_column.return_value = mock_query_builder
        mock_query_builder_class.return_value = mock_query_builder

        table = HoloTable(mock_connection, "test_table")
        vector = [0.1, 0.2, 0.3]

        result = table.search_vector(vector, "vector_col", distance_method="Euclidean")

        assert result is mock_query_builder
        mock_query_builder_class.assert_called_once_with(
            mock_connection, "test_table", None
        )
        mock_query_builder.select.assert_called_once()

    @patch("holo_search_sdk.backend.table.QueryBuilder")
    def test_search_vector_with_cached_distance_method(self, mock_query_builder_class):
        """Test vector search with cached distance method."""
        mock_connection = Mock(spec=HoloConnect)
        mock_query_builder = Mock(spec=QueryBuilder)
        mock_query_builder.select.return_value = mock_query_builder
        mock_query_builder.set_distance_column.return_value = mock_query_builder
        mock_query_builder_class.return_value = mock_query_builder

        table = HoloTable(mock_connection, "test_table")
        table._column_distance_methods["vector_col"] = "Cosine"
        vector = [0.1, 0.2, 0.3]

        result = table.search_vector(vector, "vector_col")

        assert result is mock_query_builder
        mock_query_builder.select.assert_called_once()

    def test_search_vector_no_distance_method(self):
        """Test vector search without distance method raises SqlError."""
        mock_connection = Mock(spec=HoloConnect)
        table = HoloTable(mock_connection, "test_table")
        vector = [0.1, 0.2, 0.3]

        with pytest.raises(SqlError) as exc_info:
            table.search_vector(vector, "vector_col")

        assert "Distance method must be set" in str(exc_info.value)

    @patch("holo_search_sdk.backend.table.QueryBuilder")
    def test_search_vector_with_output_name(self, mock_query_builder_class):
        """Test vector search with custom output name."""
        mock_connection = Mock(spec=HoloConnect)
        mock_query_builder = Mock(spec=QueryBuilder)
        mock_query_builder.select.return_value = mock_query_builder
        mock_query_builder.set_distance_column.return_value = mock_query_builder
        mock_query_builder_class.return_value = mock_query_builder

        table = HoloTable(mock_connection, "test_table")
        vector = [0.1, 0.2, 0.3]

        result = table.search_vector(
            vector, "vector_col", output_name="similarity", distance_method="Euclidean"
        )

        assert result is mock_query_builder
        # Check that select was called with a tuple (for aliasing in psycopg3)
        call_args = mock_query_builder.select.call_args[0][0]
        assert isinstance(call_args, tuple)

    @patch("holo_search_sdk.backend.table.QueryBuilder")
    def test_select_with_string(self, mock_query_builder_class):
        """Test select method with string column."""
        mock_connection = Mock(spec=HoloConnect)
        mock_query_builder = Mock(spec=QueryBuilder)
        mock_query_builder.select.return_value = mock_query_builder
        mock_query_builder_class.return_value = mock_query_builder

        table = HoloTable(mock_connection, "test_table")
        result = table.select("id, name")

        assert result is mock_query_builder
        mock_query_builder_class.assert_called_once_with(
            mock_connection, "test_table", None
        )
        mock_query_builder.select.assert_called_once_with("id, name")

    @patch("holo_search_sdk.backend.table.QueryBuilder")
    def test_select_with_list(self, mock_query_builder_class):
        """Test select method with list of columns."""
        mock_connection = Mock(spec=HoloConnect)
        mock_query_builder = Mock(spec=QueryBuilder)
        mock_query_builder.select.return_value = mock_query_builder
        mock_query_builder_class.return_value = mock_query_builder

        table = HoloTable(mock_connection, "test_table")
        result = table.select(["id", "name", "email"])

        assert result is mock_query_builder
        mock_query_builder.select.assert_called_once_with(["id", "name", "email"])

    @patch("holo_search_sdk.backend.table.QueryBuilder")
    def test_set_table_alias(self, mock_query_builder_class):
        """Test set_table_alias method."""
        mock_connection = Mock(spec=HoloConnect)
        mock_query_builder = Mock(spec=QueryBuilder)
        mock_query_builder_class.return_value = mock_query_builder

        table = HoloTable(mock_connection, "test_table")
        result = table.set_table_alias("t1")

        assert table._alias == "t1"
        assert result is mock_query_builder
        mock_query_builder_class.assert_called_once_with(
            mock_connection, "test_table", "t1"
        )

    def test_create_text_index_basic(self):
        """Test creating a basic text index."""
        mock_connection = Mock(spec=HoloConnect)
        table = HoloTable(mock_connection, "test_table")

        result = table.create_text_index("idx_content", "content")

        assert result is table
        mock_connection.execute.assert_called_once()
        call_args = mock_connection.execute.call_args[0]
        sql_str = call_args[0].as_string()
        assert 'CREATE INDEX IF NOT EXISTS "idx_content"' in sql_str
        assert 'ON "test_table"' in sql_str
        assert 'USING FULLTEXT ("content")' in sql_str

    def test_create_text_index_with_tokenizer(self):
        """Test creating text index with tokenizer."""
        mock_connection = Mock(spec=HoloConnect)
        table = HoloTable(mock_connection, "test_table")

        result = table.create_text_index("idx_content", "content", tokenizer="jieba")

        assert result is table
        mock_connection.execute.assert_called_once()
        call_args = mock_connection.execute.call_args[0]
        sql_str = call_args[0].as_string()
        assert 'CREATE INDEX IF NOT EXISTS "idx_content"' in sql_str
        assert 'ON "test_table"' in sql_str
        assert 'USING FULLTEXT ("content")' in sql_str
        assert "WITH (tokenizer = 'jieba')" in sql_str

    def test_get_vector_index_info_with_data(self):
        """Test get_vector_index_info with valid data."""
        mock_connection = Mock(spec=HoloConnect)
        mock_config = Mock()
        mock_config.schema = "public"
        mock_connection.get_config.return_value = mock_config
        mock_connection.fetchone.return_value = (
            '{"vector_col": {"distance_method": "Cosine"}}',
        )

        table = HoloTable(mock_connection, "test_table")
        result = table.get_vector_index_info()

        assert result is not None
        assert "vector_col" in result
        assert result["vector_col"]["distance_method"] == "Cosine"

    def test_get_vector_index_info_no_data(self):
        """Test get_vector_index_info with no data."""
        mock_connection = Mock(spec=HoloConnect)
        mock_config = Mock()
        mock_config.schema = "public"
        mock_connection.get_config.return_value = mock_config
        mock_connection.fetchone.return_value = None

        table = HoloTable(mock_connection, "test_table")
        result = table.get_vector_index_info()

        assert result is None

    def test_get_vector_index_info_invalid_json(self):
        """Test get_vector_index_info with invalid JSON."""
        mock_connection = Mock(spec=HoloConnect)
        mock_config = Mock()
        mock_config.schema = "public"
        mock_connection.get_config.return_value = mock_config
        mock_connection.fetchone.return_value = ("invalid json",)

        table = HoloTable(mock_connection, "test_table")
        result = table.get_vector_index_info()

        assert result is None

    @patch("holo_search_sdk.backend.table.QueryBuilder")
    def test_search_vector_with_get_column_distance_method(
        self, mock_query_builder_class
    ):
        """Test search_vector that calls _get_column_distance_method."""
        mock_connection = Mock(spec=HoloConnect)
        mock_config = Mock()
        mock_config.schema = "public"
        mock_connection.get_config.return_value = mock_config
        mock_connection.fetchone.return_value = (
            '{"vector_col": {"distance_method": "Euclidean"}}',
        )

        mock_query_builder = Mock(spec=QueryBuilder)
        mock_query_builder.select.return_value = mock_query_builder
        mock_query_builder.set_distance_column.return_value = mock_query_builder
        mock_query_builder_class.return_value = mock_query_builder

        table = HoloTable(mock_connection, "test_table")
        vector = [0.1, 0.2, 0.3]

        result = table.search_vector(vector, "vector_col")

        assert result is mock_query_builder
        assert table._column_distance_methods["vector_col"] == "Euclidean"

    def test_set_text_index(self):
        """Test set_text_index method."""
        mock_connection = Mock(spec=HoloConnect)
        table = HoloTable(mock_connection, "test_table")

        result = table.set_text_index("idx_content", "jieba")

        assert result is table
        mock_connection.execute.assert_called_once()
        call_args = mock_connection.execute.call_args[0]
        sql_str = call_args[0].as_string()
        assert 'ALTER INDEX "idx_content"' in sql_str
        assert "tokenizer = 'jieba'" in sql_str

    def test_set_text_index_with_params(self):
        """Test set_text_index with tokenizer and filter params."""
        mock_connection = Mock(spec=HoloConnect)
        table = HoloTable(mock_connection, "test_table")

        from collections import OrderedDict

        filter_params = OrderedDict([("lowercase", True)])

        result = table.set_text_index(
            "idx_content",
            "jieba",
            tokenizer_params={"max_token_length": 100},
            filter_params=filter_params,
        )

        assert result is table
        mock_connection.execute.assert_called_once()

    def test_reset_text_index_full(self):
        """Test reset_text_index with full reset."""
        mock_connection = Mock(spec=HoloConnect)
        table = HoloTable(mock_connection, "test_table")

        result = table.reset_text_index("idx_content", only_reset_analyzer_params=False)

        assert result is table
        mock_connection.execute.assert_called_once()
        call_args = mock_connection.execute.call_args[0]
        sql_str = call_args[0].as_string()
        assert 'ALTER INDEX "idx_content" RESET (tokenizer)' in sql_str

    def test_reset_text_index_analyzer_only(self):
        """Test reset_text_index with analyzer params only."""
        mock_connection = Mock(spec=HoloConnect)
        table = HoloTable(mock_connection, "test_table")

        result = table.reset_text_index("idx_content", only_reset_analyzer_params=True)

        assert result is table
        mock_connection.execute.assert_called_once()
        call_args = mock_connection.execute.call_args[0]
        sql_str = call_args[0].as_string()
        assert 'ALTER INDEX "idx_content" RESET (analyzer_params)' in sql_str

    def test_drop_text_index(self):
        """Test drop_text_index method."""
        mock_connection = Mock(spec=HoloConnect)
        table = HoloTable(mock_connection, "test_table")

        result = table.drop_text_index("idx_content")

        assert result is table
        mock_connection.execute.assert_called_once()
        call_args = mock_connection.execute.call_args[0]
        sql_str = call_args[0].as_string()
        assert 'DROP INDEX IF EXISTS "idx_content"' in sql_str

    def test_get_index_properties_all_fields(self):
        """Test get_index_properties with all fields."""
        mock_connection = Mock(spec=HoloConnect)
        mock_connection.fetchall.return_value = [
            (1, "public", "test_table", "idx_content", "tokenizer", "jieba")
        ]

        table = HoloTable(mock_connection, "test_table")
        result = table.get_index_properties()

        assert len(result) == 1
        assert result[0] == (
            1,
            "public",
            "test_table",
            "idx_content",
            "tokenizer",
            "jieba",
        )
        mock_connection.fetchall.assert_called_once()

    def test_get_index_properties_selective_fields(self):
        """Test get_index_properties with selective fields."""
        mock_connection = Mock(spec=HoloConnect)
        mock_connection.fetchall.return_value = [("idx_content", "tokenizer")]

        table = HoloTable(mock_connection, "test_table")
        result = table.get_index_properties(
            return_index_id=False,
            return_table_namespace=False,
            return_table_name=False,
            return_index_name=True,
            return_property_key=True,
            return_property_value=False,
        )

        assert len(result) == 1
        mock_connection.fetchall.assert_called_once()

    def test_show_tokenize_effect_with_text(self):
        """Test show_tokenize_effect with text."""
        mock_connection = Mock(spec=HoloConnect)
        mock_connection.fetchone.return_value = (["hello", "world"],)

        table = HoloTable(mock_connection, "test_table")
        result = table.show_tokenize_effect(text="hello world", tokenizer="jieba")

        assert result == ["hello", "world"]
        mock_connection.fetchone.assert_called_once()

    def test_show_tokenize_effect_with_column(self):
        """Test show_tokenize_effect with column."""
        mock_connection = Mock(spec=HoloConnect)
        mock_connection.fetchone.return_value = (["test", "content"],)

        table = HoloTable(mock_connection, "test_table")
        result = table.show_tokenize_effect(column="content", tokenizer="jieba")

        assert result == ["test", "content"]
        mock_connection.fetchone.assert_called_once()

    def test_show_tokenize_effect_no_result(self):
        """Test show_tokenize_effect with no result."""
        mock_connection = Mock(spec=HoloConnect)
        mock_connection.fetchone.return_value = None

        table = HoloTable(mock_connection, "test_table")
        result = table.show_tokenize_effect(text="hello", tokenizer="jieba")

        assert result is None

    @patch("holo_search_sdk.backend.table.QueryBuilder")
    def test_search_text_return_score_only(self, mock_query_builder_class):
        """Test search_text returning score only."""
        mock_connection = Mock(spec=HoloConnect)
        mock_query_builder = Mock(spec=QueryBuilder)
        mock_query_builder.select.return_value = mock_query_builder
        mock_query_builder.where.return_value = mock_query_builder
        mock_query_builder_class.return_value = mock_query_builder

        table = HoloTable(mock_connection, "test_table")
        result = table.search_text(
            "content", "search term", return_score=True, return_all_columns=False
        )

        assert result is mock_query_builder
        mock_query_builder.select.assert_called_once()
        mock_query_builder.where.assert_called_once()

    @patch("holo_search_sdk.backend.table.QueryBuilder")
    def test_search_text_return_all_columns(self, mock_query_builder_class):
        """Test search_text returning all columns."""
        mock_connection = Mock(spec=HoloConnect)
        mock_query_builder = Mock(spec=QueryBuilder)
        mock_query_builder.select.return_value = mock_query_builder
        mock_query_builder.where.return_value = mock_query_builder
        mock_query_builder_class.return_value = mock_query_builder

        table = HoloTable(mock_connection, "test_table")
        result = table.search_text(
            "content", "search term", return_all_columns=True, return_score=False
        )

        assert result is mock_query_builder
        mock_query_builder.select.assert_called_once_with("*")
        mock_query_builder.where.assert_called_once()

    @patch("holo_search_sdk.backend.table.QueryBuilder")
    def test_search_text_with_options(self, mock_query_builder_class):
        """Test search_text with various options."""
        mock_connection = Mock(spec=HoloConnect)
        mock_query_builder = Mock(spec=QueryBuilder)
        mock_query_builder.select.return_value = mock_query_builder
        mock_query_builder.where.return_value = mock_query_builder
        mock_query_builder_class.return_value = mock_query_builder

        from collections import OrderedDict

        filter_params = OrderedDict()
        filter_params["lowercase"] = True

        table = HoloTable(mock_connection, "test_table")
        result = table.search_text(
            "content",
            "search term",
            min_threshold=0.5,
            mode="match",
            operator="AND",
            tokenizer="jieba",
            tokenizer_params={"max_token_length": 100},
            filter_params=filter_params,
            slop=2,
        )

        assert result is mock_query_builder
        mock_query_builder.where.assert_called_once()
