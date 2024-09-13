
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import CustomUser
from .models import MinistryArticle

class CustomUserAdmin(UserAdmin):
    list_display = ('username', 'email', 'first_name', 'last_name', 'ministry_name', 'is_staff', 'is_active')
    list_filter = ('is_staff', 'is_active', 'ministry_name')
    search_fields = ('username', 'email', 'first_name', 'last_name', 'ministry_name')
    fieldsets = (
        (None, {'fields': ('username', 'password')}),
        ('Personal Info', {'fields': ('first_name', 'last_name', 'email', 'ministry_name')}),
        ('Permissions', {'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')}),
        ('Important Dates', {'fields': ('last_login', 'date_joined')}),
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('username', 'password1', 'password2', 'ministry_name'),
        }),
    )

class MinistryArticleAdmin(admin.ModelAdmin):
    list_display = ('ministry_name', 'heading', 'date', 'source', 'sentiment')
    search_fields = ('ministry_name', 'heading', 'source')

# Register the CustomUser model with the custom admin class
admin.site.register(CustomUser, CustomUserAdmin)

# Register the MinistryArticle model with the custom admin class
admin.site.register(MinistryArticle, MinistryArticleAdmin)