from openapi_server.data_models.models import Opinion, RepresentativeOpinion, TalkSession, TalkSessionReport
from openapi_server.models.reports_generates_post_request import ReportsGeneratesPostRequest

from sqlalchemy.dialects import postgresql
from sqlalchemy import create_engine
from sqlalchemy import select, insert
from sqlalchemy.orm import scoped_session
from sqlalchemy.orm import sessionmaker

import os
from datetime import datetime

from openai import OpenAI
api_key = os.getenv('OPEN_AI_API_KEY', '')
client = None
if api_key != '':
    client = OpenAI(api_key=api_key)

Session = None


def completion(new_message_text:str, settings_text:str = '', past_messages:list = []):
    if len(past_messages) == 0 and len(settings_text) != 0:
        system = {"role": "system", "content": settings_text}
        past_messages.append(system)
    new_message = {"role": "user", "content": new_message_text}
    past_messages.append(new_message)

    result = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=past_messages,
        max_tokens=1024
    )
    response_message = {"role": "assistant", "content": result.choices[0].message.content}
    past_messages.append(response_message)
    response_message_text = result.choices[0].message.content
    return response_message_text, past_messages

def prepare_dataset(session, talk_session_id: str):
    Session = session
    theme = ''
    text = ''
    with Session() as session:
        result = session.query(RepresentativeOpinion, Opinion).\
            join(Opinion, Opinion.opinion_id == RepresentativeOpinion.opinion_id).\
            where(RepresentativeOpinion.talk_session_id == talk_session_id, RepresentativeOpinion.rank < 5).\
            all()

        text = 'talk_session_id,group_id,投稿の内容,グループにおける代表順位_値が小さい方が代表性が高い\n'
        for row in result:
            talk_session_id = row[0].talk_session_id
            group_id = row[0].group_id
            content = row[1].content
            rank = row[0].rank
            row_text = f'{talk_session_id},{group_id},{content},{rank}'
            # print(row_text)
            text += row_text + '\n'

        talk_session_row = session.query(TalkSession)\
                .where(TalkSession.talk_session_id == talk_session_id)\
                .one()
        theme = talk_session_row.theme

    template_summarize = f"""
    テーマ: {theme}

    {text}

    上記データについて以下のようにまとめてください
    - グループごとに代表意見の一覧を参考にして要約してください
    - グループIDも付与してかつグループを一言でまとめた段落にする
    - テーマと分析結果をもとにいい感じのタイトルをつけてください
    - 全体的な課題の段落も作ってください
    - 最後にまとめを書いてください
    markdownを用いてブログ記事風にまとめてください。
    """
    summarize_text, past = completion(template_summarize, '', [])

    with Session() as session:
        now = datetime.now()
        stmt = postgresql.insert(TalkSessionReport).values([
            dict(
                talk_session_id = talk_session_id,
                report = summarize_text,
                created_at = now,
                updated_at = now,
            )
        ])

        upsert_stmt = stmt.on_conflict_do_update(
            index_elements=[TalkSessionReport.talk_session_id],
            set_=dict(
                report = stmt.excluded.report,
                updated_at=stmt.excluded.updated_at
            ),
        )
        result = session.execute(upsert_stmt)
        session.commit()


def reports_generates(session, reports_generates_post_request: ReportsGeneratesPostRequest):
    prepare_dataset(session, reports_generates_post_request.talk_session_id)