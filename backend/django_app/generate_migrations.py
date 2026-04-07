"""
Run this script to generate all migrations from scratch.
Usage: python generate_migrations.py
Or manually run: python manage.py makemigrations for each app
"""
import subprocess
import sys

apps = ['users', 'courses', 'enrollments', 'quizzes', 'certificates', 'payments']

print("Generating migrations for all apps...")
for app in apps:
    result = subprocess.run(
        [sys.executable, 'manage.py', 'makemigrations', app],
        capture_output=True, text=True
    )
    print(f"  {app}: {result.stdout.strip() or result.stderr.strip()}")

print("\nRunning migrations...")
result = subprocess.run(
    [sys.executable, 'manage.py', 'migrate'],
    capture_output=True, text=True
)
print(result.stdout)
if result.returncode == 0:
    print("✅ All migrations complete!")
else:
    print("❌ Migration error:", result.stderr)
