from django.contrib.auth.models import User
from django.shortcuts import get_object_or_404
from django.core import serializers as dj_serializer
from django.http import Http404, HttpResponseForbidden, HttpResponseBadRequest
from rest_framework import generics, status
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.reverse import reverse
from random import randint
from rest_framework_simplejwt.views import TokenObtainPairView
from .models import Note, VibrailleUser
from .serializers import (
    VBTokenObtainPairSerializer,
    RegisterSerializer,
    TranslationSerializer
)


@api_view(['GET'])
@permission_classes([AllowAny])
def api_root(request, format=None):
    """Root Paths for UI."""
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
    """Get all notes associated with user."""
    try:
        active_user = User.objects.filter(username=request.user.username).first()
        all_notes = dj_serializer.serialize('json', Note.objects.filter(user=active_user).all())
        return Response(data=all_notes, status=status.HTTP_200_OK)
    except Exception:
        raise Http404("No notes found for this user.")


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_note_details(request, note_id):
    """Gets details of a given note."""
    active_user = User.objects.filter(username=request.user.username).first()
    _target_note = get_object_or_404(Note, id=note_id)
    if active_user == _target_note.user:
        note_details = dj_serializer.serialize('json', [_target_note])
        return Response(data=note_details, status=status.HTTP_200_OK)
    else:
        raise HttpResponseForbidden("Note does not belong to user.")


@api_view(['PUT'])
@permission_classes([IsAuthenticated])
def edit_note_details(request, note_id):
    """Edit details on a note (Title is the only updatable field."""
    active_user = User.objects.filter(username=request.user.username).first()
    _target_note = get_object_or_404(Note, id=note_id)
    if active_user == _target_note.user:
        if request.data.get('title'):
            Note.objects.filter(id=note_id).update(title=request.data.get('title'))
            note_details = dj_serializer.serialize('json', [Note.objects.get(id=note_id)])
            return Response(data=note_details, status=status.HTTP_200_OK)
        else:
            return HttpResponseBadRequest
    else:
        raise HttpResponseForbidden("Note does not belong to user.")


@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def remove_note(request, note_id):
    """Deletes a given note."""
    active_user = User.objects.filter(username=request.user.username).first()
    _target_note = get_object_or_404(Note, id=note_id)
    if active_user == _target_note.user:
        _target_note.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
    else:
        raise HttpResponseForbidden("Note does not belong to user.")


@api_view(['PUT'])
@permission_classes([AllowAny])
def verify_phone(request):
    """Verification of phone associated with user account."""
    active_user = None
    if request.data.get('phone_number'):
        active_user = VibrailleUser.objects.filter(phone_number=request.data.get('phone_number')).first().user
    if request.data.get('verify_str'):
        attempted_token = request.data.get('verify_str')
        if active_user.vibrailleuser.veri_str_phone == attempted_token:
            _vb = VibrailleUser.objects.get(user=active_user)
            _vb.verified_phone = True
            _vb.veri_str_phone = ''
            _vb.save()
            return Response(status=status.HTTP_200_OK)
        else:
            return Response(data="Verification code did not match.", status=status.HTTP_400_BAD_REQUEST)
    else:
        return Response(data="No data passed.", status=status.HTTP_400_BAD_REQUEST)


@api_view(['PUT'])
@permission_classes([AllowAny])
def verify_email(request):
    """Verification of email associated with user account."""
    active_user = None
    if request.data.get('email'):
        active_user = User.objects.filter(email=request.data.get('email')).first()
    if request.data.get('verify_str'):
        attempted_token = request.data.get('verify_str')
        if active_user.vibrailleuser.veri_str_email == attempted_token:
            _vb = VibrailleUser.objects.get(user=active_user)
            _vb.verified_email = True
            _vb.veri_str_email = ''
            _vb.save()
            return Response(status=status.HTTP_200_OK)
        else:
            return Response(data="Verification code did not match.", status=status.HTTP_400_BAD_REQUEST)
    else:
        return Response(data="No data passed.", status=status.HTTP_400_BAD_REQUEST)


@api_view(['PUT'])
def verify_refresh(request):
    """Refreshes verification strings for endpoint."""
    _ret_data = {}
    if request.data.get('email'):
        active_user = User.objects.filter(email=request.data.get('email')).first()
    elif request.data.get('phone_number'):
        active_user = VibrailleUser.objects.filter(phone_number=request.data.get('phone_number')).first().user
    else:
        return Response(status=status.HTTP_400_BAD_REQUEST)
    _vb = VibrailleUser.objects.get(user=active_user)
    if not _vb.verified_phone:
        _vb.veri_str_phone = "%05d" % randint(0, 99999)
        _ret_data["verification_phone"] = _vb.veri_str_phone
    if not _vb.verified_email:
        _vb.veri_str_email = "%05d" % randint(0, 99999)
        _ret_data["verification_email"] = _vb.veri_str_email
    _vb.save()
    return Response(data=_ret_data, status=status.HTTP_200_OK)


class TranslatorBrailleViews(generics.CreateAPIView):
    """Generic API view for handling image to braille translation."""
    queryset = Note.objects.all()
    permission_classes = (IsAuthenticated,)
    serializer_class = TranslationSerializer


class RegisterView(generics.CreateAPIView):
    """Generic API view for registration."""
    queryset = User.objects.all()
    permission_classes = (AllowAny,)
    serializer_class = RegisterSerializer


class VBObtainTokenPairView(TokenObtainPairView):
    """JWT View for handling Login."""
    permission_classes = (AllowAny,)
    serializer_class = VBTokenObtainPairSerializer

