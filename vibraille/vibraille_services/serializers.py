from django.contrib.auth.models import User
from .models import Note, VibrailleUser
from .braille_utils import BrailleTranslator
from rest_framework import serializers, status
from rest_framework.response import Response
from rest_framework.validators import UniqueValidator
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer, PasswordField


class RegisterSerializer(serializers.ModelSerializer):
    email = serializers.EmailField(
        required=True,
        validators=[UniqueValidator(queryset=User.objects.all())]
    )
    password = serializers.CharField(write_only=True, required=True)
    phone_number = serializers.IntegerField(write_only=True, required=True)

    class Meta:
        model = User
        fields = ('username', 'password', 'email', 'phone_number')

    def create(self, validated_data):
        user = User.objects.create(
            username=validated_data['username'],
            email=validated_data['email'],
        )
        user.set_password(validated_data['password'])
        user.save()

        _vb_obj = VibrailleUser.objects.get(user=user)
        _vb_obj.phone_number = validated_data['phone_number']
        _vb_obj.save()
        return user


class VBTokenObtainPairSerializer(TokenObtainPairSerializer):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['username'] = serializers.CharField(required=False)
        self.fields['phone_number'] = serializers.IntegerField(required=False)
        self.fields['email'] = serializers.EmailField(required=False)
        self.fields['password'] = PasswordField(trim_whitespace=False)

    def validate(self, attrs):
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
            credentials['username'] = user_obj.username
        return super().validate(credentials)

    @classmethod
    def get_token(cls, user):
        token = super(VBTokenObtainPairSerializer, cls).get_token(user)
        token['username'] = user.username
        return token


class TranslationSerializer(serializers.ModelSerializer):
    title = serializers.CharField(max_length=100, required=False, allow_blank=True)
    img = serializers.ImageField(required=False)
    img_name = serializers.CharField(max_length=100, required=False, allow_blank=True)
    ascii_text = serializers.CharField(required=False, allow_blank=True)
    braille_format = serializers.CharField(required=False, allow_blank=True)

    class Meta:
        model = Note
        fields = ['user','created', 'title', 'img', 'img_name', 'ascii_text', 'braille_format']

    def create(self, data):
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
            new_note.user = user_acct
            new_note.save()
            return new_note
        except Exception as e:
            return Response(data=e, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
