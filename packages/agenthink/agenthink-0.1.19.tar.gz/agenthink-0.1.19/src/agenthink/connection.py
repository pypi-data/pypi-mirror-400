# ...existing code...
import json
from fastapi import FastAPI
from pydantic import BaseModel
import mysql.connector
from fastapi import APIRouter
import mysql.connector
from azure.identity import ClientSecretCredential
from azure.keyvault.secrets import SecretClient
from mysql.connector import pooling
import json
from azure.storage.blob import BlobServiceClient
from azure.storage.blob import BlobPrefix
import pyodbc
import agenthink.utils as utils
import os
import json
import dotenv
import logging
import re
dotenv.load_dotenv()

logger = logging.getLogger(__name__)
logger.addHandler(logging.NullHandler())



class DBConnector:
    _class_cache = {}   # session_id -> instance

    def __init__(self, session_id: str, user_id: str, workflow_id: str):
        self.session_id = session_id
        self._workflow_id = workflow_id.upper()
        self._user_id = user_id.lower()
        self.connection_object_dict = {}

        self.__account_name = os.getenv("AZURE_STORAGE_DATASETS_ACCOUNT_NAME")
        self.__account_key = os.getenv("AZURE_STORAGE_DATASETS_ACCOUNT_KEY")
        self.__container_name = os.getenv("AZURE_STORAGE_DATASETS_CONTAINER_NAME")
        blob_path =  f"{self._workflow_id}/{self._user_id}/datastores_output.json"
        data = None


        connection_str = (
            f"DefaultEndpointsProtocol=https;"
            f"AccountName={self.__account_name};"
            f"AccountKey={self.__account_key};"
            f"EndpointSuffix=core.windows.net"
        )

        logger.debug("DEBUG TEST: debug level log")
        logger.info("INFO TEST: info level log")
        logger.warning("WARNING TEST: warning level log")
        logger.error("ERROR TEST: error level log")


        try:
            blob_service = BlobServiceClient.from_connection_string(connection_str)
            self.__container_client = blob_service.get_container_client(self.__container_name)
            blob_client = self.__container_client.get_blob_client(blob_path)
            data = blob_client.download_blob().readall()
        except Exception as e:
            logger.exception("Failed to initialize BlobServiceClient or container client: %s", e)
            container_client = None

        try:
            # Fallback: if 'data' not present, log and set json_data to empty list
            if data:
                self.json_data = json.loads(data.decode("utf-8"))
            else:
                self.json_data = []
            self.no_of_datastores = len(self.json_data)
            secret_names = [entry["key"] for entry in self.json_data]
        except Exception as e:
            logger.exception("Failed to parse datastores JSON: %s", e)
            self.json_data = []
            self.no_of_datastores = 0
            secret_names = []

        self.__client_id = os.getenv("CLIENT_ID")
        self.__tenant_id = os.getenv("TENANT_ID")
        self.__client_secret = os.getenv("CLIENT_SECRET")
        self.__vault_url = os.getenv("VAULT_URL")

        for dict_creds in self.json_data:
            try:
                cleaned_key = self.__sanitize_secret_name(dict_creds["key"])
                datastore_type = dict_creds.get("datastore_type")
                name = dict_creds.get("name")
                logger.debug("Processing datastore: name=%s, key=%s, type=%s",
                             name, dict_creds.get("key"), datastore_type)
            except Exception as e:
                logger.exception("Malformed datastore entry: %s", e)
                continue

            try:
                credential = ClientSecretCredential(
                    tenant_id=self.__tenant_id,
                    client_id=self.__client_id,
                    client_secret=self.__client_secret
                )

                client = SecretClient(vault_url=self.__vault_url, credential=credential)
                secret_value = client.get_secret(cleaned_key)
                secret = json.loads(secret_value.value)
            except Exception as e:
                logger.exception("Failed to fetch or parse secret for key '%s': %s", cleaned_key, e)
                continue

            # MySQL connection
            if datastore_type == "mysql":
                try:
                    connection_object = self.__connect_mysql(secret)
                    if connection_object:
                        db_name = secret.get("database_name", "unknown")
                        connection_dict = {"database_type": "mysql", "connection_object": connection_object}
                        self.connection_object_dict[f"{db_name}"] = connection_dict
                        logger.info("Added MySQL connection for database '%s' to connection_object_dict", db_name)
                except Exception as e:
                    logger.exception("Unable to create connection object for MySQL secret: %s", e)

            # MS SQL connection
            elif datastore_type == "mssql":
                try:
                    connection_object = self.__connect_mssql(secret)
                    if connection_object:
                        db_name = secret.get("database_name", "unknown")
                        connection_dict = {"database_type": "mssql", "connection_object": connection_object}
                        self.connection_object_dict[f"{db_name}"] = connection_dict
                        logger.info("Added MSSQL connection for database '%s' to connection_object_dict", db_name)
                except Exception as e:
                    logger.exception("Unable to create connection object for MSSQL secret: %s", e)
            else:
                logger.warning("Unsupported datastore_type '%s' for key '%s'", datastore_type, cleaned_key)

    # ---- class method to create instance ----
    @classmethod
    def get(cls, session_id: str, user_id: str, workflow_id: str):
        if session_id not in cls._class_cache:
            logger.debug("Creating new DBConnector instance for session_id=%s", session_id)
            cls._class_cache[session_id] = DBConnector(session_id, user_id, workflow_id)
        else:
            logger.debug("Returning cached DBConnector instance for session_id=%s", session_id)
        return cls._class_cache[session_id]

    def __connect_mysql(self, secret):
        config = {
            "host": secret.get("cluster_ip"),
            "port": secret.get("port"),
            "user": secret.get("username"),
            "password": secret.get("password"),
            "database": secret.get("database_name")
        }

        try:
            conn = mysql.connector.connect(**config)
            logger.info("MySQL connection successfully established to database '%s' on host '%s'",
                        config["database"], config["host"])
            return conn
        except Exception as e:
            logger.exception("MySQL connection failed: %s", e)
            return None

    def __connect_mssql(self, secret):
        # Use single quotes inside f-strings to avoid syntax errors
        connection_string = (
            f"mssql+pyodbc://{secret.get('username')}:{secret.get('password')}@{secret.get('cluster_ip')}:{secret.get('port')}/{secret.get('database_name')}"
            "?driver=ODBC+Driver+17+for+SQL+Server&Encrypt=no"
        )
        logger.debug("Trying MSSQL connection for host=%s port=%s user=%s db=%s",
                     secret.get("cluster_ip"), secret.get("port"), secret.get("username"), secret.get("database_name"))
        try:
            conn = pyodbc.connect(connection_string)
            cursor = conn.cursor()
            # Fetch a row only if we can; wrap safely:
            try:
                row = cursor.fetchone()
                if row:
                    logger.info("Connected to MSSQL. Sample row/first column: %s", row[0])
                else:
                    logger.info("Connected to MSSQL. No rows returned by initial fetch.")
            except Exception:
                logger.debug("No initial row fetch possible or returned no results.")
            return conn
        except Exception as e:
            logger.exception("MS SQL Connection failed: %s", e)
            return None

    def __sanitize_secret_name(self, secret_name: str) -> str:
        """
        Convert secret name to a valid Azure Key Vault format:
        - Replaces spaces and underscores with hyphens
        - Removes any characters not allowed in Key Vault secret names
        """
        logger.debug("Sanitizing secret name: %s", secret_name)
        # Replace spaces and underscores with hyphens
        sanitized = re.sub(r"[ _]+", "-", secret_name)

        # Remove any characters that are not letters, numbers, or hyphens
        sanitized = re.sub(r"[^a-zA-Z0-9\-]", "", sanitized)

        logger.debug("Sanitized secret name: %s -> %s", secret_name, sanitized)
        return sanitized

    def display_connections(self):
        """
        Display the current connection objects for debugging purposes.
        """
        if len(self.connection_object_dict) == 0:
            logger.info("No connection objects available.")
            return "No connection objects available."
        for db_name, conn in self.connection_object_dict.items():
            logger.info("Database: %s, Connection Object: %s", db_name, conn)
            return f"Database: {db_name}, Connection Object: {conn}"

    def execute_query(self, db_name: str, query: str):

        """
        Execute a read-only SQL query on a MySQL or MSSQL database.

        Parameters
        ----------
        db_name : str
            Name of the database connection.
        query : str
            Read-only SQL query to execute (SELECT / WITH / SHOW / DESCRIBE / EXPLAIN).

        Returns
        -------
        Any or None
            Query results if successful, otherwise None.

        Notes
        -----
        - Only read-only queries are allowed and enforced by prefix checks.
        - Write or mutating queries are blocked.
        - Errors are logged and cursors are safely closed.
        - Behavior may differ slightly between MySQL and MSSQL drivers.
        """

        if db_name not in self.connection_object_dict:
            logger.error("No connection found for database: %s", db_name)
            return None
        
        database_dict = self.connection_object_dict[db_name]
        database_type = database_dict.get("database_type")
        database_connection = database_dict.get("connection_object")

        if not database_type or not database_connection:
            logger.error("Invalid database entry for '%s'", db_name)
            return None
    
        READ_ONLY_PREFIXES = (
            "select",
            "with",
            "show",
            "describe",
            "desc",
            "explain"
        )
        q = query.strip().lower()
        if not q.startswith(READ_ONLY_PREFIXES):
            return None

        if database_type == "mysql":
            try:
                cursor = database_connection.cursor()
                cursor.execute(query)
                results = cursor.fetchall()
                logger.info("Executed query on MySQL database '%s': %s", db_name, query)
                return f"{results}"
            except Exception as e:
                logger.exception("Failed to execute query on MySQL database '%s': %s", db_name, e)
                return None
            finally:
                if cursor:
                    cursor.close()
        elif database_type == "mssql":
            try:
                cursor = database_connection.cursor()
                cursor.execute(query)
                results = cursor.fetchall()
                logger.info("Executed query on MSSQL database '%s': %s", db_name, query)
                return results
            except Exception as e:
                logger.exception("Failed to execute query on MSSQL database '%s': %s", db_name, e)
                return "Inside the exception of MSSQL"
            
            finally:
                if cursor:
                    cursor.close()
            
        else:
            logger.error("Unsupported database type '%s' for database '%s'", database_type, db_name)
            return None
        
    def display_tables(self,db_name:str):
        """
        Retrieve a list of user tables from a MySQL or MSSQL database.

        Parameters
        ----------
        db_name : str
            Name of the database connection.

        Returns
        -------
        list[str] or None
            List of table names if successful, otherwise None.

        Notes
        -----
        - Uses `SHOW TABLES` for MySQL.
        - Uses `INFORMATION_SCHEMA.TABLES` for MSSQL.
        - Errors are logged and not raised.
        """
        database_dict = self.connection_object_dict[db_name]
        database_type = database_dict.get("database_type")
        database_connection = database_dict.get("connection_object")
        if database_type == "mysql":
            try:
                cursor = database_connection.cursor()
                cursor.execute("SHOW TABLES")
                tables = cursor.fetchall()
                table_list = [table[0] for table in tables]
                return table_list
            except Exception as e:
                logger.exception("Failed to retrieve tables from MySQL database '%s': %s", db_name, e)
                return None
            
        if database_type == "mssql":
            try:
                cursor = database_connection.cursor()
                cursor.execute("SELECT TABLE_NAME FROM INFORMATION_SCHEMA.TABLES WHERE TABLE_TYPE = 'BASE TABLE'")
                tables = cursor.fetchall()
                table_list = [table[0] for table in tables]
                return table_list
            except Exception as e:
                logger.exception("Failed to retrieve tables from MSSQL database '%s': %s", db_name, e)
                return None
            

    def insert_data(self,db_name:str,table_name:str,data:dict):
        """
        Insert a single row into a MySQL or MSSQL table.

        Parameters
        ----------
        db_name : str
            Name of the database connection.
        table_name : str
            Target table name (must be trusted).
        data : dict
            Column-to-value mapping for the row to insert.

        Notes
        -----
        - Uses `%s` placeholders for MySQL and `?` for MSSQL.
        - Commits the transaction on success and logs the result.
        - Table and column names are not parameterized and must be validated.
        """
        database_dict = self.connection_object_dict[db_name]
        database_type = database_dict.get("database_type")
        database_connection = database_dict.get("connection_object")
        columns = ', '.join(data.keys())
        placeholders = ', '.join(['%s'] * len(data))
        values = tuple(data.values())
        if database_type == "mysql":
            try:
                cursor = database_connection.cursor()
                sql = f"INSERT INTO {table_name} ({columns}) VALUES ({placeholders})"
                cursor.execute(sql, values)
                database_connection.commit()
                cursor.close()
                logger.info("Data inserted into MySQL database '%s', table '%s'", db_name, table_name)
            except Exception as e:
                logger.exception("Failed to insert data into MySQL database '%s', table '%s': %s", db_name, table_name, e)
        if database_type == "mssql":
            try:
                cursor = database_connection.cursor()
                columns_sql = ", ".join(f"[{c}]" for c in data.keys())
                placeholders = ", ".join("?" for _ in data)
                values = tuple(data.values())

                sql = f"INSERT INTO [{table_name}] ({columns_sql}) VALUES ({placeholders})"

                cursor.execute(sql, values)
                database_connection.commit()

                logger.info(
                    "Data inserted into MSSQL database '%s', table '%s'",
                    db_name,
                    table_name
                )
                cursor.close()
            except Exception as e:
                logger.exception("Insert failed for %s database '%s', table '%s'", database_type, db_name, table_name)

    def _debugging_function(self):
            prefix = f"{self._workflow_id}/{self._user_id}/"
            all_blob_list = self.__container_client.list_blobs(name_starts_with=prefix)
            output_message = f"""Debugging function executed. Current connections:\n
            self.__account_name = {self.__account_name}\n
            self.__account_key = {self.__account_key}\n
            self.__container_name = {self.__container_name}\n
            self.session_id = {self.session_id}\n
            self._workflow_id = {self._workflow_id}\n
            self._user_id = {self._user_id}\n
            All blobs with prefix {prefix}:\n
            {[blob.name for blob in all_blob_list]}\n
            Json data: {self.json_data}\n
            Number of datastores: {self.no_of_datastores}\n
            Current connection_object_dict: {self.connection_object_dict}\n
            """
            return output_message