# FastAPI Microservice Template

A production-ready Python microservice template following:
- **12-Factor App** methodology
- **Clean Architecture** principles
- **Event-Driven Architecture** patterns
- **Domain-Driven Design** concepts

## Features

- ✅ **FastAPI** for high-performance REST APIs
- ✅ **uv** for fast, reliable package management
- ✅ **Beanie ODM** for MongoDB with async support
- ✅ **Redis** for caching and rate limiting
- ✅ **Kafka** for event streaming with Avro serialization
- ✅ **Clean Architecture** with proper separation of concerns
- ✅ **Dependency Injection** pattern
- ✅ **Structured Logging** with correlation IDs
- ✅ **Rate Limiting** middleware
- ✅ **OpenTelemetry** integration (optional)
- ✅ **Docker** and Docker Compose for easy deployment
- ✅ **Type hints** throughout
- ✅ **Testing** setup with pytest

## Quick Start

### 1. Install Copier

```bash
pip install copier
```

### 2. Generate Your Project

```bash
copier copy gh:your-username/fastapi-microservice-template my-service
```

Or from local directory:

```bash
copier copy /path/to/fastapi-microservice-template my-service
```

### 3. Answer the Prompts

The template will ask you:
- Project name (e.g., "user-service")
- Project description
- Author information
- Service port (default: 8000)
- Python version (3.11 or 3.12)
- MongoDB database name
- Kafka topics
- Optional features (authentication, observability)

### 4. Navigate to Your Project

```bash
cd my-service
```

### 5. Start Development

```bash
# With Docker Compose (recommended)
docker-compose up -d

# Or manually
make install
make dev
```

## Project Structure

```
my-service/
├── src/
│   └── my_service/
│       ├── domain/              # Business logic (entities, events)
│       ├── application/         # Use cases and ports
│       ├── infrastructure/      # Technical implementations
│       │   ├── database/       # Beanie repositories
│       │   ├── cache/          # Redis manager
│       │   ├── messaging/      # Kafka producer/consumer
│       │   └── config/         # Settings and logging
│       └── presentation/        # FastAPI routes and middleware
├── tests/
│   ├── unit/
│   └── integration/
├── docker-compose.yml
├── Dockerfile
├── pyproject.toml
├── Makefile
└── README.md
```

## Architecture Overview

### Clean Architecture Layers

1. **Domain Layer** (`domain/`)
   - Pure business logic
   - No framework dependencies
   - Entities, value objects, domain events

2. **Application Layer** (`application/`)
   - Use cases (business workflows)
   - Ports (interfaces) for dependency inversion
   - DTOs for data transfer

3. **Infrastructure Layer** (`infrastructure/`)
   - Database implementations
   - Message brokers
   - External services
   - Configuration

4. **Presentation Layer** (`presentation/`)
   - FastAPI routes
   - Request/response schemas
   - Middleware

### Event-Driven Architecture

- **Producer**: Publishes domain events to Kafka with Avro encoding
- **Consumer**: Separate process that listens to Kafka topics
- **Decoupling**: Services communicate via events, not direct calls

### 12-Factor App Compliance

1. ✅ **Codebase**: One codebase tracked in Git
2. ✅ **Dependencies**: Explicitly declared in pyproject.toml
3. ✅ **Config**: Environment variables via .env
4. ✅ **Backing services**: Attached via URLs (MongoDB, Redis, Kafka)
5. ✅ **Build, release, run**: Strict separation
6. ✅ **Processes**: Stateless, share-nothing processes
7. ✅ **Port binding**: Self-contained service
8. ✅ **Concurrency**: Scale via process model
9. ✅ **Disposability**: Fast startup and graceful shutdown
10. ✅ **Dev/prod parity**: Same services, containers
11. ✅ **Logs**: Treat as event streams to stdout
12. ✅ **Admin processes**: Run as one-off processes

## Usage Examples

### Adding a New Entity

1. Create domain entity in `domain/entities/`:
```python
@dataclass
class Product:
    id: UUID
    name: str
    price: Decimal
```

2. Create repository port in `application/ports/repositories/`:
```python
class ProductRepository(ABC):
    @abstractmethod
    async def create(self, product: Product) -> Product:
        pass
```

3. Implement repository in `infrastructure/database/repositories/`:
```python
class BeanieProductRepository(ProductRepository):
    async def create(self, product: Product) -> Product:
        # Implementation using Beanie
```

4. Create use case in `application/use_cases/`:
```python
class CreateProductUseCase:
    def __init__(self, repo: ProductRepository, publisher: EventPublisher):
        self.repo = repo
        self.publisher = publisher
```

5. Add API route in `presentation/api/v1/routes/`:
```python
@router.post("/products/")
async def create_product(data: CreateProductDTO, use_case: CreateProductUseCase):
    return await use_case.execute(data)
```

### Publishing Events

```python
from my_service.domain.events.product_events import ProductCreatedEvent

event = ProductCreatedEvent(
    product_id=product.id,
    name=product.name,
    price=product.price
)

await event_publisher.publish(event, "product-events")
```

### Consuming Events

In `consumer.py`:
```python
async def product_event_handler(message: dict) -> None:
    logger.info("product_event_received", message=message)
    # Process the event

KafkaConsumer.register_handler("product-events", product_event_handler)
```

### Using Cache

```python
from my_service.infrastructure.cache.redis_manager import RedisManager

# Set cache
await RedisManager.set("user:123", user_data, ttl=3600)

# Get cache
user_data = await RedisManager.get("user:123")

# Delete cache
await RedisManager.delete("user:123")
```

## Development Commands

```bash
# Install dependencies
make install

# Run development server
make dev

# Run event consumer
make consumer

# Run tests
make test

# Run tests with coverage
make test-cov

# Lint code
make lint

# Format code
make format

# Clean build artifacts
make clean
```

## Docker Commands

```bash
# Build image
make docker-build

# Start all services
make docker-up

# View logs
make docker-logs

# Stop services
make docker-down
```

## Environment Variables

Copy `.env.example` to `.env` and configure:

```env
# Application
APP_NAME=my-service
ENVIRONMENT=development
LOG_LEVEL=INFO

# Database
MONGODB_URL=mongodb://localhost:27017
MONGODB_DATABASE=my_service_db

# Redis
REDIS_URL=redis://localhost:6379/0

# Kafka
KAFKA_BOOTSTRAP_SERVERS=localhost:9092
KAFKA_TOPICS=my_service_events
```

## Testing

### Unit Tests
```bash
pytest tests/unit/
```

### Integration Tests
```bash
pytest tests/integration/
```

### Coverage Report
```bash
pytest --cov=src --cov-report=html
open htmlcov/index.html
```

## Updating the Template

If the template is updated, you can update your project:

```bash
copier update
```

This will apply changes from the template while preserving your customizations.

## Best Practices

### Domain Layer
- Keep business logic pure (no framework dependencies)
- Use value objects for domain concepts
- Emit domain events for important state changes

### Application Layer
- Use cases should be single-purpose
- Define ports (interfaces) for external dependencies
- Keep DTOs simple and validation-focused

### Infrastructure Layer
- Implement ports defined in application layer
- Handle technical concerns (databases, APIs, etc.)
- Configuration via environment variables

### Presentation Layer
- Thin controllers, delegate to use cases
- Validate input at API boundary
- Use appropriate HTTP status codes

## Troubleshooting

### MongoDB Connection Issues
- Ensure MongoDB is running
- Check `MONGODB_URL` in `.env`
- Verify network connectivity

### Kafka Issues
- Verify Kafka and Zookeeper are running
- Check `KAFKA_BOOTSTRAP_SERVERS` configuration
- Ensure topics are created

### Redis Issues
- Confirm Redis is running
- Check `REDIS_URL` in `.env`
- Test connection: `redis-cli ping`

## Contributing

When extending the template:
1. Maintain clean architecture principles
2. Add tests for new features
3. Update documentation
4. Follow existing code style

## License

[Your License Here]

## Support

For issues and questions:
- GitHub Issues: [Your Repo URL]
- Documentation: [Your Docs URL]
