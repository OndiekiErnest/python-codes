# Generated by Django 4.1.7 on 2023-06-17 13:51

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('tools', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='uploads',
            name='description',
            field=models.CharField(max_length=255),
        ),
    ]
