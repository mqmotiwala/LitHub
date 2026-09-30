import os
import boto3

from dotenv import load_dotenv, find_dotenv
from utils.pushover import Pushover

# load environment variables from .env file
load_dotenv(find_dotenv())
def env(key, default=None):
    var = os.getenv(key, default)
    if var is None:
        raise RuntimeError(f"Missing env var: {key}")
    return var

# app styling
PRIMARY_COLOR = "#087405"
HIGHLIGHT_COLOR = "#C8F0C4"

# aws vars
S3_BUCKET = "lithub-676206945006"

# filenames only; the per-user key prefix is composed in User.load_user_variables()
BOOKS_JSON_FILENAME = "books.json"
READING_LIST_JSON_FILENAME = "reading_list.json"

AWS_ACCESS_KEY_ID = env("AWS_ACCESS_KEY_ID")
AWS_SECRET_ACCESS_KEY = env("AWS_SECRET_ACCESS_KEY")
AWS_REGION = env("AWS_REGION")
s3 = boto3.client(
    "s3",
    aws_access_key_id=AWS_ACCESS_KEY_ID,
    aws_secret_access_key=AWS_SECRET_ACCESS_KEY,
    region_name=AWS_REGION
)

ddb = boto3.resource(
    "dynamodb",
    aws_access_key_id=AWS_ACCESS_KEY_ID,
    aws_secret_access_key=AWS_SECRET_ACCESS_KEY,
    region_name=AWS_REGION
)

# ddb table names
USERS_TABLE = "users-lithub"

MIN_RATING = 0
MAX_RATING = 5
FILLED_STAR = "★"
EMPTY_STAR = "☆"

DATE_FORMAT = "%Y-%m-%d"
DATETIME_FORMAT = "%Y-%m-%d %H:%M:%S"

APP_NAME = "LitHub"
APP_ICON = ":material/local_library:"
APP_TAGLINE = "Keep a log of what you read."
TEXT_INPUT_PLACEHOLDER = "Provide input"
SEARCH_BAR_PLACEHOLDER = "Filter books"

# misc auth/UI vars
LOGOUT_BUTTON_KEY_NAME = "logout_button"

# Pushover client
po = Pushover(user_token=env("PUSHOVER_USER_TOKEN"), app_token=env("PUSHOVER_APP_TOKEN"), log_token=env("PUSHOVER_LOG_TOKEN"))