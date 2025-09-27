import os
import boto3

from dotenv import load_dotenv, find_dotenv

# load environment variables from .env file
load_dotenv(find_dotenv())
def env(key, default=None):
    var = os.getenv(key, default)
    if var is None:
        raise RuntimeError(f"Missing env var: {key}")
    return var

# aws vars
S3_BUCKET = "lithub-676206945006"
BOOKS_JSON_PATH = "books.json"
READING_LIST_JSON_PATH = "reading_list.json"
AWS_ACCESS_KEY_ID = env("AWS_ACCESS_KEY_ID")
AWS_SECRET_ACCESS_KEY = env("AWS_SECRET_ACCESS_KEY")
AWS_REGION = env("AWS_REGION")
s3 = boto3.client(
    "s3",
    aws_access_key_id=AWS_ACCESS_KEY_ID,
    aws_secret_access_key=AWS_SECRET_ACCESS_KEY,
    region_name=AWS_REGION
)

MIN_RATING = 0
MAX_RATING = 5
FILLED_STAR = "★"
EMPTY_STAR = "☆"

DATE_FORMAT = "%Y-%m-%d"

APP_NAME = "LitHub"
TEXT_INPUT_PLACEHOLDER = "Provide input"
SEARCH_BAR_PLACEHOLDER = "Filter books"