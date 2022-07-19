from django.contrib.auth.models import User
from django.shortcuts import get_object_or_404
from django.core import serializers as dj_serializer
from django.http import Http404, HttpResponseForbidden
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
    TranslationSerializer
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
    try:
        active_user = User.objects.filter(username=request.user.username).first()
        all_notes = dj_serializer.serialize('json', Note.objects.filter(user=active_user).all())
        return Response(data=all_notes, status=status.HTTP_200_OK)
    except Exception:
        raise Http404("No notes found for this user.")


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_note_details(request, note_id):
    active_user = User.objects.filter(username=request.user.username).first()
    _target_note = get_object_or_404(Note, id=note_id)
    if active_user == _target_note.user:
        note_details = dj_serializer.serialize('json', Note.objects.filter(id=note_id))
        return Response(data=note_details, status=status.HTTP_200_OK)
    else:
        raise HttpResponseForbidden("Note does not belong to user.")


@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def remove_note(request, note_id):
    active_user = User.objects.filter(username=request.user.username).first()
    _target_note = get_object_or_404(Note, id=note_id)
    if active_user == _target_note.user:
        _target_note.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
    else:
        raise HttpResponseForbidden("Note does not belong to user.")


class TranslatorBrailleViews(generics.CreateAPIView):
    queryset = Note.objects.all()
    permission_classes = (IsAuthenticated,)
    serializer_class = TranslationSerializer


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
