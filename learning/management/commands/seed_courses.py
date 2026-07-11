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

        course_descriptions = {
            "Python Basics": "Hey there! Ready to write your very first line of code? Python is the perfect place to start. We will walk you through the absolute basics—no confusing jargon, just practical coding to kickstart your journey. Let's build something cool together!",
            "Django Development": "Ever wanted to build a real, working web app from scratch? Django is the powerhouse used by giants like Instagram. In this course, we'll guide you step-by-step to design models, create views, and launch your own backend. Ready to build?",
            "HTML Fundamentals": "Welcome to the building blocks of the web! Every website you visit starts with HTML. We'll show you how to structure content, write clean markup, and organize web pages like a pro. No prior experience needed!",
            "CSS Masterclass": "Bring your websites to life! CSS is where logic meets design. We'll master layouts, colors, Flexbox, and CSS Grid to help you design responsive, gorgeous web pages that wow visitors. Let's make it look premium!",
            "JavaScript Essentials": "Let's make things interactive! JavaScript is the brain of the browser. We'll learn variables, loops, objects, and standard programming techniques that let you respond to clicks, create animations, and build dynamic UI.",
            "Data Structures": "Struggling to write efficient code? Data structures are the keys to optimization. We'll tackle arrays, trees, stacks, and lists with clear, real-world analogies that actually make sense (no dry math talk!).",
            "Machine Learning Intro": "Curious how Netflix recommends movies or how self-driving cars 'see'? Welcome to the world of AI. We will cover the core concepts of machine learning in a simple, friendly way—perfect for curious beginners.",
            "SQL Basics": "Data rules the world, and SQL is the language used to talk to it. Learn how to query databases, join tables, and extract valuable insights without getting lost in rows of code. Let's unlock data power!",
            "C Programming": "Let's go under the hood! C is the language that power systems, game engines, and OS kernels. We will master memory allocation, pointers, and arrays to help you write blazing fast code and truly understand computers.",
            "Java Fundamentals": "Write once, run anywhere! Java is the backbone of enterprise apps and Android development. We will dive into Object-Oriented Programming (OOP), collections, and robust software design in a structured, friendly way."
        }

        for title in course_descriptions.keys():
            course_slug = slugify(title)
            course, created = Course.objects.get_or_create(
                slug=course_slug,
                defaults={
                    "title": title,
                    "description": course_descriptions[title],
                    "instructor": teacher,
                    "difficulty": "beginner",
                    "status": "published",
                    "is_free": True,
                    "price": 0,
                    "duration_hrs": 10,
                    "thumbnail": f"course_thumbnails/{course_slug}.png",
                }
            )
            if not created and not course.thumbnail:
                course.thumbnail = f"course_thumbnails/{course_slug}.png"
                course.save(update_fields=["thumbnail"])

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
