from collections import defaultdict

from django.conf import settings
from django.core.mail import send_mail
from django.db import transaction
from rest_framework.authtoken.models import Token
from rest_framework.generics import CreateAPIView
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from rest_framework.views import APIView

from account.models import User, PasswordReset, StudentProfile, TeacherProfile
from account.permissions import IsAdmin, IsAdminOrTeacher
from account.serializers import UserSerializer, PasswordResetRequestSerializer, PasswordResetConfirmSerializer, \
    TokenSerializer, TeacherProfileSerializer, StudentProfileSerializer, UserActiveStatusSerializer


class UserRegistrationAPIView(CreateAPIView):
    serializer_class = UserSerializer
    queryset = User.objects.all()

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        with transaction.atomic():
            user = serializer.save()
            token = Token.objects.create(user=user)

            if user.user_type == User.UserType.STUDENT:
                student_serializer = StudentProfileSerializer(data=request.data)
                student_serializer.is_valid(raise_exception=True)

                StudentProfile.objects.create(
                    user=user,
                    name=user.name,
                    email=user.email,
                    department=request.data.get('department'),
                    roll=request.data.get('roll'),
                    semester=request.data.get('semester'),
                    section=request.data.get('section'),
                    student_id=request.data.get('student_id'),
                    updated_by=user
                )
            elif user.user_type == User.UserType.TEACHER:
                teacher_serializer = TeacherProfileSerializer(data=request.data)
                teacher_serializer.is_valid(raise_exception=True)

                TeacherProfile.objects.create(
                    user=user,
                    name=user.name,
                    email=user.email,
                    department=request.data.get('department'),
                    designation=request.data.get('designation'),
                    teacher_id=request.data.get('teacher_id'),
                    updated_by=user
                )

            return Response(
                data={
                    'token': token.key,
                    'user': serializer.data
                },
                status=status.HTTP_201_CREATED
            )


class UserLoginAPIView(ObtainAuthToken):
    serializer_class = TokenSerializer


class AuthUserAPIView(APIView):
    permission_classes = (IsAuthenticated,)
    serializer_class = UserSerializer

    def get(self, request):
        serializer = self.serializer_class(request.user)
        return Response(serializer.data)


class UserLogoutAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        # Delete user token
        request.user.auth_token.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class PasswordResetRequestView(APIView):
    serializer_class = PasswordResetRequestSerializer

    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid():
            email = serializer.validated_data['email']
            user = User.objects.get(email=email)

            # Create or update reset code for the user
            reset_code, created = PasswordReset.objects.get_or_create(user=user)
            if not created:
                reset_code.code = reset_code.generate_reset_code()
                reset_code.is_used = False
                reset_code.save()

            # Send the reset code via email
            send_mail(
                'Password Reset Code',
                f'Your password reset code is {reset_code.code}',
                settings.DEFAULT_FROM_EMAIL,
                [email],
                fail_silently=False,
            )

            return Response({"message": "Password reset code sent to email."}, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class PasswordResetConfirmView(APIView):
    def post(self, request):
        serializer = PasswordResetConfirmSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.validated_data['user']
            reset_code = serializer.validated_data['reset_code']
            new_password = serializer.validated_data['new_password']

            user.set_password(new_password)
            user.save()

            # Mark the reset code as used
            reset_code.is_used = True
            reset_code.save()

            return Response({"message": "Password has been reset successfully."}, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class UserProfileView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user

        if user.user_type == User.UserType.TEACHER:
            try:
                profile = TeacherProfile.objects.get(user=user)
                serializer = TeacherProfileSerializer(profile)
            except TeacherProfile.DoesNotExist:
                return Response({"error": "Teacher profile not found."}, status=status.HTTP_404_NOT_FOUND)

        elif user.user_type == User.UserType.STUDENT:
            try:
                profile = StudentProfile.objects.get(user=user)
                serializer = StudentProfileSerializer(profile)
            except StudentProfile.DoesNotExist:
                return Response({"error": "Student profile not found."}, status=status.HTTP_404_NOT_FOUND)

        else:
            return Response({"error": "Invalid user type."}, status=status.HTTP_400_BAD_REQUEST)

        return Response(serializer.data, status=status.HTTP_200_OK)

    def patch(self, request):
        user = request.user
        data = request.data

        if user.user_type == User.UserType.TEACHER:
            try:
                profile = user.teacher_profile
                serializer = TeacherProfileSerializer(profile, data=data, partial=True)
            except TeacherProfile.DoesNotExist:
                return Response(
                    data={"error": "Teacher profile not found."},
                    status=status.HTTP_404_NOT_FOUND
                )

        elif user.user_type == User.UserType.STUDENT:
            try:
                profile = user.student_profile
                serializer = StudentProfileSerializer(profile, data=data, partial=True)
            except StudentProfile.DoesNotExist:
                return Response(
                    data={"error": "Student profile not found."},
                    status=status.HTTP_404_NOT_FOUND
                )

        else:
            return Response(
                data={"error": "Invalid user type."},
                status=status.HTTP_400_BAD_REQUEST
            )

        if serializer.is_valid():
            serializer.save(updated_by=user)
            return Response(serializer.data, status=status.HTTP_200_OK)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class UpdateUserActiveStatusAPIView(APIView):
    permission_classes = [IsAuthenticated, IsAdmin]
    serializer_class = UserActiveStatusSerializer

    def patch(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)

        try:
            user = User.objects.get(id=request.data.get('user_id'))
            user.is_active = serializer.validated_data.get('is_active')
            user.save()
        except User.DoesNotExist:
            return Response(
                data={"error": "User not found."},
                status=status.HTTP_404_NOT_FOUND
            )

        return Response(
            data={
                'message': f'User active status been set {request.data.get('is_active')}'
            }
        )


class UserListAPIView(APIView):
    permission_classes = [IsAuthenticated, IsAdmin]
    serializer_class = UserSerializer

    def get(self, request, **kwargs):
        users = User.objects.exclude(user_type=User.UserType.ADMIN)
        if request.GET.get('type') and request.GET.get('type') in [User.UserType.STUDENT, User.UserType.TEACHER]:
            users = users.filter(user_type=request.GET.get('type'))
        users = users.all()

        serializer = self.serializer_class(users, many=True)

        return Response(data=serializer.data)


class StudentListAPIView(APIView):
    serializer_class = StudentProfileSerializer
    permission_classes = [IsAuthenticated, IsAdminOrTeacher]

    def get(self, request, **kwargs):
        students = StudentProfile.objects.order_by('roll').all()

        semester_students = defaultdict(list)
        for student in students:
            semester_students[student.semester].append(self.serializer_class(student).data)

        return Response(semester_students)
