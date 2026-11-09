"""
Implémentation SQLAlchemy des Ports de Repositories.
Ces adaptateurs sortants font le pont entre la persistance SQL et le domaine.
"""

from sqlalchemy.orm import Session
from app.adapters.outbound.persistence.mappers import (
    artist_to_domain,
    concert_to_domain,
    festival_to_domain,
    incident_to_domain,
    stage_to_domain,
)
from app.application.ports.repositories import (
    ArtistRepositoryPort,
    ConcertRepositoryPort,
    FestivalRepositoryPort,
    IncidentRepositoryPort,
    StageRepositoryPort,
)
from app.domain.entities.artist import Artist
from app.domain.entities.concert import Concert
from app.domain.entities.festival import Festival
from app.domain.entities.incident import Incident
from app.domain.entities.stage import Stage
from app.models import (
    Artist as SqlArtist,
    Concert as SqlConcert,
    Festival as SqlFestival,
    Incident as SqlIncident,
    Stage as SqlStage,
)


class SqlFestivalRepository(FestivalRepositoryPort):
    def __init__(self, session: Session):
        self.session = session

    def get_by_id(self, festival_id: int) -> Festival | None:
        row = self.session.query(SqlFestival).filter(SqlFestival.id == festival_id).first()
        return festival_to_domain(row) if row else None

    def list_all(self) -> list[Festival]:
        rows = self.session.query(SqlFestival).order_by(SqlFestival.id).all()
        return [festival_to_domain(r) for r in rows]

    def save(self, festival: Festival) -> Festival:
        if festival.id is not None:
            row = self.session.query(SqlFestival).filter(SqlFestival.id == festival.id).first()
            if row:
                row.name = festival.name
                row.location = festival.location
                row.start_date = festival.period.start_date
                row.end_date = festival.period.end_date
                row.status = festival.status
                self.session.flush()
                return festival_to_domain(row)

        row = SqlFestival(
            name=festival.name,
            location=festival.location,
            start_date=festival.period.start_date,
            end_date=festival.period.end_date,
            status=festival.status,
        )
        self.session.add(row)
        self.session.flush()
        return festival_to_domain(row)


class SqlArtistRepository(ArtistRepositoryPort):
    def __init__(self, session: Session):
        self.session = session

    def get_by_id(self, artist_id: int) -> Artist | None:
        row = self.session.query(SqlArtist).filter(SqlArtist.id == artist_id).first()
        return artist_to_domain(row) if row else None

    def list_all(self) -> list[Artist]:
        rows = self.session.query(SqlArtist).order_by(SqlArtist.name).all()
        return [artist_to_domain(r) for r in rows]

    def save(self, artist: Artist) -> Artist:
        if artist.id is not None:
            row = self.session.query(SqlArtist).filter(SqlArtist.id == artist.id).first()
            if row:
                row.name = artist.name
                row.genre = artist.genre
                row.required_equipment = artist.required_equipment.to_csv()
                self.session.flush()
                return artist_to_domain(row)

        row = SqlArtist(
            name=artist.name,
            genre=artist.genre,
            required_equipment=artist.required_equipment.to_csv(),
        )
        self.session.add(row)
        self.session.flush()
        return artist_to_domain(row)


class SqlStageRepository(StageRepositoryPort):
    def __init__(self, session: Session):
        self.session = session

    def get_by_id(self, stage_id: int) -> Stage | None:
        row = self.session.query(SqlStage).filter(SqlStage.id == stage_id).first()
        return stage_to_domain(row) if row else None

    def list_by_festival(self, festival_id: int) -> list[Stage]:
        rows = (
            self.session.query(SqlStage)
            .filter(SqlStage.festival_id == festival_id)
            .order_by(SqlStage.id)
            .all()
        )
        return [stage_to_domain(r) for r in rows]

    def save(self, stage: Stage) -> Stage:
        if stage.id is not None:
            row = self.session.query(SqlStage).filter(SqlStage.id == stage.id).first()
            if row:
                row.name = stage.name
                row.capacity = stage.capacity
                row.available_equipment = stage.available_equipment.to_csv()
                self.session.flush()
                return stage_to_domain(row)

        row = SqlStage(
            festival_id=stage.festival_id,
            name=stage.name,
            capacity=stage.capacity,
            available_equipment=stage.available_equipment.to_csv(),
        )
        self.session.add(row)
        self.session.flush()
        return stage_to_domain(row)


class SqlConcertRepository(ConcertRepositoryPort):
    def __init__(self, session: Session):
        self.session = session

    def get_by_id(self, concert_id: int) -> Concert | None:
        row = self.session.query(SqlConcert).filter(SqlConcert.id == concert_id).first()
        return concert_to_domain(row) if row else None

    def list_by_festival(self, festival_id: int) -> list[Concert]:
        rows = (
            self.session.query(SqlConcert)
            .filter(SqlConcert.festival_id == festival_id, SqlConcert.status != "cancelled")
            .order_by(SqlConcert.start_time)
            .all()
        )
        return [concert_to_domain(r) for r in rows]

    def save(self, concert: Concert) -> Concert:
        if concert.id is not None:
            row = self.session.query(SqlConcert).filter(SqlConcert.id == concert.id).first()
            if row:
                row.festival_id = concert.festival_id
                row.artist_id = concert.artist_id
                row.stage_id = concert.stage_id
                row.start_time = concert.time_slot.start_time
                row.end_time = concert.time_slot.end_time
                row.status = concert.status
                self.session.flush()
                return concert_to_domain(row)

        row = SqlConcert(
            festival_id=concert.festival_id,
            artist_id=concert.artist_id,
            stage_id=concert.stage_id,
            start_time=concert.time_slot.start_time,
            end_time=concert.time_slot.end_time,
            status=concert.status,
        )
        self.session.add(row)
        self.session.flush()
        return concert_to_domain(row)


class SqlIncidentRepository(IncidentRepositoryPort):
    def __init__(self, session: Session):
        self.session = session

    def get_by_id(self, incident_id: int) -> Incident | None:
        row = self.session.query(SqlIncident).filter(SqlIncident.id == incident_id).first()
        return incident_to_domain(row) if row else None

    def list_all(self, concert_id: int | None = None) -> list[Incident]:
        q = self.session.query(SqlIncident)
        if concert_id is not None:
            q = q.filter(SqlIncident.concert_id == concert_id)
        rows = q.order_by(SqlIncident.occurred_at.desc()).all()
        return [incident_to_domain(r) for r in rows]

    def save(self, incident: Incident) -> Incident:
        if incident.id is not None:
            row = self.session.query(SqlIncident).filter(SqlIncident.id == incident.id).first()
            if row:
                row.description = incident.description
                row.occurred_at = incident.occurred_at
                row.resolved = incident.resolved
                self.session.flush()
                return incident_to_domain(row)

        row = SqlIncident(
            concert_id=incident.concert_id,
            description=incident.description,
            occurred_at=incident.occurred_at,
            resolved=incident.resolved,
        )
        self.session.add(row)
        self.session.flush()
        return incident_to_domain(row)
