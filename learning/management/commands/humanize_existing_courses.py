from django.core.management.base import BaseCommand
from learning.models import Course

class Command(BaseCommand):
    help = "Update existing courses in the database to have friendly, humanized descriptions."

    def handle(self, *args, **options):
        updates = {
            "python-basics": "Hey there! Ready to write your very first line of code? Python is the perfect place to start. We will walk you through the absolute basics—no confusing jargon, just practical coding to kickstart your journey. Let's build something cool together!",
            "django-development": "Ever wanted to build a real, working web app from scratch? Django is the powerhouse used by giants like Instagram. In this course, we'll guide you step-by-step to design models, create views, and launch your own backend. Ready to build?",
            "html-fundamentals": "Welcome to the building blocks of the web! Every website you visit starts with HTML. We'll show you how to structure content, write clean markup, and organize web pages like a pro. No prior experience needed!",
            "css-masterclass": "Bring your websites to life! CSS is where logic meets design. We'll master layouts, colors, Flexbox, and CSS Grid to help you design responsive, gorgeous web pages that wow visitors. Let's make it look premium!",
            "javascript-essentials": "Let's make things interactive! JavaScript is the brain of the browser. We'll learn variables, loops, objects, and standard programming techniques that let you respond to clicks, create animations, and build dynamic UI.",
            "data-structures": "Struggling to write efficient code? Data structures are the keys to optimization. We'll tackle arrays, trees, stacks, and lists with clear, real-world analogies that actually make sense (no dry math talk!).",
            "machine-learning-intro": "Curious how Netflix recommends movies or how self-driving cars 'see'? Welcome to the world of AI. We will cover the core concepts of machine learning in a simple, friendly way—perfect for curious beginners.",
            "sql-basics": "Data rules the world, and SQL is the language used to talk to it. Learn how to query databases, join tables, and extract valuable insights without getting lost in rows of code. Let's unlock data power!",
            "c-programming": "Let's go under the hood! C is the language that power systems, game engines, and OS kernels. We will master memory allocation, pointers, and arrays to help you write blazing fast code and truly understand computers.",
            "java-fundamentals": "Write once, run anywhere! Java is the backbone of enterprise apps and Android development. We will dive into Object-Oriented Programming (OOP), collections, and robust software design in a structured, friendly way.",
            "python-programming-for-beginners": "Hey there! Ready to write your very first line of code? Python is the perfect starting point. We'll walk you through variables, loops, functions, and object-oriented programming step-by-step—with no confusing jargon, just hands-on coding fun!",
            "machine-learning-fundamentals": "Curious about the magic behind Netflix recommendations or self-driving cars? Welcome! We'll explore supervised learning, unsupervised clustering, and basic neural networks in a clear, friendly way using scikit-learn.",
            "web-development-with-django": "Let's build a real, working web app from scratch! We'll teach you how to use Django's powerful backend system to design models, create user-friendly views, and launch your own dynamic website.",
            "advanced-data-structures-algorithms": "Ready to level up your engineering skills? Data structures and algorithms are the keys to writing fast, clean code. We'll tackle arrays, trees, graphs, and dynamic programming with clear analogies that actually click.",
            "web-development-bootcamp-2026": "Ready to become a full-stack developer in 2026? We'll master HTML, CSS, JavaScript, databases, and APIs. We guide you from layout design to server deployment in a highly supportive, friendly cohort environment.",
            "javascript-dom": "Bring web pages to life! We'll explore how JavaScript interacts with HTML structure (the DOM) to create stunning interactive experiences, dynamic forms, and animations. Hands-on coding guaranteed!",
            "web-development-basics": "Start your journey in web engineering! Learn how web pages are built, styled, and loaded. We'll get our hands dirty writing basic HTML and CSS pages and learning how they communicate over the internet."
        }

        self.stdout.write("Starting database humanization updates...")
        for slug, desc in updates.items():
            try:
                course = Course.objects.get(slug=slug)
                course.description = desc
                course.save()
                self.stdout.write(self.style.SUCCESS(f"  [OK] Humanized course description for '{course.title}'"))
            except Course.DoesNotExist:
                # Fall back to matching by title if slug lookup fails
                try:
                    title_search = slug.replace("-", " ")
                    course = Course.objects.get(title__icontains=title_search)
                    course.description = desc
                    course.save()
                    self.stdout.write(self.style.SUCCESS(f"  [OK] Humanized course description for '{course.title}' (by title search)"))
                except Course.DoesNotExist:
                    pass
                except Course.MultipleObjectsReturned:
                    pass

        self.stdout.write(self.style.SUCCESS("All existing courses successfully humanized in the database."))
