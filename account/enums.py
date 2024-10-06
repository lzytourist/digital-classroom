from django.db.models import TextChoices


class Semester(TextChoices):
    FIRST_SEMESTER = '1st', 'First Semester'
    SECOND_SEMESTER = '2nd', 'Second Semester'
    THIRD_SEMESTER = '3rd', 'Third Semester'
    FOURTH_SEMESTER = '4th', 'Fourth Semester'
    FIFTH_SEMESTER = '5th', 'Fifth Semester'
    SIXTH_SEMESTER = '6th', 'Sixth Semester'
    SEVENTH_SEMESTER = '7th', 'Seventh Semester'
    EIGHTH_SEMESTER = '8th', 'Eighth Semester'
