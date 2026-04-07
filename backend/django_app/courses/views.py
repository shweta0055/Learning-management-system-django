from rest_framework import generics, permissions, status, filters
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.decorators import action
from rest_framework.viewsets import ModelViewSet
from django_filters.rest_framework import DjangoFilterBackend
from django.shortcuts import get_object_or_404
from .models import Category, Course, Section, Lesson, CourseReview, Announcement
from .serializers import (
    CategorySerializer, CourseListSerializer, CourseDetailSerializer,
    CourseCreateUpdateSerializer, SectionSerializer, LessonSerializer,
    CourseReviewSerializer, AnnouncementSerializer
)
from users.permissions import IsInstructorOrAdmin, IsInstructor


class CategoryListView(generics.ListCreateAPIView):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = [permissions.AllowAny]

    def get_permissions(self):
        if self.request.method == 'POST':
            return [permissions.IsAdminUser()]
        return [permissions.AllowAny()]


class CourseListView(generics.ListAPIView):
    serializer_class = CourseListSerializer
    permission_classes = [permissions.AllowAny]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['category', 'level', 'status', 'is_free', 'language']
    search_fields = ['title', 'description', 'instructor__username', 'tags']
    ordering_fields = ['created_at', 'price', 'rating', 'total_students']
    ordering = ['-created_at']

    def get_queryset(self):
        return Course.objects.filter(status='published').select_related('instructor', 'category')


class CourseDetailView(generics.RetrieveAPIView):
    queryset = Course.objects.filter(status='published').select_related('instructor', 'category')
    serializer_class = CourseDetailSerializer
    permission_classes = [permissions.AllowAny]
    lookup_field = 'slug'


class CourseCreateView(generics.CreateAPIView):
    serializer_class = CourseCreateUpdateSerializer
    permission_classes = [IsInstructorOrAdmin]


class CourseUpdateView(generics.UpdateAPIView):
    serializer_class = CourseCreateUpdateSerializer
    permission_classes = [IsInstructorOrAdmin]

    def get_queryset(self):
        if self.request.user.is_admin:
            return Course.objects.all()
        return Course.objects.filter(instructor=self.request.user)


class InstructorCourseListView(generics.ListAPIView):
    serializer_class = CourseListSerializer
    permission_classes = [IsInstructorOrAdmin]

    def get_queryset(self):
        if self.request.user.is_admin:
            return Course.objects.all()
        return Course.objects.filter(instructor=self.request.user)


class SectionListCreateView(generics.ListCreateAPIView):
    serializer_class = SectionSerializer
    permission_classes = [IsInstructorOrAdmin]

    def get_queryset(self):
        course_id = self.kwargs['course_id']
        return Section.objects.filter(course_id=course_id).prefetch_related('lessons')

    def perform_create(self, serializer):
        course = get_object_or_404(Course, pk=self.kwargs['course_id'])
        serializer.save(course=course)


class SectionDetailView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = SectionSerializer
    permission_classes = [IsInstructorOrAdmin]

    def get_queryset(self):
        return Section.objects.filter(course_id=self.kwargs['course_id'])


class LessonListCreateView(generics.ListCreateAPIView):
    serializer_class = LessonSerializer
    permission_classes = [IsInstructorOrAdmin]

    def get_queryset(self):
        return Lesson.objects.filter(section__course_id=self.kwargs['course_id'])


class LessonDetailView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = LessonSerializer

    def get_permissions(self):
        if self.request.method in permissions.SAFE_METHODS:
            return [permissions.IsAuthenticated()]
        return [IsInstructorOrAdmin()]

    def get_queryset(self):
        return Lesson.objects.filter(section__course_id=self.kwargs['course_id'])


class CourseReviewListCreateView(generics.ListCreateAPIView):
    serializer_class = CourseReviewSerializer

    def get_permissions(self):
        if self.request.method == 'GET':
            return [permissions.AllowAny()]
        return [permissions.IsAuthenticated()]

    def get_queryset(self):
        return CourseReview.objects.filter(
            course_id=self.kwargs['course_id']
        ).select_related('user')

    def perform_create(self, serializer):
        serializer.save(
            course_id=self.kwargs['course_id'],
            user=self.request.user
        )


class AnnouncementListCreateView(generics.ListCreateAPIView):
    serializer_class = AnnouncementSerializer

    def get_permissions(self):
        if self.request.method == 'GET':
            return [permissions.IsAuthenticated()]
        return [IsInstructorOrAdmin()]

    def get_queryset(self):
        return Announcement.objects.filter(course_id=self.kwargs['course_id'])

    def perform_create(self, serializer):
        serializer.save(course_id=self.kwargs['course_id'])
