from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth.models import User as AuthUser
from unittest.mock import patch, Mock
import uuid
from datetime import datetime

from .models import User
from .services import RandomUserAPIService


class UserModelTest(TestCase):
    def setUp(self):
        self.user_data = {
            'gender': 'male',
            'first_name': 'John',
            'last_name': 'Doe',
            'email': 'john@example.com',
            'phone': '+1234567890',
            'street_number': '123',
            'street_name': 'Main Street',
            'city': 'New York',
            'state': 'NY',
            'country': 'USA',
            'postcode': '10001',
            'picture': 'https://example.com/large.jpg',
        }
    
    def test_user_creation(self):
        """Тест создания пользователя"""
        user = User.objects.create(**self.user_data)
        self.assertEqual(user.first_name, 'John')
        self.assertEqual(user.last_name, 'Doe')
        self.assertEqual(user.email, 'john@example.com')
    
    def test_full_address_property(self):
        """Тест свойства полного адреса"""
        user = User.objects.create(**self.user_data)
        expected_address = "123 Main Street, New York, NY, USA"
        self.assertEqual(user.full_address, expected_address)


class RandomUserAPIServiceTest(TestCase):
    @patch('users.services.requests.get')
    def test_fetch_users_success(self, mock_get):
        """Тест успешного получения пользователей из API"""
        # Мокаем ответ API
        mock_response = Mock()
        mock_response.raise_for_status.return_value = None
        mock_response.json.return_value = {
            'results': [
                {
                    'gender': 'male',
                    'name': {'first': 'John', 'last': 'Doe'},
                    'email': 'john@example.com',
                    'phone': '+1234567890',
                    'location': {
                        'street': {'number': 123, 'name': 'Main St'},
                        'city': 'New York',
                        'state': 'NY',
                        'country': 'USA',
                        'postcode': '10001'
                    },
                    'picture': {
                        'large': 'https://example.com/large.jpg',
                        'medium': 'https://example.com/medium.jpg',
                        'thumbnail': 'https://example.com/thumb.jpg'
                    },
                    'dob': {'date': '1998-01-01T00:00:00.000Z', 'age': 25},
                    'nat': 'US'
                }
            ]
        }
        mock_get.return_value = mock_response
        
        users = RandomUserAPIService.fetch_users(1)
        self.assertEqual(len(users), 1)
        self.assertEqual(users[0]['name']['first'], 'John')
    
    @patch('users.services.requests.get')
    def test_fetch_users_api_error(self, mock_get):
        """Тест обработки ошибки API"""
        mock_get.side_effect = Exception("API Error")
        
        users = RandomUserAPIService.fetch_users(1)
        self.assertEqual(users, [])


class UserViewsTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create(
            gender='male',
            first_name='John',
            last_name='Doe',
            email='john@example.com',
            phone='+1234567890',
            street_number='123',
            street_name='Main Street',
            city='New York',
            state='NY',
            country='USA',
            postcode='10001',
            picture='https://example.com/large.jpg',
        )
    
    def test_index_view(self):
        """Тест главной страницы"""
        response = self.client.get(reverse('users:index'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'John')
        self.assertContains(response, 'john@example.com')
    
    def test_user_detail_view(self):
        """Тест страницы детального просмотра пользователя"""
        response = self.client.get(reverse('users:detail', args=[self.user.id]))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'John')
        self.assertContains(response, 'john@example.com')
    
    def test_random_user_view(self):
        """Тест страницы случайного пользователя"""
        response = self.client.get(reverse('users:random'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'John')
    
    def test_random_user_view_no_users(self):
        """Тест страницы случайного пользователя без пользователей в БД"""
        User.objects.all().delete()
        response = self.client.get(reverse('users:random'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Пользователи не найдены')
    
    @patch('users.services.RandomUserAPIService.load_and_save_users')
    def test_index_post_load_users(self, mock_load_users):
        """Тест загрузки пользователей через POST"""
        mock_load_users.return_value = [self.user]
        
        response = self.client.post(reverse('users:index'), {'count': '5'})
        self.assertEqual(response.status_code, 200)
        mock_load_users.assert_called_once_with(5)
    
    def test_index_post_invalid_count(self):
        """Тест POST с некорректным количеством"""
        response = self.client.post(reverse('users:index'), {'count': 'invalid'})
        self.assertEqual(response.status_code, 200)
