from openapi_server.apis.default_api_base import BaseDefaultApi
from openapi_server.models.predicts_groups_post_request import PredictsGroupsPostRequest
from openapi_server.models.test_get200_response import TestGet200Response

from openapi_server.impl.predicts_groups import predicts_groups, connect_db

class MainApi(BaseDefaultApi):
    def __init__(self):
        print("init!!!")
        connect_db()

    async def predicts_groups_post(
        self,
        predicts_groups_post_request: PredictsGroupsPostRequest,
    ) -> object:
        """"""
        predicts_groups(predicts_groups_post_request)
        return {"basic": "success"}
        ...


    async def test_get(
        self,
    ) -> TestGet200Response:
        """"""
        return {"text": "hello"}
        ...