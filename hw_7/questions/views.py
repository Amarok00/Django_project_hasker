from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.db.models import Q
from django.http import Http404, HttpResponseRedirect
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse_lazy
from django.views import View
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from hasker.signals import question_answered
from .forms import AnswerForm, QuestionForm
from .helpers import save_tags
from .models import Answer, Question, Tag, Voters
from django.views.generic.edit import CreateView

num_pages = settings.ELEMENTS_PER_PAGE


class IndexView(View):
    template_name = "questions/index.html"

    def get_queryset(self):
        return Question.objects.all().order_by("-created_on", "title")

    def get(self, request, pages=num_pages):
        queryset = self.get_queryset()
        paginator = Paginator(queryset, pages)
        page_number = request.GET.get("page")
        page_obj = paginator.get_page(page_number)
        context = {"page_obj": page_obj}
        return render(request, self.template_name, context)


class HotIndexView(IndexView):
    template_name = "questions/hot_questions.html"

    def get_queryset(self):
        return Question.objects.all().order_by("-votes", "title")


class SearchTagView(View):
    template_name = "questions/tag.html"

    def get(self, request, tag_id, pages=num_pages):
        tag = get_object_or_404(Tag, id=tag_id)
        queryset = tag.questions.all()
        paginator = Paginator(queryset, pages)
        page_number = request.GET.get("page")
        page_obj = paginator.get_page(page_number)
        context = {"page_obj": page_obj, "tag": tag}
        return render(request, self.template_name, context)


class IndexSearchView(View):
    template_name = "questions/search.html"

    def post(self, request, pages=num_pages):
        search = request.POST.get("search", None)
        if search.startswith("tag:"):
            tag_name = search[4:].strip()
            try:
                tag = Tag.objects.get(title=tag_name)
            except Tag.DoesNotExist:
                context = {"error_message": f"No tag {tag_name} found"}
                return render(request, self.template_name, context)
            return redirect("questions:search_tag", tag_id=tag.id)

        queryset = (
            Question.objects.select_related()
            .filter(
                Q(title__icontains=search)
                | Q(content__icontains=search)
                | Q(answer__content__icontains=search)
            )
            .distinct()
            .order_by("-votes", "-created_on")
        )
        paginator = Paginator(queryset, pages)
        page_number = request.GET.get("page")
        page_obj = paginator.get_page(page_number)
        context = {"page_obj": page_obj, "searchstring": search}
        return render(request, self.template_name, context)


class ShowQuestionView(View):
    template_name = "questions/question.html"

    def get(self, request, question_id):
        qw = get_object_or_404(Question, pk=question_id)
        context = {"question": qw, "form": AnswerForm()}

        answer_query = Answer.objects.filter(question=question_id).order_by(
            "-votes", "-answer_flag", "-created_on"
        )
        tags = Tag.objects.filter(questions=question_id)
        context.update({"answer_query": answer_query, "tags": tags})
        return render(request, self.template_name, context)

    def post(self, request, question_id):
        if not request.user.is_authenticated:
            return redirect("users:login")

        form = AnswerForm(request.POST, question_id=question_id)
        if form.is_valid():
            content = form.cleaned_data.get("content")
            answer = Answer(
                author=request.user, question_id=question_id, content=content
            )
            answer.save()
            # send a signal about a new answer
            question_answered.send(sender=ShowQuestionView, question=answer.question)

        return HttpResponseRedirect(request.META["HTTP_REFERER"])


class MakeQuestionView(CreateView):
    model = Question
    form_class = QuestionForm
    template_name = "questions/make_question.html"
    success_url = reverse_lazy("questions:index")

    def form_valid(self, form):
        print("Inside form_valid method")
        form.instance.author = self.request.user
        return super().form_valid(form)

    def form_invalid(self, form):
        print("Inside form_invalid method")
        return super().form_invalid(form)


class AlterFlagView(View):
    @login_required
    def get(self, request, answer_id):
        answer = get_object_or_404(Answer, pk=answer_id)
        qw = answer.question

        if not qw.author.id == request.user.id:
            return HttpResponseRedirect(request.META["HTTP_REFERER"])
        if qw.author.id == answer.author.id:
            return HttpResponseRedirect(request.META["HTTP_REFERER"])

        if answer.answer_flag == 1:
            answer.delete_flag()
        else:
            if qw.status == 0:
                answer.set_new_flag()
            elif qw.status == 1:
                answer.change_flag()

        return HttpResponseRedirect(request.META["HTTP_REFERER"])


@login_required
def answer_vote(request, answer_id, vote=1):
    try:
        answer = Answer.objects.get(pk=answer_id)
    except Answer.DoesNotExist:
        raise Http404("Answer does not exist")

    if answer.author.id == request.user.id:
        # user cannot vote for his own answers
        return HttpResponseRedirect(request.META["HTTP_REFERER"])

    try:
        Voters.register_vote(object=answer, user_id=request.user.id, vote=vote)
    except Exception as e:
        # Handle the exception
        print(f"An error occurred: {e}")

    return HttpResponseRedirect(request.META["HTTP_REFERER"])


class QuestionVoteView(View):
    def get(self, request, question_id, vote=1):
        qw = Question.objects.get(pk=question_id)
        if qw.author.id == request.user.id:
            return HttpResponseRedirect(request.META["HTTP_REFERER"])
        else:
            Voters.register_vote(object=qw, user_id=request.user.id, vote=vote)
            return HttpResponseRedirect(request.META["HTTP_REFERER"])
