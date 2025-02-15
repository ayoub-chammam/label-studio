# Generated by Django 3.2.13 on 2022-08-30 09:58

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('tasks', '0025_auto_20220711_1236'),
        ('projects', '0018_alter_project_control_weights'),
        ('weak_supervision', '0014_delete_gazetteerslf'),
    ]

    operations = [
        migrations.CreateModel(
            name='SpacyModel',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(help_text='name of the ner model', max_length=60, unique=True)),
                ('path', models.CharField(help_text='name of the ner model', max_length=60)),
                ('labels', models.JSONField(default=None, verbose_name='list of labels')),
                ('created_at', models.DateTimeField(auto_now_add=True, help_text='Time an aggreagation model was created', verbose_name='created at')),
                ('updated_at', models.DateTimeField(auto_now=True, help_text='Last time an aggreagation model was updated', verbose_name='updated at')),
                ('project', models.ForeignKey(help_text='Project ID', null=True, on_delete=django.db.models.deletion.CASCADE, to='projects.project')),
            ],
        ),
        migrations.CreateModel(
            name='SpacyModelResult',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('result', models.TextField(null=True)),
                ('model_version', models.TextField(null=True, verbose_name='model_version')),
                ('created_at', models.DateTimeField(auto_now_add=True, help_text='Time a model annotation is created', verbose_name='created at')),
                ('updated_at', models.DateTimeField(auto_now=True, help_text='Last time a model annotation was updated', verbose_name='updated at')),
                ('model', models.ForeignKey(help_text='labelling function ID', on_delete=django.db.models.deletion.CASCADE, to='weak_supervision.spacymodel')),
                ('project', models.ForeignKey(help_text='Project ID', null=True, on_delete=django.db.models.deletion.CASCADE, to='projects.project')),
                ('task', models.ForeignKey(help_text='Task ID', null=True, on_delete=django.db.models.deletion.CASCADE, to='tasks.task')),
            ],
        ),
    ]
