from django import forms
from .models import Question, Answer, Tag


class AnswerForm(forms.ModelForm):
    class Meta:
        model = Answer
        fields = ["content"]
        widgets = {"content": forms.Textarea(attrs={"rows": 3})}

    def __init__(self, *args, **kwargs):
        self.question_id = kwargs.pop("question_id", None)
        super(AnswerForm, self).__init__(*args, **kwargs)

    def clean_content(self):
        content = self.cleaned_data.get("content")
        if Answer.objects.filter(question=self.question_id, content=content).count():
            raise forms.ValidationError(
                "An answer with exactly the same text for this question already exists!"
            )
        return content


class QuestionForm(forms.ModelForm):
    tags = forms.CharField(max_length=60, required=False)

    class Meta:
        model = Question
        fields = ["title", "content"]

    def clean_tags(self):
        provided_tags = self.cleaned_data.get("tags")
        if not provided_tags:
            return []
        tags = provided_tags.split()
        if len(tags) > 3:
            raise forms.ValidationError("You can only provide up to 3 tags")
        return tags
