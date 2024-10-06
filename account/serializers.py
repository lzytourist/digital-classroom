from django.contrib.auth import authenticate
from rest_framework import serializers

from account.models import User, PasswordReset, TeacherProfile, StudentProfile


class UserSerializer(serializers.ModelSerializer):
    def create(self, validated_data):
        if validated_data['user_type'] != User.UserType.ADMIN:
            validated_data['is_active'] = False
        return User.objects.create_user(**validated_data)

    class Meta:
        model = User
        fields = ('id', 'email', 'password', 'name', 'user_type', 'is_active')
        extra_kwargs = {
            'password': {
                'write_only': True,
            }
        }


class PasswordResetRequestSerializer(serializers.Serializer):
    email = serializers.EmailField()

    def validate_email(self, value):
        if not User.objects.filter(email=value).exists():
            raise serializers.ValidationError('No user is associated with this email address.')
        return value


class PasswordResetConfirmSerializer(serializers.Serializer):
    email = serializers.EmailField()
    code = serializers.CharField(max_length=6)
    new_password = serializers.CharField(min_length=6, write_only=True)

    def validate(self, data):
        try:
            user = User.objects.get(email=data['email'])
        except User.DoesNotExist:
            raise serializers.ValidationError('No user is associated with this email address.')

        reset_code = PasswordReset.objects.filter(user=user, code=data['code'], is_used=False).first()
        if not reset_code:
            raise serializers.ValidationError('Invalid or expired reset code.')

        if reset_code.is_expired():
            raise serializers.ValidationError('Reset code has expired.')

        data['user'] = user
        data['reset_code'] = reset_code
        return data


class TokenSerializer(serializers.Serializer):
    email = serializers.EmailField(write_only=True)
    password = serializers.CharField(write_only=True, trim_whitespace=False)
    token = serializers.CharField(read_only=True)

    def validate(self, attrs):
        email = attrs.get('email')
        password = attrs.get('password')

        if email and password:
            user = authenticate(request=self.context.get('request'),
                                email=email, password=password)
            if not user or not user.is_active:
                msg = 'Unable to log in with provided credentials.'
                raise serializers.ValidationError(msg, code='authorization')
        else:
            msg = 'Must include "email" and "password".'
            raise serializers.ValidationError(msg, code='authorization')

        attrs['user'] = user
        return attrs


class TeacherProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = TeacherProfile
        fields = ['name', 'email', 'department', 'designation', 'teacher_id', 'blood_group']
        extra_kwargs = {
            'department': {'required': True},
            'designation': {'required': True},
        }


class StudentProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = StudentProfile
        fields = ['name', 'email', 'department', 'roll', 'semester', 'section', 'student_id', 'father', 'father_phone',
                  'mother', 'mother_phone', 'blood_group', 'present_address', 'permanent_address']
        extra_kwargs = {
            'semester': {'required': True},
        }


class UserActiveStatusSerializer(serializers.ModelSerializer):
    user_id = serializers.IntegerField(write_only=True)

    class Meta:
        model = User
        fields = ('user_id', 'is_active')
        extra_kwargs = {
            'user_id': {'required': True},
            'is_active': {'required': True}
        }
