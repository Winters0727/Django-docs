from django.http import HttpResponse
from django.shortcuts import render, redirect, get_object_or_404

from .models import Question
from .forms import QuestionForm, AnswerForm
# Create your views here.

def index(request):
    """
    pybo 목록 출력
    """
    question_list = Question.objects.order_by('-create_date')
    context = { 'question_list' : question_list }
    return render(request, 'pybo/question_list.html', context=context)

def detail(request, question_id):
    """
    pybo 내용 출력
    """
    question = get_object_or_404(Question, pk=question_id)
    context = {'question' : question }
    return render(request, 'pybo/question_detail.html', context=context)

def question_create(request):
    if request.method == 'POST':
        form = QuestionForm(request.POST)
        if form.is_valid():
            question = form.save(commit=False)
            question.save()
            return redirect('pybo:index')
    else:
        form = QuestionForm()
    context = {'form' : form}
    return render(request, 'pybo/question_form.html', context=context)

def answer_create(request, question_id):
    question = get_object_or_404(Question, pk=question_id)

    if request.method == 'POST':
        form = AnswerForm(request.POST)
        if form.is_valid():
            answer = form.save(commit=False)
            answer.question = question
            answer.save()
            return redirect('pybo:detail', question_id=question.id)
    else:
        form = AnswerForm()
    context = {'question' : question, 'form' : form}
    return redirect('pybo:detail', question_id=question.id)

# from django.views.generic.list import ListView
# from django.views.generic.detail import DetailView

# class index(ListView):
#     def get_queryset(self):
#         return Question.objects.order_by('-create_date')

# class detail(DetailView):
#     model = Question