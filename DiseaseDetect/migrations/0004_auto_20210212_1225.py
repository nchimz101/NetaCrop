# Generated by Django 3.1.5 on 2021-02-12 06:55

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('DiseaseDetect', '0003_auto_20210211_1416'),
    ]

    operations = [
        migrations.CreateModel(
            name='DiseaseDetect',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('ImageName', models.TextField(max_length=300)),
                ('DiseaseName', models.TextField(max_length=300)),
            ],
        ),
        migrations.DeleteModel(
            name='Disease',
        ),
    ]
