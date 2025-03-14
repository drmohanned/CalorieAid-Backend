# Generated by Django 2.1.7 on 2019-06-12 07:13

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Ingredients',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('modified', models.DateTimeField(auto_now=True)),
                ('name', models.CharField(max_length=255)),
                ('protein', models.DecimalField(decimal_places=2, max_digits=14)),
                ('fat', models.DecimalField(decimal_places=2, max_digits=14)),
                ('carbohydrate', models.DecimalField(decimal_places=2, max_digits=14)),
                ('fiber', models.DecimalField(decimal_places=2, max_digits=14)),
                ('energy', models.DecimalField(blank=True, decimal_places=2, max_digits=14, null=True)),
                ('sugar', models.DecimalField(blank=True, decimal_places=2, max_digits=14, null=True)),
                ('source_type', models.SmallIntegerField(choices=[(0, 'None'), (1, 'Fat'), (2, 'Fiber'), (3, 'Carbohydrate'), (4, 'Protein')], default=0)),
                ('sub_source_type', models.SmallIntegerField(choices=[(0, 'None'), (1, 'Fat Protein'), (2, 'Carbohydrate Protein'), (3, 'Fat Fiber'), (4, 'Carbohydrate Fiber'), (5, 'Pure Fat'), (6, 'Pure Carbohydrate'), (7, 'Vegetable')], default=0)),
                ('status', models.SmallIntegerField(choices=[(0, 'Pending'), (1, 'Active'), (2, 'Rejected')], default=0)),
            ],
        ),
        migrations.CreateModel(
            name='UserIngredient',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('modified', models.DateTimeField(auto_now=True)),
                ('ingredient', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='food.Ingredients')),
            ],
        ),
    ]
