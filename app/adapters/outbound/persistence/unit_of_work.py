"""
Implémentation de l'Unité de Travail (Unit of Work) avec SQLAlchemy.
Garantit la gestion transactionnelle et le rollback automatique en cas d'erreur.
"""

from sqlalchemy.orm import Session
from app.application.ports.unit_of_work import UnitOfWorkPort


class SqlAlchemyUnitOfWork(UnitOfWorkPort):
    def __init__(self, session: Session):
        self.session = session

    def __enter__(self) -> "SqlAlchemyUnitOfWork":
        return self

    def __exit__(self, exc_type, exc_val, exc_tb) -> None:
        if exc_type is not None:
            self.rollback()

    def commit(self) -> None:
        self.session.commit()

    def rollback(self) -> None:
        self.session.rollback()
