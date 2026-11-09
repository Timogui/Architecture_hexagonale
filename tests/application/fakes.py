"""
Doubles de test (Fakes & Mocks) pour tester les cas d'utilisation sans aucune BDD ni serveur HTTP.
"""

from app.application.ports.notification_port import NotificationPort
from app.application.ports.repositories import (
    ArtistRepositoryPort,
    ConcertRepositoryPort,
    FestivalRepositoryPort,
    IncidentRepositoryPort,
    StageRepositoryPort,
)
from app.application.ports.unit_of_work import UnitOfWorkPort
from app.domain.entities.artist import Artist
from app.domain.entities.concert import Concert
from app.domain.entities.festival import Festival
from app.domain.entities.incident import Incident
from app.domain.entities.stage import Stage


class FakeUnitOfWork(UnitOfWorkPort):
    def __init__(self):
        self.committed = False
        self.rolled_back = False

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        if exc_type is not None:
            self.rollback()

    def commit(self) -> None:
        self.committed = True

    def rollback(self) -> None:
        self.rolled_back = True


class SpyNotificationSender(NotificationPort):
    def __init__(self, should_fail: bool = False):
        self.notifications = []
        self.should_fail = should_fail

    def notify_schedule_change(self, concert_id: int, message: str) -> None:
        if self.should_fail:
            raise RuntimeError("Simulation : le service de notification est indisponible")
        self.notifications.append((concert_id, message))


class InMemoryFestivalRepository(FestivalRepositoryPort):
    def __init__(self):
        self.festivals: dict[int, Festival] = {}
        self._next_id = 1

    def get_by_id(self, festival_id: int) -> Festival | None:
        return self.festivals.get(festival_id)

    def list_all(self) -> list[Festival]:
        return list(self.festivals.values())

    def save(self, festival: Festival) -> Festival:
        if festival.id is None:
            festival.id = self._next_id
            self._next_id += 1
        self.festivals[festival.id] = festival
        return festival


class InMemoryArtistRepository(ArtistRepositoryPort):
    def __init__(self):
        self.artists: dict[int, Artist] = {}
        self._next_id = 1

    def get_by_id(self, artist_id: int) -> Artist | None:
        return self.artists.get(artist_id)

    def list_all(self) -> list[Artist]:
        return list(self.artists.values())

    def save(self, artist: Artist) -> Artist:
        if artist.id is None:
            artist.id = self._next_id
            self._next_id += 1
        self.artists[artist.id] = artist
        return artist


class InMemoryStageRepository(StageRepositoryPort):
    def __init__(self):
        self.stages: dict[int, Stage] = {}
        self._next_id = 1

    def get_by_id(self, stage_id: int) -> Stage | None:
        return self.stages.get(stage_id)

    def list_by_festival(self, festival_id: int) -> list[Stage]:
        return [s for s in self.stages.values() if s.festival_id == festival_id]

    def save(self, stage: Stage) -> Stage:
        if stage.id is None:
            stage.id = self._next_id
            self._next_id += 1
        self.stages[stage.id] = stage
        return stage


class InMemoryConcertRepository(ConcertRepositoryPort):
    def __init__(self):
        self.concerts: dict[int, Concert] = {}
        self._next_id = 1

    def get_by_id(self, concert_id: int) -> Concert | None:
        return self.concerts.get(concert_id)

    def list_by_festival(self, festival_id: int) -> list[Concert]:
        return [
            c for c in self.concerts.values()
            if c.festival_id == festival_id and not c.is_cancelled
        ]

    def save(self, concert: Concert) -> Concert:
        if concert.id is None:
            concert.id = self._next_id
            self._next_id += 1
        self.concerts[concert.id] = concert
        return concert


class InMemoryIncidentRepository(IncidentRepositoryPort):
    def __init__(self):
        self.incidents: dict[int, Incident] = {}
        self._next_id = 1

    def get_by_id(self, incident_id: int) -> Incident | None:
        return self.incidents.get(incident_id)

    def list_all(self, concert_id: int | None = None) -> list[Incident]:
        if concert_id is not None:
            return [i for i in self.incidents.values() if i.concert_id == concert_id]
        return list(self.incidents.values())

    def save(self, incident: Incident) -> Incident:
        if incident.id is None:
            incident.id = self._next_id
            self._next_id += 1
        self.incidents[incident.id] = incident
        return incident
