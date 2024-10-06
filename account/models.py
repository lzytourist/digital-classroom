import random
import string

from django.contrib.auth.base_user import BaseUserManager
from django.contrib.auth.models import AbstractBaseUser
from django.db import models
from django.utils import timezone

from account.enums import Semester


class UserManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError('Users must have an email address')
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password):
        user = self.create_user(email, password)
        user.is_staff = True
        user.is_superuser = True
        user.save(using=self._db)
        return user


class User(AbstractBaseUser):
    class UserType(models.TextChoices):
        ADMIN = 'admin', 'Admin'
        STUDENT = 'student', 'Student'
        TEACHER = 'teacher', 'Teacher'

    user_type = models.CharField(
        max_length=10,
        choices=UserType.choices,
        default=UserType.STUDENT,
    )
    email = models.EmailField(unique=True, max_length=255)
    name = models.CharField(max_length=255)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    is_superuser = models.BooleanField(default=False)
    date_joined = models.DateTimeField(default=timezone.now)

    objects = UserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['name']

    def __str__(self):
        return f"{self.name}({self.email})"

    class Meta:
        db_table = 'users'


def generate_reset_code():
    return ''.join(random.choices(string.digits, k=6))


class PasswordReset(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    code = models.CharField(max_length=6, default=generate_reset_code)
    created_at = models.DateTimeField(auto_now_add=True)
    is_used = models.BooleanField(default=False)

    def is_expired(self):
        return timezone.now() > self.created_at + timezone.timedelta(minutes=10)

    class Meta:
        db_table = 'password_reset_tokens'


class TeacherProfile(models.Model):
    user = models.OneToOneField(
        to=User,
        on_delete=models.CASCADE,
        related_name='teacher_profile',
    )
    name = models.CharField(max_length=255)
    email = models.EmailField(max_length=255, null=True)
    department = models.CharField(max_length=255, null=True)
    designation = models.CharField(max_length=255, null=True)
    teacher_id = models.CharField(max_length=50, null=True)
    blood_group = models.CharField(max_length=5, null=True)
    updated_by = models.ForeignKey(
        to=User,
        on_delete=models.DO_NOTHING,
        null=True
    )

    def __str__(self):
        return f'{self.designation} {self.user.name} | {self.department}({self.teacher_id})'

    class Meta:
        db_table = 'teacher_profiles'


class StudentProfile(models.Model):
    user = models.OneToOneField(
        to=User,
        on_delete=models.CASCADE,
        related_name='student_profile',
    )
    name = models.CharField(max_length=255)
    father = models.CharField(max_length=255, null=True)
    mother = models.CharField(max_length=255, null=True)
    father_phone = models.CharField(max_length=15, null=True)
    mother_phone = models.CharField(max_length=15, null=True)
    present_address = models.CharField(max_length=255, null=True)
    permanent_address = models.CharField(max_length=255, null=True)
    email = models.EmailField(max_length=255, null=True)
    department = models.CharField(max_length=255, null=True)
    roll = models.IntegerField(null=True, default=0)
    semester = models.CharField(
        max_length=10,
        choices=Semester.choices,
        default=Semester.FIRST_SEMESTER,
        null=True
    )
    section = models.CharField(max_length=50, null=True)
    student_id = models.CharField(max_length=50, null=True)
    blood_group = models.CharField(max_length=5, null=True)
    updated_by = models.ForeignKey(
        to=User,
        on_delete=models.DO_NOTHING,
        null=True
    )

    def __str__(self):
        return f'{self.user.name} | {self.department} | {self.semester}({self.student_id})'

    class Meta:
        db_table = 'student_profiles'
