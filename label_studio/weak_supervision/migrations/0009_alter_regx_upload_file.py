# Generated by Django 3.2.13 on 2022-08-27 16:01

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('weak_supervision', '0008_alter_regx_upload_file'),
    ]

    operations = [
        migrations.AlterField(
            model_name='regx',
            name='upload_file',
            field=models.FileField(upload_to=''),
        ),
    ]
