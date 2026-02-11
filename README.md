## FastAPI + Postgres (Dockerized)

This project is a simple FastAPI application using SQLAlchemy with a Postgres database.  
Everything runs in Docker using `docker-compose`.

### Prerequisites

- **Docker**: Install Docker Desktop from the official site: [Docker Desktop](https://www.docker.com/products/docker-desktop/)
- **Docker Compose**: Included with recent versions of Docker Desktop

Verify Docker is installed:

```bash
docker --version
docker compose version || docker-compose --version
```

### Configuration

1. **Create your `.env` file** in the project root:

   ```bash
   cp .env.example .env
   ```

2. (Optional) Edit `.env` and adjust:
   - `POSTGRES_USER`, `POSTGRES_PASSWORD`, `POSTGRES_DB`
   - `PGADMIN_DEFAULT_EMAIL`, `PGADMIN_DEFAULT_PASSWORD`
   - `DATABASE_URL` (default already points at the Docker Postgres service: `postgres-db`)

### Running the stack

From the project root (runs in background):

```bash
docker-compose up --build -d
```

### Services

- **FastAPI app**: `http://localhost:8000`
- **pgAdmin UI**: `http://localhost:5050`
  - Login with `PGADMIN_DEFAULT_EMAIL` / `PGADMIN_DEFAULT_PASSWORD` from `.env`
  - Add a new server:
    - **Host**: `postgres-db`
    - **Port**: `5432`
    - **Username**: `POSTGRES_USER`
    - **Password**: `POSTGRES_PASSWORD`

### Architecture (short overview)

- **API layer**: `src/main.py` defines the FastAPI application, request/response models wiring, and the three core endpoints: `POST /links`, `GET /{short_code}`, and `GET /stats`.
- **Domain models**: `src/models.py` contains Pydantic models for link creation, link info, link resolution, and per-link statistics (including monthly breakdown items).
- **Persistence layer**: `src/db_models.py` defines the SQLAlchemy models `LinkModel` and `LinkClickModel`, which store links, aggregate counters, and individual click events with timestamps.
- **Database setup**: `src/database.py` configures the SQLAlchemy engine and session factory using `DATABASE_URL` from the environment; `main.py` calls `Base.metadata.create_all` so tables are created when the app starts.
- **Runtime composition**: Docker (`Dockerfile`, `docker-compose.yml`) runs the FastAPI app alongside Postgres, and the endpoints interact with the DB via SQLAlchemy sessions injected through FastAPI dependencies.

