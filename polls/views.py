from typing import Any
from django.db import models
from django.http import HttpResponseRedirect
from django.shortcuts import render, get_object_or_404
from django.urls import reverse
from django.views import generic
from django.utils import timezone

from .models import Question, Choice


class IndexView(generic.ListView):
    template_name = "polls/index.html"
    context_object_name = "latest_question_list"

    # Removes the questions that arent published yet (future questions)
    # Used sources:
    #   https://forum.djangoproject.com/t/what-do-the-lt-lte-gt-gte-related-lookups-do/17558
    #   https://docs.djangoproject.com/en/4.2/topics/db/aggregation/
    def get_queryset(self):
        return Question.objects.annotate(choice_count = models.Count('choice')).filter(pub_date__lte=timezone.now()).filter(choice_count__gt=0).order_by("-pub_date")[:5]
    
class DetailView(generic.DetailView):
    model = Question
    template_name = "polls/detail.html"

    # Removes the questions that arent published yet (future questions)
    def get_queryset(self):
        return Question.objects.filter(pub_date__lte=timezone.now())

class ResultsView(generic.DetailView):
    model = Question
    template_name = "polls/results.html"

    # Removes the questions that arent published yet (future questions)
    def get_queryset(self):
        return Question.objects.filter(pub_date__lte=timezone.now())

def vote(request, question_id):
    question = get_object_or_404(Question, pk=question_id)
    try:
        selected_choice = question.choice_set.get(pk=request.POST["choice"])
    except (KeyError, Choice.DoesNotExist):
        return render(
            request,
            "polls/detail.html",
            {
                "question": question,
                "error_message": "You didn't select a choice.",
            },
        )
    else:
        selected_choice.votes += 1
        selected_choice.save()
        return HttpResponseRedirect(reverse("polls:results", args=(question.id,)))