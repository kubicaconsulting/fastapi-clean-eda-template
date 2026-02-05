# import pytest
# from src.config import load_settings
# from src.main import app
# from fastapi.testclient import TestClient

# # Load testing settings
# test_settings = load_settings()


# @pytest.fixture(scope="session")
# def settings():
#     return test_settings


# @pytest.fixture(scope="session")
# def api_base_url():
#     return test_settings.api_base_url


# @pytest.fixture()
# def client(settings):
#     test_client = TestClient(
#         app,
#         base_url="http://testserver" + settings.api_base_url,
#         headers={"Content-Type": "application/json", "Accept": "application/json"},
#     )

#     return test_client
