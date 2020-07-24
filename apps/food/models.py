import random

from django.db import models
from model_utils import Choices

from apps.core.models import AbstractBaseModel
from apps.users.models import User


class Ingredients(AbstractBaseModel):
    SOURCE_TYPE_CHOICES = Choices(
        (0, 'none', 'None'),
        (1, 'fat', 'Fat'),
        (2, 'fiber', 'Fiber'),
        (3, 'carbohydrate', 'Carbohydrate'),
        (4, 'protein', 'Protein'),

    )
    STATUS_CHOICES = Choices(
        (0, 'pending', 'Pending'),
        (1, 'active', 'Active'),
        (2, 'rejected', 'Rejected'),

    )
    SUB_SOURCE_TYPE_CHOICES = Choices(
        (0, 'none', 'None'),
        (1, 'fat_protein', 'Fat Protein'),
        (2, 'carbohydrate_protein', 'Carbohydrate Protein'),
        (3, 'fat_fiber', 'Fat Fiber'),
        (4, 'carbohydrate_fiber', 'Carbohydrate Fiber'),
        (5, 'pure_fat', 'Pure Fat'),
        (6, 'pure_carbohydrate', 'Pure Carbohydrate'),
        (7, 'vegetable', 'Vegetable'),

    )
    name = models.CharField(max_length=255, null=False, blank=False)
    protein = models.DecimalField(max_digits=14, decimal_places=2, null=False, blank=False)
    fat = models.DecimalField(max_digits=14, decimal_places=2, null=False, blank=False)
    carbohydrate = models.DecimalField(max_digits=14, decimal_places=2, null=False, blank=False)
    fiber = models.DecimalField(max_digits=14, decimal_places=2, null=False, blank=False)
    energy = models.DecimalField(max_digits=14, decimal_places=2, null=True, blank=True)
    sugar = models.DecimalField(max_digits=14, decimal_places=2, null=True, blank=True)

    source_type = models.SmallIntegerField(choices=SOURCE_TYPE_CHOICES, default=SOURCE_TYPE_CHOICES.none)
    sub_source_type = models.SmallIntegerField(choices=SUB_SOURCE_TYPE_CHOICES, default=SUB_SOURCE_TYPE_CHOICES.none)
    status = models.SmallIntegerField(choices=STATUS_CHOICES, default=STATUS_CHOICES.pending)

    def __str__(self):
        return "Ingredient id:%s name:%s" % (self.pk, self.name)

    class Meta:
        unique_together = ('name',)


class UserIngredient(AbstractBaseModel):
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=False, blank=False, )
    ingredient = models.ForeignKey(Ingredients, on_delete=models.CASCADE, null=False, blank=False, )

    def get_serving_size(self):
        ingredient = self.ingredient
        protein = float(ingredient.protein)
        fat = float(ingredient.fat)
        carbohydrate = float(ingredient.carbohydrate)
        fiber = float(ingredient.fiber)
        energy = float(ingredient.energy)
        serving_size = None

        # Protein calculation method
        if protein >= 2.8 * fat and protein >= 2 * carbohydrate:
            serving_size = 3750 / protein
            if serving_size > 450:
                serving_size = 45000 / energy
        # Vegetable calculation method
        elif protein < 5 and fat < 5 and carbohydrate < 10:
            serving_size = random.randint(50, 150)
        # Carbohydrate calculation method
        elif carbohydrate > fat and fat < 10:
            serving_size = 5400 / carbohydrate
            if serving_size > 250 and fiber < 10:
                serving_size = 25000 / energy
        # Fat calculation method
        elif fat > carbohydrate or fat > 10:
            serving_size = 1680 / fat
            if serving_size > 240:
                serving_size = 25000 / energy
            if serving_size > 370 and fiber > 10:
                serving_size = 37000 / energy
        elif 'alcohol' in ingredient.name.lower():
            serving_size = 160

        return serving_size

    def __str__(self):
        return "User %s ingredient %s" % (self.user.email, self.ingredient.name)

    class Meta:
        unique_together = ('ingredient', 'user')
