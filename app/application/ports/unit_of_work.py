"""
Port d'Unité de Travail (Unit of Work).
Permet d'encapsuler plusieurs opérations et notifications dans une transaction atomique.
"""

from typing import Protocol, runtime_checkable


@runtime_checkable
class UnitOfWorkPort(Protocol):
    def __enter__(self) -> "UnitOfWorkPort": ...
    def __exit__(self, exc_type, exc_val, exc_tb) -> None: ...
    def commit(self) -> None: ...
    def rollback(self) -> None: ...
