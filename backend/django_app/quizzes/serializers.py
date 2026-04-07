from rest_framework import serializers
from django.utils import timezone
from .models import (Quiz, Question, Answer, QuizAttempt, QuizResponse,
                     Assignment, AssignmentSubmission)


class AnswerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Answer
        fields = ['id', 'text', 'order']  # is_correct hidden from students


class AnswerWithCorrectSerializer(serializers.ModelSerializer):
    class Meta:
        model = Answer
        fields = ['id', 'text', 'is_correct', 'order']


class QuestionSerializer(serializers.ModelSerializer):
    answers = AnswerSerializer(many=True, read_only=True)

    class Meta:
        model = Question
        fields = ['id', 'text', 'question_type', 'points', 'order', 'answers']


class QuestionWithAnswersSerializer(serializers.ModelSerializer):
    answers = AnswerWithCorrectSerializer(many=True, read_only=True)

    class Meta:
        model = Question
        fields = ['id', 'text', 'question_type', 'points', 'explanation', 'order', 'answers']


class QuizSerializer(serializers.ModelSerializer):
    questions = QuestionSerializer(many=True, read_only=True)
    question_count = serializers.SerializerMethodField()

    class Meta:
        model = Quiz
        fields = ['id', 'course', 'lesson', 'title', 'description', 'time_limit',
                  'passing_score', 'max_attempts', 'shuffle_questions',
                  'show_answers_after', 'is_active', 'question_count', 'questions', 'created_at']

    def get_question_count(self, obj):
        return obj.questions.count()


class QuizResponseSerializer(serializers.ModelSerializer):
    class Meta:
        model = QuizResponse
        fields = ['question', 'selected_answer', 'text_response']


class QuizAttemptCreateSerializer(serializers.Serializer):
    responses = QuizResponseSerializer(many=True)

    def validate(self, data):
        return data


class QuizAttemptSerializer(serializers.ModelSerializer):
    responses = QuizResponseSerializer(many=True, read_only=True)

    class Meta:
        model = QuizAttempt
        fields = ['id', 'quiz', 'status', 'score', 'total_points', 'earned_points',
                  'passed', 'started_at', 'completed_at', 'time_taken', 'responses']
        read_only_fields = ['id', 'score', 'passed', 'started_at', 'completed_at']


class AssignmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Assignment
        fields = '__all__'
        read_only_fields = ['id', 'created_at']


class AssignmentSubmissionSerializer(serializers.ModelSerializer):
    student_name = serializers.CharField(source='student.get_full_name', read_only=True)

    class Meta:
        model = AssignmentSubmission
        fields = ['id', 'assignment', 'student', 'student_name', 'content', 'attachment',
                  'status', 'score', 'feedback', 'submitted_at', 'graded_at', 'graded_by']
        read_only_fields = ['id', 'student', 'status', 'score', 'feedback', 'submitted_at', 'graded_at', 'graded_by']

    def create(self, validated_data):
        validated_data['student'] = self.context['request'].user
        return super().create(validated_data)


class GradeSubmissionSerializer(serializers.Serializer):
    score = serializers.IntegerField(min_value=0)
    feedback = serializers.CharField(required=False, allow_blank=True)
