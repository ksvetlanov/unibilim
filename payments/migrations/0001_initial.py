# Generated by Django 4.2.2 on 2023-06-27 03:44

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('professors', '0002_alter_professors_user_timetable'),
    ]

    operations = [
        migrations.CreateModel(
            name='Payments',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('amount', models.DecimalField(decimal_places=2, max_digits=10)),
                ('datetime', models.DateTimeField(auto_now_add=True)),
                ('description', models.TextField()),
                ('service', models.CharField(max_length=255)),
                ('status', models.CharField(choices=[('PENDING', 'Pending'), ('COMPLETED', 'Completed'), ('DECLINED', 'Declined')], default='PENDING', max_length=10)),
                ('professor', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='professor_payments', to='professors.professors')),
            ],
        ),
    ]
