"""
Forms for managing exams, questions and their choices via formsets.
"""

from django import forms

from .models import Answer, Choice, Exam, Question


class ExamForm(forms.ModelForm):
    """Form for creating and editing an Exam."""

    class Meta:
        model = Exam
        fields = ["title", "description"]
        widgets = {
            "title": forms.TextInput(attrs={"class": "form-control", "placeholder": "Exam title"}),
            "description": forms.Textarea(attrs={"class": "form-control", "rows": 3, "placeholder": "Exam description"}),
        }


class QuestionForm(forms.ModelForm):
    """Form for creating and editing a Question."""

    class Meta:
        model = Question
        fields = ["exam", "statement", "difficulty"]
        widgets = {
            "exam": forms.Select(attrs={"class": "form-control"}),
            "statement": forms.Textarea(attrs={"class": "form-control", "rows": 3, "placeholder": "Question statement"}),
            "difficulty": forms.Select(attrs={"class": "form-control"}),
        }


ChoiceFormSet = forms.inlineformset_factory(
    parent_model=Question,
    model=Answer,
    fields=["text", "is_correct"],
    extra=3,
    can_delete=True,
    widgets={
        "text": forms.TextInput(attrs={"class": "form-control", "placeholder": "Answer option"}),
        "is_correct": forms.CheckboxInput(attrs={"class": "form-check-input"}),
    },
)
