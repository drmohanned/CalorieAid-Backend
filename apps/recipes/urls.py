from django.urls import path
from rest_framework import routers

from apps.recipes.views import DailyBoxViewSet, DailyBoxIngredientViewSet, TagViewSet, RecipeViewSet, RecipeTagsApiView, \
    FavoriteRecipeViewSet, LikeRecipeViewSet, FoodSelectorApiView, CreateNewDailybox

router = routers.DefaultRouter()

router.register('daily-box', DailyBoxViewSet)
router.register('daily-box-ingredient', DailyBoxIngredientViewSet)
router.register('tag', TagViewSet)
router.register('recipe', RecipeViewSet)
router.register('favorite-recipe', FavoriteRecipeViewSet)
router.register('like-recipe', LikeRecipeViewSet)

app_name = 'recipes'
urlpatterns = [
    path('recipe-tag', RecipeTagsApiView.as_view()),
    path('food-selector', FoodSelectorApiView.as_view()),
    path('create-new-daily-box', CreateNewDailybox.as_view()),
]
