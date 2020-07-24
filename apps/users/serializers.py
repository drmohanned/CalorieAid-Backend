from django.contrib.auth import authenticate
from django.utils.translation import ugettext_lazy as _
from rest_framework import serializers
from rest_framework.exceptions import ValidationError

from apps.core.utils import generate_unique_key, send_email_job_registration, is_invalid_password
from apps.users.models import User, MeasurementResult


class AuthTokenSerializer(serializers.Serializer):
    email = serializers.CharField(label=_("Email"))
    password = serializers.CharField(
        label=_("Password"),
        style={'input_type': 'password'},
        trim_whitespace=False
    )

    def validate(self, attrs):
        email = attrs.get('email')
        password = attrs.get('password')

        if email and password:
            user = authenticate(request=self.context.get('request'),
                                username=email, password=password)

            # The authenticate call simply returns None for is_active=False
            # users. (Assuming the default ModelBackend authentication
            # backend.)
            if not user:
                msg = _('Unable to log in with provided credentials.')
                raise serializers.ValidationError(msg, code='authorization')
        else:
            msg = _('Must include "email" and "password".')
            raise serializers.ValidationError(msg, code='authorization')

        attrs['user'] = user
        return attrs


class ForgotPasswordSerializer(serializers.Serializer):
    email = serializers.EmailField()

    @staticmethod
    def send_mail(validated_data):
        user = User.objects.get(email=validated_data['email'])
        user.reset_key = generate_unique_key(user.email)

        send_email_job_registration(
            'Nutrition',
            user.email,
            'reset_password',
            {
                'reset_key': user.reset_key,
                'name': user.name
            },
            'Reset your password',
        )
        user.save()

    def validate(self, data):
        self.check_email(data['email'])
        return data

    @staticmethod
    def check_email(value):
        user = User.objects.filter(email=value)
        if not user.exists():
            raise serializers.ValidationError('This email address does not exist.')
        if not user.filter(is_active=True).exists():
            raise serializers.ValidationError('Your account is inactive.')
        return value


class ResetPasswordSerializer(serializers.Serializer):
    password = serializers.CharField(required=True, allow_null=False, allow_blank=False)
    repeat_password = serializers.CharField(required=True, allow_null=False, allow_blank=False)
    reset_key = serializers.CharField(required=True, allow_null=False, allow_blank=False)

    def reset(self, validated_data):
        user = User.objects.get(reset_key=validated_data['reset_key'])
        user.set_password(validated_data['password'])
        user.reset_key = None
        user.save()

    def validate(self, data):
        self.check_valid_password(data)
        self.check_valid_token(data)

        return data

    def check_valid_token(self, attrs):
        if not User.objects.filter(reset_key=attrs['reset_key']).exists():
            raise serializers.ValidationError('Token is not valid.')

    def check_valid_password(self, data):
        invalid_password_message = is_invalid_password(
            data.get('password'), data.get('repeat_password'))
        if invalid_password_message:
            raise serializers.ValidationError(invalid_password_message)


class UserSerializerBase(serializers.ModelSerializer):
    email = serializers.EmailField(required=True)
    gender = serializers.ChoiceField(required=True, choices=User.GENDER_CHOICES)

    class Meta:
        model = User
        fields = [
            'id',
            'name',
            'image',
            'email',
            'gender',
            'birthday',
            'length',
            'activity',
            'is_active',
            'measurement_day',
            'goal',
        ]

    def validate(self, attrs):
        email = attrs.get('email')
        if email:
            user = User.objects.filter(email=email).first()
            if user is None:
                return attrs

            if self.context['request'].user.email == user.email:
                return attrs
            else:
                raise ValidationError('User with given email already exists.')
        if 'goal' not in attrs:
            user = self.context['request'].user
            if user.goal == User.GOAL_CHOICES.none:
                attrs['goal'] = user.get_goal_settings()
        return attrs


class UserSerializer(UserSerializerBase):
    name = serializers.CharField(required=True)
    length = serializers.IntegerField(required=True)
    activity = serializers.IntegerField(required=True, min_value=1, max_value=5)
    birthday = serializers.DateField(required=True)
    measurement_day = serializers.ChoiceField(required=True, choices=User.WEEKDAYS_CHOICES)
    goal = serializers.ChoiceField(required=True, choices=User.GOAL_CHOICES)

    goal_settings = serializers.SerializerMethodField()
    other_daily_macronutrient_need = serializers.SerializerMethodField()

    def get_goal_settings(self, obj):
        return obj.get_goal_settings()

    def get_other_daily_macronutrient_need(self, obj):
        return obj.get_other_daily_macronutrient_need()

    class Meta:
        model = User
        fields = UserSerializerBase.Meta.fields + \
            ['goal_settings', 'other_daily_macronutrient_need', ]


class AuthorizedUserSerializer(UserSerializerBase):
    token = serializers.CharField(source='auth_token')

    class Meta:
        model = User
        fields = UserSerializerBase.Meta.fields + ['token', ]


class ImageSerializer(serializers.Serializer):
    image = serializers.ImageField(required=True)


class SignUpSerializer(serializers.Serializer):
    email = serializers.EmailField()

    name = serializers.CharField(required=True)
    image = serializers.ImageField(required=False)
    length = serializers.IntegerField(required=True)
    address = serializers.CharField(required=True)
    birthday = serializers.DateField(required=True)
    gender = serializers.ChoiceField(required=True, choices=User.GENDER_CHOICES)

    password = serializers.CharField(required=True)
    repeat_password = serializers.CharField(required=True)

    @staticmethod
    def save_user(validated_data):
        user = User(email=validated_data['email'])
        user.set_password(validated_data['password'])
        user.name = validated_data.get('name', None)
        user.length = validated_data.get('length', None)
        user.birthday = validated_data.get('birthday', None)
        user.gender = validated_data.get('gender', None)
        user.is_active = True
        user.email_confirmation_token = generate_unique_key(user.email)
        user.save()

    def validate(self, data):
        self.check_valid_password(data)
        self.check_valid_email(data['email'])

        return data

    @staticmethod
    def check_valid_email(value):
        if User.objects.filter(email=value).exists():
            raise serializers.ValidationError('This email address already exists.')

        return value

    def check_valid_password(self, data):
        invalid_password_message = is_invalid_password(
            data.get('password'), data.get('repeat_password'))
        if invalid_password_message:
            raise serializers.ValidationError(invalid_password_message)


class MeasurementResultSerializer(serializers.ModelSerializer):
    id = serializers.ReadOnlyField()

    date = serializers.DateField(required=True, allow_null=False, )
    waist = serializers.IntegerField(required=True, allow_null=False, )
    weight = serializers.IntegerField(required=True, allow_null=False, )
    wrist_circumference = serializers.IntegerField(required=True, allow_null=False, )
    hip_circumference = serializers.IntegerField(required=True, allow_null=False, )
    forearm_circumference = serializers.IntegerField(required=True, allow_null=False, )
    body_fat_percentage = serializers.IntegerField(required=False, allow_null=True, )

    lean_body_mass = serializers.SerializerMethodField()
    perfect_lean_body_mass = serializers.SerializerMethodField()
    perfect_weight = serializers.SerializerMethodField()
    perfect_total_body_fat = serializers.SerializerMethodField()
    user = UserSerializer(read_only=True)

    def get_perfect_total_body_fat(self, obj):
        return obj.get_perfect_total_body_fat()

    def get_perfect_lean_body_mass(self, obj):
        return obj.get_perfect_lean_body_mass()

    def get_lean_body_mass(self, obj):
        return obj.get_lean_body_mass()

    def get_perfect_weight(self, obj):
        return obj.get_perfect_weight()

    def validate(self, attrs):
        attrs['user'] = self.context['request'].user
        return attrs

    class Meta:
        model = MeasurementResult
        fields = [
            'id',
            'user',
            'date',
            'waist',
            'weight',
            'wrist_circumference',
            'hip_circumference',
            'forearm_circumference',
            'body_fat_percentage',
            'lean_body_mass',
            'perfect_lean_body_mass',
            'perfect_weight',
            'perfect_total_body_fat',
        ]
