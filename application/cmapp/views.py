from django.shortcuts import render
from .models import Project, Todo, Milestone, Note
from .forms import ProjectForm, RisknoteForm, NoteForm, BudgetForm, TodoForm
from django.views.generic.edit import CreateView, FormMixin, UpdateView
from django.views.generic.list import ListView
from django.views.generic.detail import DetailView
from django.db.models.functions import Round
from django.db.models import Q, Count
from django.db.models.functions.comparison import NullIf
from django.urls import reverse, reverse_lazy
from django.views.generic import View
from .filters import ProjectFilter
from django.shortcuts import render, redirect, get_object_or_404
import datetime
from django.contrib import messages
from django.http import HttpResponse
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin


class ListFilteredMixin(object):
    """
    Mixin that adds support for django-filter
    """

    filter_set = None

    def get_filter_set(self):
        if self.filter_set:
            return self.filter_set
        else:
            raise ImproperlyConfigured(
                "ListFilterMixin requires either a definition of "
                "'filter_set' or an implementation of 'get_filter()'")

    def get_filter_set_kwargs(self):
        """
        Returns the keyword arguments for instanciating the filterset.
        """
        return {
            'data': self.request.GET,
            'queryset': self.get_base_queryset(),
        }

    def get_base_queryset(self):
        """
        We can decided to either alter the queryset before or after applying the
        FilterSet
        """
        return super(ListFilteredMixin, self).get_queryset()

    def get_constructed_filter(self):
        # We need to store the instantiated FilterSet cause we use it in
        # get_queryset and in get_context_data
        if getattr(self, 'constructed_filter', None):
            return self.constructed_filter
        else:
            f = self.get_filter_set()(**self.get_filter_set_kwargs())
            self.constructed_filter = f
            return f

    def get_queryset(self):
        return self.get_constructed_filter().qs

    def get_context_data(self, **kwargs):
        kwargs.update({'filter': self.get_constructed_filter()})
        return super(ListFilteredMixin, self).get_context_data(**kwargs)

class PaginatedFilterViews(View):
    def get_context_data(self, **kwargs):
        context = super(PaginatedFilterViews, self).get_context_data(**kwargs)
        if self.request.GET:
            querystring = self.request.GET.copy()
            if self.request.GET.get('page'):
                del querystring['page']
            context['querystring'] = querystring.urlencode()
        return context

class projects(ListFilteredMixin, ListView):
    model = Project
    template_name = 'project_list.html'
    ordering = ['project_title']
    paginate_by = 10
    filter_set = ProjectFilter

    queryset = Project.objects.annotate(
        todo_done=Round(Count('todo', filter=Q(todo__state=True)) * 100.0 / NullIf(Count('todo'), 0)),
        todo_left=Round(Count('todo', filter=Q(todo__state=False)) * 100.0 / NullIf(Count('todo'), 0)),
    )

class projectdetail(LoginRequiredMixin, FormMixin, DetailView):
    model = Project
    template_name = 'project_detail.html'
    slug_field = 'slug'
    form_class = BudgetForm

    def get_context_data(self, *args, **kwargs):
        context = super(projectdetail, self).get_context_data(**kwargs)

        '''Rescatar todos las tareas del pryecto'''
        project = self.get_object()
        progress_field = project.todo_set.all()
        '''Listar el campo progress'''
        progress = []
        for todos in progress_field:
            progress.append(todos.progress)
        '''eliminar los NoneType de la lista'''
        progress_not_none = [x for x in progress if x is not None]
        '''Sumar la lista'''
        sum_progress = 0
        for num in progress_not_none:
            sum_progress += num
        ''''''


        '''Rescatar todos los presupuestos opex de este proyecto'''
        budget_field_opex = project.budget_set.filter(type='Opex')
        '''Listar el campo budget'''
        budget_list_opex = []
        for budgets in budget_field_opex:
            budget_list_opex.append(budgets.money)

        '''Sumar la lista'''
        sum_budgets_opex = 0
        for num in budget_list_opex:
            sum_budgets_opex += num

        '''Rescatar todos los presupuestos capex de este proyecto'''
        budget_field_capex = project.budget_set.filter(type='Capex')
        '''Listar el campo budget'''
        budget_list_capex = []
        for budgets in budget_field_capex:
            budget_list_capex.append(budgets.money)

        '''Sumar la lista'''
        sum_budgets_capex = 0
        for num in budget_list_capex:
            sum_budgets_capex += num

        sum_budgets = sum_budgets_capex - sum_budgets_opex

        # print(sum_budgets_opex)

        if Todo.objects.filter(project=self.object).count() == 0:
            return context
        else:
            if Todo.objects.filter(project=self.object).filter(state=True).count() * 100 / Todo.objects.filter(
                    project=self.object).count() != 100:
                project.state = False
                project.save()
            else:
                project.state = True
                project.save()
        context['get_percentage_done'] = Todo.objects.filter(project=self.object).filter(
            state=True).count() * 100 / Todo.objects.filter(project=self.object).count()
        context['get_percentage_left'] = Todo.objects.filter(project=self.object).filter(
            state=False).count() * 100 / Todo.objects.filter(project=self.object).count()
        context['progress'] = sum_progress
        context['left_progress'] = 100 - sum_progress
        context['total_capex'] = sum_budgets_capex
        context['total_opex'] = sum_budgets_opex
        context['todo_done'] = Todo.objects.filter(project=self.object).filter(state=True).count()
        context['todo_total'] = Todo.objects.filter(project=self.object).all().count()

        return context

def update_mark_todo(request, id):
    # return HttpResponse(request.POST.items())
    # todo = get_object_or_404(Todo, id=id)
    context = {}
    form = RisknoteForm(request.POST or None)
    if form.is_valid():
        form.save()

    context['form'] = form

    return redirect(request.META.get('HTTP_REFERER', 'redirect_if_referer_not_found'))

def add_note_in_project(request, id):
    context = {}
    form = NoteForm(request.POST or None)
    if form.is_valid():
        form.save()

    context['form'] = form

    return redirect(request.META.get('HTTP_REFERER', 'redirect_if_referer_not_found'))

def noteDelete(request, id):
    note = get_object_or_404(Note, id=id)
    note.delete()
    return redirect(request.META.get('HTTP_REFERER', 'redirect_if_referer_not_found'))

def add_budget_in_project(request, id):
    context = {}
    form = BudgetForm(request.POST or None)
    if form.is_valid():
        form.save()

    context['form'] = form

    return redirect(request.META.get('HTTP_REFERER', 'redirect_if_referer_not_found'))

def todofinished(request, id):
    todo = get_object_or_404(Todo, id=id)

    todo.state = True
    todo.done_date = datetime.date.today()
    todo.save()

    project = todo.project
    all_todo = project.todo_set.all()
    done_todo = all_todo.filter(state=True).count() * 100 / all_todo.count()
    if done_todo == 100:
        project.state = True
        project.done_date = datetime.date.today()
        project.save()
        messages.add_message(request, messages.INFO,
                             'Excelente, has finalizado este proyecto ')
    else:
        project.state = False
        project.save()
    # print(done_todo)

    return redirect(request.META.get('HTTP_REFERER', 'redirect_if_referer_not_found'))

def milestonefinished(request, id):
    milestone = get_object_or_404(Milestone, id=id)

    milestone.state = True
    milestone.done_date = datetime.date.today()
    milestone.save()

    return redirect(request.META.get('HTTP_REFERER', 'redirect_if_referer_not_found'))

def activate_milestone(request, id):
    project = get_object_or_404(Project, id=id)

    project.display_milestone = True
    project.save()

    return redirect(request.META.get('HTTP_REFERER', 'redirect_if_referer_not_found'))

def deactivate_milestone(request, id):
    project = get_object_or_404(Project, id=id)

    project.display_milestone = False
    project.save()

    return redirect(request.META.get('HTTP_REFERER', 'redirect_if_referer_not_found'))

class projectCreate(CreateView):
    model = Project
    template_name = 'project_create.html'
    form_class = ProjectForm

    def get_success_url(self):
        return reverse_lazy('project:projectdetail', kwargs={'slug': self.object.slug})

class TodoProjectCreate(CreateView):
    model = Todo
    template_name = 'todo_project_create.html'
    form_class = TodoForm
