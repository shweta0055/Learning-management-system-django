from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('users', '0001_initial'),
        ('courses', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Quiz',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=255)),
                ('description', models.TextField(blank=True)),
                ('time_limit', models.IntegerField(default=0)),
                ('passing_score', models.IntegerField(default=70)),
                ('max_attempts', models.IntegerField(default=3)),
                ('shuffle_questions', models.BooleanField(default=False)),
                ('show_answers_after', models.BooleanField(default=True)),
                ('is_active', models.BooleanField(default=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('course', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='quizzes', to='courses.course')),
                ('lesson', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='quizzes', to='courses.lesson')),
            ],
            options={
                'verbose_name_plural': 'quizzes',
                'db_table': 'quizzes',
                'ordering': ['created_at'],
            },
        ),
        migrations.CreateModel(
            name='Question',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('text', models.TextField()),
                ('question_type', models.CharField(choices=[('multiple_choice', 'Multiple Choice'), ('true_false', 'True/False'), ('short_answer', 'Short Answer')], default='multiple_choice', max_length=20)),
                ('points', models.IntegerField(default=1)),
                ('explanation', models.TextField(blank=True)),
                ('order', models.IntegerField(default=0)),
                ('quiz', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='questions', to='quizzes.quiz')),
            ],
            options={
                'db_table': 'questions',
                'ordering': ['order'],
            },
        ),
        migrations.CreateModel(
            name='Answer',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('text', models.TextField()),
                ('is_correct', models.BooleanField(default=False)),
                ('order', models.IntegerField(default=0)),
                ('question', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='answers', to='quizzes.question')),
            ],
            options={
                'db_table': 'answers',
                'ordering': ['order'],
            },
        ),
        migrations.CreateModel(
            name='QuizAttempt',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('status', models.CharField(choices=[('in_progress', 'In Progress'), ('completed', 'Completed'), ('timed_out', 'Timed Out')], default='in_progress', max_length=20)),
                ('score', models.FloatField(default=0.0)),
                ('total_points', models.IntegerField(default=0)),
                ('earned_points', models.IntegerField(default=0)),
                ('passed', models.BooleanField(default=False)),
                ('started_at', models.DateTimeField(auto_now_add=True)),
                ('completed_at', models.DateTimeField(blank=True, null=True)),
                ('time_taken', models.IntegerField(default=0)),
                ('quiz', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='attempts', to='quizzes.quiz')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='quiz_attempts', to='users.user')),
            ],
            options={
                'db_table': 'quiz_attempts',
                'ordering': ['-started_at'],
            },
        ),
        migrations.CreateModel(
            name='QuizResponse',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('text_response', models.TextField(blank=True)),
                ('is_correct', models.BooleanField(default=False)),
                ('points_earned', models.IntegerField(default=0)),
                ('attempt', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='responses', to='quizzes.quizattempt')),
                ('question', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='quizzes.question')),
                ('selected_answer', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='quizzes.answer')),
            ],
            options={
                'db_table': 'quiz_responses',
                'unique_together': {('attempt', 'question')},
            },
        ),
        migrations.CreateModel(
            name='Assignment',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=255)),
                ('description', models.TextField()),
                ('instructions', models.TextField()),
                ('due_date', models.DateTimeField(blank=True, null=True)),
                ('total_points', models.IntegerField(default=100)),
                ('passing_score', models.IntegerField(default=60)),
                ('attachment', models.FileField(blank=True, null=True, upload_to='assignment_attachments/')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('course', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='assignments', to='courses.course')),
            ],
            options={
                'db_table': 'assignments',
                'ordering': ['due_date'],
            },
        ),
        migrations.CreateModel(
            name='AssignmentSubmission',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('content', models.TextField()),
                ('attachment', models.FileField(blank=True, null=True, upload_to='submission_attachments/')),
                ('status', models.CharField(choices=[('submitted', 'Submitted'), ('graded', 'Graded'), ('returned', 'Returned')], default='submitted', max_length=20)),
                ('score', models.IntegerField(blank=True, null=True)),
                ('feedback', models.TextField(blank=True)),
                ('submitted_at', models.DateTimeField(auto_now_add=True)),
                ('graded_at', models.DateTimeField(blank=True, null=True)),
                ('assignment', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='submissions', to='quizzes.assignment')),
                ('graded_by', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='graded_submissions', to='users.user')),
                ('student', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='submissions', to='users.user')),
            ],
            options={
                'db_table': 'assignment_submissions',
                'ordering': ['-submitted_at'],
                'unique_together': {('assignment', 'student')},
            },
        ),
    ]
