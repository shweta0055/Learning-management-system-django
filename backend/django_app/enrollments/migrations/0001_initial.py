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
            name='Enrollment',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('status', models.CharField(choices=[('active', 'Active'), ('completed', 'Completed'), ('cancelled', 'Cancelled'), ('expired', 'Expired')], default='active', max_length=20)),
                ('progress', models.FloatField(default=0.0)),
                ('enrolled_at', models.DateTimeField(auto_now_add=True)),
                ('completed_at', models.DateTimeField(blank=True, null=True)),
                ('last_accessed', models.DateTimeField(auto_now=True)),
                ('expiry_date', models.DateTimeField(blank=True, null=True)),
                ('payment_id', models.CharField(blank=True, max_length=255)),
                ('amount_paid', models.DecimalField(decimal_places=2, default=0.0, max_digits=10)),
                ('course', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='enrollments', to='courses.course')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='enrollments', to='users.user')),
            ],
            options={
                'db_table': 'enrollments',
                'ordering': ['-enrolled_at'],
                'unique_together': {('user', 'course')},
            },
        ),
        migrations.CreateModel(
            name='LessonProgress',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('is_completed', models.BooleanField(default=False)),
                ('watch_time', models.IntegerField(default=0)),
                ('completed_at', models.DateTimeField(blank=True, null=True)),
                ('last_position', models.IntegerField(default=0)),
                ('notes', models.TextField(blank=True)),
                ('enrollment', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='lesson_progress', to='enrollments.enrollment')),
                ('lesson', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='courses.lesson')),
            ],
            options={
                'db_table': 'lesson_progress',
                'unique_together': {('enrollment', 'lesson')},
            },
        ),
        migrations.CreateModel(
            name='Wishlist',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('added_at', models.DateTimeField(auto_now_add=True)),
                ('course', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='courses.course')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='wishlist', to='users.user')),
            ],
            options={
                'db_table': 'wishlist',
                'ordering': ['-added_at'],
                'unique_together': {('user', 'course')},
            },
        ),
    ]
