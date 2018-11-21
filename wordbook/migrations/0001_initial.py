# Generated by Django 2.1.3 on 2018-11-21 06:59

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('accounts', '0001_initial'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='CompletedQuiz',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('score', models.FloatField()),
                ('completed_at', models.DateTimeField(auto_now_add=True)),
            ],
        ),
        migrations.CreateModel(
            name='MultipleQuestions',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('is_correct', models.BooleanField(default=False, verbose_name='Correct Answer')),
            ],
        ),
        migrations.CreateModel(
            name='Question',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
            ],
        ),
        migrations.CreateModel(
            name='Quiz',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=255)),
            ],
        ),
        migrations.CreateModel(
            name='QuizTaker',
            fields=[
                ('user', models.OneToOneField(on_delete=django.db.models.deletion.PROTECT, primary_key=True, serialize=False, to=settings.AUTH_USER_MODEL)),
                ('quizzes', models.ManyToManyField(through='wordbook.CompletedQuiz', to='wordbook.Quiz')),
            ],
        ),
        migrations.CreateModel(
            name='QuizTakerAnswer',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('answer', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='+', to='wordbook.MultipleQuestions')),
                ('taker', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='quiz_answers', to='wordbook.QuizTaker')),
            ],
        ),
        migrations.CreateModel(
            name='Word',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('vocab', models.CharField(max_length=255)),
                ('vocab_class', models.CharField(max_length=20)),
                ('vocab_meaning', models.TextField()),
            ],
            options={
                'db_table': 'word',
            },
        ),
        migrations.CreateModel(
            name='Wordbook',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('adding_word', models.CharField(max_length=255)),
                ('understanding_level', models.PositiveIntegerField(blank=True, default=0)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to=settings.AUTH_USER_MODEL)),
                ('word', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='answers', to='wordbook.Word')),
            ],
            options={
                'db_table': 'wordbook',
            },
        ),
        migrations.AddField(
            model_name='quiz',
            name='taker',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='quizzes', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='question',
            name='game_word',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='wordbook.Word'),
        ),
        migrations.AddField(
            model_name='question',
            name='quiz',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='questions', to='wordbook.Quiz'),
        ),
        migrations.AddField(
            model_name='multiplequestions',
            name='choices',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='choices', to='wordbook.Word'),
        ),
        migrations.AddField(
            model_name='multiplequestions',
            name='question',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='answers', to='wordbook.Question'),
        ),
        migrations.AddField(
            model_name='completedquiz',
            name='quiz',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='completed_quizzes', to='wordbook.Quiz'),
        ),
        migrations.AddField(
            model_name='completedquiz',
            name='user',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='completed_quizzes', to='wordbook.QuizTaker'),
        ),
    ]
