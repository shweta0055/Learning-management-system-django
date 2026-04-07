import uuid
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
            name='Certificate',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('certificate_id', models.UUIDField(default=uuid.uuid4, editable=False, unique=True)),
                ('issued_at', models.DateTimeField(auto_now_add=True)),
                ('pdf_file', models.FileField(blank=True, null=True, upload_to='certificates/')),
                ('completion_percentage', models.FloatField(default=100.0)),
                ('course', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='certificates', to='courses.course')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='certificates', to='users.user')),
            ],
            options={
                'db_table': 'certificates',
                'ordering': ['-issued_at'],
                'unique_together': {('user', 'course')},
            },
        ),
    ]
