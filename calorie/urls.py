from django.conf import settings
from django.conf.urls import url
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path, include
from drf_yasg import openapi
from drf_yasg.views import get_schema_view
from rest_framework import routers, permissions

from apps.food.urls import router as ingredient_router
from apps.recipes.urls import router as recipes_router
from apps.users.urls import router as users_router

admin.site.site_header = 'Calorie'
admin.site.site_title = 'Calorie'
admin.site.index_title = 'Welcome to Calorie Administration'

schema_view = get_schema_view(
    openapi.Info(
        title='Calorie API',
        default_version='v1',
        description='Calorie api endpoints',
    ),
    validators=['flex', 'ssv'],
    public=True,
    permission_classes=(permissions.AllowAny,),
)


class DefaultRouter(routers.DefaultRouter):
    def extend(self, app_router):
        self.registry.extend(app_router.registry)


router = DefaultRouter()
router.extend(users_router)
router.extend(ingredient_router)
router.extend(recipes_router)

urlpatterns = [
                  path('admin/', admin.site.urls),
                  path('', include('apps.users.urls')),
                  path('', include('apps.food.urls')),
                  path('', include('apps.recipes.urls')),
                  url('^searchableselect/', include('searchableselect.urls')),
                  path('', include(router.urls)),
                  path('api-auth/', include('rest_framework.urls', namespace='rest_framework')),
                  path('swagger.json', schema_view.without_ui(cache_timeout=0), name='schema-json'),
                  path('swagger.yaml', schema_view.without_ui(cache_timeout=0), name='schema-json'),
                  path('swagger/', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
                  path('redoc/', schema_view.with_ui('redoc', cache_timeout=0), name='schema-redoc'),
              ] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT) if settings.DEBUG else []
