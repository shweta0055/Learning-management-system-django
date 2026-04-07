"""
Management command to seed the database with demo data.
Usage: python manage.py seed_data
"""
from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from django.utils.text import slugify
from django.utils import timezone
import random

User = get_user_model()


class Command(BaseCommand):
    help = 'Seed database with demo data for development'

    def add_arguments(self, parser):
        parser.add_argument('--clear', action='store_true', help='Clear existing data first')

    def handle(self, *args, **options):
        if options['clear']:
            self.stdout.write('Clearing existing data...')
            from courses.models import Course, Category
            from enrollments.models import Enrollment
            Course.objects.all().delete()
            Category.objects.all().delete()
            User.objects.filter(is_superuser=False).delete()

        self.stdout.write('Seeding database...')
        self._create_users()
        self._create_categories()
        self._create_courses()
        self._create_enrollments()
        self.stdout.write(self.style.SUCCESS('✅ Database seeded successfully!'))

    def _create_users(self):
        from users.models import InstructorProfile

        # Admin
        if not User.objects.filter(email='admin@learnhub.com').exists():
            admin = User.objects.create_superuser(
                username='admin',
                email='admin@learnhub.com',
                password='Admin123!',
                first_name='Admin',
                last_name='User',
                role='admin',
            )
            self.stdout.write(f'  Created admin: {admin.email}')

        # Instructors
        instructor_data = [
            ('john.smith', 'john@learnhub.com', 'John', 'Smith', ['Python', 'Django', 'REST APIs']),
            ('sarah.jones', 'sarah@learnhub.com', 'Sarah', 'Jones', ['React', 'JavaScript', 'TypeScript']),
            ('mike.chen', 'mike@learnhub.com', 'Mike', 'Chen', ['Data Science', 'ML', 'TensorFlow']),
            ('emily.davis', 'emily@learnhub.com', 'Emily', 'Davis', ['UI/UX', 'Figma', 'Design Systems']),
        ]
        self.instructors = []
        for username, email, first, last, expertise in instructor_data:
            if not User.objects.filter(email=email).exists():
                user = User.objects.create_user(
                    username=username, email=email, password='Test123!',
                    first_name=first, last_name=last, role='instructor',
                    bio=f'Expert {first} has 10+ years of experience in {expertise[0]}.',
                    is_verified=True,
                )
                InstructorProfile.objects.get_or_create(
                    user=user,
                    defaults={
                        'expertise': expertise,
                        'is_approved': True,
                        'rating': round(random.uniform(4.2, 4.9), 1),
                    }
                )
                self.instructors.append(user)
                self.stdout.write(f'  Created instructor: {email}')
            else:
                self.instructors.append(User.objects.get(email=email))

        # Students
        student_data = [
            ('alice.wonder', 'alice@example.com', 'Alice', 'Wonder'),
            ('bob.builder', 'bob@example.com', 'Bob', 'Builder'),
            ('carol.white', 'carol@example.com', 'Carol', 'White'),
            ('david.brown', 'david@example.com', 'David', 'Brown'),
            ('eva.green', 'eva@example.com', 'Eva', 'Green'),
        ]
        self.students = []
        for username, email, first, last in student_data:
            if not User.objects.filter(email=email).exists():
                user = User.objects.create_user(
                    username=username, email=email, password='Test123!',
                    first_name=first, last_name=last, role='student',
                    is_verified=True,
                )
                self.students.append(user)
                self.stdout.write(f'  Created student: {email}')
            else:
                self.students.append(User.objects.get(email=email))

    def _create_categories(self):
        from courses.models import Category
        cats = [
            ('Programming', 'programming', '💻'),
            ('Web Development', 'web-development', '🌐'),
            ('Data Science', 'data-science', '📊'),
            ('Design', 'design', '🎨'),
            ('Business', 'business', '💼'),
            ('Marketing', 'marketing', '📣'),
            ('DevOps', 'devops', '⚙️'),
            ('Mobile Development', 'mobile-development', '📱'),
        ]
        self.categories = {}
        for name, slug, icon in cats:
            cat, created = Category.objects.get_or_create(
                slug=slug, defaults={'name': name, 'icon': icon}
            )
            self.categories[slug] = cat
            if created:
                self.stdout.write(f'  Created category: {name}')

    def _create_courses(self):
        from courses.models import Course, Section, Lesson

        courses_data = [
            {
                'title': 'Complete Python Bootcamp: From Zero to Hero',
                'description': 'Master Python programming from beginner to advanced. Learn data structures, OOP, file handling, and build real projects.',
                'short_description': 'Learn Python programming from scratch and build real-world projects.',
                'instructor_email': 'john@learnhub.com',
                'category': 'programming',
                'price': 89.99,
                'discount_price': 19.99,
                'level': 'beginner',
                'language': 'English',
                'duration_hours': 42.5,
                'rating': 4.8,
                'total_ratings': 12450,
                'total_students': 58320,
                'objectives': [
                    'Write clean, efficient Python code',
                    'Understand OOP concepts',
                    'Build command-line applications',
                    'Work with files and APIs',
                ],
                'requirements': ['A computer with internet access', 'No prior programming experience needed'],
                'tags': ['python', 'programming', 'beginner'],
                'sections': [
                    {
                        'title': 'Getting Started with Python',
                        'lessons': [
                            ('Welcome & Course Overview', 'video', 360),
                            ('Installing Python & VS Code', 'video', 480),
                            ('Your First Python Program', 'video', 540, True),
                        ]
                    },
                    {
                        'title': 'Python Fundamentals',
                        'lessons': [
                            ('Variables and Data Types', 'video', 720),
                            ('Operators and Expressions', 'video', 600),
                            ('Fundamentals Quiz', 'quiz', 0),
                        ]
                    },
                    {
                        'title': 'Control Flow',
                        'lessons': [
                            ('If/Else Statements', 'video', 660),
                            ('For and While Loops', 'video', 780),
                            ('Functions', 'video', 900),
                        ]
                    },
                ]
            },
            {
                'title': 'React 18 & TypeScript: The Complete Guide',
                'description': 'Build modern web applications with React 18, TypeScript, hooks, context, and popular libraries like React Query and Zustand.',
                'short_description': 'Master React 18 with TypeScript for professional web development.',
                'instructor_email': 'sarah@learnhub.com',
                'category': 'web-development',
                'price': 94.99,
                'discount_price': 24.99,
                'level': 'intermediate',
                'language': 'English',
                'duration_hours': 38.0,
                'rating': 4.9,
                'total_ratings': 8920,
                'total_students': 34100,
                'objectives': [
                    'Build production-ready React apps',
                    'Use TypeScript with React',
                    'Master hooks and state management',
                    'Integrate REST APIs',
                ],
                'requirements': ['JavaScript fundamentals', 'Basic HTML & CSS knowledge'],
                'tags': ['react', 'typescript', 'frontend'],
                'sections': [
                    {
                        'title': 'React Fundamentals',
                        'lessons': [
                            ('Introduction to React', 'video', 420, True),
                            ('JSX and Components', 'video', 600),
                            ('Props and State', 'video', 720),
                        ]
                    },
                    {
                        'title': 'React Hooks Deep Dive',
                        'lessons': [
                            ('useState and useEffect', 'video', 840),
                            ('useContext and useReducer', 'video', 780),
                            ('Custom Hooks', 'video', 660),
                        ]
                    },
                ]
            },
            {
                'title': 'Machine Learning with Python & TensorFlow',
                'description': 'A comprehensive ML course covering supervised/unsupervised learning, neural networks, and deploying models to production.',
                'short_description': 'From linear regression to deep learning – all in Python.',
                'instructor_email': 'mike@learnhub.com',
                'category': 'data-science',
                'price': 99.99,
                'discount_price': 29.99,
                'level': 'advanced',
                'language': 'English',
                'duration_hours': 55.0,
                'rating': 4.7,
                'total_ratings': 6700,
                'total_students': 22000,
                'objectives': [
                    'Implement ML algorithms from scratch',
                    'Build neural networks with TensorFlow',
                    'Deploy models with Flask/FastAPI',
                    'Work with real datasets',
                ],
                'requirements': ['Python proficiency', 'Basic linear algebra', 'Statistics fundamentals'],
                'tags': ['machine-learning', 'python', 'tensorflow', 'ai'],
                'sections': [
                    {
                        'title': 'Introduction to ML',
                        'lessons': [
                            ('What is Machine Learning?', 'video', 480, True),
                            ('Types of ML Algorithms', 'video', 540),
                            ('Setting Up Your Environment', 'video', 420),
                        ]
                    },
                    {
                        'title': 'Supervised Learning',
                        'lessons': [
                            ('Linear Regression', 'video', 720),
                            ('Logistic Regression', 'video', 780),
                            ('Decision Trees & Random Forests', 'video', 900),
                        ]
                    },
                ]
            },
            {
                'title': 'UI/UX Design Masterclass with Figma',
                'description': 'Design beautiful, user-friendly interfaces from scratch. Learn design principles, prototyping, and handoff to developers.',
                'short_description': 'Design stunning interfaces using Figma and modern UX principles.',
                'instructor_email': 'emily@learnhub.com',
                'category': 'design',
                'price': 79.99,
                'discount_price': None,
                'level': 'beginner',
                'language': 'English',
                'duration_hours': 28.5,
                'rating': 4.6,
                'total_ratings': 4300,
                'total_students': 17800,
                'objectives': [
                    'Master Figma from scratch',
                    'Apply UX research methods',
                    'Create interactive prototypes',
                    'Build a design portfolio',
                ],
                'requirements': ['No design experience needed', 'Free Figma account'],
                'tags': ['design', 'figma', 'ux', 'ui'],
                'sections': [
                    {
                        'title': 'Design Fundamentals',
                        'lessons': [
                            ('Color Theory & Typography', 'video', 540, True),
                            ('Layout Principles', 'video', 600),
                            ('Design Systems', 'video', 720),
                        ]
                    },
                ]
            },
            {
                'title': 'Django REST Framework: Build APIs Like a Pro',
                'description': 'Build production-grade REST APIs with Django, DRF, JWT auth, PostgreSQL, Redis caching, Celery, and Docker deployment.',
                'short_description': 'Build robust REST APIs with Django and DRF from scratch.',
                'instructor_email': 'john@learnhub.com',
                'category': 'web-development',
                'price': 84.99,
                'discount_price': 19.99,
                'level': 'intermediate',
                'language': 'English',
                'duration_hours': 32.0,
                'rating': 4.8,
                'total_ratings': 5600,
                'total_students': 19200,
                'objectives': [
                    'Build RESTful APIs with DRF',
                    'Implement JWT authentication',
                    'Use PostgreSQL & Redis',
                    'Deploy with Docker',
                ],
                'requirements': ['Python basics', 'Basic web knowledge'],
                'tags': ['django', 'python', 'api', 'backend'],
                'sections': [
                    {
                        'title': 'Django Basics',
                        'lessons': [
                            ('Django Project Setup', 'video', 480, True),
                            ('Models & Migrations', 'video', 660),
                            ('Django Admin', 'video', 420),
                        ]
                    },
                ]
            },
            {
                'title': 'Introduction to Data Science with Python',
                'description': 'Learn data analysis with Pandas, visualization with Matplotlib & Seaborn, and statistical fundamentals for data science.',
                'short_description': 'Analyze data like a pro using Python, Pandas, and visualization tools.',
                'instructor_email': 'mike@learnhub.com',
                'category': 'data-science',
                'price': 0,
                'discount_price': None,
                'is_free': True,
                'level': 'beginner',
                'language': 'English',
                'duration_hours': 18.0,
                'rating': 4.5,
                'total_ratings': 9800,
                'total_students': 45000,
                'objectives': [
                    'Load and clean data with Pandas',
                    'Create visualizations',
                    'Perform statistical analysis',
                ],
                'requirements': ['Basic Python', 'Curiosity about data'],
                'tags': ['data-science', 'python', 'pandas', 'free'],
                'sections': [
                    {
                        'title': 'Getting Started',
                        'lessons': [
                            ('Course Introduction', 'video', 300, True),
                            ('Python for Data Science', 'video', 480),
                            ('NumPy Basics', 'video', 600),
                        ]
                    },
                ]
            },
        ]

        self.courses = []
        for data in courses_data:
            instructor = User.objects.get(email=data['instructor_email'])
            category = self.categories.get(data['category'])
            title = data['title']
            slug = slugify(title)

            # Make slug unique
            base_slug = slug
            counter = 1
            while Course.objects.filter(slug=slug).exists():
                slug = f"{base_slug}-{counter}"
                counter += 1

            course, created = Course.objects.get_or_create(
                slug=slug,
                defaults={
                    'title': title,
                    'description': data['description'],
                    'short_description': data['short_description'],
                    'instructor': instructor,
                    'category': category,
                    'price': data['price'],
                    'discount_price': data.get('discount_price'),
                    'level': data['level'],
                    'language': data['language'],
                    'duration_hours': data['duration_hours'],
                    'rating': data['rating'],
                    'total_ratings': data['total_ratings'],
                    'total_students': data['total_students'],
                    'objectives': data['objectives'],
                    'requirements': data['requirements'],
                    'tags': data['tags'],
                    'status': 'published',
                    'is_free': data.get('is_free', False),
                    'certificate_available': True,
                    'published_at': timezone.now(),
                }
            )

            if created:
                # Create sections and lessons
                for sec_order, sec_data in enumerate(data.get('sections', [])):
                    section = Section.objects.create(
                        course=course,
                        title=sec_data['title'],
                        order=sec_order,
                    )
                    total_lessons = 0
                    for les_order, lesson_info in enumerate(sec_data['lessons']):
                        title_l = lesson_info[0]
                        ctype = lesson_info[1]
                        duration = lesson_info[2]
                        is_free_preview = lesson_info[3] if len(lesson_info) > 3 else False
                        Lesson.objects.create(
                            section=section,
                            title=title_l,
                            content_type=ctype,
                            video_duration=duration,
                            video_url='https://sample-videos.com/video321/mp4/720/big_buck_bunny_720p_1mb.mp4' if ctype == 'video' else '',
                            order=les_order,
                            is_free_preview=is_free_preview,
                        )
                        total_lessons += 1

                # Update total_lessons
                total = Lesson.objects.filter(section__course=course).count()
                Course.objects.filter(pk=course.pk).update(total_lessons=total)

                self.stdout.write(f'  Created course: {title}')
            self.courses.append(course)

    def _create_enrollments(self):
        from enrollments.models import Enrollment
        from courses.models import Course

        published = Course.objects.filter(status='published')
        count = 0
        for student in self.students:
            # Enroll each student in 2-3 random courses
            sample = random.sample(list(published), min(3, published.count()))
            for course in sample:
                enroll, created = Enrollment.objects.get_or_create(
                    user=student,
                    course=course,
                    defaults={
                        'status': random.choice(['active', 'active', 'completed']),
                        'progress': random.uniform(10, 100),
                        'amount_paid': float(course.effective_price),
                    }
                )
                if created:
                    count += 1
        self.stdout.write(f'  Created {count} enrollments')
