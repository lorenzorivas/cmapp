from django.urls import path, include
from django.conf.urls import url
from . import views
from .views import *

app_name = 'project'
urlpatterns = [
	path('', projects.as_view(), name = 'projects'),
	path('project/<slug:slug>', projectdetail.as_view(), name = 'projectdetail'),
	path('todomark/<int:id>/update_mark_todo', views.update_mark_todo, name = 'update_mark_todo'),
	path('note/<int:id>/add_note_in_project', views.add_note_in_project, name = 'add_note_in_project'),
	path('delete/<int:id>/note', views.noteDelete, name='noteDelete'),
	path('budget/<int:id>/add_budget_in_project', views.add_budget_in_project, name = 'add_budget_in_project'),
	path('todo/<int:id>/todofinished', views.todofinished, name = 'todofinished'),
	path('milestone/<int:id>/milestonefinished', views.milestonefinished, name = 'milestonefinished'),
	path('add/project', projectCreate.as_view(), name = 'projectCreate'),
	path('add/notestoproject', TodoProjectCreate.as_view(), name = 'TodoProjectCreate'),
	path('activate_milestone/<int:id>/project', views.activate_milestone, name = 'activate_milestone'),
	path('deactivate_milestone/<int:id>/project', views.deactivate_milestone, name = 'deactivate_milestone'),
]
