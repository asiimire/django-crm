# Generated by Django 5.1.4 on 2025-01-12 10:20

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('website', '0004_template_smsmessage_phone_book_and_more'),
    ]

    operations = [
        migrations.CreateModel(
            name='Transaction',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('sms_count', models.IntegerField(blank=True, null=True)),
                ('amount', models.DecimalField(decimal_places=2, max_digits=10)),
                ('phone_number', models.CharField(max_length=15)),
                ('date', models.DateTimeField(auto_now_add=True)),
                ('status', models.CharField(default='Pending', max_length=20)),
            ],
        ),
    ]
