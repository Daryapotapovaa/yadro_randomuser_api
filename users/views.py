from django.shortcuts import render, get_object_or_404
from django.core.paginator import Paginator
from django.contrib import messages
import random

from .models import User
from .services import RandomUserAPIService


def index(request):
    """Главная страница с таблицей пользователей"""
    if request.method == 'POST':
        try:
            count = int(request.POST.get('count', 0))
            if count > 0 and count < 5001:
                users = RandomUserAPIService.load_and_save_users(count)
                messages.success(request, f'Успешно загружено {len(users)} пользователей!')
            else:
                messages.error(request, 'Количество должно быть от 1 до 5000')
        except ValueError:
            messages.error(request, 'Введите корректное число')
        except Exception as e:
            messages.error(request, f'Ошибка при загрузке: {str(e)}')
    
    users_list = User.objects.all()
    paginator = Paginator(users_list, 20)
    
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'page_obj': page_obj,
        'total_users': users_list.count(),
    }
    
    return render(request, 'users/index.html', context)


def user_detail(request, user_id):
    """Страница конкретного пользователя"""
    user = get_object_or_404(User, id=user_id)
    return render(request, 'users/user_detail.html', {'user': user})


def random_user(request):
    """Страница случайного пользователя"""
    users_count = User.objects.count()
    if users_count == 0:
        return render(request, 'users/no_users.html')
    
    random_offset = random.randint(0, users_count - 1)
    user = User.objects.all()[random_offset]
    
    return render(request, 'users/user_detail.html', {
        'user': user,
        'is_random': True
    })
