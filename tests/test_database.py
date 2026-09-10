from sqlalchemy import text

from app.database import SessionLocal


def test_database_session():
    with SessionLocal() as db:
        result = db.execute(text("SELECT 1"))

        assert result.scalar_one() == 1
