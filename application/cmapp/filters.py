from .models import Project, Area, Collaborator
from django.contrib.auth.models import User
from django import forms
import django_filters


class ProjectFilter(django_filters.FilterSet):
    project_title = django_filters.CharFilter(lookup_expr='icontains')
    area = django_filters.ModelMultipleChoiceFilter(queryset=Area.objects.all())
    collaborator = django_filters.ModelChoiceFilter(queryset=Collaborator.objects.all())
    state = django_filters.BooleanFilter()
    class Meta:
        model = Project
        fields = ['project_title', 'category', 'area', 'state', 'collaborator']
