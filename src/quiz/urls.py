"""
URL configuration for the quiz application.
"""

from django.urls import path

from src.quiz.views import ExamDetailView, ExamListView, QuestionCreateView

app_name = "quiz"

urlpatterns = [
    path("exams/", ExamListView.as_view(), name="exam_list"),
    path("exam/<int:pk>/", ExamDetailView.as_view(), name="exam_detail"),
    path("exam/<int:exam_pk>/question/new/", QuestionCreateView.as_view(), name="question_create"),
]
