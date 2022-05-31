from django.contrib import admin
from django.contrib.auth import get_user_model
from django.contrib.auth.admin import UserAdmin

User = get_user_model()


@admin.register(User)
class CustomUserAdmin(UserAdmin):
    list_display = (
        'pk',
        'username',
        'first_name',
        'last_name',
        'date_joined',
        'is_staff'
    )
    list_filter = ('username',)
