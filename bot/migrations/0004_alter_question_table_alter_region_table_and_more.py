# Generated by Django 4.0.3 on 2022-03-03 13:40

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('bot', '0003_question'),
    ]

    operations = [
        migrations.AlterModelTable(
            name='question',
            table='Topshiriqlar',
        ),
        migrations.AlterModelTable(
            name='region',
            table='Viloyatlar',
        ),
        migrations.AlterModelTable(
            name='user',
            table='Foydalanuvchilar',
        ),
    ]
