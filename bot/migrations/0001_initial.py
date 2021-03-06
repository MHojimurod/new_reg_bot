# Generated by Django 4.0.3 on 2022-03-03 08:32

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Region',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=255)),
            ],
        ),
        migrations.CreateModel(
            name='User',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('chat_id', models.IntegerField()),
                ('name', models.CharField(max_length=255)),
                ('number', models.CharField(max_length=255)),
                ('birthday', models.IntegerField()),
                ('region', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='bot.region')),
            ],
        ),
        migrations.CreateModel(
            name='Task',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('number', models.IntegerField(default=0)),
                ('document', models.FileField(upload_to='')),
                ('user', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='bot.user')),
            ],
        ),
    ]
