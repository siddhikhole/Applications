# Generated by Django 2.1.5 on 2019-04-22 06:40

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('HelpDeskApp', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='helprequest',
            name='created_at',
            field=models.DateTimeField(default=None, null=True),
        ),
    ]
