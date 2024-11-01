# coding: utf-8

from typing import ClassVar, Dict, List, Tuple  # noqa: F401

from typing import Any, Dict, Optional
from openapi_server.models.predicts_groups_post_request import PredictsGroupsPostRequest
from openapi_server.models.reports_generates_post_request import ReportsGeneratesPostRequest
from openapi_server.models.reports_wordclouds_post200_response import ReportsWordcloudsPost200Response
from openapi_server.models.test_get200_response import TestGet200Response
from openapi_server.security_api import get_token_basic

class BaseDefaultApi:
    subclasses: ClassVar[Tuple] = ()

    def __init_subclass__(cls, **kwargs):
        super().__init_subclass__(**kwargs)
        BaseDefaultApi.subclasses = BaseDefaultApi.subclasses + (cls,)
    async def predicts_groups_post(
        self,
        predicts_groups_post_request: Optional[PredictsGroupsPostRequest],
    ) -> object:
        """"""
        ...


    async def reports_generates_post(
        self,
        reports_generates_post_request: Optional[ReportsGeneratesPostRequest],
    ) -> object:
        """"""
        ...


    async def reports_wordclouds_post(
        self,
        reports_generates_post_request: Optional[ReportsGeneratesPostRequest],
    ) -> ReportsWordcloudsPost200Response:
        """"""
        ...


    async def test_get(
        self,
    ) -> TestGet200Response:
        """"""
        ...
