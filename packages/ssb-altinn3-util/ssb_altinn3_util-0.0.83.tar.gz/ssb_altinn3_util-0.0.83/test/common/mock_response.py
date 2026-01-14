class MockResponse:
    content: bytes
    headers: dict[str, str]
    status_code: int = 200
