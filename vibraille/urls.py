from django.urls import include, path
from django.contrib import admin
from rest_framework import routers
from vibraille.vibraille_services.views import (
    VBObtainTokenPairView,
    RegisterView,
    api_root,
    UserViewSet
)
from rest_framework_simplejwt.views import (
    TokenRefreshView,
)

router = routers.DefaultRouter()
router.register(r'users', UserViewSet)

# Wire up our API using automatic URL routing.
# Additionally, we include login URLs for the browsable API.
urlpatterns = [
    path('', api_root),
    path('admin/', admin.site.urls),
    path('login/', VBObtainTokenPairView.as_view(), name='token_obtain_pair'),
    path('login/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('register/', RegisterView.as_view(), name='auth_register'),
    path('api-auth/', include('rest_framework.urls', namespace='rest_framework'))
]
