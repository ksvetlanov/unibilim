# Generated by Django 4.2.2 on 2023-06-27 04:10

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('students', '0001_initial'),
        ('meetings', '0003_alter_meetings_duration'),
    ]

    operations = [
        migrations.AddField(
            model_name='meetings',
            name='student',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='student_meetings', to='students.student'),
        ),
    ]
