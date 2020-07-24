import django_filters

from apps.users.models import MeasurementResult, User


class MeasurementResultFilter(django_filters.FilterSet):
    user = django_filters.ModelChoiceFilter(queryset=User.objects.all())

    class Meta:
        model = MeasurementResult
        fields = {}
