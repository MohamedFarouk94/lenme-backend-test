# Generated by Django 4.2.4 on 2023-08-26 09:27

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('database', '0002_remove_person_account_created_remove_person_address_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='person',
            name='id',
            field=models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID'),
        ),
    ]
