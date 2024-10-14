from openapi_server.apis.default_api_base import BaseDefaultApi
from openapi_server.models.predicts_groups_post_request import PredictsGroupsPostRequest
from openapi_server.models.reports_generates_post_request import ReportsGeneratesPostRequest
from openapi_server.models.test_get200_response import TestGet200Response

from openapi_server.impl.predicts_groups import predicts_groups
from openapi_server.impl.reports_generates import reports_generates

from typing import Optional

from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session
from sqlalchemy.orm import sessionmaker

import os

Session = None
database_url = os.getenv('DATABASE_URL', '')
engine = None
session_factory = None
if database_url != '':
    engine = create_engine(database_url)
    session_factory = sessionmaker(autocommit=False, bind=engine)

def connect_db():
    global Session
    Session = scoped_session(session_factory)

class MainApi(BaseDefaultApi):
    def __init__(self):
        print("init!!!")
        connect_db()

    async def predicts_groups_post(
        self,
        predicts_groups_post_request: PredictsGroupsPostRequest,
    ) -> object:
        """"""
        predicts_groups(Session, predicts_groups_post_request)
        return {"basic": "success"}
        ...


    async def reports_generates_post(
        self,
        reports_generates_post_request: Optional[ReportsGeneratesPostRequest],
    ) -> object:
        """"""
        reports_generates(Session, reports_generates_post_request)
        return {"basic": "success"}
        ...


    async def test_get(
        self,
    ) -> TestGet200Response:
        """"""
        return {"text": "hello"}
        ...