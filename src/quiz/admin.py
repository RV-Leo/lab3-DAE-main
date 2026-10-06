"""
Admin configuration for the quiz application.
"""

from django.contrib import admin

from src.quiz.models import Answer, Choice, Exam, Question, Response, Session


@admin.register(Exam)
class ExamAdmin(admin.ModelAdmin):
    list_display = ("pk", "title", "description", "created_at")
    search_fields = ("title", "description")
    readonly_fields = ("created_at",)
    list_filter = ("created_at",)


@admin.register(Question)
class QuestionAdmin(admin.ModelAdmin):
    list_display = ("pk", "statement_preview", "exam", "difficulty", "created_at")
    list_filter = ("difficulty", "exam")
    search_fields = ("statement",)
    readonly_fields = ("created_at", "updated_at")
    list_select_related = ("exam",)

    def statement_preview(self, obj):  # type: ignore[no-untyped-def]
        return obj.statement[:60] if obj.statement else ""

    statement_preview.short_description = "Question"


@admin.register(Answer)
class AnswerAdmin(admin.ModelAdmin):
    list_display = ("pk", "question", "text_preview", "is_correct")
    list_filter = ("is_correct",)
    search_fields = ("text", "question__statement")

    def text_preview(self, obj):  # type: ignore[no-untyped-def]
        return obj.text[:60]

    text_preview.short_description = "Answer"


@admin.register(Choice)
class ChoiceAdmin(admin.ModelAdmin):
    list_display = ("pk", "question", "text_preview", "is_correct")
    list_filter = ("is_correct",)
    search_fields = ("text", "question__statement")
    list_select_related = ("question",)

    def text_preview(self, obj):  # type: ignore[no-untyped-def]
        return obj.text[:60]

    text_preview.short_description = "Choice"


@admin.register(Response)
class ResponseAdmin(admin.ModelAdmin):
    list_display = ("pk", "session", "question", "selected_answer")
    list_filter = ("session",)
    list_select_related = ("session", "question", "selected_answer")


@admin.register(Session)
class SessionAdmin(admin.ModelAdmin):
    list_display = ("pk", "user", "started_at", "finished_at", "score")
    list_filter = ("started_at",)
    search_fields = ("user__username",)
    readonly_fields = ("started_at", "finished_at", "score")
    list_select_related = ("user",)
