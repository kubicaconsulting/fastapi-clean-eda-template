# Example: Using the Template to Build a User Service

This guide shows how to use the template to build a complete user management service.

## Step 1: Generate the Project

```bash
copier copy . user-service
cd user-service
```

Answer the prompts:
- Project name: `user-service`
- Project description: `User management microservice`
- Service port: `8000`
- Python version: `3.12`
- Include authentication: `Yes`
- Include observability: `Yes`

## Step 2: Review Generated Structure

```
user-service/
├── src/user_service/
│   ├── domain/
│   │   ├── entities/example.py       # Replace with user.py
│   │   └── events/example_events.py  # Replace with user_events.py
│   ├── application/
│   │   ├── use_cases/
│   │   ├── ports/
│   │   └── dto/
│   ├── infrastructure/
│   └── presentation/
```

## Step 3: Customize Domain Layer

### Create User Entity (`domain/entities/user.py`)

```python
from dataclasses import dataclass, field
from datetime import datetime
from uuid import UUID, uuid4
from enum import Enum

class UserRole(Enum):
    ADMIN = "admin"
    USER = "user"
    GUEST = "guest"

@dataclass
class User:
    id: UUID = field(default_factory=uuid4)
    email: str = ""
    username: str = ""
    hashed_password: str = ""
    role: UserRole = UserRole.USER
    is_active: bool = True
    email_verified: bool = False
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: datetime = field(default_factory=datetime.utcnow)
    last_login: datetime | None = None

    def verify_email(self) -> None:
        """Mark email as verified."""
        self.email_verified = True
        self.updated_at = datetime.utcnow()

    def change_role(self, role: UserRole) -> None:
        """Change user role."""
        self.role = role
        self.updated_at = datetime.utcnow()

    def record_login(self) -> None:
        """Record last login time."""
        self.last_login = datetime.utcnow()
```

### Create User Events (`domain/events/user_events.py`)

```python
from dataclasses import dataclass
from datetime import datetime
from uuid import UUID, uuid4

@dataclass
class DomainEvent:
    event_id: UUID
    timestamp: datetime
    event_type: str

@dataclass
class UserRegisteredEvent(DomainEvent):
    user_id: UUID
    email: str
    username: str

    def __init__(self, user_id: UUID, email: str, username: str):
        super().__init__(
            event_id=uuid4(),
            timestamp=datetime.utcnow(),
            event_type="user.registered",
        )
        self.user_id = user_id
        self.email = email
        self.username = username

@dataclass
class UserEmailVerifiedEvent(DomainEvent):
    user_id: UUID

    def __init__(self, user_id: UUID):
        super().__init__(
            event_id=uuid4(),
            timestamp=datetime.utcnow(),
            event_type="user.email_verified",
        )
        self.user_id = user_id
```

## Step 4: Create Application Layer

### User DTOs (`application/dto/user_dto.py`)

```python
from pydantic import BaseModel, EmailStr, Field
from datetime import datetime
from uuid import UUID

class RegisterUserDTO(BaseModel):
    email: EmailStr
    username: str = Field(min_length=3, max_length=50)
    password: str = Field(min_length=8)

class UserDTO(BaseModel):
    id: UUID
    email: str
    username: str
    role: str
    is_active: bool
    email_verified: bool
    created_at: datetime
    last_login: datetime | None

class LoginDTO(BaseModel):
    email: EmailStr
    password: str

class TokenDTO(BaseModel):
    access_token: str
    token_type: str = "bearer"
```

### Repository Port (`application/ports/repositories/user_repository.py`)

```python
from abc import ABC, abstractmethod
from uuid import UUID
from typing import Optional

from user_service.domain.entities.user import User

class UserRepository(ABC):
    @abstractmethod
    async def create(self, user: User) -> User:
        pass

    @abstractmethod
    async def get_by_id(self, user_id: UUID) -> Optional[User]:
        pass

    @abstractmethod
    async def get_by_email(self, email: str) -> Optional[User]:
        pass

    @abstractmethod
    async def get_by_username(self, username: str) -> Optional[User]:
        pass

    @abstractmethod
    async def update(self, user: User) -> User:
        pass

    @abstractmethod
    async def delete(self, user_id: UUID) -> bool:
        pass
```

### Use Cases (`application/use_cases/user_use_cases.py`)

```python
from uuid import UUID
from passlib.context import CryptContext

from user_service.application.dto.user_dto import RegisterUserDTO, UserDTO
from user_service.application.ports.repositories.user_repository import UserRepository
from user_service.application.ports.messaging.event_publisher import EventPublisher
from user_service.domain.entities.user import User
from user_service.domain.events.user_events import UserRegisteredEvent

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

class RegisterUserUseCase:
    def __init__(
        self,
        repository: UserRepository,
        event_publisher: EventPublisher,
    ):
        self.repository = repository
        self.event_publisher = event_publisher

    async def execute(self, dto: RegisterUserDTO) -> UserDTO:
        # Check if user exists
        existing = await self.repository.get_by_email(dto.email)
        if existing:
            raise ValueError("Email already registered")

        existing = await self.repository.get_by_username(dto.username)
        if existing:
            raise ValueError("Username already taken")

        # Create user
        hashed_password = pwd_context.hash(dto.password)
        user = User(
            email=dto.email,
            username=dto.username,
            hashed_password=hashed_password,
        )

        # Save user
        created_user = await self.repository.create(user)

        # Publish event
        event = UserRegisteredEvent(
            user_id=created_user.id,
            email=created_user.email,
            username=created_user.username,
        )
        await self.event_publisher.publish(event, "user-events")

        return UserDTO(
            id=created_user.id,
            email=created_user.email,
            username=created_user.username,
            role=created_user.role.value,
            is_active=created_user.is_active,
            email_verified=created_user.email_verified,
            created_at=created_user.created_at,
            last_login=created_user.last_login,
        )
```

## Step 5: Implement Infrastructure

### Beanie Model (`infrastructure/database/models.py`)

```python
from beanie import Document, Indexed
from datetime import datetime

class UserDocument(Document):
    email: Indexed(str, unique=True)  # type: ignore
    username: Indexed(str, unique=True)  # type: ignore
    hashed_password: str
    role: str
    is_active: bool = True
    email_verified: bool = False
    created_at: datetime
    updated_at: datetime
    last_login: datetime | None = None

    class Settings:
        name = "users"
        indexes = ["email", "username"]

def get_document_models():
    return [UserDocument]
```

### Repository Implementation (`infrastructure/database/repositories/user_repository.py`)

```python
from typing import Optional
from uuid import UUID

from user_service.application.ports.repositories.user_repository import UserRepository
from user_service.domain.entities.user import User, UserRole
from user_service.infrastructure.database.models import UserDocument

class BeanieUserRepository(UserRepository):
    async def create(self, user: User) -> User:
        document = UserDocument(
            id=user.id,
            email=user.email,
            username=user.username,
            hashed_password=user.hashed_password,
            role=user.role.value,
            is_active=user.is_active,
            email_verified=user.email_verified,
            created_at=user.created_at,
            updated_at=user.updated_at,
            last_login=user.last_login,
        )
        await document.insert()
        return user

    async def get_by_email(self, email: str) -> Optional[User]:
        document = await UserDocument.find_one(UserDocument.email == email)
        if not document:
            return None
        return self._to_entity(document)

    def _to_entity(self, document: UserDocument) -> User:
        return User(
            id=document.id,
            email=document.email,
            username=document.username,
            hashed_password=document.hashed_password,
            role=UserRole(document.role),
            is_active=document.is_active,
            email_verified=document.email_verified,
            created_at=document.created_at,
            updated_at=document.updated_at,
            last_login=document.last_login,
        )
```

## Step 6: Create API Endpoints

### Routes (`presentation/api/v1/routes/users.py`)

```python
from fastapi import APIRouter, Depends, HTTPException, status

from user_service.application.dto.user_dto import RegisterUserDTO, UserDTO
from user_service.application.use_cases.user_use_cases import RegisterUserUseCase
from user_service.presentation.api.v1.dependencies import get_register_user_use_case

router = APIRouter(prefix="/users", tags=["users"])

@router.post(
    "/register",
    response_model=UserDTO,
    status_code=status.HTTP_201_CREATED,
)
async def register_user(
    data: RegisterUserDTO,
    use_case: RegisterUserUseCase = Depends(get_register_user_use_case),
) -> UserDTO:
    """Register a new user."""
    try:
        return await use_case.execute(data)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )
```

## Step 7: Configure Event Consumer

### Consumer (`consumer.py`)

```python
async def user_event_handler(message: dict) -> None:
    """Handle user events."""
    event_type = message.get("event_type")
    
    if event_type == "user.registered":
        # Send welcome email
        logger.info("sending_welcome_email", user_id=message.get("user_id"))
        # Implement email sending logic
    
    elif event_type == "user.email_verified":
        # Update analytics
        logger.info("user_verified", user_id=message.get("user_id"))

# Register handler
KafkaConsumer.register_handler("user-events", user_event_handler)
```

## Step 8: Run the Service

```bash
# Start all services
docker-compose up -d

# Check logs
docker-compose logs -f app

# Test the API
curl -X POST http://localhost:8000/api/v1/users/register \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@example.com",
    "username": "testuser",
    "password": "SecurePass123"
  }'
```

## Step 9: Add Tests

```python
# tests/unit/test_user_entity.py
def test_user_verify_email():
    user = User(email="test@example.com", username="test")
    assert user.email_verified is False
    
    user.verify_email()
    
    assert user.email_verified is True

# tests/integration/test_user_api.py
async def test_register_user():
    async with AsyncClient(app=app, base_url="http://test") as client:
        response = await client.post(
            "/api/v1/users/register",
            json={
                "email": "new@example.com",
                "username": "newuser",
                "password": "SecurePass123",
            },
        )
        
        assert response.status_code == 201
        data = response.json()
        assert data["email"] == "new@example.com"
```

## Benefits of This Template

1. **Clean Architecture**: Business logic isolated from infrastructure
2. **Testable**: Easy to test each layer independently
3. **Scalable**: Add new features without modifying existing code
4. **Event-Driven**: Loose coupling via events
5. **Production-Ready**: Includes monitoring, logging, rate limiting
6. **Type-Safe**: Full type hints for better IDE support
7. **Fast Development**: Pre-configured tools and patterns

## Next Steps

- Add authentication middleware
- Implement JWT token generation
- Add password reset flow
- Create admin endpoints
- Add email verification service
- Implement user profile management
- Add more event handlers
- Set up CI/CD pipeline
