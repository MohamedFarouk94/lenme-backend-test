# Generated by Django 4.2.4 on 2023-08-25 11:38

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('database', '0002_alter_investor_birth_date'),
    ]

    operations = [
        migrations.AlterField(
            model_name='borrower',
            name='birth_date',
            field=models.DateField(null=True),
        ),
    ]
