from django.urls import path
from rest_framework import routers

from apps.food.views import IngredientViewSet, UserIngredientViewSet, CheckIngredientCountAPIView, \
    GetIngredientPercentAPIView

router = routers.DefaultRouter()

router.register('ingredient', IngredientViewSet)
router.register('user-ingredient', UserIngredientViewSet)

app_name = 'food'
urlpatterns = [
    path('check-ingredients-count', CheckIngredientCountAPIView.as_view()),
    path('get-ingredients-by-percent', GetIngredientPercentAPIView.as_view()),
]
