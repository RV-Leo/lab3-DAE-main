"""
Tests for the quiz application.
"""

from django.test import TestCase


class QuizTestCase(TestCase):
    """Basic smoke tests for the quiz app."""

    def test_question_model_creation(self):
        from src.quiz.models import Question

        q = Question.objects.create(
            text="What is the capital of Peru?",
            difficulty=Question.Difficulty.EASY,
        )
        self.assertEqual(str(q), "What is the capital of Peru?")
        self.assertEqual(q.answers.count(), 0)

    def test_answer_model_creation(self):
        from src.quiz.models import Answer, Question

        q = Question.objects.create(
            text="2 + 2 = ?",
            difficulty=Question.Difficulty.EASY,
        )
        a = Answer.objects.create(question=q, text="4", is_correct=True)
        self.assertEqual(a.question, q)
        self.assertTrue(a.is_correct)

    def test_session_and_response_flow(self):
        from django.contrib.auth.models import User
        from src.quiz.models import Answer, Question, Response, Session

        user = User.objects.create_user(username="testuser", password="pass")
        q = Question.objects.create(text="Color of the sky?", difficulty=Question.Difficulty.EASY)
        correct = Answer.objects.create(question=q, text="Blue", is_correct=True)
        wrong = Answer.objects.create(question=q, text="Red", is_correct=False)

        session = Session.objects.create(user=user)
        resp = Response.objects.create(session=session, question=q, selected_answer=wrong)
        self.assertEqual(resp.session, session)
        self.assertFalse(resp.selected_answer.is_correct)
