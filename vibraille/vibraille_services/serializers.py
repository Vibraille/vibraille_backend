from django.contrib.auth.models import User
from .models import Note, VibrailleUser
from .braille_utils import BrailleTranslator
from rest_framework import serializers, status
from rest_framework.response import Response
from rest_framework.validators import UniqueValidator
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer, PasswordField


class RegisterSerializer(serializers.ModelSerializer):
    """Serializer for registration"""
    email = serializers.EmailField(
        required=True,
        validators=[UniqueValidator(queryset=User.objects.all())]
    )
    password = serializers.CharField(write_only=True, required=True)
    phone_number = serializers.CharField(write_only=True, required=True)

    class Meta:
        model = User
        fields = ('username', 'password', 'email', 'phone_number')

    def to_representation(self, instance):
        """Override to include verification strings."""
        representation = super(RegisterSerializer, self).to_representation(instance['user'])
        representation['verification_strings'] = instance['verification_codes']
        return representation

    def create(self, validated_data):
        """Creates a new user."""
        data = {}
        user = User.objects.create(
            username=validated_data['username'],
            email=validated_data['email'],
        )
        user.set_password(validated_data['password'])
        user.save()

        _vb_obj = VibrailleUser.objects.get(user=user)
        _vb_obj.phone_number = validated_data['phone_number']
        _vb_obj.save()

        data['user'] = user
        data['verification_codes'] = {
            "verify_email": _vb_obj.veri_str_email,
            "verify_phone": _vb_obj.veri_str_phone
        }
        return data


class VBTokenObtainPairSerializer(TokenObtainPairSerializer):
    """JWT based login and token handling serializer."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['username'] = serializers.CharField(required=False)
        self.fields['phone_number'] = serializers.CharField(required=False)
        self.fields['email'] = serializers.EmailField(required=False)
        self.fields['password'] = PasswordField(trim_whitespace=False)

    def validate(self, attrs):
        """Custom validation for checking verified accounts."""
        credentials = {
            'username': '',
            'password': attrs.get("password")
        }
        user_obj = None
        if attrs.get("phone_number"):
            _target_users = [
                users for users in User.objects.all() if users.vibrailleuser.phone_number == attrs.get("phone_number")
            ]
            if _target_users:
                user_obj = _target_users[0]
        else:
            user_obj = User.objects.filter(email=attrs.get("email")).first() or \
                       User.objects.filter(username=attrs.get("username")).first()
        if user_obj:
            if attrs.get("email") and not user_obj.vibrailleuser.verified_email:
                return "Email is not verified yet!"
            elif attrs.get("phone_number") and not user_obj.vibrailleuser.verified_phone:
                return "Phone Number is not verified yet!"
            credentials['username'] = user_obj.username

        data = super().validate(credentials)
        refresh = self.get_token(self.user)
        data['refresh'] = str(refresh)
        data['access'] = str(refresh.access_token)
        _vb = VibrailleUser.objects.get(user=user_obj)
        data['user'] = {
            "id": user_obj.id,
            "email": user_obj.email,
            "phone_number": _vb.phone_number,
            "username": user_obj.username
        }
        return data

    @classmethod
    def get_token(cls, user):
        """Retrieves token."""
        token = super(VBTokenObtainPairSerializer, cls).get_token(user)
        token['username'] = user.username
        return token


class TranslationSerializer(serializers.ModelSerializer):
    """Serializer for handling image to braille translation."""
    title = serializers.CharField(max_length=100, required=False, allow_blank=True)
    img = serializers.ImageField(required=False)
    img_name = serializers.CharField(max_length=100, required=False, allow_blank=True)
    ascii_text = serializers.CharField(required=False, allow_blank=True)
    braille_format = serializers.CharField(required=False, allow_blank=True)

    class Meta:
        model = Note
        fields = ['id', 'user', 'created', 'title', 'img', 'img_name', 'ascii_text', 'braille_format', 'braille_binary']

    def create(self, data):
        """Creates a new Note object to contain braille translation."""
        user_acct = self.context['request'].user
        new_note = Note()
        try:
            b_process = BrailleTranslator(data.get("img"))
            new_note.title = data.get("img").name
            new_note.img = data.get("img")
            b_process.upload_to_s3()
            new_note.img_name = data.get("img").name
            new_note.ascii_text = b_process.convert_img_to_str()
            new_note.braille_format = b_process.convert_str_to_braille()
            new_note.braille_binary = b_process.convert_to_binary()
            new_note.user = user_acct
            new_note.save()
            return new_note
        except Exception as e:
            return Response(data=e, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
