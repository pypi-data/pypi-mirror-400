from typing import Dict, List, Any, Optional
from contextlib import contextmanager
from urllib.parse import quote_plus

from loguru import logger
from sqlalchemy import create_engine, text, MetaData
from sqlalchemy.engine import Engine, Connection, Result
from sqlalchemy.orm import sessionmaker, Session


class SQLServerClient:
    def __init__(
            self,
            server: str,
            database: str,
            username: Optional[str] = None,
            password: Optional[str] = None,
            driver: str = "ODBC Driver 17 for SQL Server",
            trusted_connection: bool = False,
            echo: bool = False,
            mars_connection: bool = True
    ):

        self.server = server
        self.database = database
        self.username = username
        self.password = password
        self.driver = driver
        self.trusted_connection = trusted_connection
        self.echo = echo
        self.mars_connection = mars_connection
        self.engine = self._create_engine()
        self.metadata = MetaData()
        self.Session = sessionmaker(bind=self.engine)

    def _create_engine(self) -> Engine:
        connection_string = self._build_connection_string()
        return create_engine(connection_string, echo=self.echo)

    def _build_connection_string(self) -> str:
        params = {
            "driver": self.driver,
            "server": self.server,
            "database": self.database,
        }

        if self.trusted_connection:
            params["trusted_connection"] = "yes"
        else:
            params["uid"] = self.username
            params["pwd"] = self.password
        if self.mars_connection:
            params["Mars_Connection"] = "yes"
        params["TrustServerCertificate"] = "yes"
        params["MultipleActiveResultSets"] = "True" if self.mars_connection else "False"
        params["Connection Timeout"] = "30"
        params["Command Timeout"] = "30"
        connection_string_parts = []
        for key, value in params.items():
            if value is not None:
                connection_string_parts.append(f"{key}={quote_plus(str(value))}")

        connection_string = ";".join(connection_string_parts)
        return f"mssql+pyodbc:///?odbc_connect={quote_plus(connection_string)}"

    @contextmanager
    def get_connection(self) -> Connection:
        connection = self.engine.connect()
        try:
            yield connection
        finally:
            connection.close()

    @contextmanager
    def get_session(self) -> Session:
        session = self.Session()
        try:
            yield session
            session.commit()
        except:
            session.rollback()
            raise
        finally:
            session.close()

    def execute_query(self, query: str, params: Optional[Dict[str, Any]] = None) -> Result:
        with self.get_session() as session:
            result = session.execute(text(query), params or {})
            return result

    def get_all(self, query: str, params: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
        """
        :rtype: object
        """
        with self.get_session() as session:
            result = session.execute(text(query), params or {})
            rows = result.fetchall()
            return [dict(row._mapping) for row in rows]

    def get_mappings(self, query: str, params: Optional[Dict[str, Any]] = None, source_system: Optional[str] = None,
                     mapping_type: Optional[str] = None) -> List[Dict[str, Any]]:
        if source_system is not None:
            logger.warning("Source System not implemented")
        if mapping_type is not None:
            logger.warning("Mapping Type not implemented")
        return self.get_all(query, params or {})
