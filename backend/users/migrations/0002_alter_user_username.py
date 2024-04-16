# Generated by Django 3.2.16 on 2024-04-16 04:54

import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='user',
            name='username',
            field=models.CharField(max_length=150, unique=True, validators=[django.core.validators.RegexValidator(code='invalid_username', message='Имя пользователя не может быть "me"', regex='^(?!me$)[a-zA-Z0-9]+$')], verbose_name='Имя пользователя'),
        ),
    ]
