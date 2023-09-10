from django.contrib import admin
from django.contrib.auth import get_user_model
from django.contrib.auth.admin import UserAdmin

from .models import CustomFollow

User = get_user_model()


class CustomUserAdmin(UserAdmin):
    list_display = ("email", "username")
    list_filter = ("email", "username")


@admin.register(CustomFollow)
class CustomFollowAdmin(admin.ModelAdmin):
    list_display = ("id", "follower", "following")
    search_fields = ("follower__username", "following__username")
    list_filter = ("follower", "following")


admin.site.unregister(User)
admin.site.register(User, CustomUserAdmin)
