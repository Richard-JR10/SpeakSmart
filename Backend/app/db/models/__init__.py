# app/db/models/__init__.py
from app.db.models.user import User
from app.db.models.class_ import Class
from app.db.models.module import Module
from app.db.models.phrase import Phrase
from app.db.models.attempt import Attempt
from app.db.models.progress import ProgressSummary
from app.db.models.exercise import Exercise, ExercisePhrase, ExerciseAssignment
from app.db.models.analytics import ClassAnalytics