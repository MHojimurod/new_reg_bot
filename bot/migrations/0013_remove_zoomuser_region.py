
# Generated by Django 4.0.5 on 2022-06-21 08:05

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('bot', '0012_zoomuser_chat_id'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='zoomuser',
            name='region',
        ),
    ]
