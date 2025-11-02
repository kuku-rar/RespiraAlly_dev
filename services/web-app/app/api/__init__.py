# services/web-app/app/api/__init__.py

from . import auth
from . import patients
from . import questionnaires
from . import daily_metrics
from . import users
from . import uploads
from . import overview
from . import tasks
from . import education
from . import voice

__all__ = [
    'auth',
    'patients',
    'questionnaires',
    'daily_metrics',
    'users',
    'uploads',
    'overview',
    'tasks',
    'education',
    'voice'
]
