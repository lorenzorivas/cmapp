from django.db import models
from autoslug import AutoSlugField
from tinymce.models import HTMLField
from simple_history.models import HistoricalRecords
from django_countries.fields import CountryField
from multiselectfield import MultiSelectField
from django.contrib.auth.models import User
from djmoney.models.fields import MoneyField

class Area(models.Model):
    area_title = models.CharField(max_length=255, verbose_name='Area')
    responsable = models.CharField(max_length=255, verbose_name='Lider Area')

    def __str__(self):
        return self.area_title

    class Meta:
        verbose_name = 'Area'
        verbose_name_plural = 'Areas'
        ordering = ['-id']

class Collaborator(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, verbose_name='Nombre')
    country = CountryField(blank_label='(seleccionar país)', verbose_name='País')
    area = models.ForeignKey(Area, on_delete=models.CASCADE, null=True, blank=True)

    def __str__(self):
        return "%s %s" % ( self.user.first_name, self.user.last_name )

    class Meta:
        verbose_name = 'Colaborador'
        verbose_name_plural = 'Colaboradores'
        ordering = ['-id']

class Category(models.Model):
    title = models.CharField(max_length=255)
    slug = AutoSlugField(populate_from='title', always_update=True)

    def __str__(self):
        return self.title

    class Meta:
        verbose_name = 'Categoria'
        ordering = ['-id']

class Project(models.Model):
    project_title = models.CharField(max_length=200, unique=True, verbose_name='Titulo')
    slug = AutoSlugField(populate_from='project_title', always_update=True, null=True)
    year = models.IntegerField(null=True)
    area = models.ManyToManyField(Area, verbose_name='Area')
    collaborator = models.ManyToManyField(Collaborator, related_name='Colaborador', verbose_name='Colaboradores')
    category = models.ManyToManyField(Category, related_name='Categoria', verbose_name='Categorías')
    # tags = TaggableManager()
    resume = HTMLField()
    pub_date = models.DateTimeField(auto_now_add=True)
    planned_date = models.DateField(null=True, verbose_name='Fecha Planificada')
    done_date = models.DateField(null=True, verbose_name='Fecha de termino Real', blank=True)
    state = models.BooleanField(blank=True, null=True, default=False, verbose_name='Terminando?')
    display_milestone = models.BooleanField(blank=True, null=True, default=False, verbose_name='Mostrar Hitos en Template')
    history = HistoricalRecords()

    def __str__(self):
        return self.project_title

    class Meta:
        verbose_name = 'Proyecto'
        ordering = ['-id']

class Budget(models.Model):
    project = models.ForeignKey(Project, on_delete=models.CASCADE, null=True, blank=True)
    budget_title = models.CharField(max_length=200, unique=True, verbose_name='Titulo')
    budget_owner = models.ForeignKey(Collaborator, on_delete=models.CASCADE, null=True, blank=True, verbose_name='OT Manager')
    area = models.ForeignKey(Area, on_delete=models.CASCADE, null=True, blank=True, verbose_name='Area')
    pub_date = models.DateTimeField(auto_now_add=True)
    money = MoneyField(max_digits=10, decimal_places=2, null=True, default_currency=None)

    CAPEX = 'Capex'
    OPEX = 'Opex'
    TYPE_CHOICES = [
        (CAPEX, 'Capex'),
        (OPEX, 'Opex'),
    ]
    type = models.CharField(
        max_length=5,
        choices=TYPE_CHOICES,
        default=CAPEX,
    )

    def __str__(self):
        return self.budget_title

    class Meta:
        verbose_name = 'Presupuesto'
        ordering = ['budget_title']

class Todo(models.Model):
    project = models.ForeignKey(Project, on_delete=models.CASCADE, null=True, blank=True)
    todo_title = models.CharField(max_length=200, verbose_name='Titulo')
    slug = AutoSlugField(populate_from='todo_title', always_update=True, null=True)
    pub_date = models.DateTimeField(auto_now_add=True)
    deadline_date = models.DateField(null=True, verbose_name='Fecha planificación')
    collaborator = models.ForeignKey(Collaborator, on_delete=models.CASCADE, verbose_name='Encargado',null=True, blank=True)
    done_date = models.DateField(null=True, verbose_name='Fecha termino', blank=True)
    state = models.BooleanField(blank=True, null=True, default=False, verbose_name='Terminado')
    progress = models.IntegerField(blank=True, null=True, default=0)
    ordering_position = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)

    def __str__(self):
        return self.todo_title

    class Meta:
        verbose_name = 'Tareas de Proyecto'
        ordering = ['ordering_position']

    def diff_days(self):
        delta = self.deadline_date - self.done_date
        # print(delta.days)
        return delta.days > -5

class Milestone(models.Model):
    project = models.ForeignKey(Project, on_delete=models.CASCADE, null=True, blank=True)
    milestone_title = models.CharField(max_length=200, verbose_name='Titulo')
    slug = AutoSlugField(populate_from='milestone_title', always_update=True, null=True)
    pub_date = models.DateTimeField(auto_now_add=True)
    deadline_date = models.DateField(null=True, blank=True, verbose_name='Fecha planificación')
    collaborator = models.ForeignKey(Collaborator, on_delete=models.CASCADE, verbose_name='Encargado',null=True, blank=True)
    done_date = models.DateField(null=True, verbose_name='Fecha termino', blank=True)
    state = models.BooleanField(blank=True, null=True, default=False, verbose_name='Terminado')
    progress = models.IntegerField(blank=True, null=True, default=0)
    ordering_position = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)

    def __str__(self):
        return self.milestone_title

    class Meta:
        verbose_name = 'Hitos de Proyecto'
        ordering = ['ordering_position']

class Risknote(models.Model):
    todo = models.ForeignKey(Todo, on_delete=models.CASCADE, null=True, blank=True)
    info = models.TextField(blank=True, null=True, verbose_name = 'Información')
    slug = AutoSlugField(populate_from='info', always_update=True, null=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True, verbose_name = 'Asignado a')
    pub_date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.info

    class Meta:
        verbose_name = 'Riesgos|Condiciones'
        ordering = ['id']

class Note(models.Model):
    project = models.ForeignKey(Project, on_delete=models.CASCADE)
    note_title = models.CharField(max_length=200)
    slug = AutoSlugField(populate_from='note_title', always_update=True)
    body = HTMLField()
    pub_date = models.DateTimeField(auto_now_add=True, null=True)

    def __str__(self):
        return self.note_title

    class Meta:
        verbose_name = 'Nota'
        ordering = ['-id']

class File(models.Model):
    project = models.ForeignKey(Project, on_delete=models.CASCADE, null=True)
    repository = models.URLField(max_length=1000, null=True, blank=True)
    project_slug = AutoSlugField(populate_from='project', always_update=True, null=True)
    pub_date = models.DateTimeField(auto_now_add=True)

    def directory_path(instance, filename):
        return 'files_project/project_{0}/{1}'.format(instance.project_slug, filename)

    upload = models.FileField(upload_to=directory_path, null=True)

    def __str__(self):
        return self.repository

    class Meta:
        verbose_name = 'Repositorio documentos'
        ordering = ['id']
