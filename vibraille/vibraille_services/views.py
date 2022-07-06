from django.contrib.auth.models import User
from rest_framework import viewsets, permissions, generics, renderers
from .serializers import UserSerializer, VBTokenObtainPairSerializer, RegisterSerializer
from rest_framework.permissions import AllowAny
from .models import Note
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework.reverse import reverse
from rest_framework_simplejwt.views import TokenObtainPairView


@api_view(['GET'])
def api_root(request, format=None):
    return Response({
        'login': reverse('login', request=request, format=format),
        'login_refresh_jwt': reverse('login_token_refresh', request=request, format=format),
        'registration': reverse('register', request=request, format=format)
    })


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
