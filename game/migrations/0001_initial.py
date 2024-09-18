import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('users', '0001_initial'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Game',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('status', models.CharField(choices=[('ongoing', 'Ongoing'), ('completed', 'Completed'), ('draw', 'Draw')], default='ongoing', max_length=10)),
                ('turn', models.CharField(choices=[('red', 'Red'), ('black', 'Black')], max_length=10)),
                ('fen', models.CharField(max_length=500)),
                ('initial_fen', models.CharField(max_length=500)),
                ('moves', models.JSONField(blank=True, default=list)),
                ('started_at', models.DateTimeField(auto_now_add=True)),
                ('last_updated', models.DateTimeField(auto_now=True)),
                ('red_time_remaining', models.IntegerField(default=300)),
                ('black_time_remaining', models.IntegerField(default=300)),
                ('black_player', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='black_player', to='users.player')),
                ('red_player', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='red_player', to='users.player')),
                ('viewers', models.ManyToManyField(blank=True, related_name='viewers', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'indexes': [models.Index(fields=['red_player'], name='game_game_red_pla_889b7f_idx'), models.Index(fields=['black_player'], name='game_game_black_p_df3708_idx')],
            },
        ),
    ]
