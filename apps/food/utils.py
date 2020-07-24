# Todo add energy to response
import random

from apps.food.models import Ingredients, UserIngredient


def get_ingredient_source_types(data):
    protein = data['protein']  # 0.85
    fiber = data['fiber']  # 0
    fat = data['fat']  # 81.11
    carbohydrate = data['fat']  # 0.06

    data['sub_source_type'] = Ingredients.SUB_SOURCE_TYPE_CHOICES.none
    data['source_type'] = Ingredients.SOURCE_TYPE_CHOICES.none

    if protein >= 15 and fat >= 5:
        data['sub_source_type'] = Ingredients.SUB_SOURCE_TYPE_CHOICES.fat_protein

    if protein >= 15 and carbohydrate >= 15:
        data['sub_source_type'] = Ingredients.SUB_SOURCE_TYPE_CHOICES.carbohydrate_protein

    if fat >= 5 and fiber >= 10:
        data['sub_source_type'] = Ingredients.SUB_SOURCE_TYPE_CHOICES.fat_fiber

    if carbohydrate >= 15 and fiber >= 10:
        data['sub_source_type'] = Ingredients.SUB_SOURCE_TYPE_CHOICES.carbohydrate_fiber

    if fat >= 60:
        data['sub_source_type'] = Ingredients.SUB_SOURCE_TYPE_CHOICES.pure_fat

    if (fat < 5 and protein < 10 and fiber < 10) or carbohydrate >= 50:
        data['sub_source_type'] = Ingredients.SUB_SOURCE_TYPE_CHOICES.pure_carbohydrate

    if carbohydrate < 10 and protein < 5 and fiber > 0 and fat < 5:
        data['sub_source_type'] = Ingredients.SUB_SOURCE_TYPE_CHOICES.vegetable

    # Todo add ingredient source types logic.
    if protein >= 15:
        data['source_type'] = Ingredients.SOURCE_TYPE_CHOICES.protein

    if fat >= 5:
        data['source_type'] = Ingredients.SOURCE_TYPE_CHOICES.fat

    if fiber >= 10:
        data['source_type'] = Ingredients.SOURCE_TYPE_CHOICES.fiber
    if carbohydrate >= 15:
        data['source_type'] = Ingredients.SOURCE_TYPE_CHOICES.carbohydrate
    return data


def get_user_ingredients_by_percent(user):
    user_ingredients = UserIngredient.objects.filter(user=user)
    total_ingredients_count = user_ingredients.count()
    response = {
        "fat_protein": 0,
        "carbohydrate_protein": 0,
        "fat_fiber": 0,
        "carbohydrate_fiber": 0,
        "pure_fat": 0,
        "pure_carbohydrate": 0,
        "vegetable": 0,
        "total_ingredients_count": 0,
    }
    if total_ingredients_count:
        fat_protein_count = user_ingredients.filter(
            ingredient__sub_source_type=Ingredients.SUB_SOURCE_TYPE_CHOICES.fat_protein).count()
        response['fat_protein'] = fat_protein_count / total_ingredients_count * 100

        carbohydrate_protein_count = user_ingredients.filter(
            ingredient__sub_source_type=Ingredients.SUB_SOURCE_TYPE_CHOICES.carbohydrate_protein).count()
        response['carbohydrate_protein'] = carbohydrate_protein_count / total_ingredients_count * 100

        fat_fiber_count = user_ingredients.filter(
            ingredient__sub_source_type=Ingredients.SUB_SOURCE_TYPE_CHOICES.fat_fiber).count()
        response['fat_fiber'] = fat_fiber_count / total_ingredients_count * 100
        carbohydrate_fiber_count = user_ingredients.filter(
            ingredient__sub_source_type=Ingredients.SUB_SOURCE_TYPE_CHOICES.carbohydrate_fiber).count()
        response['carbohydrate_fiber'] = carbohydrate_fiber_count / total_ingredients_count * 100
        pure_fat_count = user_ingredients.filter(
            ingredient__sub_source_type=Ingredients.SUB_SOURCE_TYPE_CHOICES.pure_fat).count()
        response['pure_fat'] = pure_fat_count / total_ingredients_count * 100

        pure_carbohydrate_count = user_ingredients.filter(
            ingredient__sub_source_type=Ingredients.SUB_SOURCE_TYPE_CHOICES.pure_carbohydrate).count()
        response['pure_carbohydrate'] = pure_carbohydrate_count / total_ingredients_count * 100
        vegetable_count = user_ingredients.filter(
            ingredient__sub_source_type=Ingredients.SUB_SOURCE_TYPE_CHOICES.vegetable).count()
        response['vegetable'] = vegetable_count / total_ingredients_count * 100
        response['total_ingredients_count'] = total_ingredients_count

    return response


def get_serving_size(ingredient):
    protein = float(ingredient.protein)
    fat = float(ingredient.fat)
    carbohydrate = float(ingredient.carbohydrate)
    fiber = float(ingredient.fiber)
    energy = float(ingredient.energy)
    serving_size = 0

    # Protein calculation method
    if protein >= 2.8 * fat and protein >= 2 * carbohydrate:
        if protein == 0 or energy == 0:
            serving_size = 0
        else:
            serving_size = 3750 / protein
            if serving_size > 450:
                serving_size = 45000 / energy

    # Carbohydrate calculation method
    elif carbohydrate > fat and fat < 10:
        if energy == 0 or carbohydrate == 0:
            serving_size = 0
        else:
            serving_size = 5400 / carbohydrate
            if serving_size > 250 and fiber < 10:
                serving_size = 25000 / energy

    # Vegetable calculation method
    elif protein < 5 and fat < 5 and carbohydrate < 10:
        serving_size = random.randint(50, 150)
    # Fat calculation method
    elif fat > carbohydrate or fat > 10:
        if fat == 0 or energy == 0:
            serving_size = 0
        else:
            serving_size = 1680 / fat
            if serving_size > 240:
                serving_size = 25000 / energy
            if serving_size > 370 and fiber > 10:
                serving_size = 37000 / energy
    elif 'alcohol' in ingredient.name.lower():
        serving_size = 160

    return serving_size
