from rest_framework import status, permissions
from rest_framework.authtoken.models import Token
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.decorators import action
from rest_framework.generics import ListAPIView
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.viewsets import ModelViewSet

from apps.users.filters import MeasurementResultFilter
from apps.users.models import User, MeasurementResult
from apps.users.serializers import ForgotPasswordSerializer, ResetPasswordSerializer, AuthTokenSerializer, \
    AuthorizedUserSerializer, ImageSerializer, UserSerializer, SignUpSerializer, MeasurementResultSerializer


class Login(ObtainAuthToken):
    serializer_class = AuthTokenSerializer

    def get_serializer(self):
        return self.serializer_class()

    def post(self, request, *args, **kwargs):
        """
        ---
        serializer: AuthTokenSerializer
        """
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data['user']
        Token.objects.get_or_create(user=user)

        return Response(AuthorizedUserSerializer(user, context={'request': request}).data, status.HTTP_200_OK)


class ForgotPasswordAPIView(APIView):
    serializer_class = ForgotPasswordSerializer

    def get_serializer(self):
        return self.serializer_class()

    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid(raise_exception=True):
            serializer.send_mail(serializer.data)
            return Response(
                {
                    'result': 'success',
                },
                status=status.HTTP_200_OK,
            )

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ResetPasswordAPIView(APIView):
    serializer_class = ResetPasswordSerializer

    def get_serializer(self):
        return self.serializer_class()

    def post(self, request):
        context = {
            'request': request,
        }
        serializer = self.serializer_class(data=request.data, context=context)
        if serializer.is_valid(raise_exception=True):
            serializer.reset(serializer.data)
            return Response(
                {
                    'success': True,
                },
                status=status.HTTP_200_OK,
            )

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class SignUpAPIView(APIView):
    serializer_class = SignUpSerializer

    def get_serializer(self):
        return self.serializer_class()

    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid(raise_exception=True):
            serializer.save_user(serializer.data)
            return Response(
                {
                    'result': 'success',
                },
                status=status.HTTP_201_CREATED,
            )


class ImageAPIView(APIView):
    serializer_class = ImageSerializer
    parser_classes = (MultiPartParser, FormParser)
    permission_classes = (IsAuthenticated,)

    def get_serializer(self):
        return self.serializer_class()

    def post(self, request):
        user = request.user
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        user.image = serializer.validated_data.get('image')
        user.save()
        return Response(AuthorizedUserSerializer(user, context={'request': request}).data, status.HTTP_200_OK)


class UserViewSet(ModelViewSet):
    http_method_names = ['get', 'put', 'patch', 'delete', ]
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated]

    def get_permissions(self):
        if self.request.method == 'GET':
            return [permissions.AllowAny(), ]
        else:
            return [permissions.IsAuthenticated(), ]

    def get_queryset(self):
        if self.request.method != 'GET':
            queryset = User.objects.filter(pk=self.request.user.id)
        else:
            queryset = User.objects.all()
        return queryset

    @action(detail=True, methods=['GET'])
    def following(self, request, pk=None):
        user = self.get_object()
        followings = user.following.all()
        page = self.paginate_queryset(followings)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        serializer = self.get_serializer(followings, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=['GET', 'POST', 'DELETE'], permission_classes=(IsAuthenticated,))
    def followers(self, request, pk=None):
        user = self.get_object()
        current_user = self.request.user
        if request.method == 'POST':
            if user != current_user:
                self.get_object().add_follower(current_user)
                return Response(status=status.HTTP_201_CREATED, data={})
            return Response(status=status.HTTP_400_BAD_REQUEST, data={'detail': "You can't follow yourself."})
        elif request.method == 'DELETE':
            self.get_object().remove_follower(current_user)
            return Response(status=status.HTTP_204_NO_CONTENT)

        followers = user.followers.all()
        page = self.paginate_queryset(followers)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        serializer = self.get_serializer(followers, many=True)
        return Response(serializer.data)


class FollowerView(ListAPIView):
    serializer_class = UserSerializer
    permission_classes = (IsAuthenticated,)

    def get_queryset(self):
        return self.request.user.followers.all()


class FollowingView(ListAPIView):
    serializer_class = UserSerializer
    permission_classes = (IsAuthenticated,)

    def get_queryset(self):
        return self.request.user.following.all()


class MeasurementResultViewSet(ModelViewSet):
    http_method_names = ['get', 'put', 'patch', 'delete', 'post', ]
    queryset = MeasurementResult.objects.all()
    serializer_class = MeasurementResultSerializer
    permission_classes = [IsAuthenticated]
    filter_class = MeasurementResultFilter

    def get_permissions(self):
        if self.request.method == 'GET':
            return [permissions.AllowAny(), ]
        return [permissions.IsAuthenticated(), ]

    def get_queryset(self):
        if self.request.method != 'GET':
            queryset = MeasurementResult.objects.filter(user=self.request.user)
        else:
            queryset = MeasurementResult.objects.all()
        return queryset
