from pathlib import Path
from django.conf import settings

__version__ = '1.0.2'
__all__ = ['__version__', 'ROBOTS_PATH', 'SITEMAP_PATH']

ROBOTS_PATH = Path(getattr(settings, 'ROBOTS_PATH', settings.BASE_DIR / 'robots.txt'))
SITEMAP_PATH = Path(getattr(settings, 'SITEMAP_PATH', settings.BASE_DIR / 'sitemap.xml'))
