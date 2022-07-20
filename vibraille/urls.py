from django.urls import include, path
from django.contrib import admin
from django.conf import settings
from django.conf.urls.static import static
from rest_framework import routers
from vibraille.vibraille_services.views import (
    TranslatorBrailleViews,
    VBObtainTokenPairView,
    RegisterView,
    api_root,
    get_all_notes,
    get_note_details,
    edit_note_details,
    remove_note,
    UserViewSet
)
from rest_framework_simplejwt.views import (
    TokenRefreshView,
)

router = routers.DefaultRouter()
router.register(r'users', UserViewSet, basename='users')

urlpatterns = [
    path('', api_root),
    path('admin/', admin.site.urls),
    path('login/', VBObtainTokenPairView.as_view(), name='login'),
    path('login/refresh/', TokenRefreshView.as_view(), name='login_token_refresh'),
    path('register/', RegisterView.as_view(), name='register'),
    path('notes/translate/', TranslatorBrailleViews.as_view(), name='translate_img'),
    path('notes/', get_all_notes, name='view_all_notes'),
    path('notes/<int:note_id>/', get_note_details, name='view_note_detail'),
    path('notes/<int:note_id>/edit', edit_note_details, name='view_note_detail'),
    path('notes/<int:note_id>/delete', remove_note, name='remove_note'),
    path('api-auth/', include('rest_framework.urls', namespace='rest_framework'))
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
