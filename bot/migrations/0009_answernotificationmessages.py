# Generated by Django 4.0.3 on 2022-03-04 06:23

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('bot', '0008_alter_task_accepted'),
    ]

    operations = [
        migrations.CreateModel(
            name='AnswerNotificationMessages',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('chat_id', models.IntegerField()),
                ('message_id', models.IntegerField()),
                ('task', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='bot.task')),
            ],
        ),
    ]