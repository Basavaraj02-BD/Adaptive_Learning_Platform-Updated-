import os
import sys
import time
import django
import subprocess
from datetime import timedelta

# Set up Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'adaptive_learning.settings')
django.setup()

from django.contrib.auth.models import User
from django.utils import timezone
from learning.models import (
    Enrollment, Course, Exam, ExamResult, StudentProgress,
    LearningMaterial, UserProfile, ChatMessage
)

def prepare_data():
    print("Preparing mock database state for student1...")
    
    # 1. Get or create student1
    student, created = User.objects.get_or_create(username='student1', defaults={
        'email': 'student1@adaptlearn.com',
        'first_name': 'Arjun',
        'last_name': 'Kumar',
    })
    if created or student.password == "":
        student.set_password('student123')
        student.save()
        
    profile, _ = UserProfile.objects.get_or_create(user=student, defaults={'role': 'student', 'skill_level': 'beginner'})
    profile.total_points = 420  # Set some XP points to display
    profile.save()

    # 2. Get Python course
    course = Course.objects.filter(slug='python-programming-for-beginners').first()
    if not course:
        print("Error: Run 'python manage.py seed_data' first to seed the courses!")
        sys.exit(1)

    # 3. Setup Enrollment
    enrollment, _ = Enrollment.objects.get_or_create(student=student, course=course)
    enrollment.completion_percent = 100.0
    enrollment.status = 'completed'
    enrollment.completed_at = timezone.now() - timedelta(days=2)
    enrollment.certificate_issued = True
    enrollment.save()

    # 4. Mark all materials complete for python course to ensure 100% completion in DB
    materials = LearningMaterial.objects.filter(module__course=course)
    for m in materials:
        StudentProgress.objects.get_or_create(
            student=student, material=m,
            defaults={'enrollment': enrollment, 'is_completed': True}
        )

    # 5. Create a passing Exam Result
    exam = Exam.objects.filter(course=course).first()
    if exam:
        ExamResult.objects.get_or_create(
            student=student, exam=exam,
            defaults={
                'attempt_number': 1,
                'score': 8.0,
                'total_marks': exam.total_marks,
                'percentage': 80.0,
                'status': 'pass',
                'ai_feedback': "Excellent job, Arjun! You scored 80% on this quiz and showed solid basics. Keep it up!",
                'submitted_at': timezone.now() - timedelta(days=2)
            }
        )

    # 6. Seed a chatbot message
    ChatMessage.objects.get_or_create(
        user=student, role='user',
        defaults={'content': "Hi AdaptBot, can you explain what a list is in Python?"}
    )
    ChatMessage.objects.get_or_create(
        user=student, role='assistant',
        defaults={'content': "Hello Arjun! 🐍 A **list** in Python is like a container where you can store multiple items in a specific order. For example: `fruits = ['apple', 'banana', 'cherry']`. You can add, remove, or modify items easily!"}
    )

    print("Database is ready. Enrollment ID:", enrollment.id)
    return enrollment.id

def capture_screenshots(enrollment_id):
    from selenium import webdriver
    from selenium.webdriver.common.by import By
    from selenium.webdriver.chrome.options import Options as ChromeOptions
    from selenium.webdriver.edge.options import Options as EdgeOptions
    
    print("Starting Django development server...")
    server_process = subprocess.Popen(
        ["python", "manage.py", "runserver", "127.0.0.1:8000"],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL
    )
    time.sleep(3) # Wait for server to start
    
    driver = None
    
    # Try Chrome first, then Edge
    print("Attempting to launch browser webdriver...")
    try:
        chrome_options = ChromeOptions()
        chrome_options.add_argument("--headless")
        chrome_options.add_argument("--window-size=1280,800")
        driver = webdriver.Chrome(options=chrome_options)
        print("Chrome headless launched successfully.")
    except Exception as e:
        print("Chrome launch failed. Trying Microsoft Edge...")
        try:
            edge_options = EdgeOptions()
            edge_options.add_argument("--headless")
            edge_options.add_argument("window-size=1280,800")
            driver = webdriver.Edge(options=edge_options)
            print("Edge headless launched successfully.")
        except Exception as ex:
            print("Failed to start either Chrome or Edge WebDrivers. Please ensure you have Chrome or Edge installed and that you can run selenium.")
            server_process.terminate()
            sys.exit(1)

    try:
        # Step 1: Login
        print("Logging in as student1...")
        driver.get("http://127.0.0.1:8000/login/")
        time.sleep(1)
        driver.find_element(By.NAME, "username").send_keys("student1")
        driver.find_element(By.NAME, "password").send_keys("student123")
        driver.find_element(By.XPATH, "//button[@type='submit']").click()
        time.sleep(1.5)
        
        # Step 2: Dashboard Screenshot
        print("Capturing Student Dashboard...")
        driver.get("http://127.0.0.1:8000/dashboard/")
        time.sleep(1)
        driver.save_screenshot("dashboard.png")
        
        # Step 3: Course Detail Page
        print("Capturing Course Detail Page...")
        driver.get("http://127.0.0.1:8000/courses/python-programming-for-beginners/")
        time.sleep(1)
        driver.save_screenshot("course_detail.png")
        
        # Step 4: Chatbot Page
        print("Capturing Chatbot Page...")
        driver.get("http://127.0.0.1:8000/chatbot/")
        time.sleep(1)
        driver.save_screenshot("chatbot.png")
        
        # Step 5: Analytics Page
        print("Capturing Analytics Page...")
        driver.get("http://127.0.0.1:8000/analytics/")
        time.sleep(1.5) # Allow ChartJS animations to draw
        driver.save_screenshot("analytics.png")
        
        # Step 6: Certificate Page
        print("Capturing Certificate...")
        driver.get(f"http://127.0.0.1:8000/certificate/{enrollment_id}/")
        time.sleep(1)
        # Hide control buttons for cleaner screenshot
        driver.execute_script("document.querySelector('.controls').style.display = 'none';")
        driver.save_screenshot("certificate.png")
        
        print("All screenshots successfully captured!")
        
    finally:
        driver.quit()
        print("Stopping Django development server...")
        server_process.terminate()

if __name__ == "__main__":
    enrollment_id = prepare_data()
    
    # Try capturing screenshots
    try:
        import selenium
    except ImportError:
        print("Installing Selenium...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", "selenium"])
        
    try:
        capture_screenshots(enrollment_id)
    except Exception as err:
        print(f"Error during screenshot capture: {err}")
        print("Please ensure you have Google Chrome or MS Edge installed on your PC.")
        
    # Re-run presentation generator to embed the captured images
    print("Generating PPTX presentation file...")
    from generate_presentation import create_presentation
    create_presentation()
