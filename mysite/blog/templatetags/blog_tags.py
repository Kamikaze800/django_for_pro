from django import template
from ..models import Post

register = template.Library()  # Для того чтобы быть допустимой библиотекой тегов


@register.simple_tag
def total_posts():  # Django будет использовать имя функции в качестве имени тега
    # Если есть потребность зарегистрировать ее под другим именем, то это можно сделать, указав атрибут
    # name, например @register.simple_tag(name='my_tag').
    return Post.published.count()


@register.inclusion_tag('blog/post/latest_posts.html')
def show_latest_posts(count=5): # позволяет задавать опциональное число отображаемых постов как {% show_latest_posts 3 %}
    latest_posts = Post.published.order_by('-publish')[:count]
    return {'latest_posts': latest_posts}
