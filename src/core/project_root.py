from pathlib import Path


def get_project_root() -> Path:
    """Возвращает абсолютный путь к корню проекта."""
    return Path(__file__).parent.parent.parent


PROJECT_ROOT = get_project_root()