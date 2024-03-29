# Generated by Django 4.0.4 on 2022-07-04 09:24

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('challenges', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='categorychallenge',
            name='category',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='challenges.category'),
        ),
        migrations.AlterField(
            model_name='categorychallenge',
            name='challenge',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='challenges.challenge'),
        ),
    ]
