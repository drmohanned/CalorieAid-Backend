from rest_framework import serializers
from rest_framework.serializers import ModelSerializer, Serializer
from taggit.models import Tag

from apps.food.models import UserIngredient, Ingredients
from apps.food.serializers import UserIngredientSerializer
from apps.recipes.models import DailyBox, DailyBoxIngredient, Recipe, FavoriteRecipe, LikeRecipe
from apps.users.serializers import UserSerializer


class DailyBoxSerializer(ModelSerializer):
    id = serializers.ReadOnlyField()
    day_of_week = serializers.ChoiceField(required=True, choices=DailyBox.WEEKDAYS_CHOICES, allow_null=False,
                                          allow_blank=False, )
    user = UserSerializer(read_only=True)

    def validate(self, attrs):
        attrs['user'] = self.context['request'].user
        daily_box_exists = DailyBox.objects.filter(
            user=attrs['user'], day_of_week=attrs['day_of_week']).exists()
        if daily_box_exists:
            raise serializers.ValidationError('Daily box already exists.')
        return attrs

    class Meta:
        model = DailyBox
        fields = [
            'id',
            'user',
            'day_of_week',
        ]


class DailyBoxIngredientSerializer(ModelSerializer):
    id = serializers.ReadOnlyField()
    daily_box = serializers.PrimaryKeyRelatedField(
        queryset=DailyBox.objects.all(),
        required=True,
        allow_null=False,
    )
    user_ingredient = serializers.PrimaryKeyRelatedField(
        queryset=UserIngredient.objects.all(),
        required=True,
        allow_null=False,
    )

    serving_size = serializers.ReadOnlyField(source='get_serving_size')

    def validate(self, attrs):
        daily_box_ingredient_exists = DailyBoxIngredient.objects.filter(daily_box=attrs['daily_box'],
                                                                        user_ingredient=attrs[
                                                                            'user_ingredient']).exists()
        if daily_box_ingredient_exists:
            raise serializers.ValidationError('DailyBoxIngredient already exits.')
        return attrs

    class Meta:
        model = DailyBoxIngredient
        fields = [
            'id',
            'daily_box',
            'user_ingredient',
            'serving_size',
        ]


class TagSerializer(ModelSerializer):
    id = serializers.ReadOnlyField()

    name = serializers.CharField(
        max_length=255,
        required=True,
        allow_blank=True
    )

    slug = serializers.CharField(
        max_length=255,
        required=True,
        allow_blank=True
    )

    class Meta:
        model = Tag
        fields = '__all__'

    def create(self, validated_data):
        return super().create(validated_data)

    def update(self, instance, validated_data):
        return super().update(instance, validated_data)

    def validate(self, data):
        self.check_exist_tag(self, data['name'])
        return data

    @staticmethod
    def check_exist_tag(self, value):
        if Tag.objects.filter(name=value).exists():
            if self.instance:
                if Tag.objects.get(name=value).id == self.instance.id:
                    return value
            raise serializers.ValidationError('This tag already exists.')
        return value


class RecipeSerializer(ModelSerializer):
    id = serializers.ReadOnlyField()
    name = serializers.CharField(max_length=255, allow_null=False, allow_blank=False)
    image = serializers.ImageField(required=True)
    further_ingredients = serializers.CharField(required=True, allow_null=False, allow_blank=False)
    description = serializers.CharField(required=True, allow_null=False, allow_blank=False)
    tags = serializers.SerializerMethodField(method_name='get_recipe_tags')
    daily_box = serializers.PrimaryKeyRelatedField(queryset=DailyBox.objects.all())

    def get_recipe_tags(self, instance):
        tags = instance.get_recipe_tags()
        return TagSerializer(tags, many=True).data

    class Meta:
        model = Recipe
        fields = [
            'id',
            'name',
            'daily_box',
            'image',
            'further_ingredients',
            'description',
            'tags',
        ]


class FavoriteRecipeSerializer(ModelSerializer):
    id = serializers.ReadOnlyField()
    recipe = serializers.PrimaryKeyRelatedField(
        queryset=Recipe.objects.all(),
        required=True,
        allow_null=False,
        allow_empty=False,
    )
    user = UserSerializer(read_only=True)

    def save(self, **kwargs):
        self.validated_data['user'] = self.context['request'].user
        self.instance = self.create(self.validated_data)
        return self.instance

    def validate(self, attrs):
        exists_favorite = FavoriteRecipe.objects.filter(user=self.context['request'].user,
                                                        recipe=attrs['recipe']).exists()
        if exists_favorite:
            raise serializers.ValidationError('Recipe exists in your favorite recipes.')
        return attrs

    class Meta:
        model = FavoriteRecipe
        fields = [
            'id',
            'user',
            'recipe',
        ]


class LikeRecipeSerializer(ModelSerializer):
    id = serializers.ReadOnlyField()
    recipe = serializers.PrimaryKeyRelatedField(
        queryset=Recipe.objects.all(),
        required=True,
        allow_null=False,
        allow_empty=False,
    )
    user = UserSerializer(read_only=True)

    def save(self, **kwargs):
        self.validated_data['user'] = self.context['request'].user
        self.instance = self.create(self.validated_data)
        return self.instance

    def validate(self, attrs):
        exists_favorite = LikeRecipe.objects.filter(user=self.context['request'].user,
                                                    recipe=attrs['recipe']).exists()
        if exists_favorite:
            raise serializers.ValidationError('Recipe exists in your favorite recipes.')
        return attrs

    class Meta:
        model = LikeRecipe
        fields = [
            'id',
            'user',
            'recipe',
        ]


class RecipeTagSerializer(Serializer):
    id = serializers.ReadOnlyField()

    name = serializers.CharField(
        max_length=255,
        required=True,
        allow_blank=True
    )
    recipe = serializers.PrimaryKeyRelatedField(
        required=True,
        queryset=Recipe.objects.all(),
        allow_null=False,
        allow_empty=False,
    )

    def save(self, validated_data):
        recipe = Recipe.objects.get(pk=validated_data['recipe'])
        recipe.tags.add(validated_data['name'])
        new_tag = recipe.tags.filter(name=validated_data['name']).first()
        return new_tag

    def validate(self, data):
        self.check_exist_tag(self, data['name'])
        return data

    @staticmethod
    def check_exist_tag(self, value):
        recipe_exists_tag = Recipe.tags.filter(name=value).exists()
        if recipe_exists_tag:
            raise serializers.ValidationError('This tag already exists.')


class FoodSelectorSerializer(serializers.Serializer):
    ingridients = UserIngredientSerializer(many=True)


class CreateNewDailyboxSerializer(serializers.ModelSerializer):
    id = serializers.ReadOnlyField()
    ingridients = serializers.ListField(
        child=serializers.PrimaryKeyRelatedField(queryset=Ingredients.objects.all(), allow_null=False,
                                                 allow_empty=False), required=True)
    day_of_week = serializers.ChoiceField(required=True, choices=DailyBox.WEEKDAYS_CHOICES, allow_null=False,
                                          allow_blank=False, )

    def validate(self, attrs):
        box_ingridients = attrs['ingridients']
        attrs['user'] = self.context['request'].user

        if DailyBox.objects.filter(user=attrs['user'], day_of_week=attrs['day_of_week']).exists():
            raise serializers.ValidationError('dailybox user and day_of_week must be unique.')
        daily_box = DailyBox(user=attrs['user'], day_of_week=attrs['day_of_week'])
        daily_box.save()
        for x in box_ingridients:
            UserIngredient.objects.get_or_create(user=attrs['user'], ingredient=x)
            daily_box_ingredient = DailyBoxIngredient(ingredient=x, daily_box=daily_box)
            daily_box_ingredient.save()

        return attrs

    class Meta:
        model = DailyBox
        fields = [
            'id',
            'ingridients',
            'day_of_week',
        ]
