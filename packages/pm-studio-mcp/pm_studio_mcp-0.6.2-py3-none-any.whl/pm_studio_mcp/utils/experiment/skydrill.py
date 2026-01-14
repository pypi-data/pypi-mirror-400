import logging
import time
from typing import Iterator

import pandas as pd
import requests
from azure.core.credentials import AccessToken
from azure.identity import DefaultAzureCredential
from pandas import DataFrame
from pydantic import BaseModel
from sqlalchemy import create_engine
from sqlalchemy.engine import Engine

logger = logging.getLogger(__name__)


class EngineCache(BaseModel):
    engine: Engine
    expires_on: int

    model_config = {
        "arbitrary_types_allowed": True
    }

    def expired(self):
        one_min_later = time.time() + 60
        return self.expires_on < one_min_later


class SkyDrillConnector:
    def __init__(self):
        self._connection_url = "presto://edgeskydrilladhoc.westus2.cloudapp.azure.com:8443"
        self._skydrill_scope = "api://cd88ffdb-186a-4534-8089-b85c3d839eec/.default"
        self._engines: dict[str, EngineCache] = {}


    def _get_token(self) -> AccessToken:
        try:
            credential = DefaultAzureCredential(exclude_interactive_browser_credential=False)
            return credential.get_token(self._skydrill_scope)

        except Exception as e:
            logger.error(f"exception caught when getting access token, error: {e}")
            raise Exception(e)


    def _get_or_create_engine(
            self,
            catalog: str,
            schema: str):
        engine_key = f"{catalog}/{schema}"

        if engine_key not in self._engines or self._engines[engine_key].expired():
            session = requests.Session()
            access_token = self._get_token()
            session.headers.update({"Authorization": "Bearer " + access_token.token})

            connection_url = f"{self._connection_url}/{catalog}/{schema}"
            engine = create_engine(
                connection_url,
                connect_args={
                    'protocol': 'https',
                    'requests_session': session,
                    'session_props': {'query_max_run_time': '60m'}
                }
            )
            logger.info(f"Created new engine for {catalog}/{schema}")
            self._engines[engine_key] = EngineCache(
                engine=engine,
                expires_on=access_token.expires_on
            )

        return self._engines[engine_key].engine


    def _get_connection(self, catalog: str, schema: str):
        engine = self._get_or_create_engine(catalog, schema)
        connection = engine.connect()

        logger.info(f"get connection from {catalog}/{schema} successfully")
        return connection


    def _close_all_engines(self):
        for engine_key, engine_cache in self._engines.items():
            try:
                engine_cache.engine.dispose()
                logger.info(f"Disposed engine for {engine_key}")
            except Exception as e:
                logger.warning(f"Error disposing engine for {engine_key}: {e}")
        self._engines.clear()
        logger.info("All engines disposed")


    def __del__(self):
        try:
            self._close_all_engines()
        except Exception as e:
            logger.error(f"Exception caught while closing engines: {e}")


    def query(
            self,
            sql: str,
            catalog: str = "anaheim",
            schema: str = "") -> DataFrame | Iterator[DataFrame]:
        """
        Query an SQL query using skydrill engine, which is an adhoc query engine built from Apache Trino
        and return a pandas DataFrame.

        :param sql: The SQL query to be executed.
        :param catalog: Catalog name of the table to query, default is anaheim.
        :param schema: Schema name of the table to query, default is empty string.

        :return: DataFrame which type is pandas.DataFrame.
        """
        sql = sql.strip().rstrip(';')
        engine = self._get_or_create_engine(catalog, schema)
        
        # Use execute and fetch results manually due to pyhive compatibility issues
        with engine.connect() as connection:
            result = connection.execute(sql)
            rows = result.fetchall()
            if rows:
                columns = result.keys()
                return pd.DataFrame(rows, columns=columns)
            else:
                return pd.DataFrame()

    execute_query = query

_default_client = None


def get_default_client() -> SkyDrillConnector:
    global _default_client
    if _default_client is None:
        _default_client = SkyDrillConnector()
    return _default_client


def query_skydrill(
        sql: str,
        catalog: str = "anaheim",
        schema: str = ""):
    client = get_default_client()
    return client.query(sql, catalog, schema)


if __name__ == "__main__":
    # Option1: Pass catalog and schema as parameter
    print(query_skydrill(
        sql="desc metricsagg_union_initiativegrain_gen2",
        catalog="anaheim",
        schema="referral"))

    # Option2: Pass catalog and schema into SQL
    print(query_skydrill(
        sql="desc anaheim.referral.metricsagg_union_initiativegrain_gen2"))