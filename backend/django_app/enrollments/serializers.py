from rest_framework import serializers
from .models import Enrollment, LessonProgress, Wishlist
from courses.serializers import CourseListSerializer, LessonSerializer


class LessonProgressSerializer(serializers.ModelSerializer):
    lesson_title = serializers.CharField(source='lesson.title', read_only=True)

    class Meta:
        model = LessonProgress
        fields = ['id', 'enrollment', 'lesson', 'lesson_title', 'is_completed',
                  'watch_time', 'completed_at', 'last_position', 'notes']
        read_only_fields = ['id', 'completed_at']


class EnrollmentSerializer(serializers.ModelSerializer):
    course = CourseListSerializer(read_only=True)
    lesson_progress = LessonProgressSerializer(many=True, read_only=True)

    class Meta:
        model = Enrollment
        fields = ['id', 'user', 'course', 'status', 'progress', 'enrolled_at',
                  'completed_at', 'last_accessed', 'amount_paid', 'lesson_progress']
        read_only_fields = ['id', 'user', 'progress', 'enrolled_at', 'completed_at', 'last_accessed']


class EnrollmentCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Enrollment
        fields = ['course']

    def validate_course(self, course):
        user = self.context['request'].user
        if Enrollment.objects.filter(user=user, course=course).exists():
            raise serializers.ValidationError("Already enrolled in this course.")
        return course

    def create(self, validated_data):
        validated_data['user'] = self.context['request'].user
        enrollment = super().create(validated_data)
        course = enrollment.course
        course.total_students += 1
        course.save(update_fields=['total_students'])
        return enrollment


class WishlistSerializer(serializers.ModelSerializer):
    course = CourseListSerializer(read_only=True)

    class Meta:
        model = Wishlist
        fields = ['id', 'course', 'added_at']
        read_only_fields = ['id', 'added_at']
