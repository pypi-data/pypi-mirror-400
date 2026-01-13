import functools
from pathlib import Path
from django.http import Http404


def file_exists(path: Path):
    def decorator(func):
        @functools.wraps(func)
        def wrapper(request, *args, **kwargs):
            if not path.is_file():
                raise Http404
            return func(request, *args, **kwargs)
        return wrapper
    return decorator
