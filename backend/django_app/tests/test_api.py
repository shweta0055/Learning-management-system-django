"""
Django pytest tests for LMS Backend
Run with: pytest backend/django_app/ --ds=lms_backend.settings -v
"""
import pytest
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient
from rest_framework import status
import factory

User = get_user_model()


# ─── Factories ────────────────────────────────────────────────────────────────
class UserFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = User

    username = factory.Sequence(lambda n: f"user{n}")
    email = factory.Sequence(lambda n: f"user{n}@example.com")
    first_name = factory.Faker('first_name')
    last_name = factory.Faker('last_name')
    role = 'student'

    @classmethod
    def _create(cls, model_class, *args, **kwargs):
        password = kwargs.pop('password', 'TestPass123!')
        obj = model_class(*args, **kwargs)
        obj.set_password(password)
        obj.save()
        return obj


class InstructorFactory(UserFactory):
    role = 'instructor'


class AdminFactory(UserFactory):
    role = 'admin'
    is_staff = True
    is_superuser = True


# ─── Fixtures ─────────────────────────────────────────────────────────────────
@pytest.fixture
def api_client():
    return APIClient()


@pytest.fixture
def student(db):
    return UserFactory(password='TestPass123!')


@pytest.fixture
def instructor(db):
    return InstructorFactory(password='TestPass123!')


@pytest.fixture
def admin_user(db):
    return AdminFactory(password='TestPass123!')


@pytest.fixture
def auth_client(api_client, student):
    api_client.force_authenticate(user=student)
    return api_client


@pytest.fixture
def instructor_client(api_client, instructor):
    api_client.force_authenticate(user=instructor)
    return api_client


# ─── Auth Tests ───────────────────────────────────────────────────────────────
@pytest.mark.django_db
class TestAuth:
    def test_register_student(self, api_client):
        data = {
            "username": "newstudent",
            "email": "newstudent@example.com",
            "first_name": "New",
            "last_name": "Student",
            "role": "student",
            "password": "SecurePass123!",
            "password_confirm": "SecurePass123!",
        }
        res = api_client.post('/api/auth/register/', data)
        assert res.status_code == status.HTTP_201_CREATED
        assert 'tokens' in res.data
        assert res.data['user']['role'] == 'student'

    def test_login(self, api_client, student):
        res = api_client.post('/api/auth/login/', {
            'email': student.email,
            'password': 'TestPass123!'
        })
        assert res.status_code == status.HTTP_200_OK
        assert 'access' in res.data
        assert 'refresh' in res.data

    def test_login_wrong_password(self, api_client, student):
        res = api_client.post('/api/auth/login/', {
            'email': student.email,
            'password': 'wrongpassword'
        })
        assert res.status_code == status.HTTP_401_UNAUTHORIZED

    def test_get_profile_authenticated(self, auth_client, student):
        res = auth_client.get('/api/auth/profile/')
        assert res.status_code == status.HTTP_200_OK
        assert res.data['email'] == student.email

    def test_get_profile_unauthenticated(self, api_client):
        res = api_client.get('/api/auth/profile/')
        assert res.status_code == status.HTTP_401_UNAUTHORIZED

    def test_register_password_mismatch(self, api_client):
        data = {
            "username": "test",
            "email": "test@example.com",
            "password": "SecurePass123!",
            "password_confirm": "DifferentPass123!",
            "role": "student",
        }
        res = api_client.post('/api/auth/register/', data)
        assert res.status_code == status.HTTP_400_BAD_REQUEST


# ─── Course Tests ─────────────────────────────────────────────────────────────
@pytest.mark.django_db
class TestCourses:
    def _create_course(self, instructor):
        from courses.models import Course
        return Course.objects.create(
            title="Test Course",
            slug="test-course",
            description="A great test course",
            instructor=instructor,
            price=49.99,
            level='beginner',
            status='published',
        )

    def test_list_courses_public(self, api_client, instructor):
        self._create_course(instructor)
        res = api_client.get('/api/courses/')
        assert res.status_code == status.HTTP_200_OK
        assert res.data['count'] >= 1

    def test_course_detail_public(self, api_client, instructor):
        course = self._create_course(instructor)
        res = api_client.get(f'/api/courses/{course.slug}/')
        assert res.status_code == status.HTTP_200_OK
        assert res.data['title'] == course.title

    def test_create_course_as_instructor(self, instructor_client):
        data = {
            "title": "New Course",
            "description": "Course description",
            "price": "29.99",
            "level": "beginner",
        }
        res = instructor_client.post('/api/courses/create/', data)
        assert res.status_code == status.HTTP_201_CREATED

    def test_create_course_as_student_forbidden(self, auth_client):
        data = {"title": "Unauthorized", "description": "...", "price": "0"}
        res = auth_client.post('/api/courses/create/', data)
        assert res.status_code == status.HTTP_403_FORBIDDEN


# ─── Enrollment Tests ─────────────────────────────────────────────────────────
@pytest.mark.django_db
class TestEnrollments:
    def test_enroll_free_course(self, auth_client, instructor):
        from courses.models import Course
        course = Course.objects.create(
            title="Free Course", slug="free-course", description="Free!",
            instructor=instructor, price=0, is_free=True, status='published',
        )
        res = auth_client.post('/api/enrollments/enroll/', {'course': course.id})
        assert res.status_code == status.HTTP_201_CREATED

    def test_my_enrollments(self, auth_client):
        res = auth_client.get('/api/enrollments/my/')
        assert res.status_code == status.HTTP_200_OK

    def test_enroll_unauthenticated(self, api_client, instructor):
        from courses.models import Course
        course = Course.objects.create(
            title="Course", slug="course", description="...",
            instructor=instructor, price=0, is_free=True, status='published',
        )
        res = api_client.post('/api/enrollments/enroll/', {'course': course.id})
        assert res.status_code == status.HTTP_401_UNAUTHORIZED


# ─── Certificate Tests ────────────────────────────────────────────────────────
@pytest.mark.django_db
class TestCertificates:
    def test_verify_certificate(self, api_client, student, instructor):
        from courses.models import Course
        from certificates.models import Certificate
        course = Course.objects.create(
            title="Cert Course", slug="cert-course", description="...",
            instructor=instructor, status='published',
        )
        cert = Certificate.objects.create(user=student, course=course)
        res = api_client.get(f'/api/certificates/verify/{cert.certificate_id}/')
        assert res.status_code == status.HTTP_200_OK
        assert res.data['valid'] is True

    def test_my_certificates_authenticated(self, auth_client):
        res = auth_client.get('/api/certificates/my/')
        assert res.status_code == status.HTTP_200_OK
