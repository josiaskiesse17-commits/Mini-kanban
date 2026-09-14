from datetime import timedelta

import pytest
from fastapi import HTTPException
from fastapi.security import HTTPAuthorizationCredentials
from sqlalchemy import create_engine
from sqlalchemy.orm import Session

from app.auth.security import (
    create_access_token,
    decode_access_token,
    get_current_user,
    hash_password,
    verify_password,
)
from app.database import Base
from app.models import User


def test_password_hashing_and_verification() -> None:
    password_hash = hash_password("correct horse battery staple")

    assert password_hash != "correct horse battery staple"
    assert verify_password("correct horse battery staple", password_hash)
    assert not verify_password("wrong password", password_hash)


def test_access_token_round_trip() -> None:
    token = create_access_token(42)

    assert decode_access_token(token) == 42


def test_expired_or_tampered_access_token_is_rejected() -> None:
    with pytest.raises(HTTPException) as expired:
        decode_access_token(create_access_token(42, timedelta(seconds=-1)))
    assert expired.value.status_code == 401

    with pytest.raises(HTTPException) as tampered:
        token = create_access_token(42)
        parts = token.split(".")
        parts[2] = ("A" if parts[2][0] != "A" else "B") + parts[2][1:]
        decode_access_token(".".join(parts))
    assert tampered.value.status_code == 401


def test_current_user_dependency_requires_bearer_and_loads_user() -> None:
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)
    with Session(engine) as session:
        user = User(username="alice", hashed_password=hash_password("password"))
        session.add(user)
        session.commit()
        session.refresh(user)

        credentials = HTTPAuthorizationCredentials(
            scheme="Bearer", credentials=create_access_token(user.id)
        )
        assert get_current_user(credentials, session).username == "alice"

        with pytest.raises(HTTPException) as missing:
            get_current_user(None, session)
        assert missing.value.status_code == 401
