from django.urls import path

from . import views

app_name = 'pybo'

urlpatterns = [
    path('', views.index, name='index'),
    path('<int:question_id>/', views.detail, name='detail'),
    path('question/create/', views.question_create, name='question_create'),
    path('answer/create/<int:question_id>/', views.answer_create, name='answer_create'),
    # path('', views.index.as_view(), name='pybo_index'),
    # path('<int:pk>/', views.detail.as_view(), name='pybo_detail'),
]