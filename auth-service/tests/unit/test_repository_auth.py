from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from auth_service.domain.entities import User, UserRole
from auth_service.infrastructure.database.database import Base
from auth_service.infrastructure.database.repository import SQLAlchemyUserRepository


def _build_session():
    engine = create_engine("sqlite:///:memory:", connect_args={"check_same_thread": False})
    Base.metadata.create_all(bind=engine)
    return sessionmaker(bind=engine, autocommit=False, autoflush=False)()


def test_find_by_email_returns_none_when_not_found():
    session = _build_session()
    repo = SQLAlchemyUserRepository(session)
    assert repo.find_by_email("missing@example.com") is None
    session.close()


def test_save_and_find_by_email_roundtrip():
    session = _build_session()
    repo = SQLAlchemyUserRepository(session)

    user = User(
        name="Saved",
        email="saved@example.com",
        password_hash="hashed",
        role=UserRole.ADMIN,
    )
    saved = repo.save(user)
    loaded = repo.find_by_email("saved@example.com")

    assert saved.id is not None
    assert saved.created_at is not None
    assert loaded is not None
    assert loaded.email == "saved@example.com"
    assert loaded.role == UserRole.ADMIN
    session.close()
