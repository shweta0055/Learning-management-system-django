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
            name='Payment',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('amount', models.DecimalField(decimal_places=2, max_digits=10)),
                ('currency', models.CharField(default='USD', max_length=10)),
                ('status', models.CharField(choices=[('pending', 'Pending'), ('completed', 'Completed'), ('failed', 'Failed'), ('refunded', 'Refunded')], default='pending', max_length=20)),
                ('gateway', models.CharField(choices=[('stripe', 'Stripe'), ('paypal', 'PayPal'), ('free', 'Free')], default='stripe', max_length=20)),
                ('gateway_payment_id', models.CharField(blank=True, max_length=255)),
                ('gateway_order_id', models.CharField(blank=True, max_length=255)),
                ('receipt_url', models.URLField(blank=True)),
                ('metadata', models.JSONField(default=dict)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('course', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='payments', to='courses.course')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='payments', to='users.user')),
            ],
            options={
                'db_table': 'payments',
                'ordering': ['-created_at'],
            },
        ),
        migrations.CreateModel(
            name='Coupon',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('code', models.CharField(max_length=50, unique=True)),
                ('discount_type', models.CharField(choices=[('percentage', 'Percentage'), ('fixed', 'Fixed Amount')], default='percentage', max_length=20)),
                ('discount_value', models.DecimalField(decimal_places=2, max_digits=10)),
                ('max_uses', models.IntegerField(default=100)),
                ('used_count', models.IntegerField(default=0)),
                ('valid_from', models.DateTimeField()),
                ('valid_to', models.DateTimeField()),
                ('is_active', models.BooleanField(default=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('applicable_courses', models.ManyToManyField(blank=True, to='courses.course')),
            ],
            options={
                'db_table': 'coupons',
            },
        ),
    ]
