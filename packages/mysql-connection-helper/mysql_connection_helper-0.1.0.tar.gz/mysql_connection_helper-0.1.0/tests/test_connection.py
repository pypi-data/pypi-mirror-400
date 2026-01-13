import pytest
from unittest.mock import patch, MagicMock
from mysql_connectivity.mysql_helper import get_connection
from mysql.connector import Error

@patch("mysql_connectivity.mysql_helper.mysql.connector.connect")
def test_get_connection_success(mock_connect):
    mock_conn = MagicMock()
    mock_conn.is_connected.return_value = True
    mock_connect.return_value = mock_conn

    conn = get_connection(
        host="localhost",
        user="root",
        password="password",
        database="test_db"
    )

    assert conn.is_connected() is True

@patch("mysql_connectivity.mysql_helper.mysql.connector.connect")
def test_get_connection_failure(mock_connect):
    mock_connect.side_effect = Error("Connection failed")

    with pytest.raises(Error):
        get_connection(
            host="localhost",
            user="root",
            password="wrong",
            database="test_db"
        )
