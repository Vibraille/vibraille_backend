from django.contrib.auth.models import User
from django.core import serializers as dj_serializer
from rest_framework import viewsets, permissions, generics, status
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.decorators import api_view, permission_classes
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


@api_view(['GET'])
def api_root(request, format=None):
    return Response({
        'translate_img': reverse('translate_img', request=request, format=format),
        'view_all_notes': reverse('view_all_notes', request=request, format=format),
        'login': reverse('login', request=request, format=format),
        'login_refresh_jwt': reverse('login_token_refresh', request=request, format=format),
        'registration': reverse('register', request=request, format=format)
    })


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_all_notes(request):
    import pdb;pdb.set_trace()
    active_user = User.objects.filter(username=request.user.username).first()
    all_notes = dj_serializer.serialize('json', Note.objects.filter(user=active_user).all())
    return Response(data=all_notes, status=status.HTTP_200_OK)


# @api_view(['GET'])
# @permission_classes([IsAuthenticated])
# def get_note_details(request):
#     import pdb;pdb.set_trace()
#     active_user = User.objects.filter(username=request.user.username).first()
#     all_notes = dj_serializer.serialize('json', Note.objects.filter(user=active_user).all())
#     return Response(data=all_notes, status=status.HTTP_200_OK)


class TranslatorBrailleViews(generics.CreateAPIView):
    queryset = Note.objects.all()
    permission_classes = (IsAuthenticated,)
    serializer_class = TranslationSerializer


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
