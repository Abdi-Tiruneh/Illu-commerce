from django.contrib import admin
from .models import  User, UserProfile
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.utils.html import format_html
from django.conf import settings

# Register your models here.

@admin.register(User)
class UserAdmin(BaseUserAdmin):
    list_display       = ('email','username','first_name','last_name','last_login','is_active')
    list_display_links = ('email','username','first_name','last_name')
    readonly_fields    = ('last_login','date_joined')
    ordering           =('-date_joined',)

    list_filter=() # make the above list visible on admin site (list_display )
    fieldsets = () #make the password fields read only

@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    def thumbnail(self,object):
        return format_html('<img src="{}" width="30" style="border-radius:50%;">'.format(object.profile_pic.url))
    thumbnail.short_description = 'profile picture'
    list_display = ['thumbnail','user','city','region']


