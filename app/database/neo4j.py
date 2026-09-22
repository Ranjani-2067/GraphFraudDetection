from __future__ import annotations
import logging
from typing import Any, Optional
from neo4j import GraphDatabase, Driver
from neo4j.exceptions import ServiceUnavailable, AuthError, Neo4jError
from app.config import settings

logger = logging.getLogger(__name__)

class Neo4jUnavailableError(RuntimeError):
    pass

class Neo4jQueryError(RuntimeError):
    pass

class Neo4jConnection:
    def __init__(self, uri=None, user=None, password=None, database=None):
        self._uri = uri or settings.neo4j_uri
        self._user = user or settings.neo4j_user
        self._password = password or settings.neo4j_password
        self._database = database or settings.neo4j_database
        self._driver: Optional[Driver] = None

    def _ensure_driver(self) -> Driver:
        if self._driver is None:
            try:
                self._driver = GraphDatabase.driver(self._uri, auth=(self._user, self._password))
            except Exception as exc:
                raise Neo4jUnavailableError(f"Could not create Neo4j driver for {self._uri}: {exc}") from exc
        return self._driver

    def verify_connectivity(self) -> bool:
        try:
            self._ensure_driver().verify_connectivity()
            return True
        except (ServiceUnavailable, AuthError, Neo4jUnavailableError, OSError) as exc:
            logger.warning("Neo4j connectivity check failed: %s", exc)
            return False

    def run_query(self, cypher: str, parameters: Optional[dict[str, Any]] = None) -> list[dict[str, Any]]:
        driver = self._ensure_driver()
        try:
            with driver.session(database=self._database) as session:
                result = session.run(cypher, parameters or {})
                return [_record_to_dict(record) for record in result]
        except (ServiceUnavailable, OSError) as exc:
            raise Neo4jUnavailableError(f"Neo4j is unreachable: {exc}") from exc
        except Neo4jError as exc:
            raise Neo4jQueryError(f"Cypher query failed: {exc}") from exc

    def run_write(self, cypher: str, parameters: Optional[dict[str, Any]] = None) -> list[dict[str, Any]]:
        return self.run_query(cypher, parameters)

    def close(self) -> None:
        if self._driver is not None:
            self._driver.close()
            self._driver = None

def _record_to_dict(record) -> dict[str, Any]:
    return {key: _convert_value(value) for key, value in record.items()}

def _convert_value(value: Any) -> Any:
    if hasattr(value, "items") and hasattr(value, "labels"):
        return {**dict(value.items()), "_labels": list(value.labels)}
    if hasattr(value, "items") and hasattr(value, "type") and hasattr(value, "start_node"):
        return {**dict(value.items()), "_type": value.type}
    if isinstance(value, list):
        return [_convert_value(v) for v in value]
    if isinstance(value, dict):
        return {k: _convert_value(v) for k, v in value.items()}
    if hasattr(value, "iso_format"):
        try:
            return value.iso_format()
        except Exception:
            return str(value)
    return value

_connection: Optional[Neo4jConnection] = None

def get_connection() -> Neo4jConnection:
    global _connection
    if _connection is None:
        _connection = Neo4jConnection()
    return _connection
