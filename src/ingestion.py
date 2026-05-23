from dotenv import load_dotenv
from config.config import load_conf
from requests.adapters import HTTPAdapter
import requests
import os
import time
import json
from urllib3 import Retry
from pathlib import Path
from utils.logging import create_logger



load_dotenv()
logger = create_logger()

conf = load_conf()["API"]
BASE_URL = f"http://api.adzuna.com/v1/api/jobs/{conf.get('country', '')}/search"
params = {
    "app_id" : os.getenv("app_id", ""),
    "app_key" : os.getenv("app_key", "")
}

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
        result = data.get("results", [])
        logger.info(f"Fetching {page}")
        if page > 10:
            break
        save_json(result, page)
        page += 1
    
def save_json(all_results, page):
    path = Path(__file__).resolve().parents[1] / "data"
    path.mkdir(parents=True, exist_ok=True)
    file_path = path / f"page_{page}.json"

    with open(file_path, "w", encoding="utf-8") as f:
        json.dump(all_results, f, ensure_ascii=False, indent=2)

def main():
    session = create_session()
    logger.info(f"{session} created")
    pagination(session)
    logger.info("Pagination and saving completed")

if __name__== "__main__":
    main()