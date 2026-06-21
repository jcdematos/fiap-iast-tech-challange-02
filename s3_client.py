import os
import logging
import boto3
#from botocore.exceptions import ClientError

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

aws_access_key = os.environ['AWS_ACCESS_KEY_ID']
aws_secret_key = os.environ['AWS_SECRET_ACCESS_KEY']
aws_region = 'us-east-1'


def upload_to_s3(df, table, config) -> None:
    s3_client = boto3.client(
        's3',
        aws_access_key_id=aws_access_key,
        aws_secret_access_key=aws_secret_key,
        region_name=aws_region
    )

    logger.info(f"[+] Saving {table} dataframe to file")
    df.to_parquet(f'{table}.parquet', index=False)

    parquet_file = f"{table}.parquet"
    logger.info(f"Upload {parquet_file} to s3 bronze")
    s3_client.upload_file(str(parquet_file), config['bucket']['name'], f'{config["paths"]["bronze"]}{parquet_file}')
