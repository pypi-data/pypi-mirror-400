from django.apps import AppConfig
from django.utils.translation import gettext_lazy


class RobotsAndSitemapConfig(AppConfig):
    name = 'robots_and_sitemap'
    verbose_name = gettext_lazy("robots.txt and sitemap.xml")
