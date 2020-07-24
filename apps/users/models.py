from django.contrib.auth.base_user import BaseUserManager
from django.contrib.auth.models import AbstractUser
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
from django.utils import timezone
from model_utils import Choices

from apps.core.models import AbstractBaseModel
from apps.core.utils import UploadDir


class CustomUserManager(BaseUserManager):
    def create_user(self, email, password=None, is_active=False):
        if not email:
            raise ValueError('Users must have an email address')

        user = self.model(
            email=self.normalize_email(email),
            is_active=is_active,
        )

        user.set_password(password)
        user.save()
        return user

    def create_superuser(self, email, password):
        user = self.create_user(
            email,
            password=password,
        )
        user.is_staff = True
        user.is_superuser = True
        user.is_active = True
        user.save()
        return user


class User(AbstractUser, AbstractBaseModel):
    GENDER_CHOICES = Choices(
        (0, 'male', 'Male'),
        (1, 'female', 'Female'),
    )
    WEEKDAYS_CHOICES = Choices(
        (0, 'mon', 'Monday'), (1, 'tue', 'Tuesday'), (2, 'wed', 'Wednesday'),
        (3, 'thu', 'Thursday'), (4, 'fri', 'Friday'), (5, 'sat', 'Saturday'),
        (6, 'sun', 'Sunday'),
    )
    GOAL_CHOICES = Choices(
        (0, 'none', 'None'),
        (1, 'muscle', 'Muscle Gain'),
        (2, 'fat_loss', 'Fat Loss'),
        (3, 'maintenance', 'Maintenance'),
    )
    username = models.CharField(
        blank=True,
        null=True,
        max_length=255,
    )
    name = models.CharField(
        blank=True,
        null=True,
        max_length=255,
    )
    image = models.ImageField(
        upload_to=UploadDir('user_images'),
        null=True,
        blank=True,
    )
    email = models.EmailField(unique=True)
    email_confirmation_token = models.CharField(
        blank=True,
        null=True,
        max_length=255,
    )
    gender = models.SmallIntegerField(choices=GENDER_CHOICES, default=GENDER_CHOICES.male)
    birthday = models.DateField(default=timezone.now)
    length = models.SmallIntegerField(default=0)
    address = models.CharField(blank=True, null=True, max_length=255)
    activity = models.IntegerField(
        default=1,
        validators=[MaxValueValidator(5), MinValueValidator(1)]
    )
    reset_key = models.CharField(
        blank=True,
        null=True,
        max_length=255,
    )
    measurement_day = models.SmallIntegerField(
        choices=WEEKDAYS_CHOICES, default=WEEKDAYS_CHOICES.mon)
    goal = models.SmallIntegerField(choices=GOAL_CHOICES, default=GOAL_CHOICES.none)

    followers = models.ManyToManyField('User', related_name='following', through='Follow')

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

    objects = CustomUserManager()

    def follow(self, other_user):
        return Follow.objects.create(to_user=self, from_user=other_user)

    def unfollow(self, other_user):
        Follow.objects.filter(to_user=self, from_user=other_user).delete()

    def add_follower(self, other_user):
        return other_user.follow(self)

    def remove_follower(self, other_user):
        other_user.unfollow(self)

    def get_goal_settings(self):
        if self.goal:
            return self.goal
        else:
            measurement = MeasurementResult.objects.filter(user=self).first()
            default_goal = User.GOAL_CHOICES.none
            if measurement is not None:
                body_fat_percentage = measurement.get_body_fat_percentage()
                lean_body_mass = measurement.get_lean_body_mass()
                perfect_lean_body_mass = measurement.get_perfect_lean_body_mass()
                if self.gender == User.GENDER_CHOICES.male:
                    if body_fat_percentage < 0.05:
                        default_goal = User.GOAL_CHOICES.muscle
                    if body_fat_percentage > 0.15:
                        default_goal = User.GOAL_CHOICES.fat_loss
                    if 0.05 < body_fat_percentage < 0.15:
                        if lean_body_mass < perfect_lean_body_mass:
                            default_goal = User.GOAL_CHOICES.muscle
                        if lean_body_mass >= perfect_lean_body_mass:
                            default_goal = User.GOAL_CHOICES.maintenance
                else:
                    if body_fat_percentage < 0.1:
                        default_goal = User.GOAL_CHOICES.muscle
                    if body_fat_percentage > 0.1:
                        default_goal = User.GOAL_CHOICES.fat_loss
                    if 0.1 < body_fat_percentage < 0.2:
                        if lean_body_mass < perfect_lean_body_mass:
                            default_goal = User.GOAL_CHOICES.muscle
                        if lean_body_mass >= perfect_lean_body_mass:
                            default_goal = User.GOAL_CHOICES.maintenance
            return default_goal

    def get_other_daily_macronutrient_need(self):
        measurement = MeasurementResult.objects.filter(user=self).first()
        macronutrients = {
            'daily_fat_intake': 0,
            'daily_carbohydrates_intake': 0,
            'daily_protein_intake': 0,
            'daily_fiber_intake': 0,
        }
        if measurement is not None:
            lean_body_mass = measurement.get_lean_body_mass()
            if self.goal == User.GOAL_CHOICES.fat_loss:
                macronutrients['daily_fat_intake'] = lean_body_mass * 0.39
                macronutrients['daily_carbohydrates_intake'] = lean_body_mass * 1.234
            if self.goal == User.GOAL_CHOICES.muscle:
                macronutrients['daily_fat_intake'] = lean_body_mass * 0.5 + 4.7 * self.activity
                macronutrients['daily_carbohydrates_intake'] = lean_body_mass * \
                    1.75 + 14.25 * self.activity
            if self.goal == User.GOAL_CHOICES.maintenance:
                macronutrients['daily_fat_intake'] = lean_body_mass * 0.44 + 4.7 * self.activity
                macronutrients['daily_carbohydrates_intake'] = lean_body_mass * \
                    1.5 + 14.25 * self.activity

            macronutrients['daily_protein_intake'] = lean_body_mass
            macronutrients['daily_fiber_intake'] = 25
            if self.gender == User.GENDER_CHOICES.male:
                macronutrients['daily_fiber_intake'] = 38

        return macronutrients

    def __str__(self):
        return self.email


class MeasurementResult(AbstractBaseModel):
    user = models.ForeignKey(User, on_delete=models.CASCADE, blank=True, null=True, )
    date = models.DateField(default=timezone.now)

    waist = models.PositiveIntegerField(null=False, blank=False, )
    weight = models.PositiveIntegerField(null=False, blank=False, )

    wrist_circumference = models.PositiveIntegerField(null=True, blank=True, )
    hip_circumference = models.PositiveIntegerField(null=True, blank=True, )
    forearm_circumference = models.PositiveIntegerField(null=True, blank=True, )

    body_fat_percentage = models.PositiveIntegerField(null=True, blank=True, )

    def get_lean_body_mass(self):
        if self.body_fat_percentage:
            total_body_fat = self.weight * self.body_fat_percentage/100
            lean_body_mass = self.weight - total_body_fat
            return lean_body_mass
        else:
            if self.user.gender == User.GENDER_CHOICES.male:
                return self.weight * 1.082 - self.waist * 4.15 + 94.42
            else:
                result1 = self.weight * 0.732 + 8.987
                result2 = self.wrist_circumference / 3.14
                result3 = self.waist * 0.157
                result4 = self.hip_circumference * 0.249
                result5 = self.forearm_circumference * 0.434
                result6 = result1 + result2
                result7 = result6 - result3
                result8 = result7 - result4
                return result5 + result8

    def get_body_fat_percentage(self):
        if self.body_fat_percentage:
            return self.body_fat_percentage
        else:
            total_body_fat = self.weight - self.get_lean_body_mass()
            body_fat_percentage = total_body_fat / self.weight
            return body_fat_percentage

    def get_perfect_lean_body_mass(self):
        perfect_lean_body_mass = (self.user.length * 2.54 - 100) * 2.2
        return perfect_lean_body_mass

    def get_perfect_weight(self):
        if self.user.gender == User.GENDER_CHOICES.male:
            return self.get_perfect_lean_body_mass() / 0.85
        else:
            return self.get_perfect_lean_body_mass() / 0.8

    def get_perfect_total_body_fat(self):
        return self.get_perfect_weight() - self.get_perfect_lean_body_mass()

    def __str__(self):
        return "MeasurementResult %s" % self.user.email


class Advertisement(AbstractBaseModel):
    image = models.ImageField(upload_to=UploadDir('advert_images'), null=False, blank=False)
    text = models.TextField(null=False, blank=False)
    link = models.URLField(null=False, blank=False)

    def __str__(self):
        return "Advert Id: %s" % self.pk

    class Meta:
        verbose_name = "Advertisement"


class Follow(models.Model):
    # The user being *followed*
    from_user = models.ForeignKey(User, related_name='from_user', on_delete=models.CASCADE)
    # The user *following*
    to_user = models.ForeignKey(User, related_name='to_user', on_delete=models.CASCADE)
    created = models.DateTimeField(auto_now_add=True)

    @property
    def feed_order(self):
        return self.created
