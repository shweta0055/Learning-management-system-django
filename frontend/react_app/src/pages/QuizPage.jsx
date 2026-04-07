import React, { useState } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { useQuery, useMutation } from '@tanstack/react-query';
import { quizzesAPI } from '../services/api';
import { toast } from 'react-toastify';

export default function QuizPage() {
  const { quizId } = useParams();
  const navigate = useNavigate();
  const [answers, setAnswers] = useState({});
  const [submitted, setSubmitted] = useState(false);
  const [result, setResult] = useState(null);

  const { data: quiz, isLoading } = useQuery({
    queryKey: ['quiz', quizId],
    queryFn: () => quizzesAPI.getQuiz(quizId),
    select: (r) => r.data,
  });

  const submitMutation = useMutation({
    mutationFn: (data) => quizzesAPI.submitQuiz(quizId, data),
    onSuccess: (res) => {
      setResult(res.data);
      setSubmitted(true);
      toast[res.data.passed ? 'success' : 'error'](
        res.data.passed ? `Passed! Score: ${res.data.score}%` : `Failed. Score: ${res.data.score}%`
      );
    },
    onError: (err) => toast.error(err.response?.data?.detail || 'Submission failed'),
  });

  const handleSubmit = () => {
    const responses = quiz.questions.map((q) => ({
      question: q.id,
      selected_answer: answers[q.id] || null,
    }));
    submitMutation.mutate({ responses });
  };

  if (isLoading) return <div className="text-center py-20">Loading quiz...</div>;
  if (!quiz) return <div className="text-center py-20">Quiz not found.</div>;

  if (submitted && result) {
    return (
      <div className="max-w-2xl mx-auto px-4 py-16 text-center">
        <div className={`text-7xl mb-4`}>{result.passed ? '🎉' : '😔'}</div>
        <h1 className="text-3xl font-bold text-gray-900 mb-2">
          {result.passed ? 'Congratulations!' : 'Better luck next time!'}
        </h1>
        <p className="text-gray-600 mb-6">{quiz.title}</p>
        <div className="card p-8 mb-8">
          <div className={`text-6xl font-bold mb-2 ${result.passed ? 'text-green-600' : 'text-red-500'}`}>
            {result.score}%
          </div>
          <p className="text-gray-600">
            {result.earned_points} / {result.total_points} points
          </p>
          <p className="text-sm text-gray-500 mt-2">Passing score: {quiz.passing_score}%</p>
        </div>
        <button onClick={() => navigate(-1)} className="btn-primary px-8 py-2.5">
          Back to Course
        </button>
      </div>
    );
  }

  return (
    <div className="max-w-3xl mx-auto px-4 py-10">
      <div className="mb-8">
        <h1 className="text-2xl font-bold text-gray-900">{quiz.title}</h1>
        {quiz.description && <p className="text-gray-500 mt-2">{quiz.description}</p>}
        <div className="flex items-center gap-4 mt-3 text-sm text-gray-500">
          <span>{quiz.question_count} questions</span>
          {quiz.time_limit > 0 && <span>⏱ {quiz.time_limit} minutes</span>}
          <span>Passing: {quiz.passing_score}%</span>
        </div>
      </div>

      <div className="space-y-6 mb-8">
        {quiz.questions?.map((question, qi) => (
          <div key={question.id} className="card p-6">
            <p className="font-semibold text-gray-900 mb-4">
              <span className="text-primary-600 mr-2">Q{qi + 1}.</span>
              {question.text}
            </p>
            <div className="space-y-2">
              {question.answers?.map((answer) => (
                <label key={answer.id}
                  className={`flex items-center gap-3 p-3 rounded-lg border cursor-pointer transition-colors ${
                    answers[question.id] === answer.id
                      ? 'border-primary-500 bg-primary-50'
                      : 'border-gray-200 hover:border-gray-300 hover:bg-gray-50'
                  }`}>
                  <input
                    type="radio"
                    name={`q-${question.id}`}
                    value={answer.id}
                    checked={answers[question.id] === answer.id}
                    onChange={() => setAnswers((prev) => ({ ...prev, [question.id]: answer.id }))}
                    className="text-primary-600"
                  />
                  <span className="text-sm text-gray-700">{answer.text}</span>
                </label>
              ))}
            </div>
          </div>
        ))}
      </div>

      <div className="flex justify-between items-center">
        <button onClick={() => navigate(-1)} className="btn-secondary py-2.5 px-6">
          Cancel
        </button>
        <button
          onClick={handleSubmit}
          disabled={submitMutation.isPending || Object.keys(answers).length < (quiz.questions?.length || 0)}
          className="btn-primary py-2.5 px-8"
        >
          {submitMutation.isPending ? 'Submitting...' : 'Submit Quiz'}
        </button>
      </div>
      <p className="text-center text-xs text-gray-400 mt-2">
        {Object.keys(answers).length} of {quiz.questions?.length} answered
      </p>
    </div>
  );
}
