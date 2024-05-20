from django.contrib.auth.models import User
from django.contrib.auth import authenticate
from rest_framework import serializers
from django.core.mail import send_mail
from django.utils.crypto import get_random_string
from .models import PasswordResetCode, Question, Subject, Teacher
from .settings import EMAIL_HOST_USER


# Registration Serializer for the User
class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('id', 'username', 'email', 'password', 'first_name', 'last_name')
        extra_kwargs = {'password': {'write_only': True}}

    def create(self, validated_data):
        user = User.objects.create_user(
            username=validated_data['username'],
            email=validated_data['email'],
            password=validated_data['password'],
            first_name=validated_data['first_name'],
            last_name=validated_data['last_name']
        )
        return user

# Login Serializer for the User
class LoginSerializer(serializers.Serializer):
    username = serializers.CharField()
    password = serializers.CharField(write_only=True)

    def validate(self, data):
        user = authenticate(username=data['username'], password=data['password'])
        if user and user.is_active:
            return user
        raise serializers.ValidationError("Invalid credentials")

# Confirm Code for resetting password
class PasswordResetRequestSerializer(serializers.Serializer):
    email = serializers.EmailField()
    def validate_email(self, value):
        try:
            user = User.objects.get(email=value)
        except User.DoesNotExist:
            raise serializers.ValidationError("User with this email does not exist.")
        return value

    def save(self):
        email = self.validated_data['email']
        user = User.objects.get(email=email)
        code = get_random_string(length=6, allowed_chars='0123456789')

        PasswordResetCode.objects.create(user=user, code=code)

        send_mail(
            'Password Reset Request',
            f'Your password reset code is {code}. It will expire in 10 minutes.',
            EMAIL_HOST_USER,
            [email],
            fail_silently=False,
        )

# Reset Password Serializer
class PasswordResetConfirmSerializer(serializers.Serializer):
    code = serializers.CharField(max_length=6)
    new_password = serializers.CharField(write_only=True)

    def validate_code(self, value):
        try:
            reset_code = PasswordResetCode.objects.get(code=value)
        except PasswordResetCode.DoesNotExist:
            raise serializers.ValidationError("Invalid code.")
        if reset_code.is_expired():
            raise serializers.ValidationError("The code has expired.")
        return value

    def save(self):
        code = self.validated_data['code']
        new_password = self.validated_data['new_password']
        reset_code = PasswordResetCode.objects.get(code=code)
        user = reset_code.user
        user.set_password(new_password)
        user.save()
        reset_code.delete()


# Teacher Serializer
class TeacherSerializer(serializers.ModelSerializer):
    class Meta:
        model = Teacher
        fields = '__all__'


# Subject Serializer
class SubjectListSerializer(serializers.ModelSerializer):
    class Meta:
        model = Subject
        fields = '__all__'


# Question Serializer
class QuestionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Question
        fields = '__all__'


# User Serializer
class UserCreateUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'password', 'first_name', 'last_name', 'is_staff', 'is_superuser']
        extra_kwargs = {
            'password': {'write_only': True},
            'is_superuser': {'read_only': True}
            # 'is_staff': {'read_only': True},
        }

    def create(self, validated_data):
        user = User.objects.create_user(**validated_data)
        return user
    

    def update(self, instance, validated_data):
        instance.username = validated_data.get('username', instance.username)
        instance.email = validated_data.get('email', instance.email)
        instance.first_name = validated_data.get('first_name', instance.first_name)
        instance.last_name = validated_data.get('last_name', instance.last_name)
        instance.is_staff = bool(validated_data.get('is_staff', instance.is_staff))
        instance.save()
        return instance