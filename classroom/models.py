import os

from django.core.exceptions import ValidationError
from django.db import models

from account.enums import Semester
from account.models import User


def validate_file_type(value):
    ext = os.path.splitext(value.name)[1].lower()
    valid_extensions = ['.pdf', '.jpg', '.jpeg', '.png']
    if ext not in valid_extensions:
        raise ValidationError('Only PDF, JPEG, JPG, or PNG files are allowed.')


def validate_video_type(value):
    ext = os.path.splitext(value.name)[1].lower()
    valid_extensions = ['.mp4', '.mov', '.mkv', '.webm']
    print(ext)
    if ext not in valid_extensions:
        raise ValidationError('Only MP4, MOV, MKV, Webm are allowed.')


class Routine(models.Model):
    semester = models.CharField(
        max_length=10,
        choices=Semester.choices,
        default=Semester.FIRST_SEMESTER
    )
    file = models.FileField(
        upload_to='routines/',
        null=True,
        validators=[validate_file_type]
    )
    created_at = models.DateTimeField(auto_now_add=True)
    added_by = models.ForeignKey(
        to=User,
        on_delete=models.SET_NULL,
        null=True,
        related_name='routines'
    )

    class Meta:
        db_table = 'routines'


class Notice(models.Model):
    title = models.CharField(max_length=255)
    file = models.FileField(
        upload_to='notices/',
        null=True,
        validators=[validate_file_type]
    )
    created_at = models.DateTimeField(auto_now_add=True)
    added_by = models.ForeignKey(
        to=User,
        on_delete=models.SET_NULL,
        null=True,
        related_name='notices'
    )

    class Meta:
        db_table = 'notices'


class Class(models.Model):
    title = models.CharField(max_length=255)
    semester = models.CharField(
        max_length=10,
        choices=Semester.choices,
        default=Semester.FIRST_SEMESTER
    )
    file = models.FileField(
        upload_to='classes/',
        validators=[validate_video_type],
        null=True
    )
    link = models.CharField(
        max_length=255,
        null=True
    )
    created_at = models.DateTimeField(auto_now_add=True)
    teacher = models.ForeignKey(
        to=User,
        on_delete=models.SET_NULL,
        null=True,
        related_name='classes'
    )

    class Meta:
        db_table = 'classes'


class Assignment(models.Model):
    title = models.CharField(max_length=255)
    file = models.FileField(
        upload_to='assignments/',
        validators=[validate_file_type],
        null=True
    )
    content = models.TextField(null=True)
    semester = models.CharField(
        max_length=10,
        choices=Semester.choices,
        default=Semester.FIRST_SEMESTER
    )
    teacher = models.ForeignKey(
        to=User,
        on_delete=models.SET_NULL,
        null=True,
        related_name='assignments'
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'assignments'
