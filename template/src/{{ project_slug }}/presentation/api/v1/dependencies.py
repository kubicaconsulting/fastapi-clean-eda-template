"""FastAPI dependencies for dependency injection."""

from {{ project_slug }}.application.ports.messaging.event_publisher import EventPublisher
from {{ project_slug }}.application.ports.repositories.example_repository import (
    ExampleRepository,
)
from {{ project_slug }}.application.use_cases.example_use_cases import (
    CreateExampleUseCase,
    GetExampleUseCase,
    ListExamplesUseCase,
)
from {{ project_slug }}.infrastructure.database.repositories.example_repository import (
    BeanieExampleRepository,
)
from {{ project_slug }}.infrastructure.messaging.event_publisher_impl import (
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
