import django_filters

from apps.food.models import Ingredients, UserIngredient
from apps.users.models import User


class IngredientFilter(django_filters.FilterSet):
    name = django_filters.CharFilter(lookup_expr='icontains')
    source_type = django_filters.ChoiceFilter(choices=Ingredients.SOURCE_TYPE_CHOICES, method='filter_by_source')
    sub_source_type = django_filters.ChoiceFilter(choices=Ingredients.SUB_SOURCE_TYPE_CHOICES,
                                                  method='filter_by_sub_source_type')

    def filter_by_source(self, queryset, name, value):
        return queryset.filter(source_type=value)

    def filter_by_sub_source_type(self, queryset, name, value):
        return queryset.filter(sub_source_type=value)

    class Meta:
        model = Ingredients
        fields = {}


class UserIngredientFilter(django_filters.FilterSet):
    user = django_filters.ModelChoiceFilter(queryset=User.objects.all())
    ingredient = django_filters.ModelChoiceFilter(queryset=Ingredients.objects.all())

    class Meta:
        model = UserIngredient
        fields = {}
