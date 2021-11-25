from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import Http404
from .models import Topic, Entry
from .forms import TopicForm, EntryForm

def index(request):
    """Домашняя страница приложения Learning_log"""
    return render(request, 'learning_logs/index.html')

@login_required
def topics(request):
    """Выводит список тем"""
    topics = Topic.objects.filter(owner=request.user).order_by('date_added')
    context = {'topics': topics}
    return render(request, 'learning_logs/topics.html', context)

@login_required
def topic(request, topic_id):
    """Выводит одну тему и все её записи"""
    topic = get_object_or_404(Topic, id=topic_id)
    #Проверка того, что тема принадлежит текущему пользователю
    _check_topic_owner(topic, request)

    entries = topic.entry_set.order_by('-date_added')
    context = {'topic': topic, 'entries': entries}
    return render(request, 'learning_logs/topic.html', context)

@login_required
def new_topic(request):
    """Определяет новую темы."""
    if request.method != 'POST':
        #Данные не отправлялись. Создается пустая форма
        form = TopicForm()
    else:
        #Отправлены данные POST. Обработать данные
        form = TopicForm(data=request.POST)
        if form.is_valid():
            new_topic = form.save(commit=False)
            new_topic.owner = request.user
            new_topic.save()
            return redirect('learning_logs:topics')

    # Вывести пустую или недействительную форму
    context = {'form': form}
    return render(request, 'learning_logs/new_topic.html', context)

@login_required
def new_entry(request, topic_id):
    """Добавляет новую запись по конкретной теме"""
    topic = Topic.objects.get(id=topic_id)
    _check_topic_owner(topic, request)
    if request.method != 'POST':
        #Данные не отправлялись. Создается пустая форма
        form = EntryForm()
    else:
        #Отправка данных POST. Обработать данные
        form = EntryForm(data=request.POST)
        if form.is_valid():
            new_entry = form.save(commit=False)
            new_entry.topic = topic
            new_entry.save()
            return redirect('learning_logs:topic', topic_id=topic_id)
    #Вывести пустую страницу или недействительную форму
    context = {'topic': topic, 'form': form}
    return render(request, 'learning_logs/new_entry.html', context)

@login_required
def edit_entry(request, entry_id):
    """Редактирует существующую запись"""
    entry = Entry.objects.get(id=entry_id)
    topic = entry.topic
    _check_topic_owner(topic, request)

    if request.method != 'POST':
        # Исходный запрос. Форма заполняется данными текущей записи
        form = EntryForm(instance=entry)
    else:
        # Отправка данных POST. Обработка данных
        form = EntryForm(instance=entry, data=request.POST)
        if form.is_valid():
            form.save()
            return redirect('learning_logs:topic', topic_id=topic.id)

    context = {'entry': entry, 'topic': topic, 'form': form}
    return render(request, 'learning_logs/edit_entry.html', context)

def _check_topic_owner(topic, request):
    """Проверяет связан ли текущий пользователь с данной темой"""
    if topic.owner != request.user:
        raise Http404()