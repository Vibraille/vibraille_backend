from django.contrib.auth.models import User
from .models import Note
from .braille_utils import BrailleTranslator
from rest_framework import serializers, status
from rest_framework.response import Response
from rest_framework.validators import UniqueValidator
from django.contrib.auth.password_validation import validate_password
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer


class RegisterSerializer(serializers.ModelSerializer):
    email = serializers.EmailField(
        required=True,
        validators=[UniqueValidator(queryset=User.objects.all())]
    )
    password = serializers.CharField(write_only=True, required=True, validators=[validate_password])
    password2 = serializers.CharField(write_only=True, required=True)

    class Meta:
        model = User
        fields = ('username', 'password', 'password2', 'email', 'first_name', 'last_name')
        extra_kwargs = {
            'first_name': {'required': True},
            'last_name': {'required': True}
        }

    def validate(self, attrs):
        if attrs['password'] != attrs['password2']:
            raise serializers.ValidationError({"password": "Password fields didn't match."})

        return attrs

    def create(self, validated_data):
        user = User.objects.create(
            username=validated_data['username'],
            email=validated_data['email'],
            first_name=validated_data['first_name'],
            last_name=validated_data['last_name']
        )

        user.set_password(validated_data['password'])
        user.save()

        return user


class VBTokenObtainPairSerializer(TokenObtainPairSerializer):

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
        # if Note.objects.filter(title=data.get("img").name).exists():
        #     raise serializers.ValidationError('This image has already been translated.')
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


class NoteSerializer(serializers.ModelSerializer):
    title = serializers.CharField(max_length=100, required=False, allow_blank=True)
    img = serializers.ImageField(required=False)
    img_name = serializers.CharField(max_length=100, required=False, allow_blank=True)
    ascii_text = serializers.CharField(required=False, allow_blank=True)
    braille_format = serializers.CharField(required=False, allow_blank=True)

    class Meta:
        model = Note
        fields = ['created', 'title', 'img', 'img_name', 'ascii_text', 'braille_format']

    def get(self, data):
        try:
            return Response(data=data.braille_format.encode('utf-8'), status=status.HTTP_201_CREATED)
        except Exception as e:
            return Response(data=e, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class UserSerializer(serializers.HyperlinkedModelSerializer):
    snippets = serializers.HyperlinkedRelatedField(many=True, view_name='notes', read_only=True)

    class Meta:
        model = User
        fields = ['url', 'id', 'username', 'notes']
