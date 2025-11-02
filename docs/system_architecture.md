
# System Architecture

This document outlines the high-level architecture of the RespiraAlly audio bot system. The system is designed using a microservices-oriented architecture to ensure scalability, maintainability, and separation of concerns.

## Architecture Diagram

The following diagram illustrates the main components of the system and their interactions.

```mermaid
graph TD
    subgraph "User Domain"
        User[<font size="4"><b>User</b></font><br/>(Browser/Mobile)]
    end

    subgraph "Public Network"
        User -- HTTPS --> Nginx
    end

    subgraph "Core Services"
        Nginx[<font size="4"><b>Nginx</b></font><br/>Reverse Proxy]
        Frontend[<font size="4"><b>Frontend</b></font><br/>(React UI)]
        WebApp[<font size="4"><b>Web App</b></font><br/>(Flask API)]
    end

    subgraph "AI & Worker Services"
        AIWorker[<font size="4"><b>AI Worker</b></font><br/>(Python)]
        RabbitMQ[<font size="4"><b>RabbitMQ</b></font><br/>Message Queue]
    end

    subgraph "Data & Storage Layer"
        Postgres[<font size="4"><b>PostgreSQL</b></font><br/>Primary DB]
        Redis[<font size="4"><b>Redis</b></font><br/>Cache]
        MinIO[<font size="4"><b>MinIO</b></font><br/>Object Storage]
        Milvus[<font size="4"><b>Milvus</b></font><br/>Vector DB]
    end
    
    subgraph "External Services"
        LineAPI[<font size="4"><b>LINE API</b></font>]
        OpenAI[<font size="4"><b>OpenAI/Google AI</b></font>]
    end

    %% Connections
    Nginx -- Serves --> Frontend
    Nginx -- /api --> WebApp

    User -- Interacts with --> Frontend
    Frontend -- REST API Calls --> WebApp
    
    WebApp -- Reads/Writes --> Postgres
    WebApp -- Caches data in --> Redis
    WebApp -- Publishes tasks --> RabbitMQ
    WebApp -- Interacts with --> LineAPI
    WebApp -- Manages files in --> MinIO
    WebApp -- Vector search --> Milvus

    AIWorker -- Consumes tasks from --> RabbitMQ
    AIWorker -- Reads/Writes --> Postgres
    AIWorker -- Accesses files in --> MinIO
    AIWorker -- Calls --> OpenAI
    AIWorker -- Vector search/store --> Milvus
```

## Component Descriptions

### 1. Nginx (Reverse Proxy)
- **Role:** The single entry point for all incoming HTTP traffic.
- **Responsibilities:**
    - Routes requests to the appropriate service (`frontend` or `web-app`).
    - Handles SSL termination.
    - Can be configured for load balancing in a production environment.

### 2. Frontend (React)
- **Role:** The user interface of the application.
- **Responsibilities:**
    - Provides a rich, interactive user experience.
    - Communicates with the `web-app` via a REST API.
    - Handles user authentication and displays data.

### 3. Web App (Flask)
- **Role:** The core backend service.
- **Responsibilities:**
    - Exposes a REST API for the frontend and external services (e.g., LINE webhooks).
    - Manages business logic, user data, and authentication.
    - Interacts with the `PostgreSQL` database for persistent storage.
    - Uses `Redis` for caching and session management.
    - Publishes long-running or asynchronous tasks (like audio processing) to `RabbitMQ`.

### 4. AI Worker (Python)
- **Role:** A background service for processing computationally intensive tasks.
- **Responsibilities:**
    - Consumes tasks from the `RabbitMQ` queue.
    - Performs Speech-to-Text (STT) and Text-to-Speech (TTS) conversions.
    - Interacts with external AI services (e.g., OpenAI, Google AI) for language model processing.
    - Utilizes `Milvus` for vector embedding storage and retrieval (RAG).
    - Stores and retrieves audio files from `MinIO` object storage.

### 5. Data & Storage Layer
- **PostgreSQL:** The primary relational database for storing structured data like user profiles, messages, and metrics.
- **Redis:** An in-memory data store used for caching frequently accessed data to reduce database load and improve response times.
- **RabbitMQ:** A message broker that decouples the `web-app` from the `ai-worker`, allowing for reliable, asynchronous task processing.
- **MinIO:** An S3-compatible object storage service used to store large binary files, such as user-uploaded audio.
- **Milvus:** A vector database used to store and search high-dimensional vector embeddings, which is crucial for AI-powered features like semantic search and Retrieval-Augmented Generation (RAG).

### 6. External Services
- **LINE API:** Used for integrating with the LINE messaging platform, enabling features like login and push notifications.
- **OpenAI/Google AI:** External large language model (LLM) providers that power the core conversational AI capabilities.
