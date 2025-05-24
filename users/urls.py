from django.urls import path
from . import views

app_name = 'users'

urlpatterns = [
    path('', views.index, name='index'),
    path('random/', views.random_user, name='random'),
    path('<int:user_id>/', views.user_detail, name='detail'),
]
