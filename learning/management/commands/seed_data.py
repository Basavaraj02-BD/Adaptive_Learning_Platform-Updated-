"""
python manage.py seed_data

Creates a full demo dataset:
  - 1 admin user   (admin / admin123)
  - 3 student users (student1-3 / student123)
  - 1 instructor   (instructor / instructor123)
  - 4 courses with modules, materials, exams and questions
"""
import json
from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from django.utils.text import slugify
from learning.models import (
    UserProfile, Course, Module, LearningMaterial,
    Enrollment, Exam, Question, Notification,
)


class Command(BaseCommand):
    help = 'Seed the database with demo data'

    def add_arguments(self, parser):
        parser.add_argument('--flush', action='store_true',
                            help='Delete existing data before seeding')

    def handle(self, *args, **options):
        if options['flush']:
            self.stdout.write('Flushing existing data…')
            Question.objects.all().delete()
            Exam.objects.all().delete()
            Enrollment.objects.all().delete()
            LearningMaterial.objects.all().delete()
            Module.objects.all().delete()
            Course.objects.all().delete()
            UserProfile.objects.all().delete()
            User.objects.filter(is_superuser=False).delete()

        self.stdout.write(self.style.MIGRATE_HEADING('Creating users…'))

        # Admin
        admin, _ = User.objects.get_or_create(username='admin', defaults={
            'email': 'admin@adaptlearn.com',
            'first_name': 'Admin',
            'last_name': 'User',
            'is_staff': True,
            'is_superuser': True,
        })
        admin.set_password('admin123')
        admin.save()
        UserProfile.objects.get_or_create(user=admin, defaults={'role': 'admin'})

        # Instructor
        instructor, _ = User.objects.get_or_create(username='instructor', defaults={
            'email': 'instructor@adaptlearn.com',
            'first_name': 'Priya',
            'last_name': 'Sharma',
        })
        instructor.set_password('instructor123')
        instructor.save()
        UserProfile.objects.get_or_create(user=instructor, defaults={'role': 'instructor', 'skill_level': 'advanced'})

        # Students
        students = []
        student_data = [
            ('student1', 'Arjun',  'Kumar',  'beginner'),
            ('student2', 'Sneha',  'Patil',  'intermediate'),
            ('student3', 'Rahul',  'Mehta',  'advanced'),
        ]
        for uname, fname, lname, skill in student_data:
            u, _ = User.objects.get_or_create(username=uname, defaults={
                'email': f'{uname}@adaptlearn.com',
                'first_name': fname,
                'last_name': lname,
            })
            u.set_password('student123')
            u.save()
            UserProfile.objects.get_or_create(u, defaults={'role': 'student', 'skill_level': skill})
            students.append(u)

        self.stdout.write(self.style.SUCCESS('✓ Users created'))

        # ─────────────────────────────────────────
        # COURSES
        # ─────────────────────────────────────────
        courses_data = [
            {
                'title': 'Python Programming for Beginners',
                'difficulty': 'beginner',
                'price': 0,
                'is_free': True,
                'description': "Hey there! Ready to write your very first line of code? Python is the perfect starting point. We'll walk you through variables, loops, functions, and object-oriented programming step-by-step—with no confusing jargon, just hands-on coding fun!",
                'duration_hrs': 12,
                'tags': 'python programming beginners coding',
                'modules': [
                    {
                        'title': 'Introduction to Python',
                        'materials': [
                            ('What is Python?', 'article', '<h3>What is Python?</h3><p>Python is a high-level, interpreted programming language known for its simplicity and readability. Created by Guido van Rossum in 1991, Python emphasises code readability and allows programmers to express concepts in fewer lines of code.</p><h4>Key Features:</h4><ul><li>Easy to learn and read</li><li>Versatile — web, AI, data science</li><li>Large standard library</li><li>Active community</li></ul>'),
                            ('Setting Up Python', 'article', '<h3>Installation</h3><p>Download Python from python.org. We recommend Python 3.11+. Use VS Code or PyCharm as your IDE.</p>'),
                            ('Your First Python Program', 'article', '<h3>Hello World!</h3><pre><code>print("Hello, World!")\nname = input("Enter your name: ")\nprint(f"Hello, {name}!")</code></pre>'),
                        ],
                        'exam': {
                            'title': 'Python Basics Quiz',
                            'duration': 10, 'total': 10, 'pass': 6,
                            'questions': [
                                ('What is the correct way to print in Python?', 'mcq', ['console.log("Hi")', 'print("Hi")', 'echo "Hi"', 'System.out.println("Hi")'], 'print("Hi")', 'Python uses print() for output.', 'easy', 2),
                                ('Python is a __ language.', 'mcq', ['Compiled', 'Interpreted', 'Assembly', 'Machine'], 'Interpreted', 'Python is interpreted, not compiled.', 'easy', 2),
                                ('Which symbol is used for comments in Python?', 'mcq', ['//', '#', '/*', '--'], '#', '# is used for single-line comments.', 'easy', 2),
                                ('Is Python case-sensitive?', 'true_false', [], 'True', 'Python is case-sensitive — Name ≠ name.', 'easy', 2),
                                ('What does len() return?', 'mcq', ['The last element', 'The length of an object', 'The type of an object', 'None'], 'The length of an object', 'len() returns the number of items.', 'easy', 2),
                            ]
                        }
                    },
                    {
                        'title': 'Data Types & Variables',
                        'materials': [
                            ('Variables & Data Types', 'article', '<h3>Variables</h3><p>Variables store data. Python is dynamically typed — you don\'t declare types explicitly.</p><pre><code>name = "Alice"  # str\nage  = 25       # int\npi   = 3.14     # float\nis_student = True  # bool</code></pre>'),
                            ('Lists & Tuples', 'article', '<h3>Lists</h3><p>Lists are mutable, ordered collections.</p><pre><code>fruits = ["apple", "banana", "cherry"]\nfruits.append("mango")\nprint(fruits[0])  # apple</code></pre>'),
                        ],
                        'exam': None,
                    },
                ],
            },
            {
                'title': 'Machine Learning Fundamentals',
                'difficulty': 'intermediate',
                'price': 999,
                'is_free': False,
                'description': "Curious about the magic behind Netflix recommendations or self-driving cars? Welcome! We'll explore supervised learning, unsupervised clustering, and basic neural networks in a clear, friendly way using scikit-learn.",
                'duration_hrs': 20,
                'tags': 'machine learning AI python data science scikit-learn',
                'modules': [
                    {
                        'title': 'Introduction to ML',
                        'materials': [
                            ('What is Machine Learning?', 'article', '<h3>Machine Learning</h3><p>ML enables systems to learn from data without explicit programming. Types: Supervised, Unsupervised, Reinforcement Learning.</p>'),
                            ('ML Workflow', 'article', '<h3>The ML Pipeline</h3><ol><li>Data Collection</li><li>Preprocessing</li><li>Feature Engineering</li><li>Model Training</li><li>Evaluation</li><li>Deployment</li></ol>'),
                        ],
                        'exam': {
                            'title': 'ML Concepts Quiz',
                            'duration': 15, 'total': 15, 'pass': 9,
                            'questions': [
                                ('Which algorithm is used for classification?', 'mcq', ['Linear Regression', 'K-Means', 'Random Forest', 'DBSCAN'], 'Random Forest', 'Random Forest is a classification and regression algorithm.', 'medium', 3),
                                ('Supervised learning uses labelled data.', 'true_false', [], 'True', 'Supervised learning requires labelled training data.', 'easy', 3),
                                ('What does overfitting mean?', 'mcq', ['Model performs well on all data', 'Model memorises training data but fails on new data', 'Model cannot learn from data', 'Model has too few parameters'], 'Model memorises training data but fails on new data', 'Overfitting = high training accuracy but poor generalisation.', 'medium', 3),
                                ('Which library is most commonly used for ML in Python?', 'mcq', ['TensorFlow', 'scikit-learn', 'Keras', 'PyTorch'], 'scikit-learn', 'scikit-learn is the most popular ML library for classical algorithms.', 'easy', 3),
                                ('Cross-validation helps to detect overfitting.', 'true_false', [], 'True', 'Cross-validation evaluates the model on multiple splits of data.', 'medium', 3),
                            ]
                        }
                    },
                ],
            },
            {
                'title': 'Web Development with Django',
                'difficulty': 'intermediate',
                'price': 1499,
                'is_free': False,
                'description': "Let's build a real, working web app from scratch! We'll teach you how to use Django's powerful backend system to design models, create user-friendly views, and launch your own dynamic website.",
                'duration_hrs': 25,
                'tags': 'django web development python backend',
                'modules': [
                    {
                        'title': 'Django Basics',
                        'materials': [
                            ('What is Django?', 'article', '<h3>Django</h3><p>Django is a high-level Python web framework that follows the MVT (Model-View-Template) pattern. It\'s "batteries included" — comes with ORM, admin, auth, and more.</p>'),
                            ('Project Setup', 'article', '<pre><code>pip install django\ndjango-admin startproject myproject\ncd myproject\npython manage.py runserver</code></pre>'),
                        ],
                        'exam': {
                            'title': 'Django Quiz',
                            'duration': 12, 'total': 10, 'pass': 6,
                            'questions': [
                                ('What does MVT stand for in Django?', 'mcq', ['Model-View-Template', 'Model-View-Test', 'Module-View-Template', 'Model-View-Type'], 'Model-View-Template', 'Django follows the MVT pattern.', 'easy', 2),
                                ('Django comes with a built-in admin panel.', 'true_false', [], 'True', 'Django admin is auto-generated from models.', 'easy', 2),
                                ('Which file defines URL patterns in Django?', 'mcq', ['models.py', 'views.py', 'urls.py', 'settings.py'], 'urls.py', 'URL routing is configured in urls.py.', 'easy', 2),
                                ('What command creates a new Django app?', 'mcq', ['django-admin newapp', 'python manage.py startapp', 'python manage.py createapp', 'django-admin createapp'], 'python manage.py startapp', 'startapp creates a new application within a project.', 'easy', 2),
                                ('ORM stands for?', 'mcq', ['Object Relational Mapping', 'Object Runtime Model', 'Object Routing Manager', 'None'], 'Object Relational Mapping', 'ORM maps Python objects to database tables.', 'medium', 2),
                            ]
                        }
                    },
                ],
            },
            {
                'title': 'Advanced Data Structures & Algorithms',
                'difficulty': 'advanced',
                'price': 1999,
                'is_free': False,
                'description': "Ready to level up your engineering skills? Data structures and algorithms are the keys to writing fast, clean code. We'll tackle arrays, trees, graphs, and dynamic programming with clear analogies that actually click.",
                'duration_hrs': 30,
                'tags': 'DSA algorithms competitive programming interview',
                'modules': [
                    {
                        'title': 'Arrays & Linked Lists',
                        'materials': [
                            ('Array Operations', 'article', '<h3>Arrays</h3><p>Arrays are contiguous memory blocks. Time complexity: Access O(1), Search O(n), Insert/Delete O(n).</p>'),
                            ('Linked Lists', 'article', '<h3>Linked List</h3><p>Linked lists store nodes with data + pointer to next node. Types: Singly, Doubly, Circular.</p>'),
                        ],
                        'exam': {
                            'title': 'DSA Basics Quiz',
                            'duration': 20, 'total': 20, 'pass': 12,
                            'questions': [
                                ('What is the time complexity of binary search?', 'mcq', ['O(n)', 'O(log n)', 'O(n²)', 'O(1)'], 'O(log n)', 'Binary search halves the search space each step.', 'medium', 4),
                                ('A stack follows LIFO order.', 'true_false', [], 'True', 'LIFO = Last In First Out.', 'easy', 4),
                                ('Which data structure uses FIFO?', 'mcq', ['Stack', 'Queue', 'Tree', 'Graph'], 'Queue', 'Queue is FIFO — First In First Out.', 'easy', 4),
                                ('What is the worst-case complexity of Quick Sort?', 'mcq', ['O(n log n)', 'O(n)', 'O(n²)', 'O(log n)'], 'O(n²)', 'Quick Sort degrades to O(n²) on already-sorted data.', 'hard', 4),
                                ('Dijkstra\'s algorithm finds the shortest path in a graph.', 'true_false', [], 'True', 'Dijkstra finds shortest path in weighted graphs.', 'medium', 4),
                            ]
                        }
                    },
                ],
            },
        ]

        created_courses = []
        for cd in courses_data:
            slug = slugify(cd['title'])
            course, _ = Course.objects.get_or_create(slug=slug, defaults={
                'title': cd['title'],
                'description': cd['description'],
                'instructor': instructor,
                'difficulty': cd['difficulty'],
                'status': 'published',
                'price': cd['price'],
                'is_free': cd['is_free'],
                'tags': cd['tags'],
                'duration_hrs': cd['duration_hrs'],
                'total_enrolled': 0,
            })
            created_courses.append(course)

            for m_idx, md in enumerate(cd['modules'], 1):
                module, _ = Module.objects.get_or_create(
                    course=course, title=md['title'],
                    defaults={'order': m_idx, 'duration_mins': 30}
                )
                for mat_idx, (title, mtype, content, *_) in enumerate(md['materials'], 1):
                    LearningMaterial.objects.get_or_create(
                        module=module, title=title,
                        defaults={'material_type': mtype, 'content': content, 'order': mat_idx, 'duration_mins': 10}
                    )
                if md.get('exam'):
                    ed = md['exam']
                    exam, _ = Exam.objects.get_or_create(
                        course=course, module=module, title=ed['title'],
                        defaults={
                            'exam_type': 'module',
                            'duration_mins': ed['duration'],
                            'total_marks': ed['total'],
                            'pass_marks': ed['pass'],
                            'shuffle_questions': True,
                            'is_active': True,
                        }
                    )
                    for q_idx, qd in enumerate(ed['questions'], 1):
                        q_text, q_type, options, correct, explanation, diff, marks = qd
                        q, _ = Question.objects.get_or_create(
                            exam=exam, question_text=q_text,
                            defaults={
                                'question_type': q_type,
                                'correct_answer': correct,
                                'explanation': explanation,
                                'difficulty': diff,
                                'marks': marks,
                                'order': q_idx,
                            }
                        )
                        if options:
                            q.set_options(options)
                            q.save()

        self.stdout.write(self.style.SUCCESS('✓ Courses, modules, materials & exams created'))

        # Enroll students
        for i, student in enumerate(students):
            for course in created_courses[:i+2]:
                Enrollment.objects.get_or_create(student=student, course=course)
                course.total_enrolled = Enrollment.objects.filter(course=course).count()
                course.save(update_fields=['total_enrolled'])

        # Notifications
        for student in students:
            Notification.objects.get_or_create(
                recipient=student,
                title='Welcome to AdaptLearn! 🎉',
                defaults={
                    'message': f'Hi {student.first_name}! Your account is ready. Start learning today.',
                    'notif_type': 'system',
                }
            )

        self.stdout.write(self.style.SUCCESS('✓ Enrollments & notifications created'))
        self.stdout.write('')
        self.stdout.write(self.style.SUCCESS('═══ Seed Complete! ═══'))
        self.stdout.write('')
        self.stdout.write('  Admin:       admin / admin123')
        self.stdout.write('  Instructor:  instructor / instructor123')
        self.stdout.write('  Students:    student1, student2, student3 / student123')
        self.stdout.write('')
        self.stdout.write('  Visit: http://127.0.0.1:8000/')
        self.stdout.write('  Admin: http://127.0.0.1:8000/admin-login/')
