# Generated by Django 5.0.10 on 2024-12-30 07:27

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0006_question'),
    ]

    operations = [
        migrations.AddField(
            model_name='question',
            name='status',
            field=models.CharField(choices=[('in_progress', 'in_progress'), ('sucess', 'success'), ('failed', 'failed')], default='success', max_length=20),
            preserve_default=False,
        ),
    ]
