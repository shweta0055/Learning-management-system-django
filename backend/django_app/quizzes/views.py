from rest_framework import generics, permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView
from django.utils import timezone
from django.shortcuts import get_object_or_404
from .models import Quiz, Question, Answer, QuizAttempt, QuizResponse, Assignment, AssignmentSubmission
from .serializers import (
    QuizSerializer, QuizAttemptSerializer, QuizAttemptCreateSerializer,
    AssignmentSerializer, AssignmentSubmissionSerializer, GradeSubmissionSerializer,
    QuestionWithAnswersSerializer
)
from users.permissions import IsInstructorOrAdmin


class QuizListView(generics.ListAPIView):
    serializer_class = QuizSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        course_id = self.kwargs.get('course_id')
        return Quiz.objects.filter(course_id=course_id, is_active=True).prefetch_related('questions__answers')


class QuizDetailView(generics.RetrieveAPIView):
    queryset = Quiz.objects.all()
    serializer_class = QuizSerializer
    permission_classes = [permissions.IsAuthenticated]


class QuizCreateView(generics.CreateAPIView):
    queryset = Quiz.objects.all()
    serializer_class = QuizSerializer
    permission_classes = [IsInstructorOrAdmin]


class SubmitQuizView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, quiz_id):
        quiz = get_object_or_404(Quiz, pk=quiz_id)

        # Check attempt limit
        existing_attempts = QuizAttempt.objects.filter(
            user=request.user, quiz=quiz, status='completed'
        ).count()
        if existing_attempts >= quiz.max_attempts:
            return Response(
                {'detail': f'Maximum attempts ({quiz.max_attempts}) reached.'},
                status=status.HTTP_400_BAD_REQUEST
            )

        serializer = QuizAttemptCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        # Create attempt
        attempt = QuizAttempt.objects.create(user=request.user, quiz=quiz)
        total_points = 0
        earned_points = 0
        responses_to_create = []

        for resp_data in serializer.validated_data['responses']:
            question = resp_data['question']
            selected_answer = resp_data.get('selected_answer')
            text_response = resp_data.get('text_response', '')

            total_points += question.points
            is_correct = False
            points_earned = 0

            if selected_answer and selected_answer.is_correct:
                is_correct = True
                points_earned = question.points
                earned_points += points_earned

            responses_to_create.append(QuizResponse(
                attempt=attempt,
                question=question,
                selected_answer=selected_answer,
                text_response=text_response,
                is_correct=is_correct,
                points_earned=points_earned
            ))

        QuizResponse.objects.bulk_create(responses_to_create)

        score = (earned_points / total_points * 100) if total_points > 0 else 0
        passed = score >= quiz.passing_score

        attempt.score = round(score, 2)
        attempt.total_points = total_points
        attempt.earned_points = earned_points
        attempt.passed = passed
        attempt.status = 'completed'
        attempt.completed_at = timezone.now()
        attempt.time_taken = int((attempt.completed_at - attempt.started_at).total_seconds())
        attempt.save()

        return Response(QuizAttemptSerializer(attempt).data, status=status.HTTP_201_CREATED)


class MyQuizAttemptsView(generics.ListAPIView):
    serializer_class = QuizAttemptSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return QuizAttempt.objects.filter(
            user=self.request.user,
            quiz_id=self.kwargs.get('quiz_id')
        ).prefetch_related('responses')


class AssignmentListView(generics.ListCreateAPIView):
    serializer_class = AssignmentSerializer

    def get_permissions(self):
        if self.request.method == 'POST':
            return [IsInstructorOrAdmin()]
        return [permissions.IsAuthenticated()]

    def get_queryset(self):
        return Assignment.objects.filter(course_id=self.kwargs['course_id'])


class AssignmentDetailView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = AssignmentSerializer
    permission_classes = [permissions.IsAuthenticated]
    queryset = Assignment.objects.all()


class SubmitAssignmentView(generics.CreateAPIView):
    serializer_class = AssignmentSubmissionSerializer
    permission_classes = [permissions.IsAuthenticated]

    def perform_create(self, serializer):
        assignment = get_object_or_404(Assignment, pk=self.kwargs['assignment_id'])
        serializer.save(student=self.request.user, assignment=assignment)


class GradeSubmissionView(APIView):
    permission_classes = [IsInstructorOrAdmin]

    def post(self, request, submission_id):
        submission = get_object_or_404(AssignmentSubmission, pk=submission_id)
        serializer = GradeSubmissionSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        submission.score = serializer.validated_data['score']
        submission.feedback = serializer.validated_data.get('feedback', '')
        submission.status = 'graded'
        submission.graded_at = timezone.now()
        submission.graded_by = request.user
        submission.save()

        return Response(AssignmentSubmissionSerializer(submission).data)


class AssignmentSubmissionsView(generics.ListAPIView):
    serializer_class = AssignmentSubmissionSerializer
    permission_classes = [IsInstructorOrAdmin]

    def get_queryset(self):
        return AssignmentSubmission.objects.filter(
            assignment_id=self.kwargs['assignment_id']
        ).select_related('student')
