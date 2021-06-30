# Generated by Django 3.2.4 on 2021-06-17 00:11

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('cmapp', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='historicalproject',
            name='display_milestone',
            field=models.BooleanField(blank=True, default=False, null=True, verbose_name='Mostrar Hitos en Template'),
        ),
        migrations.AddField(
            model_name='project',
            name='display_milestone',
            field=models.BooleanField(blank=True, default=False, null=True, verbose_name='Mostrar Hitos en Template'),
        ),
        migrations.AlterField(
            model_name='collaborator',
            name='user',
            field=models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL, verbose_name='Nombre'),
        ),
    ]