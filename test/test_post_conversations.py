from fastapi.testclient import TestClient
from src import database as db
from src.api.server import app
import io
import csv
from supabase import Client, create_client
import dotenv
import os
import constant

import json

client = TestClient(app)

dotenv.load_dotenv()
supabase_api_key = os.environ.get("SUPABASE_API_KEY")
supabase_url = os.environ.get("SUPABASE_URL")

if supabase_api_key is None or supabase_url is None:
    raise Exception(
        "You must set the SUPABASE_API_KEY and SUPABASE_URL environment variables."
    )
supabase: Client = create_client(supabase_url, supabase_api_key)

sess = supabase.auth.get_session()

def download_conv():
    conversations_csv = (
        supabase.storage.from_("movie-api")
        .download("conversations.csv")
        .decode("utf-8")
    )
    conv_log = []
    for row in csv.DictReader(io.StringIO(conversations_csv), skipinitialspace=True):
        conv_log.append(row)
    return conv_log

def download_lines():
    lines_csv = (
        supabase.storage.from_("movie-api")
        .download("lines.csv")
        .decode("utf-8")
    )
    lines_log = []
    for row in csv.DictReader(io.StringIO(lines_csv), skipinitialspace=True):
        lines_log.append(row)
    return lines_log


# info_b4Call = {
#     "len_conv_log" : 0,
#     "len_lines_log" : 0,
#     "last_conv_id" : 0,
#     "last_line_id" : 0,
#     "last_line_text" : "",
#     "2nd2last_line_text" : "",
#     "3rd2last_line_text" : ""
# }
# len_conv_log = 0
def test_1_part_1():
    # global len_conv_log
    data = {
        "character_1_id": 0,
        "character_2_id": 1,
        "lines": [
            {
                "character_id": 0,
                "line_text": "Hi"
            },
            {
                "character_id": 1,
                "line_text": "How are you?"
            },
            {
                "character_id": 0,
                "line_text": "Great!"
            }
        ]
    }
    constant.len_conv_log = len(db.conv_log)

    response = client.post(
        "/movies/0/conversations/",
        json=data
    ) 
    db_conv_log = download_conv()
    db_conv_log
    assert response.status_code == 200
    assert len(db.conv_log) == constant.len_conv_log + 1
    assert len(db_conv_log) == constant.len_conv_log + 1
    assert int(db_conv_log[-1]["conversation_id"]) == db.conv_log[-1]["conversation_id"]
    assert len(db_conv_log) == constant.len_conv_log + 1
    # assert len(db.lines_log) == len_line_log + 3
    # assert len(db_lines_log) == len_line_log + 3
    assert db.conv_log[-1]["movie_id"] == 0
    
# def test_1_part_2():
#     global len_conv_log
#     db_conv_log = download_conv()
#     # db_lines_log = 
#     assert int(db_conv_log[-1]["conversation_id"]) == db.conv_log[-1]["conversation_id"]


def test_post_error():
    data = {
        "character_1_id": 0,
        "character_2_id": 1,
        "lines": [
            {
                "character_id": 0,
                "line_text": "Hi"
            },
            {
                "character_id": 4,
                "line_text": "How are you?"
            }
        ]
    }
    response = client.post(
        "/movies/0/conversations/",
        json=data
    )
    assert response.status_code == 404
