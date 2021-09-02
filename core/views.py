from django.http import HttpResponse, HttpResponseRedirect
from .models import Answer, Quiz, Question, SelectedAnswer, QuizTaken
from django.shortcuts import get_object_or_404, render
from django.template import loader
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from django.urls import reverse


def index(request):
    """Basic index view."""

    # load template
    template = loader.get_template("core/base.html")
    context = {}

    # return response along with rendered template
    return HttpResponse(template.render(context, request))


@login_required(login_url="/accounts/login/")
def quiz(request, id):
    # load correct template
    template = loader.get_template("core/quiz.html")

    def _check_if_quiz_is_started(quiz):
        """Function to check if user has already started this particular quiz."""

        quiz_already_started = False
        # check if quiz is already started - if it is then set up already_started bool
        quiz_taken = QuizTaken.objects.filter(user=request.user, quiz=quiz)
        if quiz_taken:
            quiz_already_started = True

        return quiz_already_started

    def _start_quiz(quiz):
        """Function to start a new quiz for the user, it will create an entry in the QuizTaken model."""

        # start quiz for this user - create a QuizTaken object or update
        quiz_taken, created = QuizTaken.objects.update_or_create(
            user=request.user,
            quiz=quiz,
            defaults={
                "status": QuizTaken.STATUS_STARTED,
            },
        )
        # check if object is created, if created set started_at at now()
        if created:
            quiz_taken.started_at = timezone.now()
            quiz_taken.save()

        return True

    def _get_selected_answer(question, quiz):
        """Function to get all the selected answers for question and quiz."""

        selected_answer = SelectedAnswer.objects.filter(user=request.user, quiz=quiz, question=question).first()

        return selected_answer

    def _get_questions_list(quiz):
        """Function to get all the questions/answers and few additional variables."""

        questions_list = list()
        # iterate through quiz questions
        for question in quiz.questions.all():
            selected_answer = _get_selected_answer(question=question, quiz=quiz)

            answer_is_correct = False
            # if there is selected answer - check if that answer is correct
            if selected_answer:
                correct_answer = question.answers.filter(is_correct=True).first()
                if correct_answer and correct_answer.answer == selected_answer.content:
                    answer_is_correct = True

            # prepare all the required data
            data = {
                "question": question,
                "answers": question.answers.all(),
                "selected_answer_for_this_question": selected_answer,
                "answer_is_correct": answer_is_correct,
            }
            # append data to list
            questions_list.append(data)

        return questions_list

    try:
        # try and find quiz object based on the provided `id`
        quiz_object = Quiz.objects.get(id=id, is_active=True)

        # check if quiz started
        quiz_started = _check_if_quiz_is_started(quiz=quiz_object)

        if request.GET.get("option") and request.GET["option"] == "start":
            # start new quiz
            quiz_started = _start_quiz(quiz=quiz_object)

        # define context to be sent to template
        context = {
            "quiz_object": quiz_object,
            "questions_list": _get_questions_list(quiz=quiz_object),
            "started": quiz_started,
            "quiz_completed": False,
        }
    except Exception:
        # display exception error
        error_template = loader.get_template("common/errors/http_404.html")
        context = {}
        # return response along with error template
        return HttpResponse(error_template.render(context, request))

    return HttpResponse(template.render(context, request))


def quiz_question(request, id):
    """View to store answer."""

    question = get_object_or_404(Question, pk=id)

    quiz_id = request.POST["quiz"]
    choice_id = request.POST["choice"]
    user = request.user

    quiz = None

    try:
        selected_answer_choice = question.answers.get(id=choice_id)
        quiz = Quiz.objects.get(pk=quiz_id)
    except Exception as e:
        pass

    if selected_answer_choice and quiz and user:
        # create new Selecte Answer or update existing one, if it is the Answer to the same Question
        ob, created = SelectedAnswer.objects.update_or_create(
            user=user,
            quiz=quiz,
            question=question,
            defaults={
                "content": selected_answer_choice.answer,
            },
        )

    # return redirect response to the quiz
    return HttpResponseRedirect(reverse("quiz:quiz_start", args=(quiz.id,)))
