"""Example API routes."""

from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status

from application.dto.example_dto import (
    CreateExampleDTO,
    ExampleDTO,
)
from application.use_cases.example_use_cases import (
    CreateExampleUseCase,
    GetExampleUseCase,
    ListExamplesUseCase,
)
from api.v1.dependencies import (
    get_create_example_use_case,
    get_get_example_use_case,
    get_list_examples_use_case,
)

router = APIRouter(prefix="/examples", tags=["examples"])


@router.post(
    "/",
    response_model=ExampleDTO,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new example",
)
async def create_example(
    data: CreateExampleDTO,
    use_case: CreateExampleUseCase = Depends(get_create_example_use_case),
) -> ExampleDTO:
    """Create a new example."""
    try:
        return await use_case.execute(data)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )


@router.get(
    "/{example_id}",
    response_model=ExampleDTO,
    summary="Get example by ID",
)
async def get_example(
    example_id: UUID,
    use_case: GetExampleUseCase = Depends(get_get_example_use_case),
) -> ExampleDTO:
    """Get an example by ID."""
    result = await use_case.execute(example_id)
    if not result:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Example with id {example_id} not found",
        )
    return result


@router.get(
    "/",
    response_model=list[ExampleDTO],
    summary="List examples",
)
async def list_examples(
    skip: int = 0,
    limit: int = 100,
    use_case: ListExamplesUseCase = Depends(get_list_examples_use_case),
) -> list[ExampleDTO]:
    """List examples with pagination."""
    return await use_case.execute(skip=skip, limit=limit)
