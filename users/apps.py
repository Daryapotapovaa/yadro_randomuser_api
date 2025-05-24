from django.apps import AppConfig
from django.db.models.signals import post_migrate


class UsersConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'users'
    
    def ready(self):
        """Вызывается при готовности приложения"""
        # Импортируем здесь, чтобы избежать проблем с готовностью Django
        import os
        import sys
            
        # Проверяем, что это не тестирование
        if 'test' in sys.argv:
            return

        post_migrate.connect(self.on_post_migrate, sender=self)
    
    def on_post_migrate(self, sender, **kwargs):
        """Загружает начальных пользователей, если база пуста"""
        try:
            from .models import User
            from .services import RandomUserAPIService
            
            # Проверяем, есть ли пользователи в базе
            if User.objects.count() == 0:
                print("База данных пуста. Загружаем 1000 пользователей из API...")
                users = RandomUserAPIService.load_and_save_users(1000)
                print(f"Успешно загружено {len(users)} пользователей!")
            else:
                print(f"В базе данных уже есть {User.objects.count()} пользователей.")
        except Exception as e:
            print(f"Ошибка при автоматической загрузке пользователей: {e}")
