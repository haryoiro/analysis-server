# coding: utf-8

from typing import Dict, List  # noqa: F401
import importlib
import pkgutil

from openapi_server.apis.default_api_base import BaseDefaultApi
import openapi_server.impl

from fastapi import (  # noqa: F401
    APIRouter,
    Body,
    Cookie,
    Depends,
    Form,
    Header,
    HTTPException,
    Path,
    Query,
    Response,
    Security,
    status,
)

from openapi_server.models.extra_models import TokenModel  # noqa: F401
from typing import Any, Dict, Optional
from openapi_server.models.predicts_groups_post_request import PredictsGroupsPostRequest
from openapi_server.models.reports_generates_post_request import ReportsGeneratesPostRequest
from openapi_server.models.reports_wordclouds_post200_response import ReportsWordcloudsPost200Response
from openapi_server.models.test_get200_response import TestGet200Response
from openapi_server.security_api import get_token_basic

router = APIRouter()

ns_pkg = openapi_server.impl
for _, name, _ in pkgutil.iter_modules(ns_pkg.__path__, ns_pkg.__name__ + "."):
    importlib.import_module(name)


@router.post(
    "/predicts/groups",
    responses={
        200: {"model": object, "description": ""},
    },
    tags=["default"],
    summary="group予測",
    response_model_by_alias=True,
)
async def predicts_groups_post(
    predicts_groups_post_request: Optional[PredictsGroupsPostRequest] = Body(None, description=""),
    token_basic: TokenModel = Security(
        get_token_basic
    ),
) -> object:
    """"""
    if not BaseDefaultApi.subclasses:
        raise HTTPException(status_code=500, detail="Not implemented")
    return await BaseDefaultApi.subclasses[0]().predicts_groups_post(predicts_groups_post_request)


@router.post(
    "/reports/generates",
    responses={
        200: {"model": object, "description": ""},
    },
    tags=["default"],
    summary="レポート作成",
    response_model_by_alias=True,
)
async def reports_generates_post(
    reports_generates_post_request: Optional[ReportsGeneratesPostRequest] = Body(None, description=""),
    token_basic: TokenModel = Security(
        get_token_basic
    ),
) -> object:
    """"""
    if not BaseDefaultApi.subclasses:
        raise HTTPException(status_code=500, detail="Not implemented")
    return await BaseDefaultApi.subclasses[0]().reports_generates_post(reports_generates_post_request)


@router.post(
    "/reports/wordclouds",
    responses={
        200: {"model": ReportsWordcloudsPost200Response, "description": ""},
    },
    tags=["default"],
    summary="ワードクラウドテスト",
    response_model_by_alias=True,
)
async def reports_wordclouds_post(
    reports_generates_post_request: Optional[ReportsGeneratesPostRequest] = Body(None, description=""),
) -> ReportsWordcloudsPost200Response:
    """"""
    if not BaseDefaultApi.subclasses:
        raise HTTPException(status_code=500, detail="Not implemented")
    return await BaseDefaultApi.subclasses[0]().reports_wordclouds_post(reports_generates_post_request)


@router.get(
    "/test",
    responses={
        200: {"model": TestGet200Response, "description": ""},
    },
    tags=["default"],
    summary="テストAPI",
    response_model_by_alias=True,
)
async def test_get(
) -> TestGet200Response:
    """"""
    if not BaseDefaultApi.subclasses:
        raise HTTPException(status_code=500, detail="Not implemented")
    return await BaseDefaultApi.subclasses[0]().test_get()
