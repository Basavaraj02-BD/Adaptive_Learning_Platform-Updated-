from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from learning.models import UserProfile, Course, Module, Exam, Question
from django.utils.text import slugify

class Command(BaseCommand):
    help = "Create demo free courses with exams"

    def handle(self, *args, **kwargs):
        teacher, _ = User.objects.get_or_create(username="demo_teacher", defaults={"email":"teacher@example.com"})
        teacher.set_password("teacher123")
        teacher.save()
        profile, _ = UserProfile.objects.get_or_create(user=teacher)
        profile.role = "instructor"
        profile.save()

        courses = [
            "Python Basics", "Django Development", "HTML Fundamentals",
            "CSS Masterclass", "JavaScript Essentials", "Data Structures",
            "Machine Learning Intro", "SQL Basics", "C Programming",
            "Java Fundamentals"
        ]

        for title in courses:
            course, created = Course.objects.get_or_create(
                slug=slugify(title),
                defaults={
                    "title": title,
                    "description": f"Learn {title} with hands-on examples.",
                    "instructor": teacher,
                    "difficulty": "beginner",
                    "status": "published",
                    "is_free": True,
                    "price": 0,
                    "duration_hrs": 10,
                }
            )

            module, _ = Module.objects.get_or_create(course=course, title="Introduction")
            exam, _ = Exam.objects.get_or_create(course=course, title=f"{title} Exam")

            Question.objects.get_or_create(
                exam=exam,
                question_text=f"What is the main purpose of {title}?",
                defaults={
                    "question_type":"mcq",
                    "correct_answer":"Learning",
                    "options": '["Learning", "Gaming", "Editing", "Music"]'
                }
            )

        self.stdout.write(self.style.SUCCESS("Demo courses and exams created successfully."))
