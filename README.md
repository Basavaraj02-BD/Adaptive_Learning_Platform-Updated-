![Python](https://img.shields.io/badge/Python-3.11-blue)
![Django](https://img.shields.io/badge/Django-5.0-green)
![Status](https://img.shields.io/badge/Status-Active-success)
![License](https://img.shields.io/badge/License-MIT-orange)

# 🧠 AdaptLearn — Adaptive Learning Platform with Auto Evaluation

A full-featured Django project with AI-powered adaptive learning, auto evaluation, AI chatbot, modern glassmorphism UI, and complete auth system.

---


## 📋 All 16 Database Tables Implemented

| # | Table | Description |
|---|-------|-------------|
| 1 | **UserProfile** | Extends Django User — role, skill level, XP points, learning style |
| 2 | **Course** | Courses with difficulty, pricing, tags, instructor, and thumbnails |
| 3 | **Module** | Course modules with ordering and lock system |
| 4 | **LearningMaterial** | Videos, PDFs, articles, quizzes per module |
| 5 | **Enrollment** | Student–course enrollment with progress % |
| 6 | **StudentProgress** | Per-material completion tracking |
| 7 | **Exam** | Timed exams with shuffle, attempts, pass marks |
| 8 | **Question** | MCQ, True/False, Fill-in-blank, Short Answer |
| 9 | **ExamResult** | Score, percentage, status, feedback |
| 10 | **StudentAnswer** | Per-question answers with given response |
| 11 | **Payment** | Course payments with Stripe/UPI/card support |
| 12 | **Notification** | System, enrollment, exam, payment notifications |
| 13 | **CourseReview** | Course reviews and ratings from students |
| 14 | **DiscussionThread** | Forum threads for course discussions |
| 15 | **DiscussionReply** | Thread replies in the discussion forum |
| 16 | **ChatMessage** | History of chatbot interactions with AdaptBot |

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
python -m venv .venv

# Windows (Command Prompt / PowerShell)
.venv\Scripts\activate

# Mac/Linux
source .venv/bin/activate
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
You can easily load realistic demo datasets using our management seed commands:
```bash
# Seed initial teacher and core courses
python manage.py seed_courses

# Seed full student demo dataset (users, notifications, enrollments)
python manage.py seed_data

# Seed at least 10 high-quality questions for each exam
python manage.py seed_exam_questions

# Humanize course descriptions and text in the database
python manage.py humanize_existing_courses
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

<img width="1920" height="917" alt="image" src="https://github.com/user-attachments/assets/87cddfd9-cc9a-4745-bf25-a4c322ba7228" />


---

## 🎓 Student Dashboard

<img width="1920" height="917" alt="image" src="https://github.com/user-attachments/assets/c8cab19c-47bf-4d23-a7b3-10a0649d5e45" />



---

## 📝 Exam System

<img width="1920" height="922" alt="image" src="https://github.com/user-attachments/assets/e3306e88-2256-430a-b742-0f4f1ead002b" />



---

## 🛡️ Admin Dashboard

<img width="1920" height="915" alt="image" src="https://github.com/user-attachments/assets/a30860f9-a6e3-4fe4-9350-cef0a96a917e" />
<img width="1920" height="917" alt="image" src="https://github.com/user-attachments/assets/b924d62b-83bd-44d8-bc89-e49b8f7b8773" />



---

## 📁 Project Structure

```
adaptive_learning/
├── adaptive_learning/       # Django project config
│   ├── settings.py
│   ├── urls.py
│   └── wsgi.py
├── learning/                # Main app
│   ├── models.py            # All 16 tables
│   ├── views.py             # Main views and business logic
│   ├── urls.py              # Routes
│   ├── forms.py             # Auth & course management forms
│   ├── admin.py             # Django admin settings
│   ├── signals.py           # Auto-profile creation
│   ├── context_processors.py
│   └── management/
│       └── commands/        # Custom seed & migration scripts
│           ├── seed_courses.py
│           ├── seed_data.py
│           ├── seed_exam_questions.py
│           └── humanize_existing_courses.py
├── templates/
│   ├── base.html            # Master layout
│   ├── registration/        # Login/Register templates
│   │   ├── user_login.html
│   │   ├── user_register.html
│   │   ├── admin_login.html
│   │   └── admin_register.html
│   └── learning/            # App-specific UI templates
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
├── static/                  # Static styles and assets
├── media/                   # Media files (course thumbnails)
├── manage.py
├── requirements.txt
├── setup.bat                # Setup script for Windows
├── setup.sh                 # Setup script for Linux
└── .env.example
```
