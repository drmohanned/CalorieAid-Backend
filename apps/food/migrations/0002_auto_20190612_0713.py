# Generated by Django 2.1.7 on 2019-06-12 07:13

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('food', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='useringredient',
            name='user',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL),
        ),
        migrations.AlterUniqueTogether(
            name='ingredients',
            unique_together={('name',)},
        ),
        migrations.AlterUniqueTogether(
            name='useringredient',
            unique_together={('ingredient', 'user')},
        ),
    ]
