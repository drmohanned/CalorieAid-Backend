from django.urls import path
from rest_framework import routers

from apps.users.views import Login, ForgotPasswordAPIView, ResetPasswordAPIView, ImageAPIView, UserViewSet, \
    SignUpAPIView, MeasurementResultViewSet

router = routers.DefaultRouter()

router.register('users', UserViewSet)
router.register('measurement-result', MeasurementResultViewSet)

app_name = 'users'
urlpatterns = [
    path('login', Login.as_view()),
    path('forgot-password', ForgotPasswordAPIView.as_view()),
    path('reset-password', ResetPasswordAPIView.as_view()),
    path('user-image', ImageAPIView.as_view()),
    path('sign-up', SignUpAPIView.as_view()),
]
