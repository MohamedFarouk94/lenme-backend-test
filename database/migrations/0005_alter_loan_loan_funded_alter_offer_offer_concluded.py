# Generated by Django 4.2.4 on 2023-08-25 13:59

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('database', '0004_alter_loan_annual_interest_alter_loan_investor'),
    ]

    operations = [
        migrations.AlterField(
            model_name='loan',
            name='loan_funded',
            field=models.DateTimeField(null=True),
        ),
        migrations.AlterField(
            model_name='offer',
            name='offer_concluded',
            field=models.DateTimeField(null=True),
        ),
    ]
