import requests
from datetime import datetime
from django.db import transaction


class RandomUserAPIService:
    BASE_URL = "https://randomuser.me/api/"
    
    @classmethod
    def fetch_users(cls, count=1):
        """Получение пользователей из API"""
        try:
            response = requests.get(f"{cls.BASE_URL}?results={count}")
            response.raise_for_status()
            data = response.json()
            return data.get('results', [])
        except Exception as e:
            print(f"Error fetching users from API: {e}")
            return []
    
    @classmethod
    def create_user_from_api_data(cls, api_data):
        """Создание пользователя в БД из данных API"""
        from .models import User
        
        try:
            return User(
                gender=api_data['gender'],
                first_name=api_data['name']['first'],
                last_name=api_data['name']['last'],
                email=api_data['email'],
                phone=api_data['phone'],
                street_number=str(api_data['location']['street']['number']),
                street_name=api_data['location']['street']['name'],
                city=api_data['location']['city'],
                state=api_data['location']['state'],
                country=api_data['location']['country'],
                postcode=str(api_data['location']['postcode']),
                picture=api_data['picture']['large'],
            )
        except Exception as e:
            print(f"Error creating user: {e}")
            return None
    
    @classmethod
    def load_and_save_users(cls, count=1000):
        """Загрузка и сохранение пользователей в БД"""
        from .models import User
        users_data = cls.fetch_users(count)
        user_objects = []
        
        for user_data in users_data:
            user = cls.create_user_from_api_data(user_data)
            if user:
                user_objects.append(user)

        with transaction.atomic():
            User.objects.bulk_create(user_objects)
        
        print(f"Successfully created {len(user_objects)} users")
        return user_objects
