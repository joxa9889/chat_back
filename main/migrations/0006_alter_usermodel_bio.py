# Generated by Django 5.0.2 on 2024-04-25 12:53

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0005_alter_usermodel_last_active'),
    ]

    operations = [
        migrations.AlterField(
            model_name='usermodel',
            name='bio',
            field=models.CharField(blank=True, max_length=70, null=True),
        ),
    ]
