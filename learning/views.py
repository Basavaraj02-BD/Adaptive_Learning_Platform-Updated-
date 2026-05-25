import json
import random
from datetime import timedelta

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth.models import User
from django.contrib import messages
from django.http import JsonResponse
from django.utils import timezone
from django.db import models
from django.db.models import Avg, Count, Sum
from django.views.decorators.http import require_POST
from django.views.decorators.csrf import csrf_exempt
from django.conf import settings

from .models import (
    UserProfile, Course, Module, LearningMaterial,
    Enrollment, StudentProgress, Exam, Question,
    ExamResult, StudentAnswer, Payment, Notification, ChatMessage,
)
from .forms import (
    UserRegistrationForm, AdminRegistrationForm,
    UserLoginForm, AdminLoginForm,
    UserProfileForm, CourseForm, ExamForm, QuestionForm,
)


# ──────────────────────────────────────────
# HELPERS
# ──────────────────────────────────────────
def is_admin(user):
    return user.is_authenticated and (user.is_superuser or getattr(getattr(user, 'profile', None), 'role', '') == 'admin')

def is_instructor(user):
    return user.is_authenticated and (
        getattr(getattr(user, 'profile', None), 'role', '') == 'instructor'
    )
def send_notification(recipient, title, message, notif_type='system', link=''):
    Notification.objects.create(
        recipient=recipient, title=title,
        message=message, notif_type=notif_type, link=link
    )


# ══════════════════════════════════════════
#  HOME
# ══════════════════════════════════════════
def home(request):
    if request.user.is_authenticated:
        return redirect('dashboard')
    courses = Course.objects.filter(status='published')[:6]
    return render(request, 'learning/home.html', {'courses': courses})


# ══════════════════════════════════════════
#  AUTH — USER REGISTRATION
# ══════════════════════════════════════════
def user_register(request):
    if request.user.is_authenticated:
        return redirect('dashboard')
    if request.method == 'POST':
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            send_notification(user, 'Welcome! 🎉', f'Welcome to AdaptLearn, {user.first_name}! Start your learning journey.', 'system')
            messages.success(request, f'Account created! Welcome, {user.first_name}!')
            return redirect('dashboard')
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = UserRegistrationForm()
    return render(request, 'registration/user_register.html', {'form': form})


# ══════════════════════════════════════════
#  AUTH — ADMIN REGISTRATION
# ══════════════════════════════════════════
def admin_register(request):
    if request.user.is_authenticated:
        return redirect('dashboard')
    
    # Check if an admin already exists
    if User.objects.filter(is_superuser=True).exists() or UserProfile.objects.filter(role='admin').exists():
        messages.error(request, 'An admin is already registered. Only one admin is allowed on this platform.')
        return redirect('user_login')

    if request.method == 'POST':
        form = AdminRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, f'Admin account created! Welcome, {user.first_name}!')
            return redirect('admin_dashboard')
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = AdminRegistrationForm()
    return render(request, 'registration/admin_register.html', {'form': form})


# ══════════════════════════════════════════
#  AUTH — USER LOGIN
# ══════════════════════════════════════════
def user_login(request):
    if request.user.is_authenticated:
        return redirect('dashboard')
    if request.method == 'POST':
        form = UserLoginForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            messages.success(request, f'Welcome back, {user.first_name or user.username}!')
            next_url = request.GET.get('next', 'dashboard')
            return redirect(next_url)
        else:
            messages.error(request, 'Invalid username or password.')
    else:
        form = UserLoginForm()
    return render(request, 'registration/user_login.html', {'form': form})


# ══════════════════════════════════════════
#  AUTH — ADMIN LOGIN
# ══════════════════════════════════════════
def admin_login(request):
    if request.user.is_authenticated and is_admin(request.user):
        return redirect('admin_dashboard')
    if request.method == 'POST':
        form = AdminLoginForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            if user.is_staff or user.is_superuser:
                login(request, user)
                messages.success(request, f'Admin logged in! Welcome, {user.first_name or user.username}!')
                return redirect('admin_dashboard')
            else:
                messages.error(request, 'You do not have admin privileges.')
        else:
            messages.error(request, 'Invalid admin credentials.')
    else:
        form = AdminLoginForm()
    return render(request, 'registration/admin_login.html', {'form': form})


# ══════════════════════════════════════════
#  AUTH — LOGOUT
# ══════════════════════════════════════════
def user_logout(request):
    logout(request)
    messages.info(request, 'You have been logged out.')
    return redirect('user_login')


# ══════════════════════════════════════════
#  STUDENT DASHBOARD
# ══════════════════════════════════════════
@login_required
def dashboard(request):
    user = request.user
    enrollments = Enrollment.objects.filter(student=user, status='active').select_related('course')
    recent_results = ExamResult.objects.filter(student=user).select_related('exam')[:5]
    notifications  = Notification.objects.filter(recipient=user, is_read=False)[:5]
    total_courses  = enrollments.count()
    completed      = enrollments.filter(status='completed').count()
    avg_score      = ExamResult.objects.filter(student=user).aggregate(a=Avg('percentage'))['a'] or 0

    # Adaptive recommendation
    profile = getattr(user, 'profile', None)
    skill   = profile.skill_level if profile else 'beginner'
    recommended = Course.objects.filter(status='published', difficulty=skill).exclude(
        id__in=enrollments.values_list('course_id', flat=True)
    )[:4]

    context = {
        'enrollments': enrollments,
        'recent_results': recent_results,
        'notifications': notifications,
        'total_courses': total_courses,
        'completed': completed,
        'avg_score': round(avg_score, 1),
        'recommended': recommended,
    }
    return render(request, 'learning/dashboard.html', context)


# ══════════════════════════════════════════
#  ADMIN DASHBOARD
# ══════════════════════════════════════════
@login_required
def admin_dashboard(request):
    if not is_admin(request.user):
        messages.error(request, 'Admin access required.')
        return redirect('dashboard')

    total_users   = User.objects.count()
    total_courses = Course.objects.count()
    total_enrollments = Enrollment.objects.count()
    total_revenue = Payment.objects.filter(status='completed').aggregate(s=Sum('amount'))['s'] or 0
    recent_users  = User.objects.order_by('-date_joined')[:10]
    recent_payments = Payment.objects.select_related('student','course').order_by('-created_at')[:10]
    course_stats  = Course.objects.annotate(enrolled=Count('enrollments')).order_by('-enrolled')[:8]

    context = {
        'total_users': total_users,
        'total_courses': total_courses,
        'total_enrollments': total_enrollments,
        'total_revenue': total_revenue,
        'recent_users': recent_users,
        'recent_payments': recent_payments,
        'course_stats': course_stats,
    }
    return render(request, 'learning/admin_dashboard.html', context)


# ══════════════════════════════════════════
#  COURSES
# ══════════════════════════════════════════
def course_list(request):
    courses = Course.objects.filter(status='published')
    difficulty = request.GET.get('difficulty', '')
    search     = request.GET.get('q', '')
    if difficulty:
        courses = courses.filter(difficulty=difficulty)
    if search:
        courses = courses.filter(title__icontains=search)
    return render(request, 'learning/course_list.html', {'courses': courses, 'difficulty': difficulty, 'search': search})


@login_required
def course_detail(request, slug):
    course = get_object_or_404(Course, slug=slug)
    modules = Module.objects.filter(course=course).prefetch_related('materials')
    is_enrolled = Enrollment.objects.filter(student=request.user, course=course).exists()
    enrollment = Enrollment.objects.filter(student=request.user, course=course).first()
    return render(request, 'learning/course_detail.html', {
        'course': course, 'modules': modules,
        'is_enrolled': is_enrolled, 'enrollment': enrollment,
    })


@login_required
def enroll_course(request, course_id):
    course = get_object_or_404(Course, id=course_id)
    if Enrollment.objects.filter(student=request.user, course=course).exists():
        messages.warning(request, 'Already enrolled.')
        return redirect('course_detail', slug=course.slug)

    if course.is_free or course.price == 0:
        Enrollment.objects.create(student=request.user, course=course)
        Payment.objects.create(student=request.user, course=course, amount=0,
                               status='completed', payment_method='free',
                               transaction_id=f'FREE-{request.user.id}-{course.id}-{timezone.now().timestamp():.0f}')
        course.total_enrolled += 1
        course.save(update_fields=['total_enrolled'])
        send_notification(request.user, 'Enrolled! 🎓', f'You joined "{course.title}"', 'enrollment', f'/courses/{course.slug}/')
        messages.success(request, f'Successfully enrolled in {course.title}!')
    else:
        return redirect('payment_page', course_id=course.id)
    return redirect('course_detail', slug=course.slug)


@login_required
def module_detail(request, module_id):
    module  = get_object_or_404(Module, id=module_id)
    is_enrolled = Enrollment.objects.filter(student=request.user, course=module.course).exists()
    if not is_enrolled:
        messages.error(request, 'Enroll first.')
        return redirect('course_detail', slug=module.course.slug)
    materials = module.materials.all()
    enrollment = Enrollment.objects.get(student=request.user, course=module.course)
    # Update progress
    completed_ids = StudentProgress.objects.filter(
        student=request.user, is_completed=True,
        material__module__course=module.course
    ).values_list('material_id', flat=True)
    total_mats = LearningMaterial.objects.filter(module__course=module.course).count()
    pct = (len(completed_ids) / total_mats * 100) if total_mats else 0
    enrollment.completion_percent = round(pct, 1)
    enrollment.save(update_fields=['completion_percent'])
    return render(request, 'learning/module_detail.html', {
        'module': module, 'materials': materials,
        'completed_ids': list(completed_ids),
    })


@login_required
@require_POST
def mark_material_complete(request, material_id):
    material = get_object_or_404(LearningMaterial, id=material_id)
    enrollment = get_object_or_404(Enrollment, student=request.user, course=material.module.course)
    progress, created = StudentProgress.objects.get_or_create(
        student=request.user, material=material,
        defaults={'enrollment': enrollment}
    )
    progress.is_completed = True
    progress.save()
    return JsonResponse({'status': 'ok'})


# ══════════════════════════════════════════
#  EXAMS
# ══════════════════════════════════════════
@login_required
def exam_list(request):
    enrollments = Enrollment.objects.filter(student=request.user).values_list('course_id', flat=True)
    exams = Exam.objects.filter(course_id__in=enrollments, is_active=True)
    return render(request, 'learning/exam_list.html', {'exams': exams})


@login_required
def take_exam(request, exam_id):
    exam = get_object_or_404(Exam, id=exam_id)
    enrollment = get_object_or_404(Enrollment, student=request.user, course=exam.course)

    attempts = ExamResult.objects.filter(student=request.user, exam=exam).count()
    if attempts >= exam.max_attempts:
        messages.error(request, f'Max attempts ({exam.max_attempts}) reached.')
        return redirect('exam_list')

    questions = list(exam.questions.all())
    if exam.shuffle_questions:
        random.shuffle(questions)

    if request.method == 'POST':
        result = ExamResult.objects.create(
            student=request.user, exam=exam,
            attempt_number=attempts + 1,
            total_marks=exam.total_marks,
            submitted_at=timezone.now(),
        )
        score = 0
        for q in questions:
            ans = request.POST.get(f'q_{q.id}', '').strip()
            is_correct = ans.lower() == q.correct_answer.lower()
            marks = q.marks if is_correct else 0
            score += marks
            StudentAnswer.objects.create(
                result=result, question=q,
                given_answer=ans, is_correct=is_correct, marks_obtained=marks
            )
        pct = (score / exam.total_marks * 100) if exam.total_marks else 0
        status = 'pass' if score >= exam.pass_marks else 'fail'
        result.score = score
        result.percentage = round(pct, 2)
        result.status = status
        # AI feedback
        result.ai_feedback = generate_ai_feedback(request.user, exam, score, pct)
        result.save()
        send_notification(request.user, 'Exam Submitted ✅',
                          f'"{exam.title}" — {pct:.1f}% — {status.upper()}', 'result', f'/results/{result.id}/')
        messages.success(request, 'Exam submitted!')
        return redirect('exam_result', result_id=result.id)

    return render(request, 'learning/take_exam.html', {
        'exam': exam, 'questions': questions,
        'duration': exam.duration_mins,
    })


@login_required
def exam_result(request, result_id):
    result = get_object_or_404(ExamResult, id=result_id, student=request.user)
    answers = result.answers.select_related('question')
    return render(request, 'learning/exam_result.html', {'result': result, 'answers': answers})


def generate_ai_feedback(user, exam, score, pct):
    """Generate adaptive AI feedback (fallback if API key not set)."""
    if pct >= 90:
        return f"Outstanding performance, {user.first_name}! You scored {pct:.1f}%. You've mastered this topic — consider tackling the advanced exam!"
    elif pct >= 70:
        return f"Great work, {user.first_name}! You scored {pct:.1f}%. Review the questions you missed and you'll be fully prepared."
    elif pct >= 50:
        return f"Good effort, {user.first_name}. You scored {pct:.1f}%. Focus on the areas where you lost marks and try again."
    else:
        return f"Don't give up, {user.first_name}! You scored {pct:.1f}%. We recommend revisiting the learning materials for this module."


# ══════════════════════════════════════════
#  PAYMENT
# ══════════════════════════════════════════
@login_required
def payment_page(request, course_id):
    course = get_object_or_404(Course, id=course_id)
    if request.method == 'POST':
        # Simulate payment success (integrate Stripe/Razorpay in production)
        txn_id = f'TXN-{request.user.id}-{course.id}-{timezone.now().timestamp():.0f}'
        payment = Payment.objects.create(
            student=request.user, course=course,
            amount=course.price, status='completed',
            payment_method='card', transaction_id=txn_id,
            paid_at=timezone.now(),
        )
        Enrollment.objects.get_or_create(student=request.user, course=course)
        course.total_enrolled += 1
        course.save(update_fields=['total_enrolled'])
        send_notification(request.user, 'Payment Successful 💳',
                          f'₹{course.price} paid for "{course.title}"', 'payment')
        messages.success(request, 'Payment successful! You are now enrolled.')
        return redirect('course_detail', slug=course.slug)
    return render(request, 'learning/payment.html', {
        'course': course,
        'stripe_public_key': settings.STRIPE_PUBLIC_KEY,
    })


# ══════════════════════════════════════════
#  NOTIFICATIONS
# ══════════════════════════════════════════
@login_required
def notifications(request):
    notifs = Notification.objects.filter(recipient=request.user)
    notifs.filter(is_read=False).update(is_read=True)
    return render(request, 'learning/notifications.html', {'notifications': notifs})


@login_required
@require_POST
def mark_notification_read(request, notif_id):
    notif = get_object_or_404(Notification, id=notif_id, recipient=request.user)
    notif.is_read = True
    notif.save()
    return JsonResponse({'status': 'ok'})


# ══════════════════════════════════════════
#  PROFILE
# ══════════════════════════════════════════
@login_required
def profile(request):
    profile_obj, _ = UserProfile.objects.get_or_create(user=request.user)
    if request.method == 'POST':
        form = UserProfileForm(request.POST, request.FILES, instance=profile_obj)
        if form.is_valid():
            form.save()
            request.user.first_name = request.POST.get('first_name', request.user.first_name)
            request.user.last_name  = request.POST.get('last_name', request.user.last_name)
            request.user.email      = request.POST.get('email', request.user.email)
            request.user.save()
            messages.success(request, 'Profile updated!')
            return redirect('profile')
    else:
        form = UserProfileForm(instance=profile_obj, initial={
            'first_name': request.user.first_name,
            'last_name': request.user.last_name,
            'email': request.user.email,
        })
    results = ExamResult.objects.filter(student=request.user)
    return render(request, 'learning/profile.html', {'form': form, 'results': results, 'profile_obj': profile_obj})


# ══════════════════════════════════════════
#  AI CHATBOT
# ══════════════════════════════════════════
@login_required
def chatbot_page(request):
    messages_qs = ChatMessage.objects.filter(user=request.user).order_by('created_at')
    return render(request, 'learning/chatbot.html', {'chat_messages': messages_qs})


@login_required
@require_POST
def chatbot_api(request):
    try:
        data = json.loads(request.body)
        user_message = data.get('message', '').strip()
        if not user_message:
            return JsonResponse({'error': 'Empty message'}, status=400)

        # Save user message
        ChatMessage.objects.create(user=request.user, role='user', content=user_message)

        # Build history
        history = list(ChatMessage.objects.filter(user=request.user).order_by('created_at')
                       .values('role', 'content'))
        messages_payload = [{'role': m['role'], 'content': m['content']} for m in history]

        api_key = settings.ANTHROPIC_API_KEY

        if api_key:
            import anthropic
            client = anthropic.Anthropic(api_key=api_key)
            response = client.messages.create(
                model='claude-3-5-sonnet-20240620',
                max_tokens=1024,
                system=(
                    "You are AdaptBot, an intelligent learning assistant for the AdaptLearn platform. "
                    "Help students with course content, exam tips, study strategies, and learning guidance. "
                    "Be encouraging, clear, and concise. Use markdown formatting where helpful."
                ),
                messages=messages_payload,
            )
            reply = response.content[0].text
        else:
            # Fallback demo replies
            replies = [
                "I'm AdaptBot! I'm here to help with your studies. Ask me anything about your courses or exams!",
                "Great question! Focus on reviewing the key concepts first, then practice with the exam questions.",
                "I recommend starting with the beginner modules and progressing gradually. Consistency is key!",
                "For best results, study for 25 minutes then take a 5-minute break (Pomodoro technique)!",
            ]
            reply = random.choice(replies)

        # Save assistant reply
        ChatMessage.objects.create(user=request.user, role='assistant', content=reply)
        return JsonResponse({'reply': reply})

    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


# ══════════════════════════════════════════
#  ADMIN — MANAGE USERS
# ══════════════════════════════════════════
@login_required
def admin_users(request):
    if not is_admin(request.user):
        return redirect('dashboard')
    users = User.objects.select_related('profile').order_by('-date_joined')
    return render(request, 'learning/admin_users.html', {'users': users})


@login_required
def admin_courses(request):
    if not is_admin(request.user):
        return redirect('dashboard')
    courses = Course.objects.annotate(enrolled=Count('enrollments')).order_by('-created_at')
    return render(request, 'learning/admin_courses.html', {'courses': courses})


@login_required
def admin_toggle_user(request, user_id):
    if not is_admin(request.user):
        return redirect('dashboard')
    target = get_object_or_404(User, id=user_id)
    target.is_active = not target.is_active
    target.save()
    status = 'activated' if target.is_active else 'deactivated'
    messages.success(request, f'User {target.username} {status}.')
    return redirect('admin_users')


# ══════════════════════════════════════════
#  LEADERBOARD
# ══════════════════════════════════════════
# ══════════════════════════════════════════
#  ANALYTICS
# ══════════════════════════════════════════
@login_required
def analytics(request):
    user = request.user
    enrollments = Enrollment.objects.filter(student=user).select_related('course')
    exam_results = ExamResult.objects.filter(student=user).select_related('exam').order_by('started_at')

    total_enrolled = enrollments.count()
    total_exams    = exam_results.count()
    avg_score      = round(exam_results.aggregate(a=Avg('percentage'))['a'] or 0, 1)
    pass_count     = exam_results.filter(status='pass').count()
    pass_rate      = round((pass_count / total_exams * 100) if total_exams else 0, 1)
    pass_mark      = 40

    # Score trend data
    score_data = []
    for r in exam_results[:12]:
        score_data.append({'label': r.exam.title[:20], 'score': float(r.percentage)})

    # Type distribution
    from django.db.models import Count as DjCount
    type_counts = exam_results.values('exam__exam_type').annotate(c=DjCount('id'))
    type_map    = {'module': 'Module', 'final': 'Final', 'practice': 'Practice'}
    type_data   = [{'label': type_map.get(t['exam__exam_type'], t['exam__exam_type']), 'count': t['c']} for t in type_counts]
    if not type_data:
        type_data = [{'label': 'No Data', 'count': 1}]

    # Radar data (difficulty breakdown)
    difficulties = ['easy', 'medium', 'hard']
    radar_scores = []
    for d in difficulties:
        from .models import StudentAnswer
        answers = StudentAnswer.objects.filter(
            result__student=user,
            question__difficulty=d,
        )
        total = answers.count()
        correct = answers.filter(is_correct=True).count()
        radar_scores.append(round((correct / total * 100) if total else 0, 1))
    radar_data = {
        'labels': ['Easy Questions', 'Medium Questions', 'Hard Questions', 'MCQ', 'Theory'],
        'values': radar_scores + [avg_score, max(0, avg_score - 10)],
    }
    radar_data['labels'] = radar_data['labels'][:len(radar_data['values'])]

    # Activity heatmap (12 weeks × 7 days = 84 cells)
    activity_data = [0] * 84
    from django.utils import timezone as tz
    now = tz.now()
    for r in exam_results:
        if r.submitted_at:
            delta = (now - r.submitted_at).days
            if delta < 84:
                idx = 83 - delta
                activity_data[idx] = min(activity_data[idx] + 1, 3)
    for p in StudentProgress.objects.filter(student=user):
        if p.last_accessed:
            delta = (now - p.last_accessed).days
            if delta < 84:
                idx = 83 - delta
                activity_data[idx] = min(activity_data[idx] + 1, 3)

    context = {
        'enrollments': enrollments,
        'exam_results': exam_results[:10],
        'total_enrolled': total_enrolled,
        'total_exams': total_exams,
        'avg_score': avg_score,
        'pass_rate': pass_rate,
        'pass_mark': pass_mark,
        'score_data': json.dumps(score_data),
        'type_data': json.dumps(type_data),
        'radar_data': json.dumps(radar_data),
        'activity_data': json.dumps(activity_data),
    }
    return render(request, 'learning/analytics.html', context)


# ══════════════════════════════════════════
#  CERTIFICATE
# ══════════════════════════════════════════
@login_required
def certificate(request, enrollment_id):
    enrollment = get_object_or_404(Enrollment, id=enrollment_id, student=request.user)
    if enrollment.completion_percent < 100 and not enrollment.certificate_issued:
        messages.warning(request, 'Complete the course first to get your certificate.')
        return redirect('course_detail', slug=enrollment.course.slug)
    # Mark certificate issued
    if not enrollment.certificate_issued:
        enrollment.certificate_issued = True
        if not enrollment.completed_at:
            enrollment.completed_at = timezone.now()
            enrollment.status = 'completed'
        enrollment.save()
    best_result = ExamResult.objects.filter(
        student=request.user, exam__course=enrollment.course, status='pass'
    ).order_by('-percentage').first()
    return render(request, 'learning/certificate.html', {
        'enrollment': enrollment,
        'best_result': best_result,
    })


# ══════════════════════════════════════════
#  CREATE COURSE (Instructor)
# ══════════════════════════════════════════
@login_required
def create_course(request):
    if not is_instructor(request.user):
        messages.error(request, 'Only instructors can create courses.')
        return redirect('dashboard')
    if request.method == 'POST':
        form = CourseForm(request.POST, request.FILES)
        if form.is_valid():
            course = form.save(commit=False)
            course.instructor = request.user
            # Handle is_free from hidden input
            course.is_free = request.POST.get('is_free', 'false') == 'true'
            if course.is_free:
                course.price = 0
            # Handle tags from comma-separated hidden input
            course.tags = request.POST.get('tags', '')
            course.save()
            send_notification(request.user, 'Course Created! 🎉',
                              f'Your course "{course.title}" has been created.', 'system')
            messages.success(request, f'Course "{course.title}" created successfully!')
            return redirect('course_detail', slug=course.slug)
    else:
        form = CourseForm()
    return render(request, 'learning/create_course.html', {'form': form})


# ══════════════════════════════════════════
#  PASSWORD CHANGE
# ══════════════════════════════════════════
@login_required
def change_password(request):
    from django.contrib.auth import update_session_auth_hash
    from django.contrib.auth.forms import PasswordChangeForm
    if request.method == 'POST':
        form = PasswordChangeForm(request.user, request.POST)
        if form.is_valid():
            user = form.save()
            update_session_auth_hash(request, user)
            messages.success(request, 'Password changed successfully!')
            return redirect('profile')
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = PasswordChangeForm(request.user)
    # Style the form fields
    for field in form.fields.values():
        field.widget.attrs.update({'class': 'glass-input'})
    return render(request, 'learning/change_password.html', {'form': form})


# ══════════════════════════════════════════
#  SEARCH
# ══════════════════════════════════════════
def search(request):
    q = request.GET.get('q', '').strip()
    courses = []
    if q:
        courses = Course.objects.filter(
            status='published'
        ).filter(
            models.Q(title__icontains=q) |
            models.Q(description__icontains=q) |
            models.Q(tags__icontains=q)
        )
    return render(request, 'learning/search_results.html', {'courses': courses, 'query': q})


# ══════════════════════════════════════════
#  ADD EXAM QUESTION (Instructor)
# ══════════════════════════════════════════
@login_required
def add_question(request, exam_id):
    exam = get_object_or_404(Exam, id=exam_id)
    if not is_instructor(request.user) and exam.course.instructor != request.user:
        messages.error(request, 'Permission denied.')
        return redirect('dashboard')
    if request.method == 'POST':
        form = QuestionForm(request.POST, request.FILES)
        if form.is_valid():
            q = form.save(commit=False)
            q.exam = exam
            # Build options from 4 separate fields
            opts = [
                request.POST.get('option_a', ''),
                request.POST.get('option_b', ''),
                request.POST.get('option_c', ''),
                request.POST.get('option_d', ''),
            ]
            opts = [o for o in opts if o.strip()]
            q.set_options(opts)
            q.save()
            messages.success(request, 'Question added!')
            return redirect('manage_exam', exam_id=exam.id)
    else:
        form = QuestionForm()
    return render(request, 'learning/add_question.html', {'form': form, 'exam': exam})


# ══════════════════════════════════════════
#  MANAGE EXAM (Instructor)
# ══════════════════════════════════════════
@login_required
def manage_exam(request, exam_id):
    exam = get_object_or_404(Exam, id=exam_id)
    if not is_instructor(request.user) and not is_admin(request.user):
        messages.error(request, 'Permission denied.')
        return redirect('dashboard')
    questions = exam.questions.all()
    return render(request, 'learning/manage_exam.html', {'exam': exam, 'questions': questions})


# ══════════════════════════════════════════
#  INSTRUCTOR DASHBOARD
# ══════════════════════════════════════════
@login_required
def instructor_dashboard(request):
    if not is_instructor(request.user):
        return redirect('dashboard')
    from .models import CourseReview
    my_courses = Course.objects.filter(instructor=request.user).annotate(
        student_count=Count('enrollments')
    ).order_by('-created_at')

    total_students = Enrollment.objects.filter(
        course__instructor=request.user
    ).values('student').distinct().count()

    total_revenue = Payment.objects.filter(
        course__instructor=request.user, status='completed'
    ).aggregate(s=Sum('amount'))['s'] or 0

    avg_rating = CourseReview.objects.filter(
        course__instructor=request.user
    ).aggregate(a=Avg('rating'))['a'] or 0

    recent_enrollments = Enrollment.objects.filter(
        course__instructor=request.user
    ).select_related('student', 'course').order_by('-enrolled_at')[:10]

    # Exam stats
    exam_stats = []
    for course in my_courses[:5]:
        for exam in course.exams.all():
            results = ExamResult.objects.filter(exam=exam)
            count = results.count()
            if count:
                avg_pct = results.aggregate(a=Avg('percentage'))['a'] or 0
                pass_rate = results.filter(status='pass').count() / count * 100
                exam_stats.append({
                    'title': exam.title,
                    'avg_pct': round(avg_pct, 1),
                    'attempts': count,
                    'pass_rate': round(pass_rate, 1),
                })

    return render(request, 'learning/instructor_dashboard.html', {
        'my_courses': my_courses,
        'total_students': total_students,
        'total_revenue': total_revenue,
        'avg_rating': round(avg_rating, 1),
        'recent_enrollments': recent_enrollments,
        'exam_stats': exam_stats[:5],
    })


# ══════════════════════════════════════════
#  COURSE REVIEWS
# ══════════════════════════════════════════
from .models import CourseReview, DiscussionThread, DiscussionReply

@login_required
def course_reviews(request, slug):
    course = get_object_or_404(Course, slug=slug)
    reviews = CourseReview.objects.filter(course=course).select_related('student')
    total_reviews = reviews.count()
    avg_rating = reviews.aggregate(a=Avg('rating'))['a'] or 0
    is_enrolled = Enrollment.objects.filter(student=request.user, course=course).exists()
    user_reviewed = reviews.filter(student=request.user).exists()

    # Star breakdown
    star_breakdown = []
    for star in range(5, 0, -1):
        count = reviews.filter(rating=star).count()
        pct = (count / total_reviews * 100) if total_reviews else 0
        star_breakdown.append((star, count, round(pct, 1)))

    return render(request, 'learning/course_reviews.html', {
        'course': course,
        'reviews': reviews,
        'total_reviews': total_reviews,
        'avg_rating': round(avg_rating, 1),
        'is_enrolled': is_enrolled,
        'user_reviewed': user_reviewed,
        'star_breakdown': star_breakdown,
    })


@login_required
@require_POST
def submit_review(request, course_id):
    course = get_object_or_404(Course, id=course_id)
    if not Enrollment.objects.filter(student=request.user, course=course).exists():
        messages.error(request, 'You must be enrolled to review this course.')
        return redirect('course_detail', slug=course.slug)
    rating  = int(request.POST.get('rating', 5))
    comment = request.POST.get('comment', '').strip()
    rating  = max(1, min(5, rating))
    review, created = CourseReview.objects.update_or_create(
        course=course, student=request.user,
        defaults={'rating': rating, 'comment': comment}
    )
    # Update course average rating
    avg = CourseReview.objects.filter(course=course).aggregate(a=Avg('rating'))['a'] or 0
    course.rating = round(avg, 1)
    course.save(update_fields=['rating'])
    messages.success(request, 'Review submitted! Thank you.')
    return redirect('course_reviews', slug=course.slug)


# ══════════════════════════════════════════
#  DISCUSSION FORUM
# ══════════════════════════════════════════
@login_required
def discussion(request, slug):
    course = get_object_or_404(Course, slug=slug)
    if not Enrollment.objects.filter(student=request.user, course=course).exists():
        messages.error(request, 'Enroll in the course to access discussions.')
        return redirect('course_detail', slug=course.slug)
    threads = DiscussionThread.objects.filter(course=course).select_related('author').prefetch_related('replies')
    return render(request, 'learning/discussion.html', {
        'course': course, 'threads': threads,
    })


@login_required
@require_POST
def post_thread(request, course_id):
    course = get_object_or_404(Course, id=course_id)
    title   = request.POST.get('title', '').strip()
    content = request.POST.get('content', '').strip()
    if title and content:
        DiscussionThread.objects.create(course=course, author=request.user, title=title, content=content)
        messages.success(request, 'Thread posted!')
    return redirect('discussion', slug=course.slug)


@login_required
@require_POST
def post_reply(request, thread_id):
    thread  = get_object_or_404(DiscussionThread, id=thread_id)
    content = request.POST.get('content', '').strip()
    if content:
        DiscussionReply.objects.create(thread=thread, author=request.user, content=content)
        # Notify thread author
        if thread.author != request.user:
            send_notification(
                thread.author, 'New reply on your thread 💬',
                f'{request.user.username} replied to "{thread.title}"',
                'system', f'/courses/{thread.course.slug}/discussion/'
            )
    return redirect('discussion', slug=thread.course.slug)


# ══════════════════════════════════════════



# ══════════════════════════════════════════
#  PROGRESS REPORT (JSON export)
# ══════════════════════════════════════════
@login_required
def progress_report(request):
    from django.http import JsonResponse as JR
    enrollments = Enrollment.objects.filter(student=request.user).select_related('course')
    results     = ExamResult.objects.filter(student=request.user).select_related('exam')
    data = {
        'student': request.user.get_full_name() or request.user.username,
        'email':   request.user.email,
        'generated_at': timezone.now().isoformat(),
        'enrollments': [
            {
                'course': e.course.title,
                'status': e.status,
                'completion': e.completion_percent,
                'enrolled_at': e.enrolled_at.isoformat(),
            } for e in enrollments
        ],
        'exam_results': [
            {
                'exam': r.exam.title,
                'course': r.exam.course.title,
                'score': r.score,
                'percentage': r.percentage,
                'status': r.status,
                'date': r.submitted_at.isoformat() if r.submitted_at else None,
            } for r in results
        ],
    }
    response = JR(data)
    response['Content-Disposition'] = 'attachment; filename="progress_report.json"'
    return response


def error_404(request, exception=None):
    return render(request, '404.html', status=404)

def error_500(request):
    return render(request, '500.html', status=500)


@login_required
def leaderboard(request):
    top_students = User.objects.annotate(
        avg_score=Avg('exam_results__percentage'),
        total_exams=Count('exam_results'),
    ).filter(total_exams__gt=0).order_by('-avg_score')[:20]
    return render(request, 'learning/leaderboard.html', {'top_students': top_students})
