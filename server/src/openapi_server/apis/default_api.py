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
    summary="API",
    response_model_by_alias=True,
)
async def predicts_groups_post(
    talk_session_id: str = Query(None, description="", alias="talk_session_id"),
    user_id: str = Query(None, description="", alias="user_id"),
    token_basic: TokenModel = Security(
        get_token_basic
    ),
) -> object:
    """"""
    if not BaseDefaultApi.subclasses:
        raise HTTPException(status_code=500, detail="Not implemented")
    return await BaseDefaultApi.subclasses[0]().predicts_groups_post(talk_session_id, user_id)


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
    return {"text": "hello"}
    if not BaseDefaultApi.subclasses:
        raise HTTPException(status_code=500, detail="Not implemented")
    return await BaseDefaultApi.subclasses[0]().test_get()
