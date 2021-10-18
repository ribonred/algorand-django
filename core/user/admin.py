from django.contrib import admin
from .models import User
from .forms import CustomUserCreationForm,CustomUserChangeForm
from django.contrib.auth.admin import UserAdmin




class AppUserAdmin(UserAdmin):
    add_form = CustomUserCreationForm
    form = CustomUserChangeForm
    model = User
    list_display = ('email', 'is_staff', 'is_active','username')
    list_filter = ('is_staff', 'is_active','date_joined')
    fieldsets = (
        (None, {'fields': ('email', 'username',
                           'password', 'first_name', 'last_name',)}),
        ('Permissions', {'fields': ('is_staff',
                                    'is_active', 'is_superuser', 'groups')}),
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'password1', 'password2', 'is_staff', 'is_active')}
         ),
    )
    search_fields = ('email','username')
    ordering = ('email',)


admin.site.register(User, AppUserAdmin)
