import mysql.connector
from mysql.connector import Error

def get_connection(host, user, password, database, port=3306):
    """
    Create and return a MySQL database connection.

    :param host: MySQL host
    :param user: MySQL username
    :param password: MySQL password
    :param database: Database name
    :param port: MySQL port (default: 3306)
    :return: MySQL connection object
    :raises: mysql.connector.Error
    """
    try:
        conn = mysql.connector.connect(
            host=host,
            user=user,
            password=password,
            database=database,
            port=port
        )

        if conn.is_connected():
            return conn

    except Error as e:
        raise Error(f"MySQL connection failed: {e}")
