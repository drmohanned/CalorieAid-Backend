from django import forms
from django.contrib import admin
from django.contrib.admin import ModelAdmin
from searchableselect.widgets import SearchableSelect

from apps.food.models import Ingredients, UserIngredient


class IngredientForm(forms.ModelForm):
    class Meta:
        model = Ingredients
        exclude = ()
        widgets = {
            'ingredient': SearchableSelect(model='food.Ingredients', search_field='name', many=False)
        }


@admin.register(Ingredients)
class IngredientsAdmin(ModelAdmin):
    list_display = [
        'id',
        'name',
        'protein',
        'fat',
        'carbohydrate',
        'fiber',
        'sugar',
        'source_type',
        'sub_source_type',
        'energy',
        'status',
    ]
    list_filter = [
        'sub_source_type',
        'source_type',
        'status',
    ]
    search_fields = [
        'name',
        'source_type',
        'sub_source_type',
    ]


@admin.register(UserIngredient)
class UserIngredientAdmin(ModelAdmin):
    form = IngredientForm

    list_display = [
        'id',
        'user',
        'ingredient',
    ]
    list_filter = [
        'user',
    ]
    search_fields = [
        'ingredient__name',
        'user__email',
    ]
