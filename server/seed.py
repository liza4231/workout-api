#!/usr/bin/env python3

from datetime import date
from app import app
from models import db, Exercise, Workout, WorkoutExercise


with app.app_context():
    print("Deleting old data...")

    WorkoutExercise.query.delete()
    Workout.query.delete()
    Exercise.query.delete()

    print("Creating exercises...")

    pushups = Exercise(
        name="Push Ups",
        category="Strength",
        equipment_needed=False
    )

    treadmill = Exercise(
        name="Treadmill Run",
        category="Cardio",
        equipment_needed=True
    )

    squats = Exercise(
        name="Squats",
        category="Strength",
        equipment_needed=False
    )

    stretching = Exercise(
        name="Stretching",
        category="Flexibility",
        equipment_needed=False
    )

    db.session.add_all([
        pushups,
        treadmill,
        squats,
        stretching
    ])

    db.session.commit()

    print("Creating workouts...")

    workout_one = Workout(
        date=date(2026, 6, 18),
        duration_minutes=45,
        notes="Basic full body workout."
    )

    workout_two = Workout(
        date=date(2026, 6, 19),
        duration_minutes=30,
        notes="Short cardio and stretching session."
    )

    db.session.add_all([
        workout_one,
        workout_two
    ])

    db.session.commit()

    print("Adding exercises to workouts...")

    workout_exercise_one = WorkoutExercise(
        workout_id=workout_one.id,
        exercise_id=pushups.id,
        sets=3,
        reps=12
    )

    workout_exercise_two = WorkoutExercise(
        workout_id=workout_one.id,
        exercise_id=squats.id,
        sets=4,
        reps=10
    )

    workout_exercise_three = WorkoutExercise(
        workout_id=workout_two.id,
        exercise_id=treadmill.id,
        duration_seconds=900
    )

    workout_exercise_four = WorkoutExercise(
        workout_id=workout_two.id,
        exercise_id=stretching.id,
        duration_seconds=600
    )

    db.session.add_all([
        workout_exercise_one,
        workout_exercise_two,
        workout_exercise_three,
        workout_exercise_four
    ])

    db.session.commit()

    print("Done seeding database!")