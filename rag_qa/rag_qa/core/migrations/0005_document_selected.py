# Generated by Django 5.0.10 on 2024-12-29 12:51

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0004_document_indexed'),
    ]

    operations = [
        migrations.AddField(
            model_name='document',
            name='selected',
            field=models.BooleanField(default=False),
        ),
    ]