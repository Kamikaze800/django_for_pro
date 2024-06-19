from django.contrib.sitemaps import Sitemap
from .models import Post


class PostSitemap(Sitemap):
    changefreq = 'weekly'
    priority = 0.9
    # Атрибуты changefreq и  priority указывают частоту
    # изменения страниц постов и их релевантность на веб-сайте (максимальное значение равно 1).

    def items(self):
        return Post.published.all()

    def lastmod(self, obj): # Метод lastmod получает каждый возвращаемый методом items() объект
        return obj.updated  # и возвращает время последнего изменения объекта


