# Workout

A FastAPI-based workout tracking API that manages exercise programs, logs workouts, and tracks one rep maxes.

## Features

- Track exercise logs by week within a workout program
- Automatically calculate weights based on one rep max and intensity percentages
- Update one rep maxes based on completed workout performance
- Auto-generate new weekly exercise logs when a week is completed

## Requirements

- Python 3.13+
- [uv](https://github.com/astral-sh/uv) (recommended) or pip

## Setup

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

## Running Locally

```bash
# Set database path (optional, defaults to /app/data/workout.db)
export DATABASE_PATH="./data/workout.db"

# Run the server
fastapi dev
```

The API will be available at `http://localhost:8000`.

## API Endpoints

### `GET /get-current-week-data`

Returns the current week's exercise data for a user's workout program.

**Query Parameters:**
- `user_id` (int): The user ID
- `workout_program_id` (int): The workout program ID

### `POST /generate-logs-week`

Generates a new week of exercise logs for a workout program.

**Request Body:**
```json
{
  "user_id": 1,
  "workout_program_id": 1
}
```

### `PATCH /update-logs`

Updates exercise logs and automatically recalculates one rep maxes. Generates a new week of logs if the current week is completed.

**Request Body:**
```json
[
  {
    "id": 1,
    "user_id": 1,
    "workout_day_exercise_id": 1,
    "program_week": 1,
    "weight": 135,
    "sets_completed": 3,
    "reps_in_reserve": 2,
    "notes": "Felt good",
    "completed": true
  }
]
```

## Project Structure

```
workout/
├── main.py              # FastAPI application and routes
├── db/                  # Database connection
├── services/            # Business logic
├── repositories/        # Data access layer
├── views/               # Pydantic models
├── payloads/            # Request payload models
├── helpers/             # Utility functions
└── enums/               # Enum definitions
```

## Deployment

The project is configured for deployment on [Fly.io](https://fly.io).

```bash
fly deploy
```

## Docker

```bash
# Build
docker build -t workout .

# Run
docker run -p 8000:8000 -v ./data:/app/data workout
```
