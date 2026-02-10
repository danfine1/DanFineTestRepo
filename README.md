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

