from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('users', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Category',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100, unique=True)),
                ('slug', models.SlugField(unique=True)),
                ('description', models.TextField(blank=True)),
                ('icon', models.CharField(blank=True, max_length=50)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('parent', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='children', to='courses.category')),
            ],
            options={
                'verbose_name_plural': 'categories',
                'db_table': 'categories',
                'ordering': ['name'],
            },
        ),
        migrations.CreateModel(
            name='Course',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=255)),
                ('slug', models.SlugField(unique=True)),
                ('description', models.TextField()),
                ('short_description', models.CharField(blank=True, max_length=500)),
                ('thumbnail', models.ImageField(blank=True, null=True, upload_to='course_thumbnails/')),
                ('preview_video', models.URLField(blank=True)),
                ('price', models.DecimalField(decimal_places=2, default=0.0, max_digits=10)),
                ('discount_price', models.DecimalField(blank=True, decimal_places=2, max_digits=10, null=True)),
                ('level', models.CharField(choices=[('beginner', 'Beginner'), ('intermediate', 'Intermediate'), ('advanced', 'Advanced')], default='beginner', max_length=20)),
                ('status', models.CharField(choices=[('draft', 'Draft'), ('published', 'Published'), ('archived', 'Archived')], default='draft', max_length=20)),
                ('language', models.CharField(default='English', max_length=50)),
                ('tags', models.JSONField(default=list)),
                ('requirements', models.JSONField(default=list)),
                ('objectives', models.JSONField(default=list)),
                ('duration_hours', models.FloatField(default=0.0)),
                ('total_lessons', models.IntegerField(default=0)),
                ('total_students', models.IntegerField(default=0)),
                ('rating', models.FloatField(default=0.0)),
                ('total_ratings', models.IntegerField(default=0)),
                ('is_free', models.BooleanField(default=False)),
                ('certificate_available', models.BooleanField(default=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('published_at', models.DateTimeField(blank=True, null=True)),
                ('category', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='courses', to='courses.category')),
                ('instructor', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='courses_taught', to='users.user')),
            ],
            options={
                'db_table': 'courses',
                'ordering': ['-created_at'],
            },
        ),
        migrations.CreateModel(
            name='Section',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=255)),
                ('description', models.TextField(blank=True)),
                ('order', models.IntegerField(default=0)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('course', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='sections', to='courses.course')),
            ],
            options={
                'db_table': 'sections',
                'ordering': ['order'],
            },
        ),
        migrations.CreateModel(
            name='Lesson',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=255)),
                ('description', models.TextField(blank=True)),
                ('content_type', models.CharField(choices=[('video', 'Video'), ('text', 'Text'), ('quiz', 'Quiz'), ('assignment', 'Assignment')], default='video', max_length=20)),
                ('video_url', models.URLField(blank=True)),
                ('video_duration', models.IntegerField(default=0)),
                ('content', models.TextField(blank=True)),
                ('resources', models.JSONField(default=list)),
                ('order', models.IntegerField(default=0)),
                ('is_free_preview', models.BooleanField(default=False)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('section', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='lessons', to='courses.section')),
            ],
            options={
                'db_table': 'lessons',
                'ordering': ['order'],
            },
        ),
        migrations.CreateModel(
            name='CourseReview',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('rating', models.IntegerField(choices=[(1, 1), (2, 2), (3, 3), (4, 4), (5, 5)])),
                ('comment', models.TextField()),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('course', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='reviews', to='courses.course')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='users.user')),
            ],
            options={
                'db_table': 'course_reviews',
                'ordering': ['-created_at'],
                'unique_together': {('course', 'user')},
            },
        ),
        migrations.CreateModel(
            name='Announcement',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=255)),
                ('content', models.TextField()),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('course', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='announcements', to='courses.course')),
            ],
            options={
                'db_table': 'announcements',
                'ordering': ['-created_at'],
            },
        ),
    ]
