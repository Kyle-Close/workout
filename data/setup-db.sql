-- Create Tables
CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT NOT NULL UNIQUE
);

CREATE TABLE IF NOT EXISTS workout_programs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    name TEXT,
    FOREIGN KEY (user_id) REFERENCES users(id)
);

CREATE TABLE IF NOT EXISTS exercises (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    equipment_type TEXT NOT NULL,
    weight_increment REAL
);

CREATE TABLE IF NOT EXISTS user_one_rep_maxes (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    exercise_id INTEGER NOT NULL,
    one_rep_max REAL NOT NULL,
    FOREIGN KEY (user_id) REFERENCES users(id),
    FOREIGN KEY (exercise_id) REFERENCES exercises(id)
);

CREATE TABLE IF NOT EXISTS workout_day_exercises (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    exercise_id INTEGER NOT NULL,
    workout_program_id INTEGER NOT NULL,
    workout_day INTEGER NOT NULL,
    target_sets INTEGER NOT NULL,
    target_reps INTEGER NOT NULL,
    intensity REAL NOT NULL,
    FOREIGN KEY (exercise_id) REFERENCES exercises(id),
    FOREIGN KEY (workout_program_id) REFERENCES workout_programs(id)
);

CREATE TABLE IF NOT EXISTS exercise_log (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    workout_day_exercise_id INTEGER NOT NULL,
    program_week INTEGER NOT NULL,
    weight INTEGER NOT NULL,
    sets_completed INTEGER,
    reps_completed INTEGER,
    notes TEXT,
    completed BOOLEAN NOT NULL DEFAULT 0
);

-- INSERTS
INSERT INTO users (username) VALUES ('Kyle Close');

INSERT INTO exercises (name, equipment_type, weight_increment) VALUES ('Bench Press', 'BARBELL', 5);
INSERT INTO exercises (name, equipment_type, weight_increment) VALUES ('Squat', 'BARBELL', 5);
INSERT INTO exercises (name, equipment_type, weight_increment) VALUES ('Deadlift', 'BARBELL', 5);
INSERT INTO exercises (name, equipment_type, weight_increment) VALUES ('Overhead Press', 'BARBELL', 5);
INSERT INTO exercises (name, equipment_type, weight_increment) VALUES ('Romanian Deadlift', 'BARBELL', 5);
INSERT INTO exercises (name, equipment_type, weight_increment) VALUES ('Close Grip Bench Press', 'BARBELL', 5);
INSERT INTO exercises (name, equipment_type, weight_increment) VALUES ('Bench Press', 'DUMBBELL', 5);
INSERT INTO exercises (name, equipment_type, weight_increment) VALUES ('Incline Bench Press', 'DUMBBELL', 5);
INSERT INTO exercises (name, equipment_type, weight_increment) VALUES ('Leg Press', 'MACHINE', 5);
INSERT INTO exercises (name, equipment_type, weight_increment) VALUES ('T-Bar Rows', 'MACHINE', 2.5);
INSERT INTO exercises (name, equipment_type, weight_increment) VALUES ('Lat Pull-Downs', 'MACHINE', 10);
INSERT INTO exercises (name, equipment_type, weight_increment) VALUES ('Assisted Pull-Ups', 'MACHINE', -10);

INSERT INTO user_one_rep_maxes (user_id, exercise_id, one_rep_max) VALUES (1, 1, 160); -- Bench Press
INSERT INTO user_one_rep_maxes (user_id, exercise_id, one_rep_max) VALUES (1, 2, 180); -- Squat
INSERT INTO user_one_rep_maxes (user_id, exercise_id, one_rep_max) VALUES (1, 3, 212); -- Deadlift
INSERT INTO user_one_rep_maxes (user_id, exercise_id, one_rep_max) VALUES (1, 4, 100); -- Overhead Press
INSERT INTO user_one_rep_maxes (user_id, exercise_id, one_rep_max) VALUES (1, 5, 210); -- Romanian Deadlift
INSERT INTO user_one_rep_maxes (user_id, exercise_id, one_rep_max) VALUES (1, 6, 120); -- Close Grip Bench Press
INSERT INTO user_one_rep_maxes (user_id, exercise_id, one_rep_max) VALUES (1, 7, 70); -- Dumbbell Bench Press
INSERT INTO user_one_rep_maxes (user_id, exercise_id, one_rep_max) VALUES (1, 8, 58); -- Incline Bench Press
INSERT INTO user_one_rep_maxes (user_id, exercise_id, one_rep_max) VALUES (1, 9, 420); -- Leg Press
INSERT INTO user_one_rep_maxes (user_id, exercise_id, one_rep_max) VALUES (1, 10, 65); -- T-Bar Rows
INSERT INTO user_one_rep_maxes (user_id, exercise_id, one_rep_max) VALUES (1, 11, 158); -- Lat Pull-Downs
INSERT INTO user_one_rep_maxes (user_id, exercise_id, one_rep_max) VALUES (1, 12, 50); -- Assisted Pull-Ups

INSERT INTO workout_programs (user_id, name) VALUES (1, 'Stronger by Science Linear Progression - 5 Day Varient');

-- SBS (5) - Day 1
INSERT INTO workout_day_exercises (exercise_id, workout_program_id, workout_day, target_sets, target_reps, intensity) VALUES (2, 1, 1, 3, 3, 87.5); -- Squat
INSERT INTO workout_day_exercises (exercise_id, workout_program_id, workout_day, target_sets, target_reps, intensity) VALUES (8, 1, 1, 3, 8, 75); -- Incline Bench Press
INSERT INTO workout_day_exercises (exercise_id, workout_program_id, workout_day, target_sets, target_reps, intensity) VALUES (10, 1, 1, 3, 8, 75); -- T-Bar Rows

-- SBS (5) - Day 2
INSERT INTO workout_day_exercises (exercise_id, workout_program_id, workout_day, target_sets, target_reps, intensity) VALUES (1, 1, 2, 3, 3, 87.5); -- Bench Press
INSERT INTO workout_day_exercises (exercise_id, workout_program_id, workout_day, target_sets, target_reps, intensity) VALUES (2, 1, 2, 3, 5, 82.5); -- Squat

-- SBS (5) - Day 3
INSERT INTO workout_day_exercises (exercise_id, workout_program_id, workout_day, target_sets, target_reps, intensity) VALUES (3, 1, 3, 3, 3, 87.5); -- Deadlift
INSERT INTO workout_day_exercises (exercise_id, workout_program_id, workout_day, target_sets, target_reps, intensity) VALUES (7, 1, 3, 3, 5, 82.5); -- Dumbbell Bench Press
INSERT INTO workout_day_exercises (exercise_id, workout_program_id, workout_day, target_sets, target_reps, intensity) VALUES (12, 1, 3, 3, 8, 75); -- Assisted Pull-Ups

-- SBS (5) - Day 4
INSERT INTO workout_day_exercises (exercise_id, workout_program_id, workout_day, target_sets, target_reps, intensity) VALUES (4, 1, 4, 3, 3, 87.5); -- Overhead Press
INSERT INTO workout_day_exercises (exercise_id, workout_program_id, workout_day, target_sets, target_reps, intensity) VALUES (9, 1, 4, 3, 8, 75); -- Leg Press

-- SBS (5) - Day 5
INSERT INTO workout_day_exercises (exercise_id, workout_program_id, workout_day, target_sets, target_reps, intensity) VALUES (6, 1, 5, 3, 8, 75); -- Close Grip Bench Press
INSERT INTO workout_day_exercises (exercise_id, workout_program_id, workout_day, target_sets, target_reps, intensity) VALUES (5, 1, 5, 3, 8, 75); -- Romanian Deadlift
INSERT INTO workout_day_exercises (exercise_id, workout_program_id, workout_day, target_sets, target_reps, intensity) VALUES (11, 1, 5, 3, 8, 75); -- Lat Pull-Downs
