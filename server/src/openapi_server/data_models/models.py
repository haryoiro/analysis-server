# coding: utf-8
from sqlalchemy import ForeignKey, BigInteger, Boolean, CheckConstraint, Column, DateTime, Float, Index, Integer, SmallInteger, String, Table, Text, text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql.sqltypes import NullType
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()
metadata = Base.metadata


t_geography_columns = Table(
    'geography_columns', metadata,
    Column('f_table_catalog', String),
    Column('f_table_schema', String),
    Column('f_table_name', String),
    Column('f_geography_column', String),
    Column('coord_dimension', Integer),
    Column('srid', Integer),
    Column('type', Text)
)


t_geometry_columns = Table(
    'geometry_columns', metadata,
    Column('f_table_catalog', String(256)),
    Column('f_table_schema', String),
    Column('f_table_name', String),
    Column('f_geometry_column', String),
    Column('coord_dimension', Integer),
    Column('srid', Integer),
    Column('type', String(30))
)


class Opinion(Base):
    __tablename__ = 'opinions'
    __table_args__ = (
        Index('idx_opinions_opinion_id_parent_opinion_id', 'opinion_id', 'parent_opinion_id'),
    )

    opinion_id = Column(UUID, primary_key=True)
    talk_session_id = Column(UUID, nullable=False, index=True)
    user_id = Column(UUID, nullable=False, index=True)
    parent_opinion_id = Column(UUID, index=True)
    title = Column(String)
    content = Column(String, nullable=False)
    created_at = Column(DateTime, nullable=False, server_default=text("now()"))
    picture_url = Column(String)
    reference_url = Column(String)


class RepresentativeOpinion(Base):
    __tablename__ = 'representative_opinions'

    talk_session_id = Column(UUID, primary_key=True, nullable=False)
    opinion_id = Column(UUID, ForeignKey("opinions.opinion_id"), primary_key=True, nullable=False)
    group_id = Column(Integer, primary_key=True, nullable=False)
    rank = Column(Integer, nullable=False)
    updated_at = Column(DateTime, nullable=False, server_default=text("now()"))
    created_at = Column(DateTime, nullable=False, server_default=text("now()"))


class SchemaMigration(Base):
    __tablename__ = 'schema_migrations'

    version = Column(BigInteger, primary_key=True)
    dirty = Column(Boolean, nullable=False)


class Session(Base):
    __tablename__ = 'sessions'
    __table_args__ = (
        Index('idx_session_id_user_id', 'user_id', 'session_id'),
    )

    session_id = Column(UUID, primary_key=True)
    user_id = Column(UUID, nullable=False)
    provider = Column(String, nullable=False)
    session_status = Column(Integer, nullable=False)
    expires_at = Column(DateTime, nullable=False)
    created_at = Column(DateTime, nullable=False, server_default=text("now()"))
    last_activity_at = Column(DateTime, nullable=False, server_default=text("now()"))


class SpatialRefSy(Base):
    __tablename__ = 'spatial_ref_sys'
    __table_args__ = (
        CheckConstraint('(srid > 0) AND (srid <= 998999)'),
    )

    srid = Column(Integer, primary_key=True)
    auth_name = Column(String(256))
    auth_srid = Column(Integer)
    srtext = Column(String(2048))
    proj4text = Column(String(2048))


class TalkSessionLocation(Base):
    __tablename__ = 'talk_session_locations'

    talk_session_id = Column(UUID, primary_key=True)
    location = Column(NullType, nullable=False)


class TalkSessionReport(Base):
    __tablename__ = 'talk_session_reports'

    talk_session_id = Column(UUID, primary_key=True, unique=True)
    report = Column(Text, nullable=False)
    created_at = Column(DateTime, nullable=False, server_default=text("now()"))
    updated_at = Column(DateTime, nullable=False, server_default=text("now()"))


class TalkSession(Base):
    __tablename__ = 'talk_sessions'

    talk_session_id = Column(UUID, primary_key=True)
    owner_id = Column(UUID, nullable=False)
    theme = Column(String, nullable=False)
    scheduled_end_time = Column(DateTime, nullable=False)
    created_at = Column(DateTime, nullable=False, server_default=text("now()"))
    city = Column(String)
    prefecture = Column(String)


class UserAuth(Base):
    __tablename__ = 'user_auths'
    __table_args__ = (
        Index('idx_user_id_user_subject', 'user_id', 'subject'),
    )

    user_auth_id = Column(UUID, primary_key=True)
    user_id = Column(UUID, nullable=False)
    provider = Column(String, nullable=False)
    subject = Column(String, nullable=False)
    is_verified = Column(Boolean, nullable=False)
    created_at = Column(DateTime, nullable=False, server_default=text("now()"))


class UserDemographic(Base):
    __tablename__ = 'user_demographics'

    user_demographics_id = Column(UUID, primary_key=True)
    user_id = Column(UUID, nullable=False, unique=True)
    year_of_birth = Column(Integer)
    occupation = Column(SmallInteger)
    gender = Column(SmallInteger, nullable=False)
    city = Column(String)
    household_size = Column(SmallInteger)
    created_at = Column(DateTime, nullable=False, server_default=text("now()"))
    updated_at = Column(DateTime, nullable=False, server_default=text("now()"))
    prefecture = Column(String(10))


class UserGroupInfo(Base):
    __tablename__ = 'user_group_info'

    talk_session_id = Column(UUID, primary_key=True, nullable=False)
    user_id = Column(UUID, primary_key=True, nullable=False)
    group_id = Column(Integer, nullable=False)
    pos_x = Column(Float(53), nullable=False)
    pos_y = Column(Float(53), nullable=False)
    updated_at = Column(DateTime, nullable=False, server_default=text("now()"))
    created_at = Column(DateTime, nullable=False, server_default=text("now()"))
    perimeter_index = Column(Integer)


class User(Base):
    __tablename__ = 'users'

    user_id = Column(UUID, primary_key=True, index=True)
    display_id = Column(String)
    display_name = Column(String)
    icon_url = Column(String)
    created_at = Column(DateTime, nullable=False, server_default=text("now()"))
    updated_at = Column(DateTime, nullable=False, server_default=text("now()"))


class Vote(Base):
    __tablename__ = 'votes'
    __table_args__ = (
        Index('idx_votes_vote_id_opinion_id', 'vote_id', 'opinion_id'),
        Index('idx_votes_opinion_id_user_id', 'opinion_id', 'user_id'),
        Index('idx_votes_user_id_opinion_id', 'user_id', 'opinion_id')
    )

    vote_id = Column(UUID, primary_key=True)
    opinion_id = Column(UUID, nullable=False)
    user_id = Column(UUID, nullable=False)
    vote_type = Column(SmallInteger, nullable=False)
    created_at = Column(DateTime, nullable=False, server_default=text("now()"))
    talk_session_id = Column(UUID, nullable=False)
