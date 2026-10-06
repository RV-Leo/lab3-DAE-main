"""
URL configuration for the quiz_course_session project.
"""

from django.contrib import admin
from django.urls import include, path
from rest_framework.routers import DefaultRouter
from src.quiz.views import (
    AnswerViewSet,
    ExamViewSet,
    QuestionViewSet,
    ResponseViewSet,
    SessionViewSet,
)

router = DefaultRouter()
router.register(r"exams", ExamViewSet)
router.register(r"questions", QuestionViewSet)
router.register(r"answers", AnswerViewSet)
router.register(r"sessions", SessionViewSet)
router.register(r"responses", ResponseViewSet)

urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/", include(router.urls)),
    path("", include("src.quiz.urls")),
]
