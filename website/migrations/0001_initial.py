# Generated by Django 5.1.4 on 2025-01-10 07:30

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='SMSMessage',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('to', models.CharField(max_length=255)),
                ('from_number', models.CharField(max_length=255)),
                ('message', models.TextField()),
                ('scheduled_date', models.DateTimeField(blank=True, null=True)),
                ('repeat', models.CharField(choices=[('none', 'None'), ('daily', 'Daily'), ('weekly', 'Weekly')], default='none', max_length=50)),
                ('sent', models.BooleanField(default=False)),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]