# coding: utf-8

from fastapi.testclient import TestClient


from openapi_server.models.test_get200_response import TestGet200Response  # noqa: F401


def test_predicts_groups_post(client: TestClient):
    """Test case for predicts_groups_post

    API
    """
    params = [("talk_session_id", 'talk_session_id_example'),     ("user_id", 'user_id_example')]
    headers = {
        "Authorization": "BasicZm9vOmJhcg==",
    }
    # uncomment below to make a request
    #response = client.request(
    #    "POST",
    #    "/predicts/groups",
    #    headers=headers,
    #    params=params,
    #)

    # uncomment below to assert the status code of the HTTP response
    #assert response.status_code == 200


def test_test_get(client: TestClient):
    """Test case for test_get

    テストAPI
    """

    headers = {
    }
    # uncomment below to make a request
    #response = client.request(
    #    "GET",
    #    "/test",
    #    headers=headers,
    #)

    # uncomment below to assert the status code of the HTTP response
    #assert response.status_code == 200

