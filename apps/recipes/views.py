from django.db.models import Q
from rest_framework import status
from rest_framework.parsers import MultiPartParser
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.viewsets import ModelViewSet
from taggit.models import Tag

from apps.food.models import UserIngredient, Ingredients
from apps.food.serializers import IngredientSerializer
from apps.recipes.filters import DailyBoxFilter, DailyBoxIngredientFilter, TagFilter, RecipeFilter, \
    FavoriteRecipeFilter, LikeRecipeFilter
from apps.recipes.models import DailyBox, DailyBoxIngredient, Recipe, FavoriteRecipe, LikeRecipe
from apps.recipes.permissions import IngredientsFullyWritten
from apps.recipes.serializers import DailyBoxSerializer, DailyBoxIngredientSerializer, TagSerializer, RecipeSerializer, \
    RecipeTagSerializer, FavoriteRecipeSerializer, LikeRecipeSerializer, FoodSelectorSerializer, \
    CreateNewDailyboxSerializer
from apps.recipes.utils import DailyBoxResponse


class DailyBoxViewSet(ModelViewSet):
    http_method_names = ['get', 'put', 'patch', 'delete', 'post', ]
    queryset = DailyBox.objects.all()
    serializer_class = DailyBoxSerializer
    permission_classes = [IsAuthenticated]
    filter_class = DailyBoxFilter

    def get_queryset(self):
        return self.queryset.filter(user=self.request.user)


class DailyBoxIngredientViewSet(ModelViewSet):
    http_method_names = ['get', 'put', 'patch', 'delete', 'post', ]
    queryset = DailyBoxIngredient.objects.all()
    serializer_class = DailyBoxIngredientSerializer
    permission_classes = [IsAuthenticated]
    filter_class = DailyBoxIngredientFilter

    def get_queryset(self):
        return self.queryset.filter(daily_box__user=self.request.user)


class TagViewSet(ModelViewSet):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    http_method_names = ['get', 'put', 'patch', 'delete', 'post', ]
    permission_classes = [IsAuthenticated]
    filter_class = TagFilter


class RecipeViewSet(ModelViewSet):
    queryset = Recipe.objects.all()
    http_method_names = ['get', 'post', 'delete']
    serializer_class = RecipeSerializer
    filter_class = RecipeFilter
    permission_classes = [IsAuthenticated]
    parser_classes = (MultiPartParser,)


class RecipeTagsApiView(APIView):
    serializer_class = RecipeTagSerializer
    permission_classes = [IsAuthenticated, ]

    def get_serializer(self):
        return self.serializer_class()

    def post(self, request):
        serializer = RecipeTagSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        new_tag = serializer.save(serializer.data)

        return Response(TagSerializer(new_tag, read_only=True).data, status=status.HTTP_201_CREATED)

    def delete(self, request, pk, format=None):
        Tag.objects.filter(pk=pk).delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class FavoriteRecipeViewSet(ModelViewSet):
    queryset = FavoriteRecipe.objects.all()
    http_method_names = ['get', 'post', 'delete']
    serializer_class = FavoriteRecipeSerializer
    filter_class = FavoriteRecipeFilter
    permission_classes = [IsAuthenticated]


class LikeRecipeViewSet(ModelViewSet):
    queryset = LikeRecipe.objects.all()
    http_method_names = ['get', 'post', 'delete']
    serializer_class = LikeRecipeSerializer
    filter_class = LikeRecipeFilter
    permission_classes = [IsAuthenticated]


class FoodSelectorApiView(APIView):
    serializer_class = FoodSelectorSerializer
    permission_classes = [IngredientsFullyWritten, ]

    def get_serializer(self):
        return self.serializer_class()

    def get_combinations(self, request, user_ingredients):
        daily_intakes = request.user.get_other_daily_macronutrient_need()
        daily_box = DailyBoxResponse()
        daily_fat_intake_max = daily_intakes['daily_fat_intake'] * 1.2
        daily_carbohydrates_intake_max = daily_intakes['daily_carbohydrates_intake'] * 1.2
        daily_protein_intake_max = daily_intakes['daily_protein_intake'] * 1.2
        daily_fiber_intake_max = daily_intakes['daily_fiber_intake'] * 1.2

        daily_fat_intake_min = daily_intakes['daily_fat_intake'] * 0.8
        daily_carbohydrates_intake_min = daily_intakes['daily_carbohydrates_intake'] * 0.8
        daily_protein_intake_min = daily_intakes['daily_protein_intake'] * 0.8
        daily_fiber_intake_min = daily_intakes['daily_fiber_intake'] * 0.8

        return daily_box.combinationSum2(user_ingredients, {
            'daily_fat_intake_max': daily_fat_intake_max,
            'daily_carbohydrates_intake_max': daily_carbohydrates_intake_max,
            'daily_protein_intake_max': daily_protein_intake_max,
            'daily_fiber_intake_max': daily_fiber_intake_max,

            'daily_fat_intake_min': daily_fat_intake_min,
            'daily_carbohydrates_intake_min': daily_carbohydrates_intake_min,
            'daily_protein_intake_min': daily_protein_intake_min,
            'daily_fiber_intake_min': daily_fiber_intake_min,

            'fat_total': 0,
            'fiber_total': 0,
            'carb_total': 0,
            'protein_total': 0,
        })

    def get(self, request):
        user_ingredients = UserIngredient.objects.filter(user=request.user).order_by('?')
        user_ingredients_ingredient_ids = [x.ingredient.pk for x in user_ingredients]

        combinations = self.get_combinations(request, user_ingredients)

        if len(combinations) == 0:
            all_ingredients = Ingredients.objects.filter(
                pk__in=user_ingredients_ingredient_ids).order_by('?') | Ingredients.objects.filter(
                ~Q(pk__in=user_ingredients_ingredient_ids)).order_by('?')
            combinations = self.get_combinations(request, all_ingredients)
        return Response({
            'combination': IngredientSerializer(Ingredients.objects.filter(pk__in=combinations[0]), many=True).data
        })


class CreateNewDailybox(APIView):
    serializer_class = CreateNewDailyboxSerializer
    permission_classes = [IngredientsFullyWritten, ]

    def get_serializer(self):
        return self.serializer_class()

    def post(self, request):
        serializer = self.serializer_class(data=request.data, context={'request': request})
        serializer.is_valid(raise_exception=True)
        print(serializer.data)
        return Response({
            'daily_box': DailyBoxSerializer(serializer.data).data
        })
