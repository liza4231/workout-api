from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import validates
from sqlalchemy.ext.associationproxy import association_proxy

db = SQLAlchemy()


class Exercise(db.Model):
    __tablename__ = "exercises"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False, unique=True)
    category = db.Column(db.String, nullable=False)
    equipment_needed = db.Column(db.Boolean, default=False)

    workout_exercises = db.relationship(
        "WorkoutExercise",
        back_populates="exercise",
        cascade="all, delete-orphan"
    )

    workouts = association_proxy("workout_exercises", "workout")

    @validates("name")
    def validate_name(self, key, value):
        if not value or len(value.strip()) < 3:
            raise ValueError("Exercise name must be at least 3 characters.")
        return value.strip()

    @validates("category")
    def validate_category(self, key, value):
        allowed = ["Strength", "Cardio", "Flexibility"]

        if value not in allowed:
            raise ValueError("Category must be Strength, Cardio, or Flexibility.")
        return value

    def __repr__(self):
        return f"<Exercise {self.name}>"


class Workout(db.Model):
    __tablename__ = "workouts"

    id = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.Date, nullable=False)
    duration_minutes = db.Column(db.Integer, nullable=False)
    notes = db.Column(db.Text)

    workout_exercises = db.relationship(
        "WorkoutExercise",
        back_populates="workout",
        cascade="all, delete-orphan"
    )

    exercises = association_proxy("workout_exercises", "exercise")

    @validates("duration_minutes")
    def validate_duration(self, key, value):
        if value is None or value <= 0:
            raise ValueError("Duration must be greater than 0.")
        return value

    def __repr__(self):
        return f"<Workout {self.date}>"


class WorkoutExercise(db.Model):
    __tablename__ = "workout_exercises"

    id = db.Column(db.Integer, primary_key=True)

    workout_id = db.Column(
        db.Integer,
        db.ForeignKey("workouts.id"),
        nullable=False
    )

    exercise_id = db.Column(
        db.Integer,
        db.ForeignKey("exercises.id"),
        nullable=False
    )

    reps = db.Column(db.Integer)
    sets = db.Column(db.Integer)
    duration_seconds = db.Column(db.Integer)

    workout = db.relationship("Workout", back_populates="workout_exercises")
    exercise = db.relationship("Exercise", back_populates="workout_exercises")

    @validates("sets")
    def validate_sets(self, key, value):
        if value is not None and value < 1:
            raise ValueError("Sets must be at least 1.")
        return value

    @validates("reps")
    def validate_reps(self, key, value):
        if value is not None and value < 1:
            raise ValueError("Reps must be at least 1.")
        return value

    def __repr__(self):
        return f"<WorkoutExercise workout={self.workout_id} exercise={self.exercise_id}>"