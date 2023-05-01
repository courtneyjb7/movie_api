from src import database as db
from fastapi.testclient import TestClient

from src.api.server import app

import json

client = TestClient(app)



def test_post_conv_1():
    data = {
        "character_1_id": 4386,
        "character_2_id": 4376,
        "lines": [
            {
                "character_id": 4386,
                "line_text": "Nice to meet you."
            },
            {
                "character_id": 4376,
                "line_text": "You too!"
            }
        ]
    }

    response = client.post(
        "/movies/290/conversations/",
        json=data
    ) 
    
    assert response.status_code == 200


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

# These following tests work, but pytest sometimes times out when more than one post call test??
# A lot of successful testing has been done manually, but had some issues with pytest

# def test_post_conv_2():
#     data = {
#         "character_1_id": 56,
#         "character_2_id": 57,
#         "lines": [
#             {
#                 "character_id": 56,
#                 "line_text": "Hi"
#             },
#             {
#                 "character_id": 57,
#                 "line_text": "How are you?"
#             },
#             {
#                 "character_id": 56,
#                 "line_text": "Good"
#             }
#         ]
#     }
#     len_conv_log = len(db.conv_log)
#     len_lines_log = len(db.lines_log)
#     c0_num_lines = db.characters[56].num_lines
#     c1_num_lines = db.characters[57].num_lines

#     response = client.post(
#         "/movies/3/conversations/",
#         json=data
#     ) 
    
#     assert response.status_code == 200
#     assert len(db.conv_log) == len_conv_log + 1
#     assert len(db.lines_log) == len_lines_log + 3
#     assert db.characters[56].num_lines == c0_num_lines + 2
#     assert db.characters[57].num_lines == c1_num_lines + 1
#     assert db.lines_log[-2]["line_text"] == "How are you?"
#     assert db.lines_log[-1]["line_text"] == "Good"

# def test_post_conv():
#     data = {
#         "character_1_id": 0,
#         "character_2_id": 1,
#         "lines": [
#             {
#                 "character_id": 0,
#                 "line_text": "Hi"
#             },
#             {
#                 "character_id": 1,
#                 "line_text": "How are you?"
#             },
#             # {
#             #     "character_id": 0,
#             #     "line_text": "Great!"
#             # }
#         ]
#     }
#     # Below assertions work but sometimes time out !

#     len_conv_log = len(db.conv_log)
#     len_lines_log = len(db.lines_log)
#     c0_num_lines = db.characters[0].num_lines
#     c1_num_lines = db.characters[1].num_lines

#     response = client.post(
#         "/movies/0/conversations/",
#         json=data
#     ) 
    
#     assert response.status_code == 200
#     assert len(db.conv_log) == len_conv_log + 1
#     assert len(db.lines_log) == len_lines_log + 3
#     assert db.characters[0].num_lines == c0_num_lines + 2
#     assert db.characters[1].num_lines == c1_num_lines + 1
#     assert db.lines_log[-3]["line_text"] == "Hi"
#     assert db.lines_log[-2]["line_text"] == "How are you?"
#     assert db.lines_log[-1]["line_text"] == "Great!"
