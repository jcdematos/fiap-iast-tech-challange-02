import logging
import hashlib
from google.cloud import bigquery

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def ingest_from_bigquery(tables) -> dict:
    dfs = {}

    client = bigquery.Client()

    for table in tables:
        query = f"""
    SELECT * FROM `basedosdados.br_inep_avaliacao_alfabetizacao.{table}` LIMIT 1000
    """
        logger.info(f"[+] Querying table {table}")
        try:
            query_job = client.query(query)
        except GoogleAPIError as e:
            logger.error("Failed to query table %s: %s", table, e)
            raise
        logger.info("[+] Appending to ingestion dataframes")
        df = query_job.to_dataframe()
        df['_ingestion_timestamp_'] = 'today'
        df['_source_dataset_'] = 'basedosdados'
        df['_source_table_'] = table
        df['_record_hash'] = df.drop(
            columns=['_ingestion_timestamp', '_source_url', '_source_system'],
            errors='ignore'
        ).apply(lambda row: hashlib.md5(str(row.values).encode()).hexdigest(), axis=1)

        logger.info("Registros inseridos: %s", len(df))
        logger.info("   Colunes: %s", list(df.columns))

        dfs[table] = query_job.to_dataframe()
    return dfs
