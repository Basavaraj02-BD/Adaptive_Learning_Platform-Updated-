# 🧠 AdaptLearn — Adaptive Learning Platform with Auto Evaluation

A full-featured Django project with AI-powered adaptive learning, auto evaluation, AI chatbot, modern glassmorphism UI, and complete auth system.

---


## 📋 All 12 Database Tables Implemented

| # | Table | Description |
|---|-------|-------------|
| 1 | **UserProfile** | Extends Django User — role, skill level, XP points, learning style |
| 2 | **Course** | Courses with difficulty, pricing, tags, instructor |
| 3 | **Module** | Course modules with ordering and lock system |
| 4 | **LearningMaterial** | Videos, PDFs, articles, quizzes per module |
| 5 | **Enrollment** | Student–course enrollment with progress % |
| 6 | **StudentProgress** | Per-material completion tracking |
| 7 | **Exam** | Timed exams with shuffle, attempts, pass marks |
| 8 | **Question** | MCQ, True/False, Fill-in-blank, Short Answer |
| 9 | **ExamResult** | Score, percentage, status, AI feedback |
| 10 | **StudentAnswer** | Per-question answers with AI grading |
| 11 | **Payment** | Course payments with Stripe/UPI/card support |
| 12 | **Notification** | System, enrollment, exam, payment notifications |

---

## 🔑 Auth Pages (4 pages)

| URL | Page |
|-----|------|
| `/login/` | 🎓 User Login |
| `/register/` | 🎓 User Registration (Student / Instructor) |
| `/admin-login/` | 🛡️ Admin Login (gold theme) |
| `/admin-register/` | 🛡️ Admin Registration (requires secret key) |

**Admin Secret Key (dev):** `ADAPTIVE_ADMIN_2024`

---

## 🚀 Quick Setup

### 1. Create Virtual Environment
```bash
cd adaptive_learning
python -m venv venv

# Windows
venv\Scripts\activate

# Mac/Linux
source venv/bin/activate
```

### 2. Install Dependencies
```bash
pip install -r requirements.txt
```

### 3. Configure Environment
```bash
cp .env.example .env
# Edit .env and add your API keys
```

### 4. Run Migrations
```bash
python manage.py makemigrations learning
python manage.py migrate
```

### 5. Create Superuser (Admin)
```bash
python manage.py createsuperuser
```

### 6. (Optional) Load Sample Data
```bash
python manage.py shell
```
Then paste:
```python
from django.contrib.auth.models import User
from learning.models import *

# Create a sample published course
u = User.objects.first()
c = Course.objects.create(
    title="Python for Beginners",
    slug="python-beginners",
    description="Learn Python from scratch with hands-on projects.",
    instructor=u,
    difficulty="beginner",
    status="published",
    is_free=True,
    duration_hrs=10,
    tags="python programming beginner",
)
m = Module.objects.create(course=c, title="Introduction to Python", order=1)
LearningMaterial.objects.create(
    module=m, title="What is Python?", material_type="article",
    content="<p>Python is a high-level programming language...</p>", order=1
)
exam = Exam.objects.create(
    course=c, module=m, title="Python Basics Quiz",
    exam_type="module", duration_mins=10, total_marks=10, pass_marks=6
)
q = Question.objects.create(
    exam=exam, question_text="What symbol is used for comments in Python?",
    question_type="mcq", marks=2, correct_answer="#",
    explanation="The # symbol is used for single-line comments."
)
q.set_options(["//", "#", "/*", "--"])
q.save()
print("Sample data created!")
```

### 7. Start Server
```bash
python manage.py runserver
```

Visit: **http://127.0.0.1:8000/**

---

## 🗺️ All URLs

| URL | View |
|-----|------|
| `/` | Home landing page |
| `/login/` | User login |
| `/register/` | User register |
| `/admin-login/` | Admin login |
| `/admin-register/` | Admin register |
| `/logout/` | Logout |
| `/dashboard/` | Student dashboard |
| `/admin-dashboard/` | Admin dashboard |
| `/courses/` | Course listing |
| `/courses/<slug>/` | Course detail |
| `/courses/<id>/enroll/` | Enroll in course |
| `/modules/<id>/` | Module viewer |
| `/exams/` | Exam listing |
| `/exams/<id>/take/` | Take exam |
| `/results/<id>/` | Exam result + AI feedback |
| `/payment/<id>/` | Payment page |
| `/notifications/` | Notifications |
| `/profile/` | User profile |
| `/chatbot/` | AI Chatbot |
| `/leaderboard/` | Leaderboard |
| `/admin-panel/users/` | Admin: manage users |
| `/admin-panel/courses/` | Admin: manage courses |
| `/admin/` | Django admin |

---

## 🤖 AI Chatbot Setup (Anthropic)

1. Get API key from https://console.anthropic.com
2. Add to `.env`:
   ```
   ANTHROPIC_API_KEY=sk-ant-api03-...
   ```
3. The chatbot at `/chatbot/` will use Claude AI for real responses.
   Without a key, it uses friendly fallback responses.

---

## 💳 Payment Integration (Stripe)

1. Get keys from https://stripe.com
2. Add to `.env`:
   ```
   STRIPE_PUBLIC_KEY=pk_test_...
   STRIPE_SECRET_KEY=sk_test_...
   ```
3. Currently simulates payment success — wire up Stripe JS for production.

---

## 🎨 Design Features

- **Dark glassmorphism** UI with animated mesh backgrounds
- **Syne + DM Sans** typography pairing
- **Gradient accent system** (purple/cyan/pink/gold)
- **Responsive sidebar** with role-based nav
- **AOS scroll animations**
- **Real-time exam timer** with question navigator
- **AI chatbot** with typing indicator and markdown support
- **Progress bars** with glow effects
- **Toast notifications** with auto-dismiss

---

# 📸 Screenshots

## 🏠 Landing Page
<img width="1920" height="922" alt="image" src="https://github.com/user-attachments/assets/775b2bab-4355-4c02-9bec-1effcdec1a70" /> <br>
<img width="1918" height="920" alt="image" src="https://github.com/user-attachments/assets/ce13ab5f-6be3-4c99-944a-42fe1b4d2001" />

---

## 📚 Courses

<img width="1920" height="920" alt="image" src="https://github.com/user-attachments/assets/88d3d07a-852a-447f-9f13-271b80c766c5" />

---

## 🎓 Student Dashboard

<img width="1920" height="917" alt="image" src="https://github.com/user-attachments/assets/c44cb2e9-80c5-4c96-9ad1-76f6e361b993" />


---

## 📝 Exam System

<img width="1920" height="917" alt="image" src="https://github.com/user-attachments/assets/08540cf7-0fa8-432d-ae7e-18667e5e1f55" />


---

## 🛡️ Admin Dashboard

<img width="1902" height="916" alt="image" src="https://github.com/user-attachments/assets/e78bffbf-a859-43e1-8cb5-f0a77d0910c8" />

---

## 📁 Project Structure

```
adaptive_learning/
├── adaptive_learning/       # Django project config
│   ├── settings.py
│   ├── urls.py
│   └── wsgi.py
├── learning/                # Main app
│   ├── models.py            # All 12 tables
│   ├── views.py             # All views
│   ├── urls.py              # All routes
│   ├── forms.py             # Auth + content forms
│   ├── admin.py             # Django admin
│   ├── signals.py           # Auto profile creation
│   └── context_processors.py
├── templates/
│   ├── base.html            # Master layout
│   ├── registration/
│   │   ├── user_login.html
│   │   ├── user_register.html
│   │   ├── admin_login.html
│   │   └── admin_register.html
│   └── learning/
│       ├── home.html
│       ├── dashboard.html
│       ├── admin_dashboard.html
│       ├── course_list.html
│       ├── course_detail.html
│       ├── module_detail.html
│       ├── exam_list.html
│       ├── take_exam.html
│       ├── exam_result.html
│       ├── chatbot.html
│       ├── profile.html
│       ├── notifications.html
│       ├── leaderboard.html
│       ├── payment.html
│       ├── admin_users.html
│       └── admin_courses.html
├── static/
├── manage.py
├── requirements.txt
└── .env.example
```
