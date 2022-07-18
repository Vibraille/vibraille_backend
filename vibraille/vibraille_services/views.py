from django.contrib.auth.models import User
from rest_framework import viewsets, permissions, generics, status, serializers, views
from rest_framework.permissions import AllowAny
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework.reverse import reverse
from rest_framework_simplejwt.views import TokenObtainPairView
from .models import Note
from .serializers import (
    UserSerializer,
    VBTokenObtainPairSerializer,
    RegisterSerializer,
    TranslationSerializer,
    NoteSerializer
)
from .braille_utils import BrailleTranslator


@api_view(['GET'])
def api_root(request, format=None):
    return Response({
        'translate_img': reverse('translate_img', request=request, format=format),
        'login': reverse('login', request=request, format=format),
        'login_refresh_jwt': reverse('login_token_refresh', request=request, format=format),
        'registration': reverse('register', request=request, format=format)
    })


class TranslatorBrailleViews(generics.CreateAPIView):
    queryset = Note.objects.all()
    permission_classes = (AllowAny,)
    serializer_class = TranslationSerializer


def get_notes(request, note_id):
    if request.method == "GET":
        note = Note.objects.get(id=note_id)
        return Response(data=note.braille_format.encode('utf-8'), status=status.HTTP_200_OK)


class NotesBrailleViews(generics.GenericAPIView):
    queryset = Note.objects.all()
    permission_classes = (AllowAny,)
    serializer_class = NoteSerializer


class RegisterView(generics.CreateAPIView):
    queryset = User.objects.all()
    permission_classes = (AllowAny,)
    serializer_class = RegisterSerializer


class VBObtainTokenPairView(TokenObtainPairView):
    permission_classes = (AllowAny,)
    serializer_class = VBTokenObtainPairSerializer


class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all().order_by('-date_joined')
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAuthenticated]
