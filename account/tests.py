from django.test import TestCase
from django.urls import reverse
from django.utils import timezone
from rest_framework.authtoken.models import Token
from rest_framework.test import APIClient
from django.contrib.auth import get_user_model

from account.enums import Semester
from account.models import PasswordReset, TeacherProfile, StudentProfile
from django.core import mail

User = get_user_model()


class UserAuthTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(email='testuser@example.com', password='password123')
        self.token = Token.objects.create(user=self.user)

    def test_user_registration(self):
        """Test user registration"""
        url = reverse('user_registration')
        data = {
            'name': 'New Student',
            'email': 'newuser@example.com',
            'password': 'password123',
            'user_type': 'student',
            'semester': '5th'
        }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, 201)
        self.assertIn('token', response.data)
        self.assertEqual(User.objects.count(), 2)

    def test_user_login(self):
        """Test user login and token generation"""
        url = reverse('user_login')
        data = {
            'email': 'testuser@example.com',
            'password': 'password123',
        }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, 200)
        self.assertIn('token', response.data)

    def test_user_unsuccessful_login(self):
        """Test user wrong credentials"""
        url = reverse('user_login')
        data = {
            'email': 'testuser@example.com',
            'password': 'wrong_password',
        }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, 400)

    def test_user_logout(self):
        """Test user logout"""
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.token.key)
        url = reverse('user_logout')
        response = self.client.post(url)
        self.assertEqual(response.status_code, 204)
        self.assertFalse(Token.objects.filter(user=self.user).exists())

    def test_user_unsuccessful_logout(self):
        """Test user unsuccessful logout"""
        url = reverse('user_logout')
        response = self.client.post(url)
        self.assertEqual(response.status_code, 401)


class PasswordResetTests(TestCase):
    def setUp(self):
        # Create a test user
        self.user = User.objects.create_user(email='user@example.com', password='testpassword123')
        self.client = APIClient()

    def test_password_reset_request(self):
        """Test that password reset code is sent to the user's email"""
        response = self.client.post(reverse('password_reset_request'), {'email': 'user@example.com'})

        # Assert that the response is 200 OK
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(mail.outbox), 1)

        # Assert that an email has been sent
        self.assertEqual(len(mail.outbox), 1)

        # Assert that the email is sent to the correct user
        self.assertIn('user@example.com', mail.outbox[0].to)

        # Assert that a reset code is generated
        reset_code = PasswordReset.objects.filter(user=self.user).first()
        self.assertIsNotNone(reset_code)
        self.assertFalse(reset_code.is_used)

    def test_password_reset_confirm(self):
        """Test resetting password using the correct code"""
        # Request the password reset to generate the code
        self.client.post(reverse('password_reset_request'), {'email': 'user@example.com'})
        reset_code = PasswordReset.objects.get(user=self.user)

        # Use the correct code to reset the password
        new_password = 'newpassword123'
        response = self.client.post(reverse('password_reset_confirm'), {
            'email': 'user@example.com',
            'code': reset_code.code,
            'new_password': new_password
        })

        # Assert that the response is 200 OK
        self.assertEqual(response.status_code, 200)

        # Reload the user and check if the password has been updated
        self.user.refresh_from_db()
        self.assertTrue(self.user.check_password(new_password))

        # Assert that the reset code is now marked as used
        reset_code.refresh_from_db()
        self.assertTrue(reset_code.is_used)

    def test_password_reset_with_invalid_code(self):
        """Test that using an invalid code fails"""
        # Request the password reset to generate a valid code
        self.client.post(reverse('password_reset_request'), {'email': 'user@example.com'})

        # Try to reset the password using an invalid code
        response = self.client.post(reverse('password_reset_confirm'), {
            'email': 'user@example.com',
            'code': '999999',  # invalid code
            'new_password': 'newpassword123'
        })

        # Assert that the response is 400 BAD REQUEST
        self.assertEqual(response.status_code, 400)

    def test_password_reset_with_expired_code(self):
        """Test that using an expired code fails"""
        # Request the password reset to generate a code
        self.client.post(reverse('password_reset_request'), {'email': 'user@example.com'})
        reset_code = PasswordReset.objects.get(user=self.user)

        # Manually mark the reset code as expired
        reset_code.created_at -= timezone.timedelta(minutes=15)
        reset_code.save()

        # Try to reset the password using the expired code
        response = self.client.post(reverse('password_reset_confirm'), {
            'email': 'user@example.com',
            'code': reset_code.code,
            'new_password': 'newpassword123'
        })

        # Assert that the response is 400 BAD REQUEST
        self.assertEqual(response.status_code, 400)


class UserProfileAPITest(TestCase):
    def setUp(self):
        # Create an API client
        self.client = APIClient()

        # Create a teacher user
        self.teacher_user = User.objects.create_user(email="teacher@example.com", user_type="teacher",
                                                     password="password")
        self.teacher_profile = TeacherProfile.objects.create(user=self.teacher_user, department="Science",
                                                             designation="Professor")

        # Create a student user
        self.student_user = User.objects.create_user(email="student@example.com", user_type="student",
                                                     password="password")
        self.student_profile = StudentProfile.objects.create(user=self.student_user, department="Engineering", roll=123,
                                                             semester=Semester.FIFTH_SEMESTER, section="A")

        # Generate tokens for both users
        self.teacher_token = Token.objects.create(user=self.teacher_user)
        self.student_token = Token.objects.create(user=self.student_user)

    def test_get_teacher_profile(self):
        # Authenticate the teacher by passing the token in the header
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.teacher_token.key)

        # Make a GET request to the profile endpoint
        response = self.client.get(reverse('user-profile'))

        # Check the response
        self.assertEqual(response.status_code, 200)
        self.assertIn("designation", response.data)

    def test_get_student_profile(self):
        # Authenticate the student by passing the token in the header
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.student_token.key)

        # Make a GET request to the profile endpoint
        response = self.client.get(reverse('user-profile'))

        # Check the response
        self.assertEqual(response.status_code, 200)
        self.assertIn("roll", response.data)

    def tearDown(self):
        # Clear authentication credentials after each test
        self.client.credentials()  # Reset client credentials to default
