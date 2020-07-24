from django.contrib import admin
from django.contrib.admin import ModelAdmin
from django.contrib.auth.admin import UserAdmin
from django.utils.html import format_html

from apps.users.forms import CustomUserChangeForm, CustomUserCreationForm
from apps.users.models import User, Advertisement, MeasurementResult


@admin.register(User)
class CustomUserAdmin(UserAdmin):
    fieldsets = (
        (None, {'fields': ('email',)}),
        ('User Info',
         {'fields': (
             'profile_photo', 'name', 'gender', 'birthday', 'length', 'activity', 'measurement_day', "goal",)}),
    )
    add_fieldsets = (
        (None, {'classes': ('wide',),
                'fields': (
                    'email', 'password1', 'password2', 'gender', 'length', 'activity', 'measurement_day',
                    'birthday', "goal",)}),
    )
    filter_horizontal = ()
    form = CustomUserChangeForm
    add_form = CustomUserCreationForm

    list_display = ('id', 'email', 'name', 'birthday', 'length', 'activity', 'measurement_day',)
    list_filter = ('is_active',)
    search_fields = ('email', 'name', )
    ordering = ('id',)
    readonly_fields = ["profile_photo"]

    def profile_photo(self, obj):
        image_path = obj.image.url if obj.image is not None else None
        return format_html("<img src='{}'  width='175' height='150' />".format(image_path)) if image_path else 'None'


@admin.register(Advertisement)
class AdvertisementModelAdmin(ModelAdmin):
    list_display = [
        'id',
        'text',
        'link',
        'image',
    ]


@admin.register(MeasurementResult)
class MeasurementResultModelAdmin(ModelAdmin):
    list_display = [
        'id',
        'user',
        'date',
        'waist',
        'weight',
        'wrist_circumference',
        'hip_circumference',
        'forearm_circumference',
        'body_fat_percentage',
    ]
