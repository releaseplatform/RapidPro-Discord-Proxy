# coding: utf-8
from sqlalchemy import (
    ARRAY,
    Boolean,
    CheckConstraint,
    Column,
    DateTime,
    ForeignKey,
    Integer,
    String,
    Text,
    text,
)
from sqlalchemy.sql.sqltypes import NullType
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.ext.declarative import declarative_base


Base = declarative_base()
metadata = Base.metadata


class AuthUser(Base):
    __tablename__ = "auth_user"

    id = Column(
        Integer,
        primary_key=True,
        server_default=text("nextval('auth_user_id_seq'::regclass)"),
    )
    password = Column(String(128), nullable=False)
    last_login = Column(DateTime(True))
    is_superuser = Column(Boolean, nullable=False)
    username = Column(String(254), nullable=False, unique=True)
    first_name = Column(String(30), nullable=False)
    last_name = Column(String(150), nullable=False)
    email = Column(String(254), nullable=False)
    is_staff = Column(Boolean, nullable=False)
    is_active = Column(Boolean, nullable=False)
    date_joined = Column(DateTime(True), nullable=False)


class LocationsAdminboundary(Base):
    __tablename__ = "locations_adminboundary"
    __table_args__ = (
        CheckConstraint("lft >= 0"),
        CheckConstraint("rght >= 0"),
        CheckConstraint("tree_id >= 0"),
    )

    id = Column(
        Integer,
        primary_key=True,
        server_default=text("nextval('locations_adminboundary_id_seq'::regclass)"),
    )
    osm_id = Column(String(15), nullable=False, unique=True)
    name = Column(String(128), nullable=False)
    level = Column(Integer, nullable=False)
    path = Column(String(768), nullable=False)
    simplified_geometry = Column(NullType, index=True)
    lft = Column(Integer, nullable=False, index=True)
    rght = Column(Integer, nullable=False, index=True)
    tree_id = Column(Integer, nullable=False, index=True)
    parent_id = Column(
        ForeignKey("locations_adminboundary.id", deferrable=True, initially="DEFERRED"),
        index=True,
    )

    parent = relationship("LocationsAdminboundary", remote_side=[id])


class OrgsLanguage(Base):
    __tablename__ = "orgs_language"

    id = Column(
        Integer,
        primary_key=True,
        server_default=text("nextval('orgs_language_id_seq'::regclass)"),
    )
    is_active = Column(Boolean, nullable=False)
    created_on = Column(DateTime(True), nullable=False)
    modified_on = Column(DateTime(True), nullable=False)
    name = Column(String(128), nullable=False)
    iso_code = Column(String(4), nullable=False)
    created_by_id = Column(
        ForeignKey("auth_user.id", deferrable=True, initially="DEFERRED"),
        nullable=False,
        index=True,
    )
    modified_by_id = Column(
        ForeignKey("auth_user.id", deferrable=True, initially="DEFERRED"),
        nullable=False,
        index=True,
    )
    org_id = Column(
        ForeignKey("orgs_org.id", deferrable=True, initially="DEFERRED"),
        nullable=False,
        index=True,
    )

    created_by = relationship(
        "AuthUser", primaryjoin="OrgsLanguage.created_by_id == AuthUser.id"
    )
    modified_by = relationship(
        "AuthUser", primaryjoin="OrgsLanguage.modified_by_id == AuthUser.id"
    )
    org = relationship("OrgsOrg", primaryjoin="OrgsLanguage.org_id == OrgsOrg.id")


class OrgsOrg(Base):
    __tablename__ = "orgs_org"

    id = Column(
        Integer,
        primary_key=True,
        server_default=text("nextval('orgs_org_id_seq'::regclass)"),
    )
    is_active = Column(Boolean, nullable=False)
    created_on = Column(DateTime(True), nullable=False)
    modified_on = Column(DateTime(True), nullable=False)
    uuid = Column(UUID, nullable=False, unique=True)
    name = Column(String(128), nullable=False)
    plan = Column(String(16), nullable=False)
    stripe_customer = Column(String(32))
    language = Column(String(64))
    timezone = Column(String(63), nullable=False)
    date_format = Column(String(1), nullable=False)
    config = Column(Text)
    slug = Column(String(255), unique=True)
    is_anon = Column(Boolean, nullable=False)
    brand = Column(String(128), nullable=False)
    surveyor_password = Column(String(128))
    country_id = Column(
        ForeignKey("locations_adminboundary.id", deferrable=True, initially="DEFERRED"),
        index=True,
    )
    created_by_id = Column(
        ForeignKey("auth_user.id", deferrable=True, initially="DEFERRED"),
        nullable=False,
        index=True,
    )
    modified_by_id = Column(
        ForeignKey("auth_user.id", deferrable=True, initially="DEFERRED"),
        nullable=False,
        index=True,
    )
    parent_id = Column(
        ForeignKey("orgs_org.id", deferrable=True, initially="DEFERRED"), index=True
    )
    primary_language_id = Column(
        ForeignKey("orgs_language.id", deferrable=True, initially="DEFERRED"),
        index=True,
    )
    is_flagged = Column(Boolean, nullable=False)
    is_suspended = Column(Boolean, nullable=False)
    uses_topups = Column(Boolean, nullable=False)
    is_multi_org = Column(Boolean, nullable=False)
    is_multi_user = Column(Boolean, nullable=False)

    country = relationship("LocationsAdminboundary")
    created_by = relationship(
        "AuthUser", primaryjoin="OrgsOrg.created_by_id == AuthUser.id"
    )
    modified_by = relationship(
        "AuthUser", primaryjoin="OrgsOrg.modified_by_id == AuthUser.id"
    )
    parent = relationship("OrgsOrg", remote_side=[id])
    primary_language = relationship(
        "OrgsLanguage", primaryjoin="OrgsOrg.primary_language_id == OrgsLanguage.id"
    )


class ChannelsChannel(Base):
    __tablename__ = "channels_channel"

    id = Column(
        Integer,
        primary_key=True,
        server_default=text("nextval('channels_channel_id_seq'::regclass)"),
    )
    is_active = Column(Boolean, nullable=False)
    created_on = Column(DateTime(True), nullable=False)
    modified_on = Column(DateTime(True), nullable=False)
    uuid = Column(String(36), nullable=False, unique=True)
    channel_type = Column(String(3), nullable=False)
    name = Column(String(64))
    address = Column(String(255))
    country = Column(String(2))
    claim_code = Column(String(16), unique=True)
    secret = Column(String(64), unique=True)
    last_seen = Column(DateTime(True), nullable=False, index=True)
    device = Column(String(255))
    os = Column(String(255))
    alert_email = Column(String(254))
    config = Column(Text)
    schemes = Column(ARRAY(String(length=16)), nullable=False)
    role = Column(String(4), nullable=False)
    bod = Column(Text)
    tps = Column(Integer)
    created_by_id = Column(
        ForeignKey("auth_user.id", deferrable=True, initially="DEFERRED"),
        nullable=False,
        index=True,
    )
    modified_by_id = Column(
        ForeignKey("auth_user.id", deferrable=True, initially="DEFERRED"),
        nullable=False,
        index=True,
    )
    org_id = Column(
        ForeignKey("orgs_org.id", deferrable=True, initially="DEFERRED"), index=True
    )
    parent_id = Column(
        ForeignKey("channels_channel.id", deferrable=True, initially="DEFERRED"),
        index=True,
    )

    created_by = relationship(
        "AuthUser", primaryjoin="ChannelsChannel.created_by_id == AuthUser.id"
    )
    modified_by = relationship(
        "AuthUser", primaryjoin="ChannelsChannel.modified_by_id == AuthUser.id"
    )
    org = relationship("OrgsOrg")
    parent = relationship("ChannelsChannel", remote_side=[id])

