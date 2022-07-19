from django.urls import include, path
from django.contrib import admin
from django.conf import settings
from django.conf.urls.static import static
from rest_framework import routers
from vibraille.vibraille_services.views import (
    NotesBrailleViews,
    TranslatorBrailleViews,
    VBObtainTokenPairView,
    RegisterView,
    api_root,
    get_all_notes,
    UserViewSet
)
from rest_framework_simplejwt.views import (
    TokenRefreshView,
)

router = routers.DefaultRouter()
router.register(r'users', UserViewSet, basename='users')

# Wire up our API using automatic URL routing.
# Additionally, we include login URLs for the browsable API.
urlpatterns = [
    path('', api_root),
    path('admin/', admin.site.urls),
    path('login/', VBObtainTokenPairView.as_view(), name='login'),
    path('login/refresh/', TokenRefreshView.as_view(), name='login_token_refresh'),
    path('register/', RegisterView.as_view(), name='register'),
    path('notes/translate/', TranslatorBrailleViews.as_view(), name='translate_img'),
    path('notes/', get_all_notes, name='view_all_notes'),
    path('api-auth/', include('rest_framework.urls', namespace='rest_framework'))
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
