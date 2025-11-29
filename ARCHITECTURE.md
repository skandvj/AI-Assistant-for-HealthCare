# Architecture Documentation

## Overview

This dental practice chatbot is built using **Clean Architecture** principles and **SOLID** design patterns to ensure scalability, maintainability, and testability.

## Architecture Layers

### 1. Domain Layer (`domain/`)

**Purpose**: Contains core business logic and entities, independent of external frameworks.

**Components**:
- **Entities**: Core business objects (`Patient`, `Appointment`)
- **Value Objects**: Immutable objects (`TimeSlot`, `ConversationState`)

**Principles**:
- No dependencies on other layers
- Pure business logic
- Domain-driven design

### 2. Application Layer (`application/`)

**Purpose**: Orchestrates use cases and coordinates between domain and infrastructure.

**Components**:
- **Services**: Business logic services (`PatientService`, `AppointmentService`)
- **Graph**: LangGraph state machine for conversation workflows

**Principles**:
- Depends only on domain layer
- Implements use cases
- Coordinates domain objects

### 3. Infrastructure Layer (`infrastructure/`)

**Purpose**: External integrations and technical implementations.

**Components**:
- **Database**: Repository implementations (JSON, ready for Supabase)
- **LLM**: LLM provider implementations (DeepSeek, Gemini, OpenAI)
- **Tools**: LangChain tools for function calling

**Principles**:
- Implements interfaces from domain/application
- Dependency inversion
- Swappable implementations

### 4. Presentation Layer (`presentation/`)

**Purpose**: User interface and API endpoints.

**Components**:
- **API**: FastAPI routes and endpoints
- **Frontend**: Next.js React application

**Principles**:
- Thin layer, delegates to application services
- Handles HTTP requests/responses
- UI/UX concerns only

## SOLID Principles Implementation

### Single Responsibility Principle (SRP)

- Each class has one reason to change
- `PatientService` handles only patient operations
- `AppointmentService` handles only appointment operations
- Repositories handle only data persistence

### Open/Closed Principle (OCP)

- Repository interfaces allow extension without modification
- New LLM providers can be added without changing existing code
- Database implementations are swappable

### Liskov Substitution Principle (LSP)

- All repository implementations are interchangeable
- LLM providers implement the same interface
- Services work with any repository implementation

### Interface Segregation Principle (ISP)

- Separate interfaces for `PatientRepository` and `AppointmentRepository`
- Clients depend only on interfaces they use
- No fat interfaces

### Dependency Inversion Principle (DIP)

- High-level modules depend on abstractions (interfaces)
- Services depend on repository interfaces, not implementations
- Dependency injection used throughout

## Design Patterns

### 1. Repository Pattern

**Location**: `infrastructure/database/repository.py`

Abstracts data access, allowing easy swapping between JSON, Supabase, or other databases.

### 2. Factory Pattern

**Location**: `infrastructure/llm/llm_factory.py`

Creates LLM providers based on configuration, with auto-detection fallback.

### 3. Service Layer Pattern

**Location**: `application/services/`

Encapsulates business logic and coordinates between repositories and domain entities.

### 4. State Machine Pattern

**Location**: `application/graph/conversation_graph.py`

LangGraph manages conversation state and workflow transitions.

### 5. Dependency Injection

**Location**: Throughout the codebase

Services and repositories are injected, not instantiated directly.

## Conversation Flow (LangGraph)

```
User Message
    ↓
Agent Node (LLM)
    ↓
Has Tool Calls?
    ├─ Yes → Tools Node → Agent Node
    └─ No → End
```

The graph handles:
- Intent detection
- Tool selection
- State management
- Error recovery

## Data Flow

```
Frontend (React)
    ↓ HTTP Request
API Routes (FastAPI)
    ↓
Conversation Graph (LangGraph)
    ↓
LLM Provider (LangChain)
    ↓
Tools (LangChain Tools)
    ↓
Services (Application Layer)
    ↓
Repositories (Infrastructure)
    ↓
Database (JSON/Supabase)
```

## Error Handling Strategy

1. **Domain Level**: Validation in entities and value objects
2. **Service Level**: Business rule validation and error messages
3. **API Level**: HTTP error codes and user-friendly messages
4. **Graph Level**: Fallback responses and error recovery

## Scalability Considerations

### Horizontal Scaling

- Stateless API design
- Database can be moved to Supabase/PostgreSQL
- LLM calls are stateless

### Vertical Scaling

- Async/await throughout
- Efficient database queries
- Caching opportunities (future enhancement)

### Extensibility

- New appointment types: Add to `AppointmentType` enum
- New LLM providers: Implement `LLMProvider` interface
- New databases: Implement repository interfaces
- New tools: Add LangChain tools and register in graph

## Technology Stack

### Backend
- **FastAPI**: Modern, fast web framework
- **LangChain**: LLM orchestration
- **LangGraph**: State machine for conversations
- **Pydantic**: Data validation
- **Python 3.10+**: Language

### Frontend
- **Next.js 14**: React framework
- **TypeScript**: Type safety
- **Tailwind CSS**: Styling
- **Framer Motion**: Animations

### Database
- **JSON** (default): Local file storage
- **Supabase** (optional): PostgreSQL cloud database

### LLM Providers
- **DeepSeek**: Free tier available
- **Google Gemini**: Free tier available
- **OpenAI**: Free tier (if available)

## Security Considerations

1. **API Keys**: Stored in environment variables
2. **Input Validation**: Pydantic models validate all inputs
3. **CORS**: Configured for specific origins
4. **Error Messages**: Don't expose internal details

## Testing Strategy (Future Enhancement)

1. **Unit Tests**: Domain entities and services
2. **Integration Tests**: Repository implementations
3. **E2E Tests**: Full conversation flows
4. **Mock LLM**: For consistent testing

## Deployment Considerations

1. **Environment Variables**: All configuration via `.env`
2. **Database Migration**: Scripts for initialization
3. **Docker**: Containerization ready (future)
4. **CI/CD**: GitHub Actions ready (future)

## Performance Optimizations

1. **Async Operations**: All I/O operations are async
2. **Connection Pooling**: Ready for database connection pooling
3. **Caching**: Opportunities for LLM response caching
4. **Batch Operations**: For family scheduling

## Monitoring & Observability (Future)

1. **Logging**: Structured logging
2. **Metrics**: Request/response times
3. **Error Tracking**: Sentry integration
4. **Analytics**: Conversation analytics

