# Generated by Django 3.2.6 on 2021-08-28 18:24

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0003_auto_20210828_1719'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='question',
            name='answers',
        ),
        migrations.AddField(
            model_name='answer',
            name='question',
            field=models.ForeignKey(default='', on_delete=django.db.models.deletion.CASCADE, to='core.question'),
            preserve_default=False,
        ),
    ]
