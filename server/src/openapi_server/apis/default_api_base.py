# coding: utf-8

from typing import ClassVar, Dict, List, Tuple  # noqa: F401

from openapi_server.models.predicts_groups_post_request import PredictsGroupsPostRequest
from openapi_server.models.test_get200_response import TestGet200Response
from openapi_server.security_api import get_token_basic

class BaseDefaultApi:
    subclasses: ClassVar[Tuple] = ()

    def __init_subclass__(cls, **kwargs):
        super().__init_subclass__(**kwargs)
        BaseDefaultApi.subclasses = BaseDefaultApi.subclasses + (cls,)
    async def predicts_groups_post(
        self,
        predicts_groups_post_request: PredictsGroupsPostRequest,
    ) -> object:
        """"""
        ...


    async def test_get(
        self,
    ) -> TestGet200Response:
        """"""
        ...
