"""FastAPI dependencies for dependency injection."""

from application.ports.messaging.event_publisher import EventPublisher
from application.ports.repositories.example_repository import (
    ExampleRepository,
)
from application.use_cases.example_use_cases import (
    CreateExampleUseCase,
    GetExampleUseCase,
    ListExamplesUseCase,
)
from infra.database.repositories.example_repository import (
    BeanieExampleRepository,
)
from infra.messaging.event_publisher_impl import (
    KafkaEventPublisher,
)


def get_example_repository() -> ExampleRepository:
    """Get example repository instance."""
    return BeanieExampleRepository()


def get_event_publisher() -> EventPublisher:
    """Get event publisher instance."""
    return KafkaEventPublisher()


def get_create_example_use_case(
    repository: ExampleRepository = None,
    event_publisher: EventPublisher = None,
) -> CreateExampleUseCase:
    """Get create example use case."""
    if repository is None:
        repository = get_example_repository()
    if event_publisher is None:
        event_publisher = get_event_publisher()

    return CreateExampleUseCase(repository, event_publisher)


def get_get_example_use_case(
    repository: ExampleRepository = None,
) -> GetExampleUseCase:
    """Get get example use case."""
    if repository is None:
        repository = get_example_repository()

    return GetExampleUseCase(repository)


def get_list_examples_use_case(
    repository: ExampleRepository = None,
) -> ListExamplesUseCase:
    """Get list examples use case."""
    if repository is None:
        repository = get_example_repository()

    return ListExamplesUseCase(repository)
