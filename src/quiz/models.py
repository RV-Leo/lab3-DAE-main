"""
Data models for the quiz application.
"""

from django.db import models
from django.conf import settings


class Exam(models.Model):
    """An exam consisting of one or more questions."""

    title = models.CharField(max_length=200, verbose_name="Title")
    description = models.TextField(verbose_name="Description")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Created at")

    class Meta:
        ordering = ["-created_at"]
        verbose_name = "Exam"
        verbose_name_plural = "Exams"

    def __str__(self) -> str:
        return self.title


class Question(models.Model):
    """A single quiz question with multiple-choice answers."""

    class Difficulty(models.TextChoices):
        EASY = "E", "Easy"
        MEDIUM = "M", "Medium"
        HARD = "H", "Hard"

    exam = models.ForeignKey(
        "Exam",
        on_delete=models.CASCADE,
        related_name="questions",
        verbose_name="Exam",
        blank=True,
        null=True,
    )
    statement = models.TextField(verbose_name="Question statement", blank=True, null=True)
    difficulty = models.CharField(
        max_length=1,
        choices=Difficulty.choices,
        default=Difficulty.EASY,
        verbose_name="Difficulty",
    )
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Created at")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Updated at")
    score = models.PositiveIntegerField(default=1, verbose_name="Score")

    class Meta:
        ordering = ["-created_at"]
        verbose_name = "Question"
        verbose_name_plural = "Questions"

    def __str__(self) -> str:
        return self.statement[:50]


class Answer(models.Model):
    """An answer option attached to a question."""

    question = models.ForeignKey(
        Question,
        on_delete=models.CASCADE,
        related_name="answers",
        verbose_name="Question",
    )
    text = models.TextField(verbose_name="Answer text")
    is_correct = models.BooleanField(default=False, verbose_name="Is correct")

    class Meta:
        ordering = ["pk"]
        verbose_name = "Answer"
        verbose_name_plural = "Answers"

    def __str__(self) -> str:
        prefix = "✓ " if self.is_correct else "  "
        return f"{prefix}{self.text[:50]}"


class Choice(models.Model):
    """A choice option attached to a question."""

    question = models.ForeignKey(
        Question,
        on_delete=models.CASCADE,
        related_name="choices",
        verbose_name="Question",
    )
    text = models.CharField(max_length=500, verbose_name="Choice text")
    is_correct = models.BooleanField(default=False, verbose_name="Is correct")

    class Meta:
        ordering = ["id"]
        verbose_name = "Choice"
        verbose_name_plural = "Choices"

    def __str__(self) -> str:
        return self.text[:50]


class Session(models.Model):
    """A quiz session – a user's attempt at a subset of questions."""

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="quiz_sessions",
        verbose_name="User",
    )
    started_at = models.DateTimeField(auto_now_add=True, verbose_name="Started at")
    finished_at = models.DateTimeField(null=True, blank=True, verbose_name="Finished at")
    score = models.PositiveIntegerField(default=0, verbose_name="Score")

    class Meta:
        ordering = ["-started_at"]
        verbose_name = "Quiz Session"
        verbose_name_plural = "Quiz Sessions"

    def __str__(self) -> str:
        return f"Session #{self.pk} – {self.user}"


class Response(models.Model):
    """A user's answer to a question within a session."""

    session = models.ForeignKey(
        Session,
        on_delete=models.CASCADE,
        related_name="responses",
        verbose_name="Session",
    )
    question = models.ForeignKey(
        Question,
        on_delete=models.CASCADE,
        related_name="responses",
        verbose_name="Question",
    )
    selected_answer = models.ForeignKey(
        Answer,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="responses",
        verbose_name="Answer selected",
    )

    class Meta:
        ordering = ["pk"]
        verbose_name = "Response"
        verbose_name_plural = "Responses"
        unique_together = ["session", "question"]

    def __str__(self) -> str:
        return f"Q#{self.question.pk} in session #{self.session.pk}"
