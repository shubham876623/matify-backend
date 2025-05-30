# admin.py
from django.contrib import admin
from .models import TrainedModel

from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import CustomUser, TrainedModel,Gallery ,UserCredits , GeneratedImage, ProcessedImage

@admin.register(CustomUser)
class CustomUserAdmin(UserAdmin):
    model = CustomUser
    list_display = ('id', 'email', 'username', 'is_staff', 'is_active')
    list_filter = ('is_staff', 'is_active', 'is_superuser')
    search_fields = ('email', 'username')
    ordering = ('email',)

    fieldsets = (
        (None, {'fields': ('username', 'email', 'password')}),
        ('Permissions', {'fields': ('is_staff', 'is_active', 'is_superuser', 'groups', 'user_permissions')}),
        ('Important dates', {'fields': ('last_login',)}),
    )

    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('username', 'email', 'password1', 'password2', 'is_staff', 'is_active')}
        ),
    )

@admin.register(TrainedModel)
class TrainedModelAdmin(admin.ModelAdmin):
    list_display = ['id', 'get_user_email', 'training_id', 'status', 'created_at']
    
    def get_user_email(self, obj):
        return obj.user.email
    get_user_email.short_description = 'User Email'
    
    
    

@admin.register(Gallery)
class TrainedModelAdmin(admin.ModelAdmin):
    list_display = ['id', 'user','image_url', 'created_at']



@admin.register(UserCredits)
class UserCreditsAdmin(admin.ModelAdmin):
    list_display = ('user', 'credits_remaining', 'credits_used')
    
    
    
@admin.register(GeneratedImage)
class GeneratedImageAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'image_url', 'created_at')
    search_fields = ('user__email',)
    list_filter = ('created_at',)

@admin.register(ProcessedImage)
class ProcessedImageAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'image_url', 'source', 'created_at')
    search_fields = ('user__email',)
    list_filter = ('created_at',)