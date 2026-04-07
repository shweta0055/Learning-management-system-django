from rest_framework import serializers
from .models import Category, Course, Section, Lesson, CourseReview, Announcement
from users.serializers import UserSerializer


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ['id', 'name', 'slug', 'description', 'icon', 'parent']


class LessonSerializer(serializers.ModelSerializer):
    class Meta:
        model = Lesson
        fields = ['id', 'section', 'title', 'description', 'content_type',
                  'video_url', 'video_duration', 'content', 'resources',
                  'order', 'is_free_preview', 'created_at']
        read_only_fields = ['id', 'created_at']


class LessonListSerializer(serializers.ModelSerializer):
    """Lightweight serializer for lesson lists"""
    class Meta:
        model = Lesson
        fields = ['id', 'title', 'content_type', 'video_duration', 'order', 'is_free_preview']


class SectionSerializer(serializers.ModelSerializer):
    lessons = LessonListSerializer(many=True, read_only=True)

    class Meta:
        model = Section
        fields = ['id', 'course', 'title', 'description', 'order', 'lessons']
        read_only_fields = ['id']


class CourseReviewSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)

    class Meta:
        model = CourseReview
        fields = ['id', 'course', 'user', 'rating', 'comment', 'created_at']
        read_only_fields = ['id', 'user', 'created_at']

    def create(self, validated_data):
        validated_data['user'] = self.context['request'].user
        return super().create(validated_data)


class CourseListSerializer(serializers.ModelSerializer):
    instructor = UserSerializer(read_only=True)
    category = CategorySerializer(read_only=True)
    effective_price = serializers.ReadOnlyField()

    class Meta:
        model = Course
        fields = ['id', 'title', 'slug', 'short_description', 'instructor',
                  'category', 'thumbnail', 'price', 'discount_price', 'effective_price',
                  'level', 'status', 'duration_hours', 'total_lessons',
                  'total_students', 'rating', 'total_ratings', 'is_free',
                  'certificate_available', 'created_at']


class CourseDetailSerializer(serializers.ModelSerializer):
    instructor = UserSerializer(read_only=True)
    category = CategorySerializer(read_only=True)
    sections = SectionSerializer(many=True, read_only=True)
    reviews = CourseReviewSerializer(many=True, read_only=True)
    effective_price = serializers.ReadOnlyField()

    class Meta:
        model = Course
        fields = '__all__'
        read_only_fields = ['id', 'slug', 'total_students', 'rating', 'total_ratings', 'created_at', 'updated_at']


class CourseCreateUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Course
        exclude = ['instructor', 'total_students', 'rating', 'total_ratings', 'created_at', 'updated_at']

    def create(self, validated_data):
        validated_data['instructor'] = self.context['request'].user
        # Auto-generate slug from title
        from django.utils.text import slugify
        base_slug = slugify(validated_data['title'])
        slug = base_slug
        counter = 1
        while Course.objects.filter(slug=slug).exists():
            slug = f"{base_slug}-{counter}"
            counter += 1
        validated_data['slug'] = slug
        return super().create(validated_data)


class AnnouncementSerializer(serializers.ModelSerializer):
    class Meta:
        model = Announcement
        fields = '__all__'
        read_only_fields = ['id', 'created_at']
