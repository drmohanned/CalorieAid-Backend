from django.db import models
from model_utils import Choices
from taggit.managers import TaggableManager

from apps.core.models import AbstractBaseModel
from apps.core.utils import UploadDir
from apps.food.models import UserIngredient, Ingredients
from apps.food.utils import get_serving_size
from apps.users.models import User


class DailyBox(AbstractBaseModel):
    WEEKDAYS_CHOICES = Choices(
        (0, 'mon', 'Monday'), (1, 'tue', 'Tuesday'), (2, 'wed', 'Wednesday'),
        (3, 'thu', 'Thursday'), (4, 'fri', 'Friday'), (5, 'sat', 'Saturday'),
        (6, 'sun', 'Sunday'),
    )

    user = models.ForeignKey(User, on_delete=models.CASCADE, null=False, blank=False)
    day_of_week = models.SmallIntegerField(choices=WEEKDAYS_CHOICES, default=WEEKDAYS_CHOICES.mon)

    def __str__(self):
        return 'Daily box : %d' % self.pk

    class Meta:
        verbose_name = 'Daily Box'
        unique_together = (('user', 'day_of_week'),)


class DailyBoxIngredient(AbstractBaseModel):
    daily_box = models.ForeignKey(DailyBox, on_delete=models.CASCADE, null=False, blank=False)
    ingredient = models.ForeignKey(Ingredients, on_delete=models.CASCADE, null=False, blank=False)

    def __str__(self):
        return "Daily Box Ingredient : %d" % self.pk

    @property
    def get_serving_size(self):
        return get_serving_size(self.ingredient)

    class Meta:
        verbose_name = 'Daily Box Ingredient'
        unique_together = (('daily_box', 'ingredient'),)


class Recipe(AbstractBaseModel):
    daily_box = models.ForeignKey(DailyBox, on_delete=models.CASCADE, null=False, blank=False)
    name = models.CharField(max_length=255, null=False, blank=False)
    image = models.ImageField(upload_to=UploadDir('recipe_images'), null=False, blank=False)
    further_ingredients = models.TextField(null=True, blank=True)
    description = models.TextField(null=False, blank=False)

    tags = TaggableManager(blank=True)

    def get_recipe_tags(self):
        return self.tags.all()

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'Recipe'


class FavoriteRecipe(AbstractBaseModel):
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=False, blank=False)
    recipe = models.ForeignKey(Recipe, on_delete=models.CASCADE, null=False, blank=False)

    def __str__(self):
        return "FavoriteRecipe %s" % self.pk

    class Meta:
        verbose_name = 'FavoriteRecipe'
        unique_together = (('user', 'recipe'),)


class LikeRecipe(AbstractBaseModel):
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=False, blank=False)
    recipe = models.ForeignKey(Recipe, on_delete=models.CASCADE, null=False, blank=False)

    def __str__(self):
        return "LikeRecipe %s" % self.pk

    class Meta:
        verbose_name = 'LikeRecipe'
        unique_together = (('user', 'recipe'),)
