"""
Views for managing exams and questions (rendered with templates).
"""

from django.contrib import messages
from django.shortcuts import get_object_or_404, redirect, render
from django.views.generic import DetailView, ListView
from django.views.generic.edit import FormView
from rest_framework import mixins, permissions, serializers, status, viewsets
from rest_framework.response import Response
from rest_framework.serializers import (
    BooleanField,
    CharField,
    ChoiceField,
    DateTimeField,
    IntegerField,
    PrimaryKeyRelatedField,
    SerializerMethodField,
    StringRelatedField,
)

from src.quiz.forms import ChoiceFormSet, QuestionForm
from src.quiz.models import Answer, Exam, Question, Response, Session


# ── Exam Serializers ──────────────────────────────────────────────────────


class ExamReadSerializer(serializers.Serializer):
    pk = IntegerField(read_only=True)
    title = CharField()
    description = CharField(max_length=None)
    created_at = DateTimeField(read_only=True)
    questions = SerializerMethodField()

    def get_questions(self, obj):
        return [
            {
                "pk": q.pk,
                "statement": q.statement,
                "difficulty": q.difficulty,
            }
            for q in obj.questions.all()
        ]


class ExamWriteSerializer(serializers.Serializer):
    title = CharField(max_length=200)
    description = CharField(max_length=None)


class ExamViewSet(viewsets.ModelViewSet):
    queryset = Exam.objects.all()

    def get_serializer_class(self):
        if self.action in ("create", "update", "partial_update"):
            return ExamWriteSerializer
        return ExamReadSerializer


# ── Question Serializers ──────────────────────────────────────────────────


class QuestionReadSerializer(serializers.Serializer):
    pk = IntegerField(read_only=True)
    text = CharField(max_length=None, source="statement")
    difficulty = ChoiceField(choices=Question.Difficulty.choices)
    score = IntegerField(read_only=True)
    created_at = DateTimeField(read_only=True)
    updated_at = DateTimeField(read_only=True)
    answers = PrimaryKeyRelatedField(many=True, read_only=True)


class QuestionWriteSerializer(serializers.Serializer):
    statement = CharField(max_length=None)
    difficulty = ChoiceField(
        choices=Question.Difficulty.choices,
        default=Question.Difficulty.EASY,
    )
    score = IntegerField(default=1)


class QuestionViewSet(viewsets.ModelViewSet):
    queryset = Question.objects.all()

    def get_serializer_class(self):
        if self.action in ("create", "update", "partial_update"):
            return QuestionWriteSerializer
        return QuestionReadSerializer


# ── Answer Serializers ────────────────────────────────────────────────────


class AnswerReadSerializer(serializers.Serializer):
    pk = IntegerField(read_only=True)
    question = PrimaryKeyRelatedField(read_only=True)
    text = CharField(max_length=None)
    is_correct = BooleanField(read_only=True)


class AnswerWriteSerializer(serializers.Serializer):
    text = CharField(max_length=None)
    is_correct = BooleanField(default=False)


class AnswerViewSet(viewsets.ModelViewSet):
    serializer_class = None
    queryset = Answer.objects.select_related("question")

    def get_queryset(self):
        qs = super().get_queryset()
        question_pk = self.kwargs.get("question_pk")
        if question_pk:
            qs = qs.filter(question_id=question_pk)
        return qs

    def get_serializer_class(self):
        if self.action in ("create", "update", "partial_update"):
            return AnswerWriteSerializer
        return AnswerReadSerializer


# ── Session Serializers ───────────────────────────────────────────────────


class SessionReadSerializer(serializers.Serializer):
    pk = IntegerField(read_only=True)
    user = StringRelatedField(read_only=True)
    started_at = DateTimeField(read_only=True)
    finished_at = DateTimeField(read_only=True)
    score = IntegerField(read_only=True)
    responses = SerializerMethodField()

    def get_responses(self, obj):
        return [
            {
                "question_id": r.question_id,
                "selected_answer_id": r.selected_answer_id,
                "is_correct": r.selected_answer_id is not None
                and r.selected_answer.is_correct,
            }
            for r in obj.responses.all()
        ]


class SessionWriteSerializer(serializers.Serializer):
    question_ids = PrimaryKeyRelatedField(
        many=True, queryset=Question.objects.all(),
    )


class SessionViewSet(
    mixins.ListModelMixin,
    mixins.CreateModelMixin,
    viewsets.GenericViewSet,
):
    queryset = Session.objects.select_related("user").prefetch_related(
        "responses__question", "responses__selected_answer",
    )
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    def get_serializer_class(self):
        if self.action in ("create", "partial_update"):
            return SessionWriteSerializer
        return SessionReadSerializer

    def perform_create(self, serializer):
        question_ids = self.request.data.get("question_ids", [])
        session = Session.objects.create(user=self.request.user)
        for qid in question_ids:
            Response.objects.create(session=session, question_id=qid)
        session.save()


# ── Response Serializers ──────────────────────────────────────────────────


class ResponseReadSerializer(serializers.Serializer):
    pk = IntegerField(read_only=True)
    session = PrimaryKeyRelatedField(read_only=True)
    question = PrimaryKeyRelatedField(read_only=True)
    selected_answer = PrimaryKeyRelatedField(read_only=True, allow_null=True)


class ResponseWriteSerializer(serializers.Serializer):
    selected_answer_id = PrimaryKeyRelatedField(
        queryset=Answer.objects.all(), allow_null=True,
    )


class ResponseViewSet(
    mixins.ListModelMixin,
    mixins.UpdateModelMixin,
    viewsets.GenericViewSet,
):
    queryset = Response.objects.select_related(
        "session", "question", "selected_answer",
    )
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    def get_serializer_class(self):
        if self.action in ("partial_update",):
            return ResponseWriteSerializer
        return ResponseReadSerializer

    def partial_update(self, request, *args, **kwargs):
        instance = self.get_object()
        answer_id = request.data.get("selected_answer_id")
        if answer_id:
            instance.selected_answer_id = answer_id
            instance.save()
        return Response(
            {
                "pk": instance.pk,
                "selected_answer_id": instance.selected_answer_id,
                "is_correct": (
                    instance.selected_answer_id is not None
                    and instance.selected_answer.is_correct
                ),
            },
            status=status.HTTP_200_OK,
        )


# ── Template Views ────────────────────────────────────────────────────────


class ExamListView(ListView):
    """Display all exams."""
    model = Exam
    template_name = "quiz/exam_list.html"
    context_object_name = "exams"


class ExamDetailView(DetailView):
    """Show an exam with its questions and their choices."""
    model = Exam
    template_name = "quiz/exam_detail.html"
    context_object_name = "exam"

    def get_context_data(self, **kwargs):  # type: ignore[no-untyped-def]
        context = super().get_context_data(**kwargs)
        context["questions"] = self.object.questions.all()
        return context


class QuestionCreateView(FormView):
    """Add a question to an exam with its answer choices (formset)."""
    template_name = "quiz/question_form.html"
    form_class = QuestionForm

    def get_initial(self):  # type: ignore[no-untyped-def]
        initial = super().get_initial()
        initial["exam"] = self.kwargs.get("exam_pk")
        return initial

    def get_context_data(self, **kwargs):  # type: ignore[no-untyped-def]
        context = super().get_context_data(**kwargs)
        exam = get_object_or_404(Exam, pk=self.kwargs.get("exam_pk"))
        context["exam"] = exam
        if context.get("form"):
            context["choice_formset"] = ChoiceFormSet(
                self.request.POST if self.request.method == "POST" else None,
                instance=None,
            )
        else:
            context["choice_formset"] = ChoiceFormSet(instance=None)
        return context

    def form_valid(self, form):  # type: ignore[no-untyped-def]
        form.instance.exam_id = self.kwargs.get("exam_pk")
        question = form.save()
        formset = ChoiceFormSet(
            self.request.POST,
            instance=question,
        )
        if not formset.is_valid():
            return self.render_to_response(
                self.get_context_data(form=form, choice_formset=formset)
            )

        # Validate that exactly one choice is marked correct
        correct_choices = [f.cleaned_data for f in formset.forms if f.cleaned_data and f.cleaned_data.get("is_correct")]
        if len(correct_choices) != 1:
            formset.add_error(
                None,
                "Exactly one answer must be marked as correct.",
            )
            return self.render_to_response(
                self.get_context_data(form=form, choice_formset=formset)
            )

        formset.save()
        messages.success(self.request, "Question added successfully.")
        return redirect("quiz:exam_detail", pk=question.exam.pk)

    def form_invalid(self, form):  # type: ignore[no-untyped-def]
        return self.render_to_response(
            self.get_context_data(form=form, choice_formset=ChoiceFormSet())
        )
