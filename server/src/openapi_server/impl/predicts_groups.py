from openapi_server.data_models.models import Vote, Opinion, UserGroupInfo, RepresentativeOpinion
from openapi_server.models.predicts_groups_post_request import PredictsGroupsPostRequest

from sqlalchemy.dialects import postgresql
from sqlalchemy import create_engine
from sqlalchemy import select, insert
from sqlalchemy.orm import scoped_session
from sqlalchemy.orm import sessionmaker
# from sqlalchemy import text
import os
from datetime import datetime
import itertools

import numpy as np
import pandas as pd
from sklearn.decomposition import PCA
from sklearn.cluster import KMeans
from sklearn.metrics import silhouette_score

from typing import Any, Dict, List

seed = 302
Session = None

def connect_db():
    global Session
    database_url = os.getenv('DATABASE_URL', '')
    engine = create_engine(database_url)
    session_factory = sessionmaker(autocommit=False, bind=engine)
    Session = scoped_session(session_factory)


def prepare_dataset(talk_session_id: str) -> List[Vote]:
    idx_to_userid = None
    predict = None
    dataset = None
    representative_group_opinion_idx = None
    n_clusters = None

    with Session() as session:
        stmt = select(Vote).filter(Vote.talk_session_id == talk_session_id).order_by(Vote.vote_id)
        result = session.execute(stmt).all()

        votes = []
        users = []
        user_votes = []
        opinions = []
        for row in result:
            opinions.append(row[0].opinion_id)
            votes.append(row[0].opinion_id)
            users.append(row[0].user_id)

        votes_count = len(votes)
        voteid_to_idx = dict(zip(votes, range(votes_count)))
        idx_to_voteid = dict(zip(range(votes_count), votes))

        opinions = set(opinions)
        opinions = list(opinions)
        opinions.sort()
        opinions_count = len(opinions)
        opinionid_to_idx = dict(zip(opinions, range(opinions_count)))
        idx_to_opinionid = dict(zip(range(opinions_count), opinions))

        users = set(users)
        users = list(users)
        users.sort()
        users_count = len(users)
        userid_to_idx = dict(zip(users, range(users_count)))
        idx_to_userid = dict(zip(range(users_count), users))

        users_indices = [i for i in range(users_count)]
        votes_indices = [i for i in range(votes_count)]
        opinions_indices = [i for i in range(opinions_count)]

        vectors = [[0 for j in range(opinions_count)] for i in range(users_count)]

        for row in result:
            # vote_type unvote:0 agree:1 disagree:2 pass:3
            opinion_idx = opinionid_to_idx[row[0].opinion_id]
            user_idx = userid_to_idx[row[0].user_id]
            vote_type = row[0].vote_type
            if vote_type == 1:
                vectors[user_idx][opinion_idx] = 1
            elif vote_type == 2:
                vectors[user_idx][opinion_idx] = -1

        predict = None
        n_clusters = 2
        best_silhouette_score = -1

        for _n_clusters in range(2, 10):
            _predict = KMeans(n_clusters=_n_clusters,random_state=seed).fit_predict(vectors)
            score = silhouette_score(vectors, _predict)
            # print(f"clusters {_n_clusters} score {score}")
            if score > best_silhouette_score:
                predict = _predict
                n_clusters = _n_clusters
                best_silhouette_score = score

        print(f"clusters {n_clusters} score {best_silhouette_score}")
        DIMENTION_NUM = 2
        pca = PCA(n_components=DIMENTION_NUM)
        dataset = pca.fit_transform(vectors)

        dataset = np.array(dataset)

        # あるクラスターの賛成数と投票数
        agree_gv = [[0 for j in range(len(opinions_indices))] for i in range(n_clusters)]
        all_gv = [[0 for j in range(len(opinions_indices))] for i in range(n_clusters)]

        # あるクラスター以外の賛成数と投票数
        other_agree_gv = [[0 for j in range(len(opinions_indices))] for i in range(n_clusters)]
        other_all_gv = [[0 for j in range(len(opinions_indices))] for i in range(n_clusters)]

        clusters_set = set([i for i in range(n_clusters)])

        for i in range(len(vectors)):
            cluster_idx = predict[i]
            for j in range(len(vectors[i])):
                # あるクラスターの賛成数と投票数
                if 1 == vectors[i][j]:
                    agree_gv[cluster_idx][j] += 1
                    all_gv[cluster_idx][j] += 1
                elif -1 == vectors[i][j]:
                    all_gv[cluster_idx][j] += 1

                other_clusters = clusters_set - {cluster_idx}
                other_clusters = list(other_clusters)
                for k in range(len(other_clusters)):
                    other_cluster_idx = other_clusters[k]
                    if 1 == vectors[i][j]:
                        other_agree_gv[other_cluster_idx][j] += 1
                        other_all_gv[other_cluster_idx][j] += 1
                    elif -1 == vectors[i][j]:
                        other_all_gv[other_cluster_idx][j] += 1

        agree_gv = np.array(agree_gv)
        all_gv = np.array(all_gv)

        group_beta_expection = np.divide((1+agree_gv), (2+all_gv))

        other_agree_gv = np.array(other_agree_gv)
        other_all_gv = np.array(other_all_gv)

        other_group_beta_expection = np.divide((1+other_agree_gv), (2+other_all_gv))

        representative_group_opinion = np.divide(group_beta_expection, other_group_beta_expection)
        representative_group_opinion_idx = np.argsort(-representative_group_opinion, axis=1)

        vote_rate = np.divide(agree_gv, all_gv, out=np.zeros_like(agree_gv, dtype=float), where=(all_gv!=0))


    with Session() as session:
        now = datetime.now()
        stmt = postgresql.insert(UserGroupInfo).values([
            dict(
                talk_session_id = talk_session_id,
                user_id = idx_to_userid[user_idx],
                group_id = int(predict[user_idx]),
                pos_x = float(dataset[user_idx][0]),
                pos_y = float(dataset[user_idx][1]),
                created_at = now,
                updated_at = now
            ) for user_idx in users_indices
        ])

        upsert_stmt = stmt.on_conflict_do_update(
            index_elements=[UserGroupInfo.talk_session_id, UserGroupInfo.user_id],
            set_=dict(
                group_id=stmt.excluded.group_id,
                pos_x=stmt.excluded.pos_x,
                pos_y=stmt.excluded.pos_y,
                updated_at=stmt.excluded.updated_at
            ),
        )

        result = session.execute(upsert_stmt)
        session.commit()


    with Session() as session:
        now = datetime.now()
        values = [
            [dict(
                talk_session_id = talk_session_id,
                opinion_id = idx_to_opinionid[int(opinion_idx)],
                group_id = int(group_id),
                rank = rank,
                created_at = now,
                updated_at = now
                ) for rank, opinion_idx in enumerate(opinios_idx)
            ] for group_id, opinios_idx in enumerate(representative_group_opinion_idx)
        ]
        values = list(itertools.chain.from_iterable(values))

        stmt = postgresql.insert(RepresentativeOpinion).values(values)


        upsert_stmt = stmt.on_conflict_do_update(
            index_elements=[RepresentativeOpinion.talk_session_id, RepresentativeOpinion.opinion_id, RepresentativeOpinion.group_id],
            set_=dict(
                rank=stmt.excluded.rank,
                updated_at=stmt.excluded.updated_at
            ),
        )

        result = session.execute(upsert_stmt)
        session.commit()

def predicts_groups(predicts_groups_post_request: PredictsGroupsPostRequest):
    prepare_dataset(predicts_groups_post_request.talk_session_id)