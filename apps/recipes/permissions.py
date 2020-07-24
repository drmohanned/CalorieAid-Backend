from rest_framework.permissions import BasePermission

from apps.food.models import UserIngredient, Ingredients


class IngredientsFullyWritten(BasePermission):
    def has_permission(self, request, view):
        if bool(request.user and request.user.is_authenticated):
            user_ingredients = UserIngredient.objects.filter(user=request.user)
            fat_protein = user_ingredients.filter(
                ingredient__sub_source_type=Ingredients.SUB_SOURCE_TYPE_CHOICES.fat_protein
            ).count()
            carbohydrate_protein = user_ingredients.filter(
                ingredient__sub_source_type=Ingredients.SUB_SOURCE_TYPE_CHOICES.carbohydrate_protein
            ).count()
            fat_fiber = user_ingredients.filter(
                ingredient__sub_source_type=Ingredients.SUB_SOURCE_TYPE_CHOICES.fat_fiber
            ).count()
            carbohydrate_fiber = user_ingredients.filter(
                ingredient__sub_source_type=Ingredients.SUB_SOURCE_TYPE_CHOICES.carbohydrate_fiber
            ).count()
            pure_fat = user_ingredients.filter(
                ingredient__sub_source_type=Ingredients.SUB_SOURCE_TYPE_CHOICES.pure_fat
            ).count()
            pure_carbohydrate = user_ingredients.filter(
                ingredient__sub_source_type=Ingredients.SUB_SOURCE_TYPE_CHOICES.pure_carbohydrate
            ).count()
            vegetable_count = user_ingredients.filter(
                ingredient__sub_source_type=Ingredients.SUB_SOURCE_TYPE_CHOICES.vegetable
            ).count()

            fat_count = fat_protein + fat_fiber + pure_fat
            fiber_count = fat_fiber + carbohydrate_fiber
            carbohydrate_count = (
                carbohydrate_protein + carbohydrate_fiber + pure_carbohydrate
            )
            protein_count = fat_protein + carbohydrate_protein

            if (
                protein_count < 3
                or fat_count < 3
                or fiber_count < 2
                or carbohydrate_count < 3
                or vegetable_count < 4
                or user_ingredients.count() < 15
            ):
                return False
            return True
        return False
