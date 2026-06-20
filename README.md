# Workout Tracker API

## Description

This project is a Flask API that allows users to create workouts, create exercises, view workout and exercise information, delete workouts and exercises, and add exercises to workouts.

## Installation

Create and activate a virtual environment:

```bash
python -m venv venv
source venv/bin/activate
```

Install packages:

```bash
pip install -r requirements.txt
```

## Database Setup

From the server folder:

```bash
flask db upgrade
python seed.py
```

## Run the Application

From the server folder:

```bash
python app.py
```

The application runs on:

```text
http://localhost:5555
```

## Endpoints

### Workouts

* GET /workouts
* GET /workouts/<id>
* POST /workouts
* DELETE /workouts/<id>

### Exercises

* GET /exercises
* GET /exercises/<id>
* POST /exercises
* DELETE /exercises/<id>

### Workout Exercises

* POST /workouts/<workout_id>/exercises/<exercise_id>/workout_exercises
