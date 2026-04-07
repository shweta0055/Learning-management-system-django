from rest_framework import generics, permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView
from django.utils import timezone
from django.shortcuts import get_object_or_404
from .models import Enrollment, LessonProgress, Wishlist
from .serializers import (
    EnrollmentSerializer, EnrollmentCreateSerializer,
    LessonProgressSerializer, WishlistSerializer
)
from courses.models import Course


class EnrollView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        serializer = EnrollmentCreateSerializer(data=request.data, context={'request': request})
        serializer.is_valid(raise_exception=True)
        enrollment = serializer.save()
        return Response(EnrollmentSerializer(enrollment).data, status=status.HTTP_201_CREATED)


class MyEnrollmentsView(generics.ListAPIView):
    serializer_class = EnrollmentSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Enrollment.objects.filter(
            user=self.request.user
        ).select_related('course', 'course__instructor').prefetch_related('lesson_progress')


class EnrollmentDetailView(generics.RetrieveAPIView):
    serializer_class = EnrollmentSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Enrollment.objects.filter(user=self.request.user)


class LessonProgressUpdateView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, enrollment_id, lesson_id):
        enrollment = get_object_or_404(Enrollment, pk=enrollment_id, user=request.user)
        progress_data = request.data

        lesson_progress, created = LessonProgress.objects.get_or_create(
            enrollment=enrollment,
            lesson_id=lesson_id
        )

        if 'watch_time' in progress_data:
            lesson_progress.watch_time = progress_data['watch_time']
        if 'last_position' in progress_data:
            lesson_progress.last_position = progress_data['last_position']
        if 'notes' in progress_data:
            lesson_progress.notes = progress_data['notes']
        if progress_data.get('is_completed') and not lesson_progress.is_completed:
            lesson_progress.is_completed = True
            lesson_progress.completed_at = timezone.now()

        lesson_progress.save()

        # Update overall enrollment progress
        new_progress = enrollment.calculate_progress()
        enrollment.progress = new_progress
        if new_progress >= 100:
            enrollment.status = 'completed'
            enrollment.completed_at = timezone.now()
        enrollment.save(update_fields=['progress', 'status', 'completed_at'])

        return Response({
            'lesson_progress': LessonProgressSerializer(lesson_progress).data,
            'enrollment_progress': new_progress
        })


class WishlistView(generics.ListCreateAPIView):
    serializer_class = WishlistSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Wishlist.objects.filter(user=self.request.user).select_related('course')

    def create(self, request, *args, **kwargs):
        course_id = request.data.get('course_id')
        course = get_object_or_404(Course, pk=course_id)
        wishlist_item, created = Wishlist.objects.get_or_create(user=request.user, course=course)
        if not created:
            wishlist_item.delete()
            return Response({'detail': 'Removed from wishlist.'}, status=status.HTTP_200_OK)
        return Response(WishlistSerializer(wishlist_item).data, status=status.HTTP_201_CREATED)


class CourseStudentsView(generics.ListAPIView):
    """For instructors to see their enrolled students"""
    serializer_class = EnrollmentSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        course_id = self.kwargs['course_id']
        if self.request.user.is_admin:
            return Enrollment.objects.filter(course_id=course_id)
        return Enrollment.objects.filter(
            course_id=course_id,
            course__instructor=self.request.user
        )
