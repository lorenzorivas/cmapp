from django import forms
from .models import *
from datetime import datetime
from bootstrap_datepicker_plus import DatePickerInput

class ProjectForm(forms.ModelForm):
    class Meta:
        model = Project
        fields = ('project_title', 'year', 'area', 'collaborator', 'category', 'resume', 'planned_date')

    area = forms.ModelMultipleChoiceField(
        label = 'Areas involucradas',
        queryset=Area.objects.all(),
        widget=forms.CheckboxSelectMultiple
    )

    # state = forms.ChoiceField(
    #     label = 'Estado',
    #     choices = [('no_iniciado', 'No inciado'),
    #                   ('iniciado', 'Iniciado'),
    #                   ('retrasado', 'Retrasado'),
    #                   ('terminado', 'Terminado')],
    #     widget = forms.RadioSelect,
    # )

    def possible_years(first_year_in_scroll, last_year_in_scroll):
        p_year = []
        for i in range(first_year_in_scroll, last_year_in_scroll, -1):
            p_year_tuple = str(i), i
            p_year.append(p_year_tuple)
        return p_year

    year = forms.ChoiceField(
        choices=possible_years(((datetime.now()).year), 2010),
        label='Año proyecto',
    )

    # widgets = {
    #         'planned_date': DatePickerInput(),
    #     }

    planned_date = forms.DateField(
        widget=DatePickerInput(format='%d/%m/%Y')
    )

    # collaborator = forms.ModelMultipleChoiceField(
    #     label = 'Especialistas',
    #     queryset=Collaborator.objects.all(),
    #     widget=forms.CheckboxSelectMultiple
    # )

class TodoForm(forms.ModelForm):
    class Meta:
        model = Todo
        fields = '__all__'

    todo_title = forms.CharField(initial='Ingresa un titulo')

class RisknoteForm(forms.ModelForm):
    class Meta:
        model = Risknote
        fields = ['todo', 'user', 'info',]

class NoteForm(forms.ModelForm):
    class Meta:
        model = Note
        fields = ['project', 'note_title', 'body']


class BudgetForm(forms.ModelForm):
    class Meta:
        model = Budget
        fields = '__all__'
