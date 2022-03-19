# Generated by Django 4.0.3 on 2022-03-04 05:44

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('bot', '0006_task_accepted'),
    ]

    operations = [
        migrations.AlterField(
            model_name='task',
            name='accepted',
            field=models.IntegerField(choices=[(0, 'Waiting'), (1, 'Accepted'), (2, 'Rejected')]),
        ),
    ]