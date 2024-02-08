from django.urls import path

from .views import (
    IndexView,
    HotIndexView,
    SearchTagView,
    IndexSearchView,
    ShowQuestionView,
    MakeQuestionView,
    AlterFlagView,
    AnswerVoteView,
    QuestionVoteView,
)

app_name = "questions"
urlpatterns = [
    path("", IndexView.as_view(), name="index"),
    path("search", IndexSearchView.as_view(), name="search"),
    path("<int:question_id>", ShowQuestionView.as_view(), name="question"),
    path("hot", HotIndexView.as_view(), name="hot"),
    path("add/", MakeQuestionView.as_view(), name="make_question"),
    path("alterflag/<int:answer_id>", AlterFlagView.as_view(), name="alterflag"),
    path("tag/<int:tag_id>", SearchTagView.as_view(), name="searchtag"),
    path(
        "answervote/<int:answer_id>/<int:vote>",
        AnswerVoteView.as_view(),
        name="answervote",
    ),
    path(
        "questionvote/<int:question_id>/<int:vote>",
        QuestionVoteView.as_view(),
        name="questionvote",
    ),
]
