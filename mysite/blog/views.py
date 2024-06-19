from django.shortcuts import render, get_object_or_404
from .models import Post, Comment
from django.http import Http404
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.views.generic import ListView
from .forms import EmailPostForm, CommentForm, SearchForm
from django.core.mail import send_mail
from django.views.decorators.http import require_POST
from taggit.models import Tag
from django.db.models import Count
from django.contrib.postgres.search import SearchVector, SearchQuery, SearchRank
from django.contrib.postgres.search import TrigramSimilarity

def post_detail(request, year, month, day, post):
    post = get_object_or_404(Post,
                             slug=post,
                             publish__year=year,
                             publish__month=month,
                             publish__day=day,
                             status=Post.Status.PUBLISHED)
    # Список активных комментариев к этому посту
    comments = post.comments.filter(active=True)
    # Форма для комментирования пользователями
    form = CommentForm()

    # Список схожих постов
    post_tags_ids = post.tags.values_list('id',
                                          flat=True)  # извлекается Python’овский список идентификаторов тегов текущего
    # поста. Набор запросов QuerySet values_list() возвращает кортежи со
    # значениями заданных полей. Ему передается параметр flat=True, чтобы
    # получить одиночные значения, такие как [1, 2, 3, ...],

    similar_posts = Post.published.filter(tags__in=post_tags_ids).exclude(
        id=post.id)  # берутся все посты, содержащие любой из этих тегов, за исключением
    # текущего поста

    similar_posts = similar_posts.annotate(same_tags=Count('tags')).order_by('-same_tags', '-publish')[:4]
    # применяется функция агрегирования Count. Ее работа – генерировать вычисляемое поле – same_tags, – которое содержит
    # число тегов, общих со всеми запрошенными тегами;
    # результат упорядочивается по числу общих тегов (в  убывающем порядке) и  по publish, чтобы сначала отображать последние посты для
    # постов с одинаковым числом общих тегов. Результат нарезается, чтобы
    # получить только первые четыре поста;

    return render(request,
                  'blog/post/detail.html',
                  {'post': post,
                   'comments': comments,
                   'form': form,
                   'similar_posts': similar_posts})


class PostListView(ListView):
    """
    Альтернативное представление списка постов
    """
    queryset = Post.published.all()
    context_object_name = 'posts'
    paginate_by = 3
    template_name = 'blog/post/list.html'


def post_list(request, tag_slug=None):
    post_list = Post.published.all()

    tag = None
    if tag_slug:
        tag = get_object_or_404(Tag, slug=tag_slug)
        post_list = post_list.filter(
            tags__in=[tag])  # из-за связи многие-ко-многим необходимо фильтровать записи по тегам,
        # содержащимся в заданном списке,который в данном случае содержит только один элемент

    # Постраничная разбивка с 3 постами на страницу
    paginator = Paginator(post_list, 3)
    page_number = request.GET.get('page', 1)
    try:
        posts = paginator.page(page_number)
    except PageNotAnInteger:
        # Если page_number не целое число, то
        # выдать первую страницу
        posts = paginator.page(1)
    except EmptyPage:
        # Если page_number находится вне диапазона, то
        # выдать последнюю страницу
        posts = paginator.page(paginator.num_pages)
    return render(request,
                  'blog/post/list.html',
                  {'posts': posts,
                   'tag': tag})


def post_share(request, post_id):
    # Извлечь пост по его идентификатору id
    post = get_object_or_404(Post,
                             id=post_id,
                             status=Post.Status.PUBLISHED)
    sent = False
    if request.method == 'POST':
        # Форма была передана на обработку
        form = EmailPostForm(request.POST)
        if form.is_valid():
            # Поля формы успешно прошли валидацию
            cd = form.cleaned_data
            post_url = request.build_absolute_uri(
                post.get_absolute_url())
            subject = f"{cd['name']} recommends you read " \
                      f"{post.title}"
            message = f"Read {post.title} at {post_url}\n\n" \
                      f"{cd['name']}\'s comments: {cd['comments']}"
            send_mail(subject, message, 'o1d.kuk@yandex.ru',
                      [cd['to']])
            sent = True
    else:
        form = EmailPostForm()
    return render(request, 'blog/post/share.html', {'post': post,
                                                    'form': form,
                                                    'sent': sent})


@require_POST  # разрешает запросы методом POST
def post_comment(request, post_id):
    post = get_object_or_404(Post,
                             id=post_id,
                             status=Post.Status.PUBLISHED)  # получаю кокретный post по is и status из бд
    comment = None  # используется для хранения комментарного блока при его создании
    # Комментарий был отправлен
    form = CommentForm(data=request.POST)  # создаётся экземпляр формы, используя данные POST
    if form.is_valid():
        # Создать объект класса Comment, не сохраняя его в базе данных
        comment = form.save(
            commit=False)  # тут создаётся объект класса Comment, пока не сохранённый в бд из-за commit=False
        # такой подход позволяет изменять объект перед окончательным сохранением в бд
        # при том метод save доступен только для ModelForm, ибо у экзепляров класса Form нет привязанных моделей

        # Назначить пост комментарию
        comment.post = post  # это работает за счёт прописаного в related_name в модели Comment в поле post
        # related_name позволяет обратиться к ассоциативному объекту или же
        # но вот нахуя посту присваивать пост...видимо, по умолчанию commtnt.post пустой🤔

        comment.save()  # Сохранить комментарий в базе данных
    return render(request, 'blog/post/comment.html',
                  {'post': post,
                   'form': form,
                   'comment': comment})


def post_search(request):
    form = SearchForm()
    query = None
    results = []
    if 'query' in request.GET:
        form = SearchForm(request.GET)
        if form.is_valid():
            query = form.cleaned_data['query']
            search_vector = SearchVector('title', weight='A') + \
                            SearchVector('body', weight='B')
            search_query = SearchQuery(query, config='english')
            results = Post.published.annotate(
                similarity=TrigramSimilarity('title', query),
            ).filter(similarity__gt=0.1).order_by('-similarity')
    return render(request,
                  'blog/post/search.html',
                  {'form': form,
                   'query': query,
                   'results': results})
