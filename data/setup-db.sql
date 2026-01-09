-- Create Tables
CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS workout_programs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    name TEXT,
    FOREIGN KEY (user_id) REFERENCES users(id)
);

CREATE TABLE IF NOT EXISTS workout_day (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    day_num INTEGER NOT NULL -- To keep track of the order
);

CREATE TABLE IF NOT EXISTS workout_program_days (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    workout_program_id INTEGER NOT NULL,
    workout_day_id INTEGER NOT NULL,
    FOREIGN KEY (workout_program_id) REFERENCES workout_programs(id),
    FOREIGN KEY (workout_day_id) REFERENCES workout_day(id)
);

CREATE TABLE IF NOT EXISTS exercises (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    equipment_type TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS workout_day_exercises (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    exercise_id INTEGER NOT NULL,
    workout_day_id INTEGER NOT NULL,
    sets INTEGER NOT NULL,
    reps INTEGER NOT NULL,
    weight REAL NOT NULL,
    FOREIGN KEY (exercise_id) REFERENCES exercises(id),
    FOREIGN KEY (workout_day_id) REFERENCES workout_day(id)
);

CREATE TABLE IF NOT EXISTS user_one_rep_maxes (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    exercise_id INTEGER NOT NULL,
    one_rep_max INTEGER NOT NULL
);
