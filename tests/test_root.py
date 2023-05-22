import os
import sys

sys.path.append(os.path.abspath("."))

from fastapi.testclient import TestClient

import main

client = TestClient(main.app)


def test_root():
    response = client.get("/")
    assert response.status_code == 200


if __name__ == "__main__":
    test_root()
