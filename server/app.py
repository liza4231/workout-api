from datetime import datetime

from flask import Flask, request, make_response
from flask_migrate import Migrate
from marshmallow import Schema, fields, validates, ValidationError

from models import db, Exercise, Workout, WorkoutExercise


app = Flask(__name__)

app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///app.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

migrate = Migrate(app, db)
db.init_app(app)


class WorkoutExerciseSchema(Schema):
    id = fields.Int(dump_only=True)
    workout_id = fields.Int(dump_only=True)
    exercise_id = fields.Int(dump_only=True)
    reps = fields.Int(allow_none=True)
    sets = fields.Int(allow_none=True)
    duration_seconds = fields.Int(allow_none=True)

    exercise = fields.Nested(lambda: ExerciseSchema(exclude=("workouts",)), dump_only=True)

    @validates("sets")
    def validate_sets(self, value):
        if value is not None and value < 1:
            raise ValidationError("Sets must be at least 1.")

    @validates("duration_seconds")
    def validate_duration_seconds(self, value):
        if value is not None and value < 1:
            raise ValidationError("Duration seconds must be at least 1.")


class ExerciseSchema(Schema):
    id = fields.Int(dump_only=True)
    name = fields.Str(required=True)
    category = fields.Str(required=True)
    equipment_needed = fields.Bool()

    workout_exercises = fields.Nested(
        WorkoutExerciseSchema,
        many=True,
        dump_only=True,
        exclude=("exercise",)
    )

    workouts = fields.Method("get_workouts", dump_only=True)

    def get_workouts(self, obj):
        return [
            {
                "id": workout_exercise.workout.id,
                "date": workout_exercise.workout.date.isoformat(),
                "duration_minutes": workout_exercise.workout.duration_minutes,
                "notes": workout_exercise.workout.notes
            }
            for workout_exercise in obj.workout_exercises
        ]

    @validates("name")
    def validate_name(self, value):
        if not value or len(value.strip()) < 3:
            raise ValidationError("Exercise name must be at least 3 characters.")

    @validates("category")
    def validate_category(self, value):
        allowed = ["Strength", "Cardio", "Flexibility"]

        if value not in allowed:
            raise ValidationError("Category must be Strength, Cardio, or Flexibility.")


class WorkoutSchema(Schema):
    id = fields.Int(dump_only=True)
    date = fields.Date(required=True)
    duration_minutes = fields.Int(required=True)
    notes = fields.Str(allow_none=True)

    workout_exercises = fields.Nested(
        WorkoutExerciseSchema,
        many=True,
        dump_only=True
    )

    @validates("duration_minutes")
    def validate_duration_minutes(self, value):
        if value <= 0:
            raise ValidationError("Duration must be greater than 0.")

    @validates("notes")
    def validate_notes(self, value):
        if value and len(value) > 500:
            raise ValidationError("Notes cannot be over 500 characters.")


exercise_schema = ExerciseSchema()
exercises_schema = ExerciseSchema(many=True)

workout_schema = WorkoutSchema()
workouts_schema = WorkoutSchema(many=True)

workout_exercise_schema = WorkoutExerciseSchema()


@app.route("/")
def index():
    return "<h1>Workout API</h1>"


@app.route("/workouts", methods=["GET", "POST"])
def workouts():
    if request.method == "GET":
        workouts = Workout.query.all()
        return make_response(workouts_schema.dump(workouts), 200)

    if request.method == "POST":
        try:
            data = workout_schema.load(request.get_json())

            new_workout = Workout(
                date=data["date"],
                duration_minutes=data["duration_minutes"],
                notes=data.get("notes")
            )

            db.session.add(new_workout)
            db.session.commit()

            return make_response(workout_schema.dump(new_workout), 201)

        except Exception as error:
            db.session.rollback()
            return make_response({"error": str(error)}, 400)


@app.route("/workouts/<int:id>", methods=["GET", "DELETE"])
def workout_by_id(id):
    workout = Workout.query.get(id)

    if not workout:
        return make_response({"error": "Workout not found"}, 404)

    if request.method == "GET":
        return make_response(workout_schema.dump(workout), 200)

    if request.method == "DELETE":
        db.session.delete(workout)
        db.session.commit()

        return make_response({}, 204)


@app.route("/exercises", methods=["GET", "POST"])
def exercises():
    if request.method == "GET":
        exercises = Exercise.query.all()
        return make_response(exercises_schema.dump(exercises), 200)

    if request.method == "POST":
        try:
            data = exercise_schema.load(request.get_json())

            new_exercise = Exercise(
                name=data["name"],
                category=data["category"],
                equipment_needed=data.get("equipment_needed", False)
            )

            db.session.add(new_exercise)
            db.session.commit()

            return make_response(exercise_schema.dump(new_exercise), 201)

        except Exception as error:
            db.session.rollback()
            return make_response({"error": str(error)}, 400)


@app.route("/exercises/<int:id>", methods=["GET", "DELETE"])
def exercise_by_id(id):
    exercise = Exercise.query.get(id)

    if not exercise:
        return make_response({"error": "Exercise not found"}, 404)

    if request.method == "GET":
        return make_response(exercise_schema.dump(exercise), 200)

    if request.method == "DELETE":
        db.session.delete(exercise)
        db.session.commit()

        return make_response({}, 204)


@app.route(
    "/workouts/<int:workout_id>/exercises/<int:exercise_id>/workout_exercises",
    methods=["POST"]
)
def add_exercise_to_workout(workout_id, exercise_id):
    workout = Workout.query.get(workout_id)
    exercise = Exercise.query.get(exercise_id)

    if not workout:
        return make_response({"error": "Workout not found"}, 404)

    if not exercise:
        return make_response({"error": "Exercise not found"}, 404)

    try:
        data = workout_exercise_schema.load(request.get_json())

        new_workout_exercise = WorkoutExercise(
            workout_id=workout_id,
            exercise_id=exercise_id,
            reps=data.get("reps"),
            sets=data.get("sets"),
            duration_seconds=data.get("duration_seconds")
        )

        db.session.add(new_workout_exercise)
        db.session.commit()

        return make_response(workout_exercise_schema.dump(new_workout_exercise), 201)

    except Exception as error:
        db.session.rollback()
        return make_response({"error": str(error)}, 400)


if __name__ == "__main__":
    app.run(port=5555, debug=True)