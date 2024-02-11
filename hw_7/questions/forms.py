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
    tags = forms.CharField(max_length=100, required=False)  # Define the tags field

    class Meta:
        model = Question
        fields = ["title", "content", "tags"]  # Include the tags field in the form

    def clean_tags(self):
        provided_tags = self.cleaned_data.get("tags")
        if not provided_tags:
            return []
        tags = provided_tags.split()
        if len(tags) > 3:
            raise forms.ValidationError("You can only provide up to 3 tags")
        return tags

    def save(self, commit=True):
        question = super().save(commit=False)
        if self.request:
            question.author = self.request.user  # Update to associate the user with the question
        if commit:
            question.save()
        return question

    def __init__(self, *args, **kwargs):
        self.request = kwargs.pop("request", None)
        super().__init__(*args, **kwargs)
        print("Form fields:", self.fields)
