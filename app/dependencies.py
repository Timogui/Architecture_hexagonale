"""
Module de composition (Composition Root) et Injection de Dépendances.
Assemble les adaptateurs techniques pour instancier les cas d'utilisation.
"""

from fastapi import Depends
from sqlalchemy.orm import Session

from app.adapters.outbound.notifications.email_notification_adapter import (
    EmailNotificationAdapter,
)
from app.adapters.outbound.persistence.sql_repositories import (
    SqlArtistRepository,
    SqlConcertRepository,
    SqlFestivalRepository,
    SqlIncidentRepository,
    SqlStageRepository,
)
from app.adapters.outbound.persistence.unit_of_work import SqlAlchemyUnitOfWork
from app.application.ports.notification_port import NotificationPort
from app.application.ports.repositories import (
    ArtistRepositoryPort,
    ConcertRepositoryPort,
    FestivalRepositoryPort,
    IncidentRepositoryPort,
    StageRepositoryPort,
)
from app.application.ports.unit_of_work import UnitOfWorkPort
from app.application.use_cases.artist_use_cases import (
    CreateArtistUseCase,
    ListArtistsUseCase,
)
from app.application.use_cases.concert_use_cases import (
    CancelConcertUseCase,
    CreateConcertUseCase,
    GetConcertUseCase,
    ListConcertsUseCase,
    RescheduleConcertUseCase,
)
from app.application.use_cases.festival_use_cases import (
    CreateFestivalUseCase,
    GetFestivalUseCase,
    ListFestivalsUseCase,
    PublishFestivalUseCase,
)
from app.application.use_cases.incident_use_cases import (
    CreateIncidentUseCase,
    ListIncidentsUseCase,
)
from app.application.use_cases.stage_use_cases import (
    CreateStageUseCase,
    ListStagesUseCase,
)
from app.database import get_db

# --- Fournisseurs d'Adaptateurs ---


def get_uow(db: Session = Depends(get_db)) -> UnitOfWorkPort:
    return SqlAlchemyUnitOfWork(db)


def get_notification_port() -> NotificationPort:
    return EmailNotificationAdapter()


def get_festival_repository(db: Session = Depends(get_db)) -> FestivalRepositoryPort:
    return SqlFestivalRepository(db)


def get_artist_repository(db: Session = Depends(get_db)) -> ArtistRepositoryPort:
    return SqlArtistRepository(db)


def get_stage_repository(db: Session = Depends(get_db)) -> StageRepositoryPort:
    return SqlStageRepository(db)


def get_concert_repository(db: Session = Depends(get_db)) -> ConcertRepositoryPort:
    return SqlConcertRepository(db)


def get_incident_repository(db: Session = Depends(get_db)) -> IncidentRepositoryPort:
    return SqlIncidentRepository(db)


# --- Fournisseurs de Cas d'Utilisation ---


def get_reschedule_concert_use_case(
    concert_repo: ConcertRepositoryPort = Depends(get_concert_repository),
    festival_repo: FestivalRepositoryPort = Depends(get_festival_repository),
    stage_repo: StageRepositoryPort = Depends(get_stage_repository),
    artist_repo: ArtistRepositoryPort = Depends(get_artist_repository),
    notification_sender: NotificationPort = Depends(get_notification_port),
    uow: UnitOfWorkPort = Depends(get_uow),
) -> RescheduleConcertUseCase:
    return RescheduleConcertUseCase(
        concert_repo=concert_repo,
        festival_repo=festival_repo,
        stage_repo=stage_repo,
        artist_repo=artist_repo,
        notification_sender=notification_sender,
        uow=uow,
    )


def get_create_concert_use_case(
    concert_repo: ConcertRepositoryPort = Depends(get_concert_repository),
    festival_repo: FestivalRepositoryPort = Depends(get_festival_repository),
    stage_repo: StageRepositoryPort = Depends(get_stage_repository),
    artist_repo: ArtistRepositoryPort = Depends(get_artist_repository),
    uow: UnitOfWorkPort = Depends(get_uow),
) -> CreateConcertUseCase:
    return CreateConcertUseCase(
        concert_repo=concert_repo,
        festival_repo=festival_repo,
        stage_repo=stage_repo,
        artist_repo=artist_repo,
        uow=uow,
    )


def get_cancel_concert_use_case(
    concert_repo: ConcertRepositoryPort = Depends(get_concert_repository),
    festival_repo: FestivalRepositoryPort = Depends(get_festival_repository),
    uow: UnitOfWorkPort = Depends(get_uow),
) -> CancelConcertUseCase:
    return CancelConcertUseCase(
        concert_repo=concert_repo, festival_repo=festival_repo, uow=uow
    )


def get_get_concert_use_case(
    concert_repo: ConcertRepositoryPort = Depends(get_concert_repository),
) -> GetConcertUseCase:
    return GetConcertUseCase(concert_repo=concert_repo)


def get_list_concerts_use_case(
    concert_repo: ConcertRepositoryPort = Depends(get_concert_repository),
) -> ListConcertsUseCase:
    return ListConcertsUseCase(concert_repo=concert_repo)


def get_create_festival_use_case(
    festival_repo: FestivalRepositoryPort = Depends(get_festival_repository),
    uow: UnitOfWorkPort = Depends(get_uow),
) -> CreateFestivalUseCase:
    return CreateFestivalUseCase(festival_repo=festival_repo, uow=uow)


def get_publish_festival_use_case(
    festival_repo: FestivalRepositoryPort = Depends(get_festival_repository),
    concert_repo: ConcertRepositoryPort = Depends(get_concert_repository),
    notification_sender: NotificationPort = Depends(get_notification_port),
    uow: UnitOfWorkPort = Depends(get_uow),
) -> PublishFestivalUseCase:
    return PublishFestivalUseCase(
        festival_repo=festival_repo,
        concert_repo=concert_repo,
        notification_sender=notification_sender,
        uow=uow,
    )


def get_list_festivals_use_case(
    festival_repo: FestivalRepositoryPort = Depends(get_festival_repository),
) -> ListFestivalsUseCase:
    return ListFestivalsUseCase(festival_repo=festival_repo)


def get_create_stage_use_case(
    stage_repo: StageRepositoryPort = Depends(get_stage_repository),
    festival_repo: FestivalRepositoryPort = Depends(get_festival_repository),
    uow: UnitOfWorkPort = Depends(get_uow),
) -> CreateStageUseCase:
    return CreateStageUseCase(
        stage_repo=stage_repo, festival_repo=festival_repo, uow=uow
    )


def get_list_stages_use_case(
    stage_repo: StageRepositoryPort = Depends(get_stage_repository),
) -> ListStagesUseCase:
    return ListStagesUseCase(stage_repo=stage_repo)


def get_create_artist_use_case(
    artist_repo: ArtistRepositoryPort = Depends(get_artist_repository),
    uow: UnitOfWorkPort = Depends(get_uow),
) -> CreateArtistUseCase:
    return CreateArtistUseCase(artist_repo=artist_repo, uow=uow)


def get_list_artists_use_case(
    artist_repo: ArtistRepositoryPort = Depends(get_artist_repository),
) -> ListArtistsUseCase:
    return ListArtistsUseCase(artist_repo=artist_repo)


def get_create_incident_use_case(
    incident_repo: IncidentRepositoryPort = Depends(get_incident_repository),
    concert_repo: ConcertRepositoryPort = Depends(get_concert_repository),
    uow: UnitOfWorkPort = Depends(get_uow),
) -> CreateIncidentUseCase:
    return CreateIncidentUseCase(
        incident_repo=incident_repo, concert_repo=concert_repo, uow=uow
    )


def get_list_incidents_use_case(
    incident_repo: IncidentRepositoryPort = Depends(get_incident_repository),
) -> ListIncidentsUseCase:
    return ListIncidentsUseCase(incident_repo=incident_repo)
