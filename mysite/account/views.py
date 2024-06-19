from django.http import HttpResponse
from django.shortcuts import render
from django.contrib.auth import authenticate, login
from .forms import LoginForm
from django.contrib.auth.decorators import login_required


# def user_login(request):
#     if request.method == 'POST':
#         form = LoginForm(request.POST)
#         if form.is_valid():
#             cd = form.cleaned_data
#             user = authenticate(request,
#                                 username=cd['username'],
#                                 password=cd['password'])
#             if user is not None:
#                 if user.is_active:
#                     login(request, user)
#                     return HttpResponse('Authenticated successfully')
#                 else:
#                     return HttpResponse('Disabled account')
#             else:
#                 return HttpResponse('Invalid login')
#     else:
#         form = LoginForm()
#     return render(request, 'account/login.html', {'form': form})


@login_required  # функция исполнится, если выполнен вход
# если пользователь не аутентифицирован, то оно перенаправляет пользователя на URL-адрес
# входа с изначально запрошенным URL адресом в качестве GET-параметра с именем next
# с этой целью в шаблон входа был добавлен скрытый HTMLэлемент <input> с именем next.
# Мы также определили переменную section. Эта переменная будет использоваться для
# подсвечивания текущего раздела в главном меню сайта.
def dashboard(request):
    return render(request,
                  'account/dashboard.html',
                  {'section': 'dashboard'})
