from rest_framework import permissions, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.viewsets import ModelViewSet

from apps.food.filters import IngredientFilter, UserIngredientFilter
from apps.food.models import Ingredients, UserIngredient
from apps.food.serializers import IngredientSerializer, UserIngredientSerializer, CheckIngredientSerializer
from apps.food.utils import get_user_ingredients_by_percent


class IngredientViewSet(ModelViewSet):
    http_method_names = ['get', 'put', 'patch', 'delete', 'post', ]
    queryset = Ingredients.objects.filter(status=Ingredients.STATUS_CHOICES.active)
    serializer_class = IngredientSerializer
    permission_classes = [IsAuthenticated]
    filter_class = IngredientFilter

    def get_permissions(self):
        if self.request.method == 'GET':
            return [permissions.AllowAny(), ]
        return [permissions.IsAuthenticated(), ]


class UserIngredientViewSet(ModelViewSet):
    http_method_names = ['get', 'put', 'patch', 'delete', 'post', ]
    queryset = UserIngredient.objects.all()
    serializer_class = UserIngredientSerializer
    permission_classes = [IsAuthenticated]
    filter_class = UserIngredientFilter

    def get_queryset(self):
        if self.request.method != 'GET':
            return UserIngredient.objects.filter(user=self.request.user)
        return UserIngredient.objects.all()


class CheckIngredientCountAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        serializer = CheckIngredientSerializer(data={}, context={'request': request})
        serializer.is_valid(raise_exception=True)
        return Response(
            {
                'result': 'valid',
            },
            status=status.HTTP_200_OK,
        )


class GetIngredientPercentAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        response = get_user_ingredients_by_percent(request.user)

        return Response(
            {
                'result': response,
            },
            status=status.HTTP_200_OK,
        )
