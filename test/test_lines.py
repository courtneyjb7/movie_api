from fastapi.testclient import TestClient

from src.api.server import app

import json

client = TestClient(app)


def test_get_line():
    response = client.get("/lines/238")
    assert response.status_code == 200

    with open("test/lines/238.json", encoding="utf-8") as f:
        assert response.json() == json.load(f)


def test_lines():
    response = client.get("/lines/")
    assert response.status_code == 200

    with open("test/lines/root.json", encoding="utf-8") as f:
        assert response.json() == json.load(f)


def test_sort_filter():
    response = client.get(
        "/lines/?name=what&limit=15&offset=60&sort=movie_title"
    )
    assert response.status_code == 200

    with open(
        "test/lines/lines-name=what&limit=15&offset=60&sort=movie_title.json",
        encoding="utf-8",
    ) as f:
        assert response.json() == json.load(f)


def test_conv():
    response = client.get(
        "/lines/conv/500"
    )
    assert response.status_code == 200

    with open(
        "test/lines/conv-500.json",
        encoding="utf-8",
    ) as f:
        assert response.json() == json.load(f)


def test_404():
    response = client.get("/lines/400")
    assert response.status_code == 404
