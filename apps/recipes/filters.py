import django_filters
from taggit.models import Tag

from apps.food.models import UserIngredient
from apps.recipes.models import DailyBox, DailyBoxIngredient, Recipe, FavoriteRecipe, LikeRecipe
from apps.users.models import User


class DailyBoxFilter(django_filters.FilterSet):
    day_of_week = django_filters.ChoiceFilter(choices=DailyBox.WEEKDAYS_CHOICES, method='filter_by_day_of_week')
    user = django_filters.ModelChoiceFilter(queryset=User.objects.all())

    def filter_by_day_of_week(self, queryset, name, value):
        return queryset.filter(day_of_week=value)

    class Meta:
        model = DailyBox
        fields = {}


class DailyBoxIngredientFilter(django_filters.FilterSet):
    daily_box = django_filters.ModelChoiceFilter(queryset=DailyBox.objects.all())
    user_ingredient = django_filters.ModelChoiceFilter(queryset=UserIngredient.objects.all())

    class Meta:
        model = DailyBoxIngredient
        fields = {}


class FavoriteRecipeFilter(django_filters.FilterSet):
    user = django_filters.ModelChoiceFilter(queryset=User.objects.all())
    recipe = django_filters.ModelChoiceFilter(queryset=Recipe.objects.all())

    class Meta:
        model = FavoriteRecipe
        fields = {}


class LikeRecipeFilter(django_filters.FilterSet):
    user = django_filters.ModelChoiceFilter(queryset=User.objects.all())
    recipe = django_filters.ModelChoiceFilter(queryset=Recipe.objects.all())

    class Meta:
        model = LikeRecipe
        fields = {}


class TagFilter(django_filters.FilterSet):
    class Meta:
        model = Tag
        fields = {
            'name': ['icontains', ]
        }


class RecipeFilter(django_filters.FilterSet):
    name = django_filters.CharFilter(method='filter_by_name')
    tags = django_filters.CharFilter(method='filter_by_tags')

    def filter_by_tags(self, queryset, name, value):
        tags = value.split(',')
        return queryset.filter(tags__name__in=tags)

    def filter_by_name(self, queryset, name, value):
        return queryset.filter(name__icontains=value)

    class Meta:
        model = Recipe
        fields = {}
