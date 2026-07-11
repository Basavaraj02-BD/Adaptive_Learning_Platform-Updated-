import json
import random
from datetime import timedelta
import stripe

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
from django.urls import reverse

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


# HELPERS

def is_admin(user):
    return user.is_authenticated and (
                user.is_superuser or getattr(getattr(user, 'profile', None), 'role', '') == 'admin')


def is_instructor(user):
    return user.is_authenticated and (
            getattr(getattr(user, 'profile', None), 'role', '') == 'instructor'
    )


def send_notification(recipient, title, message, notif_type='system', link=''):
    Notification.objects.create(
        recipient=recipient, title=title,
        message=message, notif_type=notif_type, link=link
    )


#  HOME

def home(request):
    if request.user.is_authenticated:
        if is_admin(request.user):
            return redirect('admin_dashboard')
        elif is_instructor(request.user):
            return redirect('instructor_dashboard')
        else:
            return redirect('dashboard')
    courses = Course.objects.filter(status='published')[:6]
    return render(request, 'learning/home.html', {'courses': courses})


#  AUTH — USER REGISTRATION

def user_register(request):
    if request.user.is_authenticated:
        return redirect('dashboard')
    if request.method == 'POST':
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            send_notification(user, 'Welcome! 🎉',
                              f'Welcome to AdaptLearn, {user.first_name}! Start your learning journey.', 'system')
            messages.success(request, f'Account created! Welcome, {user.first_name}!')
            return redirect('dashboard')
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = UserRegistrationForm()
    return render(request, 'registration/user_register.html', {'form': form})


#  AUTH — ADMIN REGISTRATION

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


#  AUTH — CAPTCHA GENERATOR

def generate_captcha(request):
    from PIL import Image, ImageDraw, ImageFont
    import random
    import io
    from django.http import HttpResponse

    # Generate random 5-character string (omit ambiguous characters like 0, O, 1, I)
    chars = 'ABCDEFGHJKLMNPQRSTUVWXYZ23456789'
    code = ''.join(random.choice(chars) for _ in range(5))
    request.session['login_captcha'] = code

    # Create image
    img = Image.new('RGB', (120, 45), color=(20, 24, 33))  # Dark theme background
    draw = ImageDraw.Draw(img)

    # Draw noise lines
    for _ in range(8):
        x1 = random.randint(0, 120)
        y1 = random.randint(0, 45)
        x2 = random.randint(0, 120)
        y2 = random.randint(0, 45)
        draw.line([(x1, y1), (x2, y2)], fill=(108, 99, 255), width=1)

    # Draw text
    try:
        font = ImageFont.truetype("arial.ttf", 22)
    except IOError:
        font = ImageFont.load_default()

    # Draw characters with slight random spacing/position
    for i, char in enumerate(code):
        x = 12 + i * 20 + random.randint(-2, 2)
        y = 8 + random.randint(-4, 4)
        draw.text((x, y), char, font=font, fill=(0, 212, 255))

    # Save to buffer
    buf = io.BytesIO()
    img.save(buf, format='png')
    buf.seek(0)

    return HttpResponse(buf.read(), content_type='image/png')


#  AUTH — USER LOGIN

def user_login(request):
    if request.user.is_authenticated:
        if is_admin(request.user):
            return redirect('admin_dashboard')
        elif is_instructor(request.user):
            return redirect('instructor_dashboard')
        else:
            return redirect('dashboard')
    if request.method == 'POST':
        captcha_input = request.POST.get('captcha', '').strip().upper()
        session_captcha = request.session.get('login_captcha', '')
        if not session_captcha or captcha_input != session_captcha:
            messages.error(request, 'Invalid captcha. Please try again.')
            form = UserLoginForm(request, data=request.POST)
            return render(request, 'registration/user_login.html', {'form': form})

        form = UserLoginForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            messages.success(request, f'Welcome back, {user.first_name or user.username}!')
            next_url = request.GET.get('next')
            if next_url:
                return redirect(next_url)
            if is_admin(user):
                return redirect('admin_dashboard')
            elif is_instructor(user):
                return redirect('instructor_dashboard')
            return redirect('dashboard')
        else:
            messages.error(request, 'Invalid username or password.')
    else:
        form = UserLoginForm()
    return render(request, 'registration/user_login.html', {'form': form})


#  AUTH — ADMIN LOGIN

def admin_login(request):
    if request.user.is_authenticated and is_admin(request.user):
        return redirect('admin_dashboard')
    if request.method == 'POST':
        captcha_input = request.POST.get('captcha', '').strip().upper()
        session_captcha = request.session.get('login_captcha', '')
        if not session_captcha or captcha_input != session_captcha:
            messages.error(request, 'Invalid captcha. Please try again.')
            form = AdminLoginForm(request, data=request.POST)
            return render(request, 'registration/admin_login.html', {'form': form})

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


#  AUTH — LOGOUT

def user_logout(request):
    logout(request)
    messages.info(request, 'You have been logged out.')
    return redirect('user_login')


#  STUDENT DASHBOARD

@login_required
def dashboard(request):
    user = request.user
    enrollments = Enrollment.objects.filter(student=user, status__in=['active', 'completed']).select_related('course')
    recent_results = ExamResult.objects.filter(student=user).select_related('exam')[:5]
    notifications = Notification.objects.filter(recipient=user, is_read=False)[:5]
    total_courses = enrollments.count()
    completed = enrollments.filter(models.Q(status='completed') | models.Q(completion_percent__gte=100)).count()
    avg_score = ExamResult.objects.filter(student=user).aggregate(a=Avg('percentage'))['a'] or 0

    # Annotate each enrollment with total time spent (in minutes)
    for enr in enrollments:
        total_mins = StudentProgress.objects.filter(
            student=user, enrollment=enr
        ).aggregate(total=Sum('time_spent_mins'))['total'] or 0
        enr.total_time_spent_mins = total_mins
        hours, mins = divmod(total_mins, 60)
        enr.time_spent_display = f"{hours}h {mins}m" if hours else f"{mins}m"

    # Adaptive recommendation
    profile = getattr(user, 'profile', None)
    skill = profile.skill_level if profile else 'beginner'
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


#  ADMIN DASHBOARD

@login_required
def admin_dashboard(request):
    if not is_admin(request.user):
        messages.error(request, 'Admin access required.')
        return redirect('dashboard')

    total_users = User.objects.count()
    total_courses = Course.objects.count()
    total_enrollments = Enrollment.objects.count()
    total_revenue = Payment.objects.filter(status='completed').aggregate(s=Sum('amount'))['s'] or 0
    recent_users = User.objects.order_by('-date_joined')[:10]
    recent_payments = Payment.objects.select_related('student', 'course').order_by('-created_at')[:10]
    course_stats = Course.objects.annotate(enrolled=Count('enrollments')).order_by('-enrolled')[:8]

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


#  COURSES

def course_list(request):
    courses = Course.objects.filter(status='published')
    difficulty = request.GET.get('difficulty', '')
    search = request.GET.get('q', '')
    if difficulty:
        courses = courses.filter(difficulty=difficulty)
    if search:
        courses = courses.filter(title__icontains=search)
    return render(request, 'learning/course_list.html',
                  {'courses': courses, 'difficulty': difficulty, 'search': search})


@login_required
def course_detail(request, slug):
    course = get_object_or_404(Course, slug=slug)
    modules = Module.objects.filter(course=course).prefetch_related('materials')
    is_enrolled = Enrollment.objects.filter(student=request.user, course=course).exists()
    enrollment = Enrollment.objects.filter(student=request.user, course=course).first()

    # Check if the user has paid for this course (completed payment, excluding 'free' method)
    has_paid = Payment.objects.filter(
        student=request.user, course=course, status='completed'
    ).exclude(payment_method='free').exists()

    # Get the first learning material of the entire course
    first_material = LearningMaterial.objects.filter(
        module__course=course
    ).order_by('module__order', 'order').first()
    first_material_id = first_material.id if first_material else None

    return render(request, 'learning/course_detail.html', {
        'course': course, 'modules': modules,
        'is_enrolled': is_enrolled, 'enrollment': enrollment,
        'has_paid': has_paid, 'first_material_id': first_material_id,
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
        send_notification(request.user, 'Enrolled! 🎓', f'You joined "{course.title}"', 'enrollment',
                          f'/courses/{course.slug}/')
        messages.success(request, f'Successfully enrolled in {course.title}!')
    else:
        return redirect('payment_page', course_id=course.id)
    return redirect('course_detail', slug=course.slug)


@login_required
def module_detail(request, module_id):
    module = get_object_or_404(Module, id=module_id)
    is_enrolled = Enrollment.objects.filter(student=request.user, course=module.course).exists()
    if not is_enrolled:
        messages.error(request, 'Enroll first.')
        return redirect('course_detail', slug=module.course.slug)
    materials = module.materials.all()
    enrollment = Enrollment.objects.get(student=request.user, course=module.course)

    # Check if the user has paid for this course (completed payment, excluding 'free' method)
    has_paid = Payment.objects.filter(
        student=request.user, course=module.course, status='completed'
    ).exclude(payment_method='free').exists()

    # Get the first learning material of the entire course
    first_material = LearningMaterial.objects.filter(
        module__course=module.course
    ).order_by('module__order', 'order').first()
    first_material_id = first_material.id if first_material else None

    # Calculate price_to_pay (using same logic: course.price if > 0 else 299.00)
    course = module.course
    price_to_pay = course.price if (course.price and course.price > 0) else 299.00

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
        'has_paid': has_paid,
        'first_material_id': first_material_id,
        'price_to_pay': price_to_pay,
    })


@login_required
@require_POST
def mark_material_complete(request, material_id):
    material = get_object_or_404(LearningMaterial, id=material_id)
    course = material.module.course
    enrollment = get_object_or_404(Enrollment, student=request.user, course=course)

    # If the course is free and user hasn't paid, they can only complete the first lesson
    if course.is_free:
        has_paid = Payment.objects.filter(
            student=request.user, course=course, status='completed'
        ).exclude(payment_method='free').exists()

        if not has_paid:
            first_material = LearningMaterial.objects.filter(
                module__course=course
            ).order_by('module__order', 'order').first()

            if first_material and material.id != first_material.id:
                messages.error(request, 'You must pay to unlock this lesson and mark it complete.')
                return redirect('module_detail', module_id=material.module.id)

    progress, created = StudentProgress.objects.get_or_create(
        student=request.user, material=material,
        defaults={'enrollment': enrollment}
    )
    if not progress.is_completed:
        progress.is_completed = True
        progress.save()

        # Award 10 XP points
        profile, _ = UserProfile.objects.get_or_create(user=request.user)
        profile.total_points += 10
        profile.save()
        messages.success(request, 'Material marked as complete. Earned +10 XP! 🌟')
    else:
        messages.info(request, 'Material is already marked as complete.')

    return redirect('module_detail', module_id=material.module.id)


#  EXAMS

@login_required
def exam_list(request):
    enrollments = Enrollment.objects.filter(student=request.user).values_list('course_id', flat=True)
    exams = Exam.objects.filter(course_id__in=enrollments, is_active=True).select_related('course', 'module')

    # Calculate locked status for each exam
    for exam in exams:
        if exam.course.is_free:
            has_paid = Payment.objects.filter(
                student=request.user, course=exam.course, status='completed'
            ).exclude(payment_method='free').exists()
            if not has_paid:
                first_module = Module.objects.filter(course=exam.course).order_by('order').first()
                exam.is_locked = (exam.module != first_module)
            else:
                exam.is_locked = False
        else:
            exam.is_locked = False

    return render(request, 'learning/exam_list.html', {'exams': exams})


@login_required
def take_exam(request, exam_id):
    exam = get_object_or_404(Exam, id=exam_id)
    enrollment = get_object_or_404(Enrollment, student=request.user, course=exam.course)

    # If the course is free and user hasn't paid, they can only take exams in the first module
    if exam.course.is_free:
        has_paid = Payment.objects.filter(
            student=request.user, course=exam.course, status='completed'
        ).exclude(payment_method='free').exists()

        if not has_paid:
            first_module = Module.objects.filter(course=exam.course).order_by('order').first()
            if exam.module != first_module:
                messages.error(request, 'You must pay to unlock this exam.')
                return redirect('course_detail', slug=exam.course.slug)

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
        # Generate score feedback
        result.ai_feedback = generate_ai_feedback(request.user, exam, score, pct)
        result.save()

        # Award XP if passed and haven't passed before
        xp_earned = 0
        if status == 'pass':
            already_passed = ExamResult.objects.filter(student=request.user, exam=exam, status='pass').exclude(
                id=result.id).exists()
            if not already_passed:
                xp_earned = 100 if exam.exam_type == 'final' else 50
                profile, _ = UserProfile.objects.get_or_create(user=request.user)
                profile.total_points += xp_earned
                profile.save()

        send_notification(request.user, 'Exam Submitted ✅',
                          f'"{exam.title}" — {pct:.1f}% — {status.upper()}', 'result', f'/results/{result.id}/')

        if xp_earned > 0:
            messages.success(request, f'Exam submitted! You passed and earned +{xp_earned} XP! 🏆')
        else:
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
    """Generate course exam feedback based on student score percentages."""
    name = user.first_name or user.username
    if pct >= 90:
        return (
            f"Wow, absolute rockstar move, {name}! 🚀 Scoring {pct:.1f}% on the {exam.title} is incredible. "
            f"You've clearly got a solid handle on this material. Ready to push your boundaries? "
            f"I'd highly recommend checking out some advanced challenges or diving straight into the next module!"
        )
    elif pct >= 70:
        return (
            f"High five, {name}! 🌟 You did great and scored {pct:.1f}%. You're so close to perfection. "
            f"Take a quick peek at the couple of questions that tripped you up, and you'll have this fully mastered. "
            f"Keep up this amazing momentum!"
        )
    elif pct >= 50:
        return (
            f"Good job on completing the exam, {name}! You got {pct:.1f}%. You've got the core basics down, "
            f"but there are a few concepts that could use a quick review. Try revisiting the module's summary articles "
            f"and give it another shot—you've got this!"
        )
    else:
        return (
            f"Don't sweat it, {name}! Learning is all about trial and error, and this is just a stepping stone. "
            f"You got {pct:.1f}%. I'd suggest taking a short break, reviewing the module materials, and asking AdaptBot "
            f"for any clarifications. We believe in you—try again when you're ready! 💪"
        )


#  PAYMENT

@login_required
def payment_page(request, course_id):
    course = get_object_or_404(Course, id=course_id)
    # If the course is free or has a 0 price, charge a default unlock fee of 299.00
    price_to_pay = course.price if (course.price and course.price > 0) else 299.00

    if request.method == 'POST':
        stripe.api_key = settings.STRIPE_SECRET_KEY
        
        success_url = request.build_absolute_uri(reverse('payment_success', args=[course.id])) + "?session_id={CHECKOUT_SESSION_ID}"
        cancel_url = request.build_absolute_uri(reverse('payment_cancel', args=[course.id]))

        try:
            checkout_session = stripe.checkout.Session.create(
                payment_method_types=['card'],
                line_items=[
                    {
                        'price_data': {
                            'currency': 'inr',
                            'product_data': {
                                'name': course.title,
                                'description': course.description[:250],
                            },
                            'unit_amount': int(price_to_pay * 100), # Amount in paise (1 INR = 100 paise)
                        },
                        'quantity': 1,
                    }
                ],
                mode='payment',
                success_url=success_url,
                cancel_url=cancel_url,
                metadata={
                    'course_id': course.id,
                    'student_id': request.user.id
                }
            )
            return redirect(checkout_session.url, code=303)
        except Exception as e:
            messages.error(request, f"Error initializing Stripe Checkout: {str(e)}")
            return redirect('payment_page', course_id=course.id)

    return render(request, 'learning/payment.html', {
        'course': course,
        'price_to_pay': price_to_pay,
        'stripe_public_key': settings.STRIPE_PUBLIC_KEY,
    })


@login_required
def payment_success(request, course_id):
    course = get_object_or_404(Course, id=course_id)
    session_id = request.GET.get('session_id')
    if not session_id:
        messages.error(request, "Invalid payment session.")
        return redirect('payment_page', course_id=course.id)

    stripe.api_key = settings.STRIPE_SECRET_KEY
    try:
        session = stripe.checkout.Session.retrieve(session_id)
        if session.payment_status == 'paid':
            txn_id = session.payment_intent or f'STRIPE-{session_id}'
            
            payment_exists = Payment.objects.filter(transaction_id=txn_id).exists()
            if not payment_exists:
                payment = Payment.objects.create(
                    student=request.user, course=course,
                    amount=course.price if (course.price and course.price > 0) else 299.00,
                    status='completed',
                    payment_method='card', transaction_id=txn_id,
                    paid_at=timezone.now(),
                )
                Enrollment.objects.get_or_create(student=request.user, course=course)
                course.total_enrolled += 1
                course.save(update_fields=['total_enrolled'])
                send_notification(request.user, 'Payment Successful 💳',
                                  f'₹{payment.amount} paid for "{course.title}"', 'payment')
            
            messages.success(request, 'Payment successful! You have unlocked the complete course.')
            return redirect('course_detail', slug=course.slug)
        else:
            messages.error(request, "Payment has not been completed.")
            return redirect('payment_page', course_id=course.id)
    except Exception as e:
        messages.error(request, f"Error verifying payment: {str(e)}")
        return redirect('payment_page', course_id=course.id)


@login_required
def payment_cancel(request, course_id):
    course = get_object_or_404(Course, id=course_id)
    messages.warning(request, "Payment was cancelled. You can try again below.")
    return redirect('payment_page', course_id=course.id)


#  NOTIFICATIONS

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


#  PROFILE

@login_required
def profile(request):
    profile_obj, _ = UserProfile.objects.get_or_create(user=request.user)
    if request.method == 'POST':
        form = UserProfileForm(request.POST, request.FILES, instance=profile_obj)
        if form.is_valid():
            form.save()
            request.user.first_name = request.POST.get('first_name', request.user.first_name)
            request.user.last_name = request.POST.get('last_name', request.user.last_name)
            request.user.email = request.POST.get('email', request.user.email)
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


#  MENTOR CHATBOT

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
                    "You are AdaptBot, a warm, friendly, and highly empathetic learning mentor for the AdaptLearn platform. "
                    "Speak conversationally, encourage the student, and ask light check-in questions to make learning interactive. "
                    "Break down technical concepts using easy-to-understand analogies. Avoid sounding like a dry text generator. "
                    "Use markdown formatting nicely."
                ),
                messages=messages_payload,
            )
            reply = response.content[0].text
        else:
            # Use static replies if API key is not configured
            replies = [
                f"Hey there, {request.user.first_name or request.user.username}! I'm AdaptBot, your study sidekick. What are we learning today? Drop any questions or code snippets here!",
                "Oh, that's a super interesting topic! I always recommend breaking it down: review the core concepts for 15 minutes, write a simple example, and test yourself. What part of it feels the trickiest right now?",
                "Progress is all about small, consistent steps. Don't worry if it doesn't click immediately—try starting with the beginner modules and build up. How can I help clarify things for you?",
                "If your brain is feeling a bit fried, try the Pomodoro technique: study intensely for 25 minutes, then take a guilt-free 5-minute break to stretch. Want to set a goal for the next 25 minutes?",
                "I'm right here with you! If you're stuck on a particular exam or concept, tell me what it is and we can dissect it together. You've got this!"
            ]
            reply = random.choice(replies)

        # Save assistant reply
        ChatMessage.objects.create(user=request.user, role='assistant', content=reply)
        return JsonResponse({'reply': reply})

    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


#  ADMIN — MANAGE USERS

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


#  LEADERBOARD
#  ANALYTICS

@login_required
def analytics(request):
    user = request.user
    enrollments = Enrollment.objects.filter(student=user).select_related('course')
    exam_results = ExamResult.objects.filter(student=user).select_related('exam').order_by('started_at')

    total_enrolled = enrollments.count()
    total_exams = exam_results.count()
    avg_score = round(exam_results.aggregate(a=Avg('percentage'))['a'] or 0, 1)
    pass_count = exam_results.filter(status='pass').count()
    pass_rate = round((pass_count / total_exams * 100) if total_exams else 0, 1)
    pass_mark = 40

    # Score trend data
    score_data = []
    for r in exam_results[:12]:
        score_data.append({'label': r.exam.title[:20], 'score': float(r.percentage)})

    # Type distribution
    from django.db.models import Count as DjCount
    type_counts = exam_results.values('exam__exam_type').annotate(c=DjCount('id'))
    type_map = {'module': 'Module', 'final': 'Final', 'practice': 'Practice'}
    type_data = [{'label': type_map.get(t['exam__exam_type'], t['exam__exam_type']), 'count': t['c']} for t in
                 type_counts]
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


#  CERTIFICATE

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

        # Award 200 XP completion bonus points
        profile, _ = UserProfile.objects.get_or_create(user=request.user)
        profile.total_points += 200
        profile.save()
        messages.success(request, 'Certificate issued! Earned +200 XP for course completion! 🎓')
    best_result = ExamResult.objects.filter(
        student=request.user, exam__course=enrollment.course, status='pass'
    ).order_by('-percentage').first()
    return render(request, 'learning/certificate.html', {
        'enrollment': enrollment,
        'best_result': best_result,
    })


#  CREATE COURSE (Instructor)

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


@login_required
def edit_course(request, course_id):
    course = get_object_or_404(Course, id=course_id, instructor=request.user)
    if request.method == 'POST':
        form = CourseForm(request.POST, request.FILES, instance=course)
        if form.is_valid():
            c = form.save(commit=False)
            c.is_free = request.POST.get('is_free', 'false') == 'true'
            if c.is_free:
                c.price = 0
            c.tags = request.POST.get('tags', '')
            c.save()
            messages.success(request, f'Course "{c.title}" updated successfully!')
            return redirect('instructor_dashboard')
    else:
        form = CourseForm(instance=course)
    return render(request, 'learning/edit_course.html', {'form': form, 'course': course})


@login_required
@require_POST
def delete_course(request, course_id):
    course = get_object_or_404(Course, id=course_id, instructor=request.user)
    title = course.title
    course.delete()
    messages.success(request, f'Course "{title}" has been deleted.')
    return redirect('instructor_dashboard')


#  PASSWORD CHANGE

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


#  SEARCH

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


#  ADD EXAM QUESTION (Instructor)

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


#  MANAGE EXAM (Instructor)

@login_required
def manage_exam(request, exam_id):
    exam = get_object_or_404(Exam, id=exam_id)
    if not is_instructor(request.user) and not is_admin(request.user):
        messages.error(request, 'Permission denied.')
        return redirect('dashboard')
    questions = exam.questions.all()
    return render(request, 'learning/manage_exam.html', {'exam': exam, 'questions': questions})


#  INSTRUCTOR DASHBOARD

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


#  COURSE REVIEWS

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
    rating = int(request.POST.get('rating', 5))
    comment = request.POST.get('comment', '').strip()
    rating = max(1, min(5, rating))
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


#  DISCUSSION FORUM

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
    title = request.POST.get('title', '').strip()
    content = request.POST.get('content', '').strip()
    if title and content:
        DiscussionThread.objects.create(course=course, author=request.user, title=title, content=content)
        messages.success(request, 'Thread posted!')
    return redirect('discussion', slug=course.slug)


@login_required
@require_POST
def post_reply(request, thread_id):
    thread = get_object_or_404(DiscussionThread, id=thread_id)
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


#  PROGRESS REPORT (JSON export)

@login_required
def progress_report(request):
    import io
    from django.http import HttpResponse
    from reportlab.lib.pagesizes import letter
    from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.lib import colors

    enrollments = Enrollment.objects.filter(student=request.user).select_related('course')
    results = ExamResult.objects.filter(student=request.user).select_related('exam')

    buffer = io.BytesIO()
    doc = SimpleDocTemplate(
        buffer,
        pagesize=letter,
        rightMargin=40,
        leftMargin=40,
        topMargin=40,
        bottomMargin=40
    )

    styles = getSampleStyleSheet()

    # Premium color palette
    primary_color = colors.HexColor('#1a1a2e')  # Dark blue/navy
    accent_color = colors.HexColor('#6c63ff')  # Purple accent
    text_color = colors.HexColor('#374151')  # Charcoal body text
    muted_color = colors.HexColor('#9ca3af')  # Muted gray

    title_style = ParagraphStyle(
        'DocTitle',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=22,
        leading=26,
        textColor=primary_color
    )

    section_heading = ParagraphStyle(
        'SectionHeading',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=13,
        leading=17,
        textColor=primary_color,
        spaceAfter=8,
        spaceBefore=14
    )

    body_style = ParagraphStyle(
        'BodyTextCustom',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=10,
        leading=14,
        textColor=text_color
    )

    meta_label_style = ParagraphStyle(
        'MetaLabel',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=9,
        leading=12,
        textColor=primary_color
    )

    meta_val_style = ParagraphStyle(
        'MetaVal',
        parent=body_style,
        fontSize=9,
        leading=12
    )

    table_header_style = ParagraphStyle(
        'TableHeader',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=9,
        leading=12,
        textColor=colors.white
    )

    table_body_style = ParagraphStyle(
        'TableBody',
        parent=body_style,
        fontSize=9,
        leading=12
    )

    table_body_bold_style = ParagraphStyle(
        'TableBodyBold',
        parent=table_body_style,
        fontName='Helvetica-Bold'
    )

    status_pass_style = ParagraphStyle(
        'StatusPass',
        parent=table_body_bold_style,
        textColor=colors.HexColor('#10b981')
    )

    status_fail_style = ParagraphStyle(
        'StatusFail',
        parent=table_body_bold_style,
        textColor=colors.HexColor('#ef4444')
    )

    elements = []

    # Title & Header Table
    header_data = [
        [
            Paragraph("🧠 AdaptLearn", ParagraphStyle('Logo', parent=title_style, fontSize=18, textColor=accent_color)),
            Paragraph("STUDENT PROGRESS REPORT",
                      ParagraphStyle('ReportType', parent=title_style, alignment=2, fontSize=14))
        ]
    ]
    header_table = Table(header_data, colWidths=[200, 332])
    header_table.setStyle(TableStyle([
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
    ]))
    elements.append(header_table)

    # Divider line
    divider = Table([[""]], colWidths=[532])
    divider.setStyle(TableStyle([
        ('LINEBELOW', (0, 0), (-1, -1), 1, colors.HexColor('#e5e7eb')),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 0),
        ('TOPPADDING', (0, 0), (-1, -1), 0),
    ]))
    elements.append(divider)
    elements.append(Spacer(1, 10))

    # Meta information block
    meta_data = [
        [
            Paragraph("Student Name:", meta_label_style),
            Paragraph(request.user.get_full_name() or request.user.username, meta_val_style),
            Paragraph("Report Date:", meta_label_style),
            Paragraph(timezone.now().strftime("%d %B %Y, %H:%M"), meta_val_style)
        ],
        [
            Paragraph("Email Address:", meta_label_style),
            Paragraph(request.user.email, meta_val_style),
            Paragraph("Total Points (XP):", meta_label_style),
            Paragraph(str(getattr(request.user.profile, 'total_points', 0)), meta_val_style)
        ]
    ]
    meta_table = Table(meta_data, colWidths=[90, 176, 90, 176])
    meta_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor('#f9fafb')),
        ('PADDING', (0, 0), (-1, -1), 6),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('BOX', (0, 0), (-1, -1), 0.5, colors.HexColor('#e5e7eb')),
        ('INNERGRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#f3f4f6')),
    ]))
    elements.append(meta_table)
    elements.append(Spacer(1, 12))

    # Section 1: Course Enrollments
    elements.append(Paragraph("📚 Enrolled Courses", section_heading))

    course_headers = ["Course Title", "Status", "Completion", "Enrolled Date"]
    course_rows = [[Paragraph(h, table_header_style) for h in course_headers]]

    for e in enrollments:
        status_text = "Completed" if e.status == 'completed' or e.completion_percent >= 100 else e.get_status_display()
        status_color = colors.HexColor(
            '#10b981') if e.status == 'completed' or e.completion_percent >= 100 else colors.HexColor('#3b82f6')

        course_rows.append([
            Paragraph(e.course.title, table_body_bold_style),
            Paragraph(status_text, ParagraphStyle('CStatus', parent=table_body_style, fontName='Helvetica-Bold',
                                                  textColor=status_color)),
            Paragraph(f"{e.completion_percent}%", table_body_style),
            Paragraph(e.enrolled_at.strftime("%d %b %Y"), table_body_style)
        ])

    if not enrollments:
        course_rows.append([Paragraph("No courses enrolled yet.", table_body_style), "", "", ""])

    course_table = Table(course_rows, colWidths=[240, 100, 92, 100])
    course_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), primary_color),
        ('PADDING', (0, 0), (-1, -1), 6),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#f9fafb')]),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#e5e7eb')),
    ]))
    elements.append(course_table)
    elements.append(Spacer(1, 15))

    # Section 2: Exam Performance
    elements.append(Paragraph("🏆 Exam Results", section_heading))

    exam_headers = ["Exam Name", "Course", "Score", "Percentage", "Status", "Date"]
    exam_rows = [[Paragraph(h, table_header_style) for h in exam_headers]]

    for r in results:
        status_style = status_pass_style if r.status == 'pass' else status_fail_style

        exam_rows.append([
            Paragraph(r.exam.title, table_body_bold_style),
            Paragraph(r.exam.course.title, table_body_style),
            Paragraph(f"{r.score}/{r.total_marks}", table_body_style),
            Paragraph(f"{r.percentage}%", table_body_bold_style),
            Paragraph(r.status.upper(), status_style),
            Paragraph(r.submitted_at.strftime("%d %b %Y") if r.submitted_at else "N/A", table_body_style)
        ])

    if not results:
        exam_rows.append([Paragraph("No exams taken yet.", table_body_style), "", "", "", "", ""])

    exam_table = Table(exam_rows, colWidths=[120, 120, 70, 72, 70, 80])
    exam_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), primary_color),
        ('PADDING', (0, 0), (-1, -1), 6),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#f9fafb')]),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#e5e7eb')),
    ]))
    elements.append(exam_table)

    # Footer Notice
    elements.append(Spacer(1, 30))
    elements.append(divider)
    elements.append(Spacer(1, 6))
    elements.append(Paragraph(
        "This progress report is generated dynamically by the AdaptLearn platform. Thank you for learning with us!",
        ParagraphStyle('FooterNotice', parent=body_style, alignment=1, fontSize=8, textColor=muted_color)))

    doc.build(elements)

    pdf = buffer.getvalue()
    buffer.close()

    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="progress_report_{request.user.username}.pdf"'
    response.write(pdf)
    return response


@login_required
@require_POST
def restart_course(request, course_id):
    course = get_object_or_404(Course, id=course_id)
    enrollment = get_object_or_404(Enrollment, student=request.user, course=course)

    # Delete student progress for this course's materials
    StudentProgress.objects.filter(
        student=request.user,
        material__module__course=course
    ).delete()

    # Reset enrollment progress
    enrollment.completion_percent = 0.0
    enrollment.status = 'active'
    enrollment.completed_at = None
    enrollment.certificate_issued = False
    enrollment.save()

    messages.success(request, f'Progress for "{course.title}" has been reset. You can now start fresh!')
    return redirect('course_detail', slug=course.slug)


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


def password_reset_custom(request):
    if request.method == 'POST':
        email = request.POST.get('email', '').strip()
        if not email:
            messages.error(request, 'Please enter your registered email address.')
            return render(request, 'registration/password_reset_form.html')

        from django.contrib.auth.models import User
        # Filter users with matching email (case-insensitive)
        users = User.objects.filter(email__iexact=email)
        if not users.exists():
            messages.error(request, 'No user account found with that email address.')
            return render(request, 'registration/password_reset_form.html')

        import random
        import time
        from django.core.mail import send_mail
        from django.conf import settings

        otp = f"{random.randint(100000, 999999)}"

        request.session['reset_otp'] = otp
        request.session['reset_email'] = email
        request.session['reset_otp_expiry'] = time.time() + 600  # 10 minutes

        # Print the OTP to terminal console for easy developer validation
        print(
            f"\n========================================\n[OTP DEBUG] Generated OTP '{otp}' for email '{email}'\n========================================\n")

        subject = 'Reset Your AdaptLearn Password'
        message = (
            "Hello,\n\n"
            "You requested a password reset for your AdaptLearn account.\n\n"
            f"Your 6-digit OTP verification code is: {otp}\n\n"
            "This code is valid for 10 minutes. If you did not request this, please ignore this email.\n\n"
            "Thanks,\n"
            "The AdaptLearn Team"
        )

        try:
            send_mail(
                subject,
                message,
                getattr(settings, 'DEFAULT_FROM_EMAIL', 'noreply@adaptlearn.com'),
                [email],
                fail_silently=False,
            )
            messages.success(request, 'A verification code has been sent to your email.')
            return redirect('password_reset_verify')
        except Exception as e:
            messages.error(request, f'Failed to send email: {str(e)}')
            return render(request, 'registration/password_reset_form.html')

    return render(request, 'registration/password_reset_form.html')


def password_reset_verify(request):
    reset_email = request.session.get('reset_email')
    reset_otp = request.session.get('reset_otp')
    reset_otp_expiry = request.session.get('reset_otp_expiry')

    # If there is no reset session active, redirect to request page
    if not reset_email or not reset_otp or not reset_otp_expiry:
        messages.error(request, 'Session expired or invalid. Please request a new OTP.')
        return redirect('password_reset')

    if request.method == 'POST':
        otp_input = request.POST.get('otp', '').strip()
        new_password = request.POST.get('new_password', '')
        confirm_password = request.POST.get('confirm_password', '')

        import time
        current_time = time.time()

        if current_time > reset_otp_expiry:
            messages.error(request, 'The OTP has expired. Please request a new one.')
            return redirect('password_reset')

        if otp_input != reset_otp:
            messages.error(request, 'Invalid verification code. Please try again.')
            return render(request, 'registration/password_reset_verify.html')

        if not new_password or not confirm_password:
            messages.error(request, 'Please fill in both password fields.')
            return render(request, 'registration/password_reset_verify.html')

        if new_password != confirm_password:
            messages.error(request, 'Passwords do not match.')
            return render(request, 'registration/password_reset_verify.html')

        if len(new_password) < 8:
            messages.error(request, 'Password must be at least 8 characters long.')
            return render(request, 'registration/password_reset_verify.html')

        from django.contrib.auth.models import User
        users = User.objects.filter(email__iexact=reset_email)
        if not users.exists():
            messages.error(request, 'No user found with the registered email. Please contact support.')
            return redirect('password_reset')

        # Update password for all users associated with this email
        for user in users:
            user.set_password(new_password)
            user.save()

        # Clear reset session
        request.session.pop('reset_otp', None)
        request.session.pop('reset_email', None)
        request.session.pop('reset_otp_expiry', None)

        messages.success(request, 'Password reset successfully! You can now sign in with your new password.')
        return redirect('user_login')

    return render(request, 'registration/password_reset_verify.html')


# GOOGLE OAUTH VIEWS

def google_login(request):
    import os
    import urllib.parse
    import uuid

    role = request.GET.get('role', 'student')
    if role not in ['student', 'instructor']:
        role = 'student'
    request.session['google_auth_role'] = role

    client_id = os.getenv('GOOGLE_CLIENT_ID')
    client_secret = os.getenv('GOOGLE_CLIENT_SECRET')

    # If not configured, redirect to the simulator
    if not client_id or not client_secret:
        return redirect('google_simulator')

    redirect_uri = request.build_absolute_uri('/google/callback/')
    state = str(uuid.uuid4())
    request.session['google_auth_state'] = state

    params = {
        'client_id': client_id,
        'redirect_uri': redirect_uri,
        'response_type': 'code',
        'scope': 'openid email profile',
        'state': state,
        'prompt': 'select_account',
    }
    url = 'https://accounts.google.com/o/oauth2/v2/auth?' + urllib.parse.urlencode(params)
    return redirect(url)


def google_callback(request):
    import os
    import urllib.parse
    import urllib.request
    import json

    code = request.GET.get('code')
    state = request.GET.get('state')
    session_state = request.session.pop('google_auth_state', None)

    if not code:
        messages.error(request, 'Google authentication failed: no code returned.')
        return redirect('user_login')

    if state != session_state:
        messages.error(request, 'Google authentication failed: state mismatch.')
        return redirect('user_login')

    client_id = os.getenv('GOOGLE_CLIENT_ID')
    client_secret = os.getenv('GOOGLE_CLIENT_SECRET')
    redirect_uri = request.build_absolute_uri('/google/callback/')

    try:
        # 1. Exchange code for access token
        token_url = 'https://oauth2.googleapis.com/token'
        token_data = urllib.parse.urlencode({
            'code': code,
            'client_id': client_id,
            'client_secret': client_secret,
            'redirect_uri': redirect_uri,
            'grant_type': 'authorization_code'
        }).encode('utf-8')

        token_req = urllib.request.Request(token_url, data=token_data, headers={
            'Content-Type': 'application/x-www-form-urlencoded'
        })

        with urllib.request.urlopen(token_req) as response:
            token_response = json.loads(response.read().decode('utf-8'))

        access_token = token_response.get('access_token')
        if not access_token:
            messages.error(request, 'Failed to obtain access token from Google.')
            return redirect('user_login')

        # 2. Get user profile info
        userinfo_url = 'https://www.googleapis.com/oauth2/v3/userinfo'
        userinfo_req = urllib.request.Request(userinfo_url, headers={
            'Authorization': f'Bearer {access_token}'
        })

        with urllib.request.urlopen(userinfo_req) as response:
            userinfo = json.loads(response.read().decode('utf-8'))

        email = userinfo.get('email')
        given_name = userinfo.get('given_name', '')
        family_name = userinfo.get('family_name', '')

        if not email:
            messages.error(request, 'Failed to retrieve email address from Google.')
            return redirect('user_login')

        # 3. Authenticate or create user
        role = request.session.pop('google_auth_role', 'student')

        username = email.split('@')[0]
        base_username = username
        counter = 1
        while User.objects.filter(username=username).exists():
            existing_user = User.objects.filter(username=username).first()
            if existing_user and existing_user.email == email:
                break
            username = f"{base_username}{counter}"
            counter += 1

        user, created = User.objects.get_or_create(
            email=email,
            defaults={
                'username': username,
                'first_name': given_name or username.capitalize(),
                'last_name': family_name or '',
            }
        )

        if created:
            user.set_unusable_password()
            user.save()

        profile, p_created = UserProfile.objects.get_or_create(
            user=user,
            defaults={
                'role': role,
                'bio': 'Registered via Google Login.',
            }
        )

        login(request, user)
        if created:
            send_notification(user, 'Welcome! 🎉', f'Welcome to AdaptLearn, {user.first_name}! Registered via Google.',
                              'system')
            messages.success(request, f'Successfully registered via Google! Role: {profile.get_role_display()}')
        else:
            messages.success(request, f'Welcome back, {user.first_name or user.username}! Logged in via Google.')

        if profile.role == 'admin':
            return redirect('admin_dashboard')
        elif profile.role == 'instructor':
            return redirect('instructor_dashboard')
        else:
            return redirect('dashboard')

    except Exception as e:
        messages.error(request, f'Authentication error: {str(e)}')
        return redirect('user_login')


@csrf_exempt
def google_callback_js(request):
    import json
    import urllib.request
    import urllib.parse
    import os

    if request.method != 'POST':
        return JsonResponse({'success': False, 'message': 'Invalid request method.'}, status=400)

    try:
        if request.content_type == 'application/json':
            data = json.loads(request.body)
            credential = data.get('credential')
            role = data.get('role', 'student')
        else:
            credential = request.POST.get('credential')
            role = request.POST.get('role', 'student')
    except Exception as e:
        return JsonResponse({'success': False, 'message': f'Payload parsing error: {str(e)}'}, status=400)

    if not credential:
        return JsonResponse({'success': False, 'message': 'Missing credential (ID Token).'}, status=400)

    # Verify ID Token with Google's tokeninfo API
    try:
        verify_url = 'https://oauth2.googleapis.com/tokeninfo?' + urllib.parse.urlencode({'id_token': credential})
        req = urllib.request.Request(verify_url)
        with urllib.request.urlopen(req) as response:
            user_data = json.loads(response.read().decode('utf-8'))

        # Check token validity (aud should match GOOGLE_CLIENT_ID)
        client_id = os.getenv('GOOGLE_CLIENT_ID')
        if not client_id:
            return JsonResponse({'success': False, 'message': 'Google OAuth not configured on server.'}, status=500)

        if user_data.get('aud') != client_id:
            return JsonResponse({'success': False, 'message': 'Audience verification failed.'}, status=400)

        email = user_data.get('email')
        given_name = user_data.get('given_name', '')
        family_name = user_data.get('family_name', '')

        if not email:
            return JsonResponse({'success': False, 'message': 'Failed to retrieve verified email from token.'}, status=400)

        # Get/create user and login
        username = email.split('@')[0]
        base_username = username
        counter = 1
        while User.objects.filter(username=username).exists():
            existing_user = User.objects.filter(username=username).first()
            if existing_user and existing_user.email == email:
                break
            username = f"{base_username}{counter}"
            counter += 1

        user, created = User.objects.get_or_create(
            email=email,
            defaults={
                'username': username,
                'first_name': given_name or username.capitalize(),
                'last_name': family_name or '',
            }
        )

        if created:
            user.set_unusable_password()
            user.save()

        profile, p_created = UserProfile.objects.get_or_create(
            user=user,
            defaults={
                'role': role,
                'bio': 'Registered via Google One Tap/Sign-In.',
            }
        )

        login(request, user)
        if created:
            send_notification(user, 'Welcome! 🎉', f'Welcome to AdaptLearn, {user.first_name}! Registered via Google.',
                              'system')
            messages.success(request, f'Successfully registered via Google! Role: {profile.get_role_display()}')
        else:
            messages.success(request, f'Welcome back, {user.first_name or user.username}! Logged in via Google.')

        if profile.role == 'admin':
            redirect_url = '/admin-dashboard/'
        elif profile.role == 'instructor':
            redirect_url = '/instructor/'
        else:
            redirect_url = '/dashboard/'

        return JsonResponse({
            'success': True,
            'redirect_url': redirect_url
        })

    except Exception as e:
        return JsonResponse({'success': False, 'message': f'Verification failed: {str(e)}'}, status=400)


def google_simulator(request):
    role = request.session.get('google_auth_role', 'student')
    if request.method == 'POST':
        # Accept JSON or POST form data
        if request.content_type == 'application/json':
            try:
                import json
                data = json.loads(request.body)
                email = data.get('email', '').strip()
                first_name = data.get('first_name', '').strip()
                last_name = data.get('last_name', '').strip()
                role = data.get('role', role)
            except Exception:
                email, first_name, last_name = '', '', ''
        else:
            email = request.POST.get('email', '').strip()
            first_name = request.POST.get('first_name', '').strip()
            last_name = request.POST.get('last_name', '').strip()
            role = request.POST.get('role', role)

        is_ajax = request.headers.get('x-requested-with') == 'XMLHttpRequest' or request.content_type == 'application/json' or request.POST.get('ajax') == 'true'

        if not email:
            if is_ajax:
                return JsonResponse({'success': False, 'message': 'Email is required.'})
            messages.error(request, 'Email is required.')
            return render(request, 'registration/google_simulator.html', {'role': role})

        # Clean user registration/login
        username = email.split('@')[0]
        base_username = username
        counter = 1
        while User.objects.filter(username=username).exists():
            existing_user = User.objects.filter(username=username).first()
            if existing_user and existing_user.email == email:
                break
            username = f"{base_username}{counter}"
            counter += 1

        user, created = User.objects.get_or_create(
            email=email,
            defaults={
                'username': username,
                'first_name': first_name or username.capitalize(),
                'last_name': last_name or '',
            }
        )

        if created:
            user.set_unusable_password()
            user.save()

        profile, p_created = UserProfile.objects.get_or_create(
            user=user,
            defaults={
                'role': role,
                'bio': 'Signed up via Google Login Simulator.',
            }
        )

        login(request, user)
        if created:
            send_notification(user, 'Welcome! 🎉', f'Welcome to AdaptLearn, {user.first_name}! Registered via Google.',
                              'system')
            messages.success(request, f'Successfully registered via Google! Role: {profile.get_role_display()}')
        else:
            messages.success(request, f'Welcome back, {user.first_name or user.username}! Logged in via Google.')

        if profile.role == 'admin':
            redirect_url = '/admin-dashboard/'
        elif profile.role == 'instructor':
            redirect_url = '/instructor/'
        else:
            redirect_url = '/dashboard/'

        if is_ajax:
            return JsonResponse({'success': True, 'redirect_url': redirect_url})
        return redirect(redirect_url)

    mock_users = [
        {'email': 'sarah.student@gmail.com', 'first_name': 'Sarah', 'last_name': 'Connor', 'role': 'student'},
        {'email': 'alex.instructor@gmail.com', 'first_name': 'Alex', 'last_name': 'Mercer', 'role': 'instructor'},
    ]
    return render(request, 'registration/google_simulator.html', {
        'role': role,
        'mock_users': mock_users,
    })


# ── TIME TRACKING ──────────────────────────────────────────────────────────────

@login_required
@require_POST
def record_time_spent(request, material_id):
    """
    Called by the JS timer on module_detail every 30 s.
    Body: { "seconds": <int> }
    Increments time_spent_mins on StudentProgress (rounded up to whole minutes).
    """
    try:
        data = json.loads(request.body)
        seconds = int(data.get('seconds', 0))
    except (ValueError, KeyError):
        return JsonResponse({'error': 'Invalid payload'}, status=400)

    if seconds <= 0:
        return JsonResponse({'status': 'noop'})

    material = get_object_or_404(LearningMaterial, id=material_id)
    enrollment = Enrollment.objects.filter(
        student=request.user, course=material.module.course
    ).first()

    if not enrollment:
        return JsonResponse({'error': 'Not enrolled'}, status=403)

    progress, _ = StudentProgress.objects.get_or_create(
        student=request.user,
        material=material,
        defaults={'enrollment': enrollment},
    )

    # Convert seconds → whole minutes (ceiling), add to existing total
    import math
    added_mins = math.ceil(seconds / 60)
    StudentProgress.objects.filter(pk=progress.pk).update(
        time_spent_mins=models.F('time_spent_mins') + added_mins
    )

    return JsonResponse({'status': 'ok', 'added_mins': added_mins})