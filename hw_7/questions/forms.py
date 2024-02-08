from django import forms

from .models import Question, Answer


class AnswerForm(forms.Form):
    content = forms.CharField(
        max_length=10000,
        required=True,
        widget=forms.Textarea,
        help_text="Try to be clear and polite",
    )

    def __init__(self, *args, **kwargs):
        self.question_id = kwargs.pop("question_id", None)
        super(AnswerForm, self).__init__(*args, **kwargs)

    def clean_content(self):
        content = self.cleaned_data.get("content")
        if Answer.objects.filter(question=self.question_id, content=content).count():
            raise forms.ValidationError(
                "There is an answer with exactly the same text" " for this question!"
            )
        return content


class QuestionForm(forms.ModelForm):
    class Meta:
        model = Question
        fields = ["title", "content"]

    def clean_title(self):
        provided_title = self.cleaned_data.get("title")
        if Question.objects.filter(title=provided_title).exists():
            raise forms.ValidationError("A question with this title already exists")
        return provided_title
