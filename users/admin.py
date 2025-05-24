from django.contrib import admin
from .models import User


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = [
        'first_name', 'last_name', 'gender', 'email', 
        'phone', 'city', 'country', 'created_at'
    ]
    list_filter = ['gender', 'country', 'created_at']
    search_fields = ['first_name', 'last_name', 'email', 'phone']
    readonly_fields = ['id', 'created_at']
    
    fieldsets = (
        ('Основная информация', {
            'fields': ('id', 'gender', 'first_name', 'last_name')
        }),
        ('Контакты', {
            'fields': ('email', 'phone')
        }),
        ('Адрес', {
            'fields': (
                'street_number', 'street_name', 'city', 
                'state', 'country', 'postcode'
            )
        }),
        ('Фотография', {
            'fields': ('picture',)
        }),
        ('Системная информация', {
            'fields': ('created_at',),
            'classes': ('collapse',)
        }),
    )
