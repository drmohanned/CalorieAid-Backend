from django.contrib import admin
from django.contrib.admin import ModelAdmin

from apps.recipes.models import DailyBox, DailyBoxIngredient, Recipe


@admin.register(DailyBox)
class DailyBoxAdmin(ModelAdmin):
    list_display = [
        'id',
        'user',
        'day_of_week',
    ]
    list_filter = [
        'user',
        'day_of_week',
    ]
    search_fields = [
        'day_of_week',
        'user__email',
        'user__name',
    ]


@admin.register(DailyBoxIngredient)
class DailyBoxIngredientAdmin(ModelAdmin):
    list_display = [
        'id',
        'daily_box',
        'ingredient',
    ]
    list_filter = [
        'daily_box',
        'ingredient',
    ]
    search_fields = [
        'ingredient',
        'daily_box',
    ]


@admin.register(Recipe)
class RecipeAdmin(ModelAdmin):
    list_display = [
        'id',
        'name',
        'description',
    ]
    list_filter = [
        'tags',
    ]
    search_fields = [
        'name',
        'description',
    ]
