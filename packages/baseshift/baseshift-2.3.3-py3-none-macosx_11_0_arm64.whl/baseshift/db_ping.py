"""
Database connectivity validation module.

Provides ping functionality for PostgreSQL, MySQL, and MongoDB connections
to validate that a clone is accessible after starting.
"""

import logging
import time
import psycopg
import pymysql
from pymongo import MongoClient
from pymongo.errors import ConnectionFailure

from urllib.parse import urlparse

logger = logging.getLogger(__name__)


def ping_database(
    connection_string: str,
    db_type: str = "postgres",
    timeout: int = 10,
    max_retries: int = 5,
) -> tuple[bool, str]:
    """
    Ping a database to verify connectivity with retries.

    Args:
        connection_string: Database connection string (DSN or URI format)
        db_type: Type of database ("postgres", "mysql", "mongodb")
        timeout: Connection timeout in seconds
        max_retries: Maximum number of retry attempts (default: 5)

    Returns:
        Tuple of (success: bool, message: str)
    """
    last_error = None

    for attempt in range(max_retries):
        try:
            if db_type == "postgres":
                success, message = _ping_postgres(connection_string, timeout)
            elif db_type == "mysql":
                success, message = _ping_mysql(connection_string, timeout)
            elif db_type == "mongodb":
                success, message = _ping_mongodb(connection_string, timeout)
            else:
                return False, f"Unsupported database type: {db_type}"

            if success:
                return True, message

            last_error = message
        except Exception as e:
            last_error = f"Database ping failed: {str(e)}"
            logger.debug(
                f"Attempt {attempt + 1}/{max_retries} failed for {db_type} database: {last_error}"
            )

        # Sleep before next retry (except on last attempt)
        if attempt < max_retries - 1:
            time.sleep(1)

    # All retries failed
    return False, last_error if last_error else "Database ping failed after all retries"


def _ping_postgres(connection_string: str, timeout: int) -> tuple[bool, str]:
    """Ping PostgreSQL database."""
    try:
        # Add connect_timeout if not already present
        if "connect_timeout" not in connection_string:
            if "://" in connection_string:
                # URI format
                separator = "?" if "?" not in connection_string else "&"
                connection_string = (
                    f"{connection_string}{separator}connect_timeout={timeout}"
                )
            else:
                # DSN format
                connection_string = f"{connection_string} connect_timeout={timeout}"

        with psycopg.connect(connection_string) as conn:
            with conn.cursor() as cur:
                cur.execute("SELECT 1")
                result = cur.fetchone()
                if result and result[0] == 1:
                    return True, "PostgreSQL database is accessible"
                else:
                    return (
                        False,
                        "PostgreSQL database responded but SELECT 1 did not return expected result",
                    )
    except ImportError:
        return (
            False,
            "psycopg library not installed. Install with: pip install psycopg[binary]",
        )
    except Exception as e:
        return False, f"PostgreSQL connection failed: {str(e)}"


def _ping_mysql(connection_string: str, timeout: int) -> tuple[bool, str]:
    """Ping MySQL database."""
    try:
        # Parse connection string
        if "://" in connection_string:
            # URI format: mysql://user:password@host:port/database
            parsed = urlparse(connection_string)
            config = {
                "host": parsed.hostname or "localhost",
                "port": parsed.port or 3306,
                "user": parsed.username or "root",
                "password": parsed.password or "",
                "database": parsed.path.lstrip("/") if parsed.path else "",
                "connect_timeout": timeout,
            }
        else:
            # DSN-like format: user:password@tcp(host:port)/database
            import re

            user_match = re.match(r"^([^@:]+)", connection_string)
            password_match = re.search(r":(.*?)(?=@)", connection_string)
            host_match = re.search(r"\(([^:]+)", connection_string)
            port_match = re.search(r":(\d+)(?![^@]*@)", connection_string)
            db_match = re.search(r"/([^/]+)$", connection_string)

            config = {
                "host": host_match.group(1) if host_match else "localhost",
                "port": int(port_match.group(1)) if port_match else 3306,
                "user": user_match.group(1) if user_match else "root",
                "password": password_match.group(1) if password_match else "",
                "database": db_match.group(1) if db_match else "",
                "connect_timeout": timeout,
            }

        conn = pymysql.connect(**config)
        try:
            with conn.cursor() as cur:
                cur.execute("SELECT 1")
                result = cur.fetchone()
                if result and result[0] == 1:
                    return True, "MySQL database is accessible"
                else:
                    return (
                        False,
                        "MySQL database responded but SELECT 1 did not return expected result",
                    )
        finally:
            conn.close()
    except ImportError:
        return False, "pymysql library not installed. Install with: pip install pymysql"
    except Exception as e:
        return False, f"MySQL connection failed: {str(e)}"


def _ping_mongodb(connection_string: str, timeout: int) -> tuple[bool, str]:
    """Ping MongoDB database."""
    try:
        # Add timeout parameter if not present
        if "?" in connection_string:
            if (
                "connectTimeoutMS" not in connection_string
                and "serverSelectionTimeoutMS" not in connection_string
            ):
                connection_string = f"{connection_string}&connectTimeoutMS={timeout*1000}&serverSelectionTimeoutMS={timeout*1000}"
        else:
            connection_string = f"{connection_string}?connectTimeoutMS={timeout*1000}&serverSelectionTimeoutMS={timeout*1000}"

        client = MongoClient(connection_string)
        try:
            # The ping command is a simple way to test connectivity
            client.admin.command("ping")
            return True, "MongoDB database is accessible"
        finally:
            client.close()
    except ImportError:
        return False, "pymongo library not installed. Install with: pip install pymongo"
    except ConnectionFailure as e:
        return False, f"MongoDB connection failed: {str(e)}"
    except Exception as e:
        return False, f"MongoDB ping failed: {str(e)}"
