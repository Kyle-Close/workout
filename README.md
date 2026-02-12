# Workout Tracker API

A RESTful API for tracking strength training programs, exercise logs, and progressive overload. Built with FastAPI and SQLite.

![Application Screenshot](docs/images/placeholder.png)

## Overview

Workout Tracker helps lifters follow structured training programs by automatically calculating working weights from one rep max percentages, tracking completed sets across weekly training cycles, and adjusting maxes over time based on performance. The API includes a built-in Stronger by Science (SBS) Linear Progression template and supports fully custom program creation.

### Key Features

- **Automated weight calculation** — Working weights derived from one rep max and prescribed intensity percentages, with plate breakdowns for barbell exercises
- **Progressive overload tracking** — One rep maxes update automatically based on completed workout performance
- **Weekly cycle management** — Exercise logs auto-generate for the next week when all mandatory work in the current week is complete
- **Program management** — Create custom programs or use the built-in SBS Linear Progression template (5-day, 28 exercises)
- **Body weight tracking** — Log and retrieve weight history over time
- **Exercise history** — View historical performance data for any exercise
- **Demo mode** — Pre-seeded demo account with 5 weeks of realistic training data for quick evaluation

## Tech Stack

- **Framework:** [FastAPI](https://fastapi.tiangolo.com/)
- **Database:** SQLite
- **Authentication:** JWT (python-jose) with bcrypt password hashing
- **Deployment:** Docker / [Fly.io](https://fly.io)
- **Testing:** pytest

## Requirements

- Python 3.13+
- [uv](https://github.com/astral-sh/uv) (recommended) or pip

## Getting Started

### Installation

```bash
# Clone the repository
git clone <repo-url>
cd workout

# Create virtual environment and install dependencies
uv sync

# Or with pip
python -m venv .venv
source .venv/bin/activate
pip install .
```

### Environment Variables

| Variable | Description | Default |
|---|---|---|
| `DATABASE_PATH` | Path to the SQLite database file | `/app/data/workout.db` |
| `JWT_SECRET_KEY` | Secret key for signing JWT tokens | `fallback-dev-key` |

### Running Locally

```bash
fastapi dev
```

The API will be available at `http://localhost:8000`. Interactive docs are at `http://localhost:8000/docs`.

### Running Tests

```bash
# Install test dependencies
uv sync --extra test

# Run the test suite
pytest
```

## API Reference

All endpoints except authentication require a Bearer token in the `Authorization` header.

### Authentication

| Method | Endpoint | Description |
|---|---|---|
| `POST` | `/register` | Create a new account |
| `POST` | `/login` | Log in with existing credentials |
| `POST` | `/demo-login` | Log in to the pre-seeded demo account |

### Programs

Users are limited to one program at a time. Delete the existing program before creating a new one.

| Method | Endpoint | Description |
|---|---|---|
| `GET` | `/programs` | List the user's programs |
| `GET` | `/programs/{program_id}` | Get full program detail (days, exercises) |
| `POST` | `/programs` | Create a custom program |
| `POST` | `/programs/recommended` | Create the SBS Linear Progression program |
| `PATCH` | `/programs/{program_id}` | Update program name |
| `PATCH` | `/programs/{program_id}/exercises` | Update exercise sets, reps, and intensity |
| `DELETE` | `/programs/{program_id}` | Delete a program and all associated data |

### Workout Logs

| Method | Endpoint | Description |
|---|---|---|
| `GET` | `/get-current-week-data` | Get the current week's exercise data with plate calculations |
| `GET` | `/week-logs` | Get exercise logs for a specific week |
| `GET` | `/active-week` | Get the current week number for a program |
| `POST` | `/generate-logs-week` | Manually generate a new week of logs |
| `PATCH` | `/update-logs` | Update exercise logs (sets, RIR, notes, completion) |

### One Rep Maxes

| Method | Endpoint | Description |
|---|---|---|
| `GET` | `/one-rep-maxes` | Get all one rep maxes for the current user |
| `PUT` | `/one-rep-maxes` | Set or update one rep maxes |

### Exercises

| Method | Endpoint | Description |
|---|---|---|
| `GET` | `/exercises` | List all available exercises |
| `GET` | `/exercises/history` | Get historical log data for a specific exercise |
| `POST` | `/exercises` | Create a new exercise (admin only) |

### Body Weight

| Method | Endpoint | Description |
|---|---|---|
| `GET` | `/user-weight` | Get weight history |
| `POST` | `/user-weight` | Log a new weight entry |
| `DELETE` | `/user-weight/{weight_id}` | Delete a weight entry |

## Project Structure

```
workout/
├── main.py                # FastAPI application and route definitions
├── auth/                  # JWT authentication and authorization
├── services/              # Business logic layer
├── repositories/          # Data access layer (SQL queries)
├── views/                 # Response models (Pydantic)
├── payloads/              # Request body models (Pydantic)
├── helpers/               # Utility functions (plate calculator, rounding)
├── enums/                 # Enum definitions (equipment types)
├── db/                    # Database connection management
├── data/                  # SQL schema and database files
└── tests/                 # Test suite
    ├── repositories/      # Repository unit tests
    ├── services/          # Service unit tests
    ├── test_api.py        # API integration tests
    └── conftest.py        # Test fixtures and in-memory database setup
```

## Deployment

### Docker

```bash
# Build
docker build -t workout .

# Run
docker run -p 8000:8000 -v ./data:/app/data workout
```

### Fly.io

```bash
fly deploy
```
