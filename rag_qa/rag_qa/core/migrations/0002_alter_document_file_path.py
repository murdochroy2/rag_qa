# Generated by Django 5.0.10 on 2024-12-28 13:08

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='document',
            name='file_path',
            field=models.CharField(max_length=1024),
        ),
    ]
