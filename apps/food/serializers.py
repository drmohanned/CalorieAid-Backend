from rest_framework import serializers

from apps.food.models import Ingredients, UserIngredient
from apps.food.utils import get_ingredient_source_types
from apps.users.serializers import UserSerializer


class IngredientSerializer(serializers.ModelSerializer):
    id = serializers.ReadOnlyField()
    name = serializers.CharField(max_length=255, required=True, allow_blank=False, allow_null=False)

    protein = serializers.DecimalField(max_digits=14, decimal_places=2, allow_null=False)
    fat = serializers.DecimalField(max_digits=14, decimal_places=2, allow_null=False)
    carbohydrate = serializers.DecimalField(max_digits=14, decimal_places=2, allow_null=False)
    fiber = serializers.DecimalField(max_digits=14, decimal_places=2, allow_null=False)

    energy = serializers.ReadOnlyField()
    source_type = serializers.ReadOnlyField()
    sub_source_type = serializers.ReadOnlyField()

    def save(self, **kwargs):
        data = get_ingredient_source_types(self.validated_data)
        return self.create(data)

    class Meta:
        model = Ingredients
        fields = [
            'id',
            'name',
            'protein',
            'fat',
            'carbohydrate',
            'fiber',
            'energy',
            'source_type',
            'sub_source_type',

        ]


class UserIngredientSerializer(serializers.ModelSerializer):
    id = serializers.ReadOnlyField()

    user = UserSerializer(read_only=True)
    ingredient = serializers.PrimaryKeyRelatedField(
        queryset=Ingredients.objects.all(),
        allow_null=False,
        allow_empty=False,
    )

    def validate(self, attrs):
        user_ingredient_exists = UserIngredient.objects.filter(user=self.context['request'].user,
                                                               ingredient=attrs['ingredient']).exists()
        if user_ingredient_exists:
            raise serializers.ValidationError(
                "Duplicate ingredient user violates unique constraint.")

        return attrs

    def save(self, **kwargs):
        self.validated_data['user'] = self.context['request'].user
        return self.create(self.validated_data)

    class Meta:
        model = UserIngredient
        fields = [
            'id',
            'user',
            'ingredient',
        ]


class CheckIngredientSerializer(serializers.Serializer):
    def validate(self, attrs):
        self.check_valid_ingredients(self.context['request'].user)

        return attrs

    def check_valid_ingredients(self, user):
        user_ingredients = UserIngredient.objects.filter(user=user)
        fat_protein = user_ingredients.filter(
            ingredient__sub_source_type=Ingredients.SUB_SOURCE_TYPE_CHOICES.fat_protein).count()
        carbohydrate_protein = user_ingredients.filter(
            ingredient__sub_source_type=Ingredients.SUB_SOURCE_TYPE_CHOICES.carbohydrate_protein).count()
        fat_fiber = user_ingredients.filter(
            ingredient__sub_source_type=Ingredients.SUB_SOURCE_TYPE_CHOICES.fat_fiber).count()
        carbohydrate_fiber = user_ingredients.filter(
            ingredient__sub_source_type=Ingredients.SUB_SOURCE_TYPE_CHOICES.carbohydrate_fiber).count()
        pure_fat = user_ingredients.filter(
            ingredient__sub_source_type=Ingredients.SUB_SOURCE_TYPE_CHOICES.pure_fat).count()
        pure_carbohydrate = user_ingredients.filter(
            ingredient__sub_source_type=Ingredients.SUB_SOURCE_TYPE_CHOICES.pure_carbohydrate).count()
        vegetable_count = user_ingredients.filter(
            ingredient__sub_source_type=Ingredients.SUB_SOURCE_TYPE_CHOICES.vegetable).count()

        fat_count = fat_protein + fat_fiber + pure_fat
        fiber_count = fat_fiber + carbohydrate_fiber
        carbohydrate_count = carbohydrate_protein + carbohydrate_fiber + pure_carbohydrate
        protein_count = fat_protein + carbohydrate_protein

        if protein_count < 3:
            raise serializers.ValidationError('Protein sources count is invalid.')
        if fat_count < 3:
            raise serializers.ValidationError('Fat sources count is invalid.')
        if fiber_count < 2:
            raise serializers.ValidationError('Fiber sources count is invalid.')
        if carbohydrate_count < 3:
            raise serializers.ValidationError('Carbohydrate sources count is invalid.')
        if vegetable_count < 4:
            raise serializers.ValidationError('Vegetable sources count is invalid.')
        if user_ingredients.count() < 15:
            raise serializers.ValidationError('Please select minimum 15 ingredients.')
        return True
