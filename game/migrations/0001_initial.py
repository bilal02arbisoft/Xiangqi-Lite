# Generated by Django 5.1 on 2024-09-02 09:47

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('users', '0005_remove_profile_rating'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Game',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('fen', models.CharField(max_length=500)),
                ('initial_fen', models.CharField(max_length=500)),
                ('moves', models.JSONField(blank=True, default=list)),
                ('turn', models.CharField(choices=[('red', 'Red'), ('black', 'Black')], max_length=10)),
                ('status', models.CharField(choices=[('ongoing', 'Ongoing'), ('completed', 'Completed'), ('draw', 'Draw'), ('abandoned', 'Abandoned')], default='ongoing', max_length=10)),
                ('started_at', models.DateTimeField(auto_now_add=True)),
                ('last_updated', models.DateTimeField(auto_now=True)),
                ('red_time_remaining', models.IntegerField(default=600)),
                ('black_time_remaining', models.IntegerField(default=600)),
                ('black_player', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='black_player', to='users.player')),
                ('red_player', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='red_player', to='users.player')),
                ('viewers', models.ManyToManyField(blank=True, related_name='viewers', to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]
