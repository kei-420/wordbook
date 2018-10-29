# Generated by Django 2.1.1 on 2018-10-29 00:50

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('wordbook', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='RepeatedGame',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('trials', models.PositiveIntegerField(default=0)),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='wordbook.Wordbook')),
            ],
            options={
                'db_table': 'repeated_game',
            },
        ),
    ]