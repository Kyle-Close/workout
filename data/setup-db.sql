-- Create Tables
CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT NOT NULL UNIQUE
);

CREATE TABLE IF NOT EXISTS user_weight (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    weight INTEGER NOT NULL,
    date TEXT NOT NULL,
    FOREIGN KEY (user_id) REFERENCES users(id)
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
    original_one_rep_max NOT NULL,
    current_one_rep_max REAL NOT NULL,
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
    optional BOOLEAN NOT NULL DEFAULT 0,
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
    reps_in_reserve INTEGER,
    notes TEXT,
    completed BOOLEAN NOT NULL DEFAULT 0
);

-- INSERTS
INSERT INTO users (username) VALUES ('Kyle Close');

INSERT INTO user_weight (user_id, weight, date) VALUES (1, 195, date('now'));

INSERT INTO exercises (name, equipment_type, weight_increment) VALUES ('Bench Press', 'BARBELL', 5);
INSERT INTO exercises (name, equipment_type, weight_increment) VALUES ('Squat', 'BARBELL', 5);
INSERT INTO exercises (name, equipment_type, weight_increment) VALUES ('Deadlift', 'BARBELL', 5);
INSERT INTO exercises (name, equipment_type, weight_increment) VALUES ('Overhead Press', 'BARBELL', 5);
INSERT INTO exercises (name, equipment_type, weight_increment) VALUES ('Romanian Deadlift', 'BARBELL', 5);
INSERT INTO exercises (name, equipment_type, weight_increment) VALUES ('Close Grip Bench Press', 'BARBELL', 5);
INSERT INTO exercises (name, equipment_type, weight_increment) VALUES ('DB Bench Press', 'DUMBBELL', 5);
INSERT INTO exercises (name, equipment_type, weight_increment) VALUES ('Incline Bench Press', 'DUMBBELL', 5);
INSERT INTO exercises (name, equipment_type, weight_increment) VALUES ('Leg Press', 'MACHINE', 5);
INSERT INTO exercises (name, equipment_type, weight_increment) VALUES ('T-Bar Rows', 'MACHINE', 2.5);
INSERT INTO exercises (name, equipment_type, weight_increment) VALUES ('Lat Pull-Downs', 'MACHINE', 10);
INSERT INTO exercises (name, equipment_type, weight_increment) VALUES ('Assisted Pull-Ups', 'MACHINE', 10);
INSERT INTO exercises (name, equipment_type, weight_increment) VALUES ('Bulgarian Split Squat', 'DUMBBELL', 5);
INSERT INTO exercises (name, equipment_type, weight_increment) VALUES ('Seated Machine Row', 'MACHINE', 10);
INSERT INTO exercises (name, equipment_type, weight_increment) VALUES ('Hanging Leg Raises', 'BODY WEIGHT', 5);
INSERT INTO exercises (name, equipment_type, weight_increment) VALUES ('Seated Leg Curl', 'MACHINE', 10);
INSERT INTO exercises (name, equipment_type, weight_increment) VALUES ('Reverse Pec Deck', 'MACHINE', 10);
INSERT INTO exercises (name, equipment_type, weight_increment) VALUES ('Cable Tricep Pushdown', 'MACHINE', 5);
INSERT INTO exercises (name, equipment_type, weight_increment) VALUES ('Seated Cable Row', 'MACHINE', 10);
INSERT INTO exercises (name, equipment_type, weight_increment) VALUES ('Face Pulls', 'MACHINE', 5);
INSERT INTO exercises (name, equipment_type, weight_increment) VALUES ('Hammer Curls', 'DUMBBELL', 5);
INSERT INTO exercises (name, equipment_type, weight_increment) VALUES ('Lateral Raises', 'DUMBBELL', 5);
INSERT INTO exercises (name, equipment_type, weight_increment) VALUES ('Calf Raises', 'MACHINE', 2.5);
INSERT INTO exercises (name, equipment_type, weight_increment) VALUES ('Plank', 'BODY WEIGHT', 5);
INSERT INTO exercises (name, equipment_type, weight_increment) VALUES ('Hip Thrusts', 'MACHINE', 2.5);
INSERT INTO exercises (name, equipment_type, weight_increment) VALUES ('Neutral-Grip Pulldown', 'MACHINE', 2.5);
INSERT INTO exercises (name, equipment_type, weight_increment) VALUES ('DB Curls', 'DUMBBELL', 5);
INSERT INTO exercises (name, equipment_type, weight_increment) VALUES ('Squat (2)', 'BARBELL', 5);

INSERT INTO user_one_rep_maxes (user_id, exercise_id, original_one_rep_max, current_one_rep_max) VALUES (1, 1, 155, 155); -- Bench Press
INSERT INTO user_one_rep_maxes (user_id, exercise_id, original_one_rep_max, current_one_rep_max) VALUES (1, 2, 170, 170); -- Squat
INSERT INTO user_one_rep_maxes (user_id, exercise_id, original_one_rep_max, current_one_rep_max) VALUES (1, 3, 200, 200); -- Deadlift
INSERT INTO user_one_rep_maxes (user_id, exercise_id, original_one_rep_max, current_one_rep_max) VALUES (1, 4, 90, 90); -- Overhead Press (Push Press)
INSERT INTO user_one_rep_maxes (user_id, exercise_id, original_one_rep_max, current_one_rep_max) VALUES (1, 5, 190, 190); -- Romanian Deadlift
INSERT INTO user_one_rep_maxes (user_id, exercise_id, original_one_rep_max, current_one_rep_max) VALUES (1, 6, 100, 100); -- Close Grip Bench Press
INSERT INTO user_one_rep_maxes (user_id, exercise_id, original_one_rep_max, current_one_rep_max) VALUES (1, 7, 65, 65); -- Dumbbell Bench Press
INSERT INTO user_one_rep_maxes (user_id, exercise_id, original_one_rep_max, current_one_rep_max) VALUES (1, 8, 50, 50); -- Incline Bench Press
INSERT INTO user_one_rep_maxes (user_id, exercise_id, original_one_rep_max, current_one_rep_max) VALUES (1, 9, 380, 380); -- Leg Press
INSERT INTO user_one_rep_maxes (user_id, exercise_id, original_one_rep_max, current_one_rep_max) VALUES (1, 10, 60, 60); -- T-Bar Rows
INSERT INTO user_one_rep_maxes (user_id, exercise_id, original_one_rep_max, current_one_rep_max) VALUES (1, 11, 150, 150); -- Lat Pull-Downs
INSERT INTO user_one_rep_maxes (user_id, exercise_id, original_one_rep_max, current_one_rep_max) VALUES (1, 12, 85, 170); -- Assisted Pull-Ups
INSERT INTO user_one_rep_maxes (user_id, exercise_id, original_one_rep_max, current_one_rep_max) VALUES (1, 13, 70, 70);  -- Bulgarian Split Squat
INSERT INTO user_one_rep_maxes (user_id, exercise_id, original_one_rep_max, current_one_rep_max) VALUES (1, 14, 150, 150); -- Seated Machine Row
INSERT INTO user_one_rep_maxes (user_id, exercise_id, original_one_rep_max, current_one_rep_max) VALUES (1, 15, 0, 0);   -- Hanging Leg Raises
INSERT INTO user_one_rep_maxes (user_id, exercise_id, original_one_rep_max, current_one_rep_max) VALUES (1, 16, 110, 110);  -- Seated Leg Curl
INSERT INTO user_one_rep_maxes (user_id, exercise_id, original_one_rep_max, current_one_rep_max) VALUES (1, 17, 70, 70);  -- Reverse Pec Deck
INSERT INTO user_one_rep_maxes (user_id, exercise_id, original_one_rep_max, current_one_rep_max) VALUES (1, 18, 85, 85);  -- Cable Tricep Pushdown
INSERT INTO user_one_rep_maxes (user_id, exercise_id, original_one_rep_max, current_one_rep_max) VALUES (1, 19, 145, 145); -- Seated Cable Row
INSERT INTO user_one_rep_maxes (user_id, exercise_id, original_one_rep_max, current_one_rep_max) VALUES (1, 20, 55, 55);  -- Face Pulls
INSERT INTO user_one_rep_maxes (user_id, exercise_id, original_one_rep_max, current_one_rep_max) VALUES (1, 21, 45, 45);  -- Hammer Curls
INSERT INTO user_one_rep_maxes (user_id, exercise_id, original_one_rep_max, current_one_rep_max) VALUES (1, 22, 30, 30);  -- Lateral Raises
INSERT INTO user_one_rep_maxes (user_id, exercise_id, original_one_rep_max, current_one_rep_max) VALUES (1, 23, 260, 260); -- Calf Raises
INSERT INTO user_one_rep_maxes (user_id, exercise_id, original_one_rep_max, current_one_rep_max) VALUES (1, 24, 0, 0);   -- Plank
INSERT INTO user_one_rep_maxes (user_id, exercise_id, original_one_rep_max, current_one_rep_max) VALUES (1, 25, 240, 240); -- Hip Thrusts
INSERT INTO user_one_rep_maxes (user_id, exercise_id, original_one_rep_max, current_one_rep_max) VALUES (1, 26, 130, 130); -- Neutral-Grip Pulldown
INSERT INTO user_one_rep_maxes (user_id, exercise_id, original_one_rep_max, current_one_rep_max) VALUES (1, 27, 35, 35);  -- DB Curls
INSERT INTO user_one_rep_maxes (user_id, exercise_id, original_one_rep_max, current_one_rep_max) VALUES (1, 28, 170, 170); -- Squat Accessory

INSERT INTO workout_programs (user_id, name) VALUES (1, 'Stronger by Science Linear Progression - 5 Day Varient');

-- SBS (5) - Day 1
INSERT INTO workout_day_exercises (exercise_id, workout_program_id, workout_day, target_sets, target_reps, intensity) VALUES (2, 1, 1, 3, 3, 87.5); -- Squat
INSERT INTO workout_day_exercises (exercise_id, workout_program_id, workout_day, target_sets, target_reps, intensity) VALUES (8, 1, 1, 3, 8, 75); -- Incline Bench Press
INSERT INTO workout_day_exercises (exercise_id, workout_program_id, workout_day, target_sets, target_reps, intensity) VALUES (10, 1, 1, 3, 8, 75); -- T-Bar Rows
-- SBS (5) - Day 1 (Optionals)
INSERT INTO workout_day_exercises (exercise_id, workout_program_id, workout_day, target_sets, target_reps, intensity, optional) VALUES (13, 1, 1, 3, 8, 75, 1); -- Bulgarian Split Squat
INSERT INTO workout_day_exercises (exercise_id, workout_program_id, workout_day, target_sets, target_reps, intensity, optional) VALUES (14, 1, 1, 3, 10, 75, 1); -- Seated Machine Row
INSERT INTO workout_day_exercises (exercise_id, workout_program_id, workout_day, target_sets, target_reps, intensity, optional) VALUES (15, 1, 1, 3, 12, 100, 1);  -- Hanging Leg Raises

-- SBS (5) - Day 2
INSERT INTO workout_day_exercises (exercise_id, workout_program_id, workout_day, target_sets, target_reps, intensity) VALUES (1, 1, 2, 3, 3, 87.5); -- Bench Press
INSERT INTO workout_day_exercises (exercise_id, workout_program_id, workout_day, target_sets, target_reps, intensity) VALUES (28, 1, 2, 3, 5, 82.5); -- Squat Accessory
-- SBS (5) - Day 2 (Optionals)
INSERT INTO workout_day_exercises (exercise_id, workout_program_id, workout_day, target_sets, target_reps, intensity, optional) VALUES (16, 1, 2, 3, 12, 75, 1); -- Seated Leg Curl
INSERT INTO workout_day_exercises (exercise_id, workout_program_id, workout_day, target_sets, target_reps, intensity, optional) VALUES (17, 1, 2, 3, 15, 70, 1); -- Reverse Pec Deck
INSERT INTO workout_day_exercises (exercise_id, workout_program_id, workout_day, target_sets, target_reps, intensity, optional) VALUES (18, 1, 2, 3, 12, 72.5, 1); -- Cable Tricep Pushdown

-- SBS (5) - Day 3
INSERT INTO workout_day_exercises (exercise_id, workout_program_id, workout_day, target_sets, target_reps, intensity) VALUES (3, 1, 3, 3, 3, 87.5); -- Deadlift
INSERT INTO workout_day_exercises (exercise_id, workout_program_id, workout_day, target_sets, target_reps, intensity) VALUES (7, 1, 3, 3, 5, 82.5); -- Dumbbell Bench Press
INSERT INTO workout_day_exercises (exercise_id, workout_program_id, workout_day, target_sets, target_reps, intensity) VALUES (12, 1, 3, 3, 8, 75); -- Assisted Pull-Ups
-- SBS (5) - Day 3 (Optionals)
INSERT INTO workout_day_exercises (exercise_id, workout_program_id, workout_day, target_sets, target_reps, intensity, optional) VALUES (19, 1, 3, 3, 10, 75, 1);  -- Seated Cable Row
INSERT INTO workout_day_exercises (exercise_id, workout_program_id, workout_day, target_sets, target_reps, intensity, optional) VALUES (20, 1, 3, 3, 15, 70, 1);  -- Face Pulls
INSERT INTO workout_day_exercises (exercise_id, workout_program_id, workout_day, target_sets, target_reps, intensity, optional) VALUES (21, 1, 3, 3, 12, 70, 1);  -- Hammer Curls

-- SBS (5) - Day 4
INSERT INTO workout_day_exercises (exercise_id, workout_program_id, workout_day, target_sets, target_reps, intensity) VALUES (4, 1, 4, 3, 3, 87.5); -- Overhead Press
INSERT INTO workout_day_exercises (exercise_id, workout_program_id, workout_day, target_sets, target_reps, intensity) VALUES (9, 1, 4, 3, 8, 75); -- Leg Press
-- SBS (5) - Day 4 (Optionals)
INSERT INTO workout_day_exercises (exercise_id, workout_program_id, workout_day, target_sets, target_reps, intensity, optional) VALUES (22, 1, 4, 3, 15, 70, 1);  -- Lateral Raises
INSERT INTO workout_day_exercises (exercise_id, workout_program_id, workout_day, target_sets, target_reps, intensity, optional) VALUES (23, 1, 4, 4, 12, 75, 1);  -- Calf Raises
INSERT INTO workout_day_exercises (exercise_id, workout_program_id, workout_day, target_sets, target_reps, intensity, optional) VALUES (24, 1, 4, 3, 60, 100, 1);   -- Plank (seconds; intensity unused)

-- SBS (5) - Day 5
INSERT INTO workout_day_exercises (exercise_id, workout_program_id, workout_day, target_sets, target_reps, intensity) VALUES (6, 1, 5, 3, 8, 75); -- Close Grip Bench Press
INSERT INTO workout_day_exercises (exercise_id, workout_program_id, workout_day, target_sets, target_reps, intensity) VALUES (5, 1, 5, 3, 8, 75); -- Romanian Deadlift
INSERT INTO workout_day_exercises (exercise_id, workout_program_id, workout_day, target_sets, target_reps, intensity) VALUES (11, 1, 5, 3, 8, 75); -- Lat Pull-Downs
-- SBS (5) - Day 5 (Optionals)
INSERT INTO workout_day_exercises (exercise_id, workout_program_id, workout_day, target_sets, target_reps, intensity, optional) VALUES (25, 1, 5, 3, 10, 75, 1);  -- Hip Thrusts
INSERT INTO workout_day_exercises (exercise_id, workout_program_id, workout_day, target_sets, target_reps, intensity, optional) VALUES (26, 1, 5, 3, 10, 75, 1);  -- Neutral-Grip Pulldown
INSERT INTO workout_day_exercises (exercise_id, workout_program_id, workout_day, target_sets, target_reps, intensity, optional) VALUES (27, 1, 5, 3, 12, 70, 1);  -- DB Curls
