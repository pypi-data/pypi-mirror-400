"""
Tests for HoloConnect class in Holo Search SDK.

This module contains comprehensive tests for connection functionality.
"""

from unittest.mock import Mock, patch

import pytest

from holo_search_sdk.backend.connection import HoloConnect
from holo_search_sdk.exceptions import ConnectionError, QueryError


class TestHoloConnect:
    """Test cases for the HoloConnect class."""

    def test_holo_connect_initialization(self, sample_connection_config):
        """Test HoloConnect initialization."""
        conn = HoloConnect(sample_connection_config)

        assert conn._connection is None
        assert conn._config == sample_connection_config

    def test_get_config(self, sample_connection_config):
        """Test get_config method."""
        conn = HoloConnect(sample_connection_config)

        config = conn.get_config()

        assert config == sample_connection_config

    @patch("holo_search_sdk.backend.connection.psycopg.connect")
    def test_connect_success(self, mock_psycopg_connect, sample_connection_config):
        """Test successful connection."""
        mock_connection = Mock()
        mock_psycopg_connect.return_value = mock_connection

        conn = HoloConnect(sample_connection_config)
        result = conn.connect()

        assert result is conn
        assert conn._connection is mock_connection
        mock_psycopg_connect.assert_called_once()

    @patch("holo_search_sdk.backend.connection.psycopg.connect")
    def test_connect_failure(self, mock_psycopg_connect, sample_connection_config):
        """Test connection failure."""
        mock_psycopg_connect.side_effect = Exception("Connection failed")

        conn = HoloConnect(sample_connection_config)

        with pytest.raises(ConnectionError) as exc_info:
            conn.connect()

        assert "Failed to connect to Hologres database" in str(exc_info.value)

    def test_close(self, sample_connection_config):
        """Test close method."""
        mock_connection = Mock()
        conn = HoloConnect(sample_connection_config)
        conn._connection = mock_connection

        conn.close()

        mock_connection.close.assert_called_once()
        assert conn._connection is None

    def test_close_without_connection(self, sample_connection_config):
        """Test close method without active connection."""
        conn = HoloConnect(sample_connection_config)
        conn._connection = None

        # Should not raise any error
        conn.close()

        assert conn._connection is None

    def test_execute_without_connection(self, sample_connection_config):
        """Test execute without connection raises error."""
        conn = HoloConnect(sample_connection_config)

        with pytest.raises(ConnectionError) as exc_info:
            conn.execute("SELECT 1")

        assert "Connection not established" in str(exc_info.value)

    def test_execute_with_transaction(self, sample_connection_config):
        """Test execute with transaction."""
        mock_connection = Mock()
        mock_cursor = Mock()
        mock_connection.cursor.return_value = mock_cursor
        mock_connection.autocommit = False

        conn = HoloConnect(sample_connection_config)
        conn._connection = mock_connection

        conn.execute("INSERT INTO test VALUES (1)", use_transaction=True)

        mock_connection.cursor.assert_called()
        mock_cursor.execute.assert_called_once()
        mock_connection.commit.assert_called_once()
        mock_cursor.close.assert_called_once()

    def test_execute_without_transaction(self, sample_connection_config):
        """Test execute without transaction."""
        mock_connection = Mock()
        mock_cursor = Mock()
        mock_connection.cursor.return_value = mock_cursor
        mock_connection.autocommit = True

        conn = HoloConnect(sample_connection_config)
        conn._connection = mock_connection

        conn.execute("INSERT INTO test VALUES (1)", use_transaction=False)

        mock_connection.cursor.assert_called()
        mock_cursor.execute.assert_called_once()
        mock_cursor.close.assert_called_once()

    def test_execute_with_params(self, sample_connection_config):
        """Test execute with parameters."""
        mock_connection = Mock()
        mock_cursor = Mock()
        mock_connection.cursor.return_value = mock_cursor
        mock_connection.autocommit = False

        conn = HoloConnect(sample_connection_config)
        conn._connection = mock_connection

        params = (1, "test")
        conn.execute("INSERT INTO test VALUES (%s, %s)", params, use_transaction=True)

        mock_cursor.execute.assert_called_once()
        call_args = mock_cursor.execute.call_args
        assert call_args[0][1] == params

    def test_execute_query_error(self, sample_connection_config):
        """Test execute with query error."""
        mock_connection = Mock()
        mock_cursor = Mock()
        mock_cursor.execute.side_effect = Exception("Query error")
        mock_connection.cursor.return_value = mock_cursor
        mock_connection.autocommit = False

        conn = HoloConnect(sample_connection_config)
        conn._connection = mock_connection

        with pytest.raises(QueryError) as exc_info:
            conn.execute("INVALID SQL", use_transaction=True)

        assert "Error executing SQL query" in str(exc_info.value)
        mock_cursor.close.assert_called_once()

    def test_fetchone_without_connection(self, sample_connection_config):
        """Test fetchone without connection raises error."""
        conn = HoloConnect(sample_connection_config)

        with pytest.raises(ConnectionError) as exc_info:
            conn.fetchone("SELECT 1")

        assert "Connection not established" in str(exc_info.value)

    def test_fetchone_success(self, sample_connection_config):
        """Test fetchone returns result."""
        mock_connection = Mock()
        mock_cursor = Mock()
        mock_cursor.fetchone.return_value = (1, "test")
        mock_connection.cursor.return_value = mock_cursor
        mock_connection.autocommit = True

        conn = HoloConnect(sample_connection_config)
        conn._connection = mock_connection

        result = conn.fetchone("SELECT * FROM test WHERE id = 1")

        assert result == (1, "test")
        mock_cursor.execute.assert_called_once()
        mock_cursor.fetchone.assert_called_once()
        mock_cursor.close.assert_called_once()

    def test_fetchone_with_commit(self, sample_connection_config):
        """Test fetchone with commit when autocommit is False."""
        mock_connection = Mock()
        mock_cursor = Mock()
        mock_cursor.fetchone.return_value = (1, "test")
        mock_connection.cursor.return_value = mock_cursor
        mock_connection.autocommit = False

        conn = HoloConnect(sample_connection_config)
        conn._connection = mock_connection

        result = conn.fetchone("SELECT * FROM test WHERE id = 1")

        assert result == (1, "test")
        mock_connection.commit.assert_called_once()

    def test_fetchone_query_error(self, sample_connection_config):
        """Test fetchone with query error."""
        mock_connection = Mock()
        mock_cursor = Mock()
        mock_cursor.execute.side_effect = Exception("Query error")
        mock_connection.cursor.return_value = mock_cursor

        conn = HoloConnect(sample_connection_config)
        conn._connection = mock_connection

        with pytest.raises(QueryError) as exc_info:
            conn.fetchone("INVALID SQL")

        assert "Error executing SQL query" in str(exc_info.value)
        mock_cursor.close.assert_called_once()

    def test_fetchall_without_connection(self, sample_connection_config):
        """Test fetchall without connection raises error."""
        conn = HoloConnect(sample_connection_config)

        with pytest.raises(ConnectionError) as exc_info:
            conn.fetchall("SELECT * FROM test")

        assert "Connection not established" in str(exc_info.value)

    def test_fetchall_success(self, sample_connection_config):
        """Test fetchall returns results."""
        mock_connection = Mock()
        mock_cursor = Mock()
        mock_cursor.fetchall.return_value = [(1, "test1"), (2, "test2")]
        mock_connection.cursor.return_value = mock_cursor
        mock_connection.autocommit = True

        conn = HoloConnect(sample_connection_config)
        conn._connection = mock_connection

        result = conn.fetchall("SELECT * FROM test")

        assert result == [(1, "test1"), (2, "test2")]
        mock_cursor.execute.assert_called_once()
        mock_cursor.fetchall.assert_called_once()
        mock_cursor.close.assert_called_once()

    def test_fetchall_with_commit(self, sample_connection_config):
        """Test fetchall with commit when autocommit is False."""
        mock_connection = Mock()
        mock_cursor = Mock()
        mock_cursor.fetchall.return_value = [(1, "test")]
        mock_connection.cursor.return_value = mock_cursor
        mock_connection.autocommit = False

        conn = HoloConnect(sample_connection_config)
        conn._connection = mock_connection

        result = conn.fetchall("SELECT * FROM test")

        assert result == [(1, "test")]
        mock_connection.commit.assert_called_once()

    def test_fetchall_query_error(self, sample_connection_config):
        """Test fetchall with query error."""
        mock_connection = Mock()
        mock_cursor = Mock()
        mock_cursor.execute.side_effect = Exception("Query error")
        mock_connection.cursor.return_value = mock_cursor

        conn = HoloConnect(sample_connection_config)
        conn._connection = mock_connection

        with pytest.raises(QueryError) as exc_info:
            conn.fetchall("INVALID SQL")

        assert "Error executing SQL query" in str(exc_info.value)
        mock_cursor.close.assert_called_once()

    def test_fetchmany_without_connection(self, sample_connection_config):
        """Test fetchmany without connection raises error."""
        conn = HoloConnect(sample_connection_config)

        with pytest.raises(ConnectionError) as exc_info:
            conn.fetchmany("SELECT * FROM test", size=5)

        assert "Connection not established" in str(exc_info.value)

    def test_fetchmany_success(self, sample_connection_config):
        """Test fetchmany returns results."""
        mock_connection = Mock()
        mock_cursor = Mock()
        mock_cursor.fetchmany.return_value = [(1, "test1"), (2, "test2")]
        mock_connection.cursor.return_value = mock_cursor
        mock_connection.autocommit = True

        conn = HoloConnect(sample_connection_config)
        conn._connection = mock_connection

        result = conn.fetchmany("SELECT * FROM test", size=2)

        assert result == [(1, "test1"), (2, "test2")]
        mock_cursor.execute.assert_called_once()
        mock_cursor.fetchmany.assert_called_once_with(2)
        mock_cursor.close.assert_called_once()

    def test_fetchmany_with_commit(self, sample_connection_config):
        """Test fetchmany with commit when autocommit is False."""
        mock_connection = Mock()
        mock_cursor = Mock()
        mock_cursor.fetchmany.return_value = [(1, "test")]
        mock_connection.cursor.return_value = mock_cursor
        mock_connection.autocommit = False

        conn = HoloConnect(sample_connection_config)
        conn._connection = mock_connection

        result = conn.fetchmany("SELECT * FROM test", size=1)

        assert result == [(1, "test")]
        mock_connection.commit.assert_called_once()

    def test_fetchmany_query_error(self, sample_connection_config):
        """Test fetchmany with query error."""
        mock_connection = Mock()
        mock_cursor = Mock()
        mock_cursor.execute.side_effect = Exception("Query error")
        mock_connection.cursor.return_value = mock_cursor

        conn = HoloConnect(sample_connection_config)
        conn._connection = mock_connection

        with pytest.raises(QueryError) as exc_info:
            conn.fetchmany("INVALID SQL", size=5)

        assert "Error executing SQL query" in str(exc_info.value)
        mock_cursor.close.assert_called_once()

    @patch("holo_search_sdk.backend.connection.psycopg.connect")
    def test_context_manager_enter(
        self, mock_psycopg_connect, sample_connection_config
    ):
        """Test context manager __enter__ method."""
        mock_connection = Mock()
        mock_psycopg_connect.return_value = mock_connection

        conn = HoloConnect(sample_connection_config)

        with conn as c:
            assert c is conn
            assert conn._connection is mock_connection

    def test_context_manager_exit(self, sample_connection_config):
        """Test context manager __exit__ method."""
        mock_connection = Mock()
        conn = HoloConnect(sample_connection_config)
        conn._connection = mock_connection

        with conn:
            pass

        mock_connection.close.assert_called_once()
        assert conn._connection is None

    @patch("holo_search_sdk.backend.connection.psycopg.connect")
    def test_context_manager_full_flow(
        self, mock_psycopg_connect, sample_connection_config
    ):
        """Test full context manager flow."""
        mock_connection = Mock()
        mock_cursor = Mock()
        mock_cursor.fetchone.return_value = (1,)
        mock_connection.cursor.return_value = mock_cursor
        mock_connection.autocommit = True
        mock_psycopg_connect.return_value = mock_connection

        conn = HoloConnect(sample_connection_config)

        with conn as c:
            result = c.fetchone("SELECT 1")
            assert result == (1,)

        mock_connection.close.assert_called_once()
