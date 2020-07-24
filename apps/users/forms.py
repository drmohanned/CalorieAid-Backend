from django.contrib.auth.forms import UserCreationForm, UserChangeForm, UsernameField


class CustomUserCreationForm(UserCreationForm):

    class Meta:
        fields = ('email',)
        field_classes = {'email': UsernameField}


class CustomUserChangeForm(UserChangeForm):

    class Meta:
        fields = '__all__'
        field_classes = {'email': UsernameField}
