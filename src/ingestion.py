from dotenv import load_dotenv
from config.config import load_conf
from requests.adapters import HTTPAdapter
import requests
import os
import time
from urllib3 import Retry
from utils.logging import create_logger
import io
from google.cloud import storage
import pandas as pd

load_dotenv()
logger = create_logger()

conf = load_conf()["API"]
BASE_URL = f"http://api.adzuna.com/v1/api/jobs/{conf.get('country', '')}/search"
params = {
    "app_id" : os.getenv("app_id", ""),
    "app_key" : os.getenv("app_key", "")
}
bucket_name = os.getenv("bucket_name", "")

def create_session():
    retry_strategy = Retry(
        total=3,
        backoff_factor=1,
        allowed_methods=["GET"],
        status_forcelist=[429, 500, 502, 503, 504]
    )

    adapter = HTTPAdapter(max_retries=retry_strategy)
    session = requests.Session()
    session.mount("https://", adapter)
    session.mount("http://", adapter)
    return session

def rate_limit(last_request_time, time_interval = 5):    
    now = time.time()
    elapsed =  now - last_request_time
    if elapsed < time_interval:
        time.sleep(time_interval - elapsed)
    return time.time()

def make_request(session, url, last_request_time, params):
    response = session.get(url, params=params)
    last_request_time = rate_limit(last_request_time)
    return response, last_request_time

def pagination(session):
    page = 1
    last_request_time = 0
    while True:
        url = f"{BASE_URL}/{page}"
        response, last_request_time = make_request(session, url, last_request_time, params)        
        if response.status_code != 200:
            logger.info(f"Error {response.status_code}")
        data = response.json()
        logger.info(f"Fetching {page}")
        if page > 100:
            break
        page += 1
    return data

def upload_to_gcs(bucket_name, object_name, buffer):
    client = storage.Client()
    bucket = client.bucket(bucket_name)
    blob = bucket.blob(object_name)
    buffer.seek(0)
    blob.upload_from_file(buffer, content_type="application/vnd.apache.parquet")
    print(f"Uploaded to GCS {bucket} the object {blob}")

def run_ingestion(data, bucket_name, object_name):
    buffer = io.BytesIO()
    df = pd.DataFrame(data.get("results", []))
    df.to_parquet(buffer, index=False)
    upload_to_gcs(bucket_name, object_name, buffer)

def main(date_path, run_id):
    session = create_session()
    data = pagination(session)
    object_name = f"landing/adzuna_api/{date_path}/{run_id}"
    run_ingestion(data, bucket_name, object_name)

if __name__ == "__main__":
    main()
