# quotesboard

## Overview

A FastAPI-based service designed to archive and serve quotes from family and friends that I've been writing down for years. This project provides a structured way to query, filter, and analyze the faces and musings in our lives. It also provides a way for me to get to know FastAPI and the related toolings, as I've been meaning to learn it recently.

## Features

- **Randomized Retrieval:** Fetch a random quote from the entire collection.
- **Author Filtering:** Retrieve quotes or a random selection filtered by a specific author.
- **Statistical Analysis:** Built-in endpoints to calculate quote distributions and top contributors.

## Technical Stack

- **Framework:** [FastAPI](https://fastapi.tiangolo.com/)
- **Database:** SQLite (Development) / PostgreSQL (Production)
- **ORM:** [SQLModel](https://sqlmodel.tiangolo.com/)
- **Infrastructure:** Dockerized and orchestrated via Docker Compose.
- **Networking:** Hosted via Caddy with CloudFlare DNS management.

## Configuring

### Environment Variables

The application requires the following environment variables to be defined in a `.env` file:

| Variable | Description | Example |
| --- | --- | --- |
| `DB_NAME` | The name of the database file, as a filestem relative to the current working directory (e.g., `./<DB_NAME>.db`). | `database` |

If you elect to instead use Postgres, you'll have to also define the following:

| Variable | Description | Example | Default |
| --- | --- | --- | --- |
| `DB_TYPE` | The type of database connection to use. | `postgresql://user:pass@db:5432/quotes` | `"SQLITE"` |
| `DB_NAME` | The name of the Postgres database. | `quotesboard_db` | N/A |
| `DB_USER` | Database username. | `myuser` | N/A |
| `DB_PASSWORD` | Database password. | `hunter2` | N/A |
| `DB_PORT` | The port the Postgres instance is runnning on. | 5432 | 5432 |
| `DB_HOSTNAME` | The hostname of the Postgres instance. | `postgres` | `"quotesboard-postgres"` |
<!-- | `ADMIN_PASSWORD` | Used for quote creation and management | `your-secure-password` |
| `SITE_PASSWORD` | Shared password for group access | `friendship-is-magic` | -->

### Docker Secrets

This app will look for certain values in [Docker secret files](https://docs.docker.com/compose/how-tos/use-secrets/). If a setting is set based on one such file, the corresponding environment variable will be ignored. This configuration method is likely better suited for the productionized container, rather than your local development environment.

## Installation and Local Development

### Prerequisites

- Python 3.10+
- Docker and Docker Compose

### Setup

1. Clone the repository.
2. Create and populate the `.env` file based on the table above.
3. Set up your virtual environment. I love [`uv`](https://docs.astral.sh/uv/), with it it's simply `uv venv && uv sync`.
4. [Insert command for running migrations].

### Running Locally

To start the application for development:

```bash
fastapi dev
```

## Testing

To ensure the integrity of the friend lore, we maintain high test coverage using `pytest`.

```bash
# Run tests with coverage report
pytest --cov=app --cov-report=term
```

## Deployment

This project is built to be deployed at `quotesboard.mattdies.com`.

### Docker Architecture

The deployment utilizes a file similar to the [`prod/docker-compose.yaml`](./prod/docker-compose.yaml) file, which contains:

- **App:** The FastAPI container, built from a custom [Dockerfile](./prod/Dockerfile).
- **Database:** A PostgreSQL instance for persistent storage.

To fully deploy this app, you'll need to create your own to suit your specific need. Once you have, you can deploy to production with:

```bash
docker compose up -d <compose_filepath>
```

## API Documentation

Once the application is running, interactive documentation is available at:

- **Swagger UI:** `https://quotesboard.mattdies.com/docs`
- **ReDoc:** `https://quotesboard.mattdies.com/redoc`

## License

[MIT](./LICENSE).
