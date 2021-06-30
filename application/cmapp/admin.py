from django.contrib import admin
from .models import (Area, Collaborator, Project, Category, Todo, Risknote, Note, File, Budget, Milestone)
from django.db import models
from django.forms import TextInput, Textarea
from .forms import ProjectForm, TodoForm, BudgetForm
from django.contrib.admin.models import LogEntry, DELETION
from django.urls import reverse
from django.utils.html import escape
from django.utils.safestring import mark_safe


admin.site.site_header = "CUADRO DE MANDO HISPAM"
admin.site.site_title = "CUADRO DE MANDO HISPAM"

class LogEntryAdmin(admin.ModelAdmin):
    date_hierarchy = 'action_time'
    list_per_page = 20
    list_filter = [
        'user',
        'content_type',
        'action_flag'
    ]

    search_fields = [
        'object_repr',
        'change_message'
    ]

    list_display = [
        'user',
        'object_link',
        'content_type',
        'action_flag_',
        'action_time',
        'id',
    ]

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return request.user.is_superuser and request.method != 'POST'

    def has_delete_permission(self, request, obj=None):
        return False

    def action_flag_(self, obj):
        flags = {
            1: "Addition",
            2: "Changed",
            3: "Deleted",
        }
        return flags[obj.action_flag]

    def object_link(self, obj):
        if obj.action_flag == DELETION:
            link = escape(obj.object_repr)
        else:
            ct = obj.content_type
            link = u'<a href="%s">%s</a>' % (
                reverse('admin:%s_%s_change' % (ct.app_label, ct.model), args=[obj.object_id]),
                escape(obj.object_repr),
            )
        return mark_safe(link)

    object_link.allow_tags = True
    object_link.admin_order_field = 'object_repr'
    object_link.short_description = u'object'


admin.site.register(LogEntry, LogEntryAdmin)

class CollaboratorInline(admin.TabularInline):
    model = Collaborator
    extra = 0

class AreaAdmin(admin.ModelAdmin):
    def collaborator_count(self, obj):
        return obj.collaborator_set.count()

    collaborator_count.short_description = 'Colaboradores'

    list_display = ['area_title', 'responsable', 'collaborator_count']
    inlines = [CollaboratorInline]

admin.site.register(Area, AreaAdmin)

class CollaboratorAdmin(admin.ModelAdmin):
    list_display = ['user', 'country', 'area', 'get_responsable']
    list_filter = ['area__responsable', 'area__area_title']

    def get_responsable(self, obj):
        return obj.area.responsable
    get_responsable.short_description = 'Lider'
    get_responsable.admin_order_field = 'area__responsable'

admin.site.register(Collaborator, CollaboratorAdmin)

class CategoryAdmin(admin.ModelAdmin):
    search_fields = ['title']
    list_per_page = 10

admin.site.register(Category, CategoryAdmin)

class TodoInline(admin.TabularInline):
    model = Todo
    extra = 10
    form = TodoForm
    classes = ['collapse']
    fields = ('line_number', 'todo_title', 'deadline_date', 'collaborator', 'done_date', 'state', 'ordering_position')
    readonly_fields = ('line_number',)
    ordering = ('ordering_position', )

    line_numbering = 0
    def line_number(self, obj):
        self.line_numbering += 1
        return self.line_numbering

    line_number.short_description = '#'

from django import forms

class MilestoneInline(admin.TabularInline):
    model = Milestone
    extra = 10
    max_num = 10
    classes = ['collapse']
    fields = ('line_number', 'milestone_title', 'deadline_date', 'collaborator', 'done_date', 'state', 'ordering_position')
    readonly_fields = ('line_number',)
    ordering = ('ordering_position', )

    initial = [
        {'milestone_title': 'Aprobación de recursos CAR/PAC'},
        {'milestone_title': 'Cesta en Compra'},
        {'milestone_title': 'Adjudicación '},
        {'milestone_title': 'Adecuación de emplazamiento (Espacio, Energía, Clima)'},
        {'milestone_title': 'Infraestructura de Computo (TC)'},
        {'milestone_title': 'Delivery local'},
        {'milestone_title': 'Integraciones con otras redes '},
        {'milestone_title': 'Pruebas funcionales'},
        {'milestone_title': 'Puesta en Servicio'},
        {'milestone_title': 'Certificación (Acta de aceptación/ Generación de HEM)'},
    ]

    create_from_default = True

    def get_formset(self, request, obj=None, **kwargs):
        initial = self.initial[:]

        class _Form(forms.ModelForm):
            form_initial = initial

            def __init__(self, *args, **kwargs):
                if len(self.form_initial) and not 'instance' in kwargs:
                    kwargs['initial'] = self.form_initial.pop(0)
                return super(_Form, self).__init__(*args, **kwargs)

        if self.create_from_default:
            if request.method == 'GET':
                self.form = _Form
            else:
                self.form = forms.ModelForm
        else:
            self.form = _Form

        return super(MilestoneInline, self).get_formset(request, obj, **kwargs)

    line_numbering = 0
    def line_number(self, obj):
        self.line_numbering += 1
        return self.line_numbering

    line_number.short_description = '#'

class MilestoneAdmin(admin.ModelAdmin):
    search_fields = ['ilestone_title']
    list_display = ['project', 'milestone_title', 'deadline_date', 'collaborator', 'state']

admin.site.register(Milestone, MilestoneAdmin)

class NoteInline(admin.StackedInline):
    model = Note
    extra = 0
    fields = ('note_title', 'body')
    readonly_fields = ('line_number',)
    classes = ['collapse']

    line_numbering = 0
    def line_number(self, obj):
        self.line_numbering += 1
        return self.line_numbering

    line_number.short_description = '#'

class FileInline(admin.TabularInline):
    model = File
    extra = 1
    max_num = 1
    exclude = ('upload',)
    classes = ['collapse']

class BudgetInline(admin.TabularInline):
    model = Budget
    extra = 0
    classes = ['collapse']

class BudgetAdmin(admin.ModelAdmin):
    search_fields = ["budget_title"]
    list_display = ['project', 'budget_title', 'type', 'area', 'budget_owner', 'money']
    list_editable = ('type', 'money', )

admin.site.register(Budget, BudgetAdmin)

class ProjectAdmin(admin.ModelAdmin):
    # form = ProjectForm
    filter_horizontal = ('area', 'collaborator',)
    autocomplete_fields = ['category', ]
    list_per_page = 10
    inlines = [FileInline, BudgetInline, TodoInline, MilestoneInline, NoteInline, ]
    formfield_overrides = {
        models.CharField: {'widget': TextInput(attrs={'size': '100%'})},
    }

class NoteAdmin(admin.ModelAdmin):
    exclude = ('project', )

admin.site.register(Note, NoteAdmin)

admin.site.register(Project, ProjectAdmin)

admin.site.register(Todo)

class RisknoteAdmin(admin.ModelAdmin):
    exclude = ('todo', )

admin.site.register(Risknote, RisknoteAdmin)
