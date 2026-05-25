from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
import json

class UserProfile(models.Model):
    ROLE_CHOICES = [('student', 'Student'), ('instructor', 'Instructor'), ('admin', 'Admin')]
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='student')
    avatar = models.ImageField(upload_to='avatars/', null=True, blank=True)
    bio = models.TextField(blank=True)
    phone = models.CharField(max_length=15, blank=True)
    date_of_birth = models.DateField(null=True, blank=True)
    learning_style = models.CharField(max_length=50, blank=True)  # visual/auditory/reading/kinesthetic
    skill_level = models.CharField(max_length=20, default='beginner',
                                   choices=[('beginner','Beginner'),('intermediate','Intermediate'),('advanced','Advanced')])
    total_points = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.user.username} – {self.role}"

    def get_avatar_url(self):
        if self.avatar:
            return self.avatar.url
        return '/static/images/default_avatar.png'



class Course(models.Model):
    DIFFICULTY = [('beginner','Beginner'),('intermediate','Intermediate'),('advanced','Advanced')]
    STATUS     = [('draft','Draft'),('published','Published'),('archived','Archived')]

    title        = models.CharField(max_length=200)
    slug         = models.SlugField(unique=True)
    description  = models.TextField()
    instructor   = models.ForeignKey(User, on_delete=models.CASCADE, related_name='courses_taught')
    thumbnail    = models.ImageField(upload_to='course_thumbnails/', null=True, blank=True)
    difficulty   = models.CharField(max_length=20, choices=DIFFICULTY, default='beginner')
    status       = models.CharField(max_length=20, choices=STATUS, default='draft')
    price        = models.DecimalField(max_digits=8, decimal_places=2, default=0.00)
    is_free      = models.BooleanField(default=False)
    tags         = models.CharField(max_length=300, blank=True)
    duration_hrs = models.FloatField(default=0)
    language     = models.CharField(max_length=50, default='English')
    rating       = models.FloatField(default=0.0)
    total_enrolled = models.IntegerField(default=0)
    created_at   = models.DateTimeField(auto_now_add=True)
    updated_at   = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return self.title

    def get_thumbnail_url(self):
        if self.thumbnail:
            return self.thumbnail.url
        return '/static/images/default_course.png'



class Module(models.Model):
    course      = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='modules')
    title       = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    order       = models.PositiveIntegerField(default=0)
    is_locked   = models.BooleanField(default=False)
    duration_mins = models.IntegerField(default=0)
    created_at  = models.DateTimeField(auto_now_add=True)
    updated_at  = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['order']

    def __str__(self):
        return f"{self.course.title} › {self.title}"



class LearningMaterial(models.Model):
    TYPE_CHOICES = [
        ('video','Video'), ('article','Article'), ('pdf','PDF'),
        ('quiz','Quiz'), ('audio','Audio'), ('interactive','Interactive'),
    ]
    module       = models.ForeignKey(Module, on_delete=models.CASCADE, related_name='materials')
    title        = models.CharField(max_length=200)
    material_type = models.CharField(max_length=20, choices=TYPE_CHOICES, default='article')
    content      = models.TextField(blank=True)          # HTML / text content
    file         = models.FileField(upload_to='materials/', null=True, blank=True)
    video_url    = models.URLField(blank=True)           # YouTube / Vimeo
    duration_mins = models.IntegerField(default=0)
    order        = models.PositiveIntegerField(default=0)
    is_free_preview = models.BooleanField(default=False)
    created_at   = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['order']

    def __str__(self):
        return f"{self.module.title} › {self.title}"



class Enrollment(models.Model):
    STATUS_CHOICES = [
        ('active','Active'), ('completed','Completed'),
        ('dropped','Dropped'), ('suspended','Suspended'),
    ]
    student    = models.ForeignKey(User, on_delete=models.CASCADE, related_name='enrollments')
    course     = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='enrollments')
    status     = models.CharField(max_length=20, choices=STATUS_CHOICES, default='active')
    enrolled_at = models.DateTimeField(auto_now_add=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    completion_percent = models.FloatField(default=0.0)
    certificate_issued = models.BooleanField(default=False)

    class Meta:
        unique_together = ('student', 'course')

    def __str__(self):
        return f"{self.student.username} → {self.course.title}"



class StudentProgress(models.Model):
    student    = models.ForeignKey(User, on_delete=models.CASCADE, related_name='progress')
    material   = models.ForeignKey(LearningMaterial, on_delete=models.CASCADE, related_name='progress')
    enrollment = models.ForeignKey(Enrollment, on_delete=models.CASCADE, related_name='progress', null=True)
    is_completed = models.BooleanField(default=False)
    time_spent_mins = models.IntegerField(default=0)
    last_accessed = models.DateTimeField(auto_now=True)
    notes        = models.TextField(blank=True)

    class Meta:
        unique_together = ('student', 'material')

    def __str__(self):
        return f"{self.student.username} – {self.material.title}"



class Exam(models.Model):
    TYPE_CHOICES = [('module','Module Exam'),('final','Final Exam'),('practice','Practice')]
    course      = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='exams')
    module      = models.ForeignKey(Module, on_delete=models.CASCADE, related_name='exams', null=True, blank=True)
    title       = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    exam_type   = models.CharField(max_length=20, choices=TYPE_CHOICES, default='module')
    duration_mins = models.IntegerField(default=30)
    total_marks = models.IntegerField(default=100)
    pass_marks  = models.IntegerField(default=40)
    max_attempts = models.IntegerField(default=3)
    shuffle_questions = models.BooleanField(default=True)
    is_active   = models.BooleanField(default=True)
    start_date  = models.DateTimeField(null=True, blank=True)
    end_date    = models.DateTimeField(null=True, blank=True)
    created_at  = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.course.title} – {self.title}"



class Question(models.Model):
    TYPE_CHOICES = [
        ('mcq','Multiple Choice'), ('true_false','True/False'),
        ('fill_blank','Fill in the Blank'), ('short_answer','Short Answer'),
    ]
    DIFFICULTY = [('easy','Easy'),('medium','Medium'),('hard','Hard')]

    exam        = models.ForeignKey(Exam, on_delete=models.CASCADE, related_name='questions')
    question_text = models.TextField()
    question_type = models.CharField(max_length=20, choices=TYPE_CHOICES, default='mcq')
    difficulty  = models.CharField(max_length=10, choices=DIFFICULTY, default='medium')
    marks       = models.IntegerField(default=1)
    explanation = models.TextField(blank=True)   # shown after answer
    image       = models.ImageField(upload_to='question_images/', null=True, blank=True)
    order       = models.PositiveIntegerField(default=0)


    options     = models.TextField(blank=True, default='[]')
    correct_answer = models.TextField()

    class Meta:
        ordering = ['order']

    def __str__(self):
        return self.question_text[:80]

    def get_options(self):
        try:
            return json.loads(self.options)
        except:
            return []

    def set_options(self, options_list):
        self.options = json.dumps(options_list)



class ExamResult(models.Model):
    STATUS_CHOICES = [('pass','Pass'),('fail','Fail'),('pending','Pending')]

    student     = models.ForeignKey(User, on_delete=models.CASCADE, related_name='exam_results')
    exam        = models.ForeignKey(Exam, on_delete=models.CASCADE, related_name='results')
    attempt_number = models.IntegerField(default=1)
    score       = models.FloatField(default=0)
    total_marks = models.IntegerField(default=0)
    percentage  = models.FloatField(default=0)
    status      = models.CharField(max_length=10, choices=STATUS_CHOICES, default='pending')
    time_taken_mins = models.IntegerField(default=0)
    ai_feedback = models.TextField(blank=True)   # AI-generated personalised feedback
    started_at  = models.DateTimeField(auto_now_add=True)
    submitted_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ['-started_at']

    def __str__(self):
        return f"{self.student.username} – {self.exam.title} ({self.percentage:.1f}%)"



class StudentAnswer(models.Model):
    result      = models.ForeignKey(ExamResult, on_delete=models.CASCADE, related_name='answers')
    question    = models.ForeignKey(Question, on_delete=models.CASCADE, related_name='student_answers')
    given_answer = models.TextField(blank=True)
    is_correct  = models.BooleanField(default=False)
    marks_obtained = models.FloatField(default=0)
    ai_evaluation = models.TextField(blank=True)   # for short-answer AI grading
    answered_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.result.student.username} → Q{self.question.id}"



class Payment(models.Model):
    STATUS_CHOICES = [
        ('pending','Pending'), ('completed','Completed'),
        ('failed','Failed'), ('refunded','Refunded'),
    ]
    METHOD_CHOICES = [
        ('card','Credit/Debit Card'), ('upi','UPI'),
        ('netbanking','Net Banking'), ('wallet','Wallet'), ('free','Free'),
    ]
    student     = models.ForeignKey(User, on_delete=models.CASCADE, related_name='payments')
    course      = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='payments')
    amount      = models.DecimalField(max_digits=10, decimal_places=2)
    currency    = models.CharField(max_length=5, default='INR')
    status      = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    payment_method = models.CharField(max_length=20, choices=METHOD_CHOICES, default='card')
    transaction_id = models.CharField(max_length=200, blank=True, unique=True, null=True)
    stripe_payment_intent = models.CharField(max_length=200, blank=True)
    receipt_url = models.URLField(blank=True)
    paid_at     = models.DateTimeField(null=True, blank=True)
    created_at  = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.student.username} – {self.course.title} – ₹{self.amount}"



class Notification(models.Model):
    TYPE_CHOICES = [
        ('enrollment','Enrollment'), ('exam','Exam'),
        ('result','Result'), ('payment','Payment'),
        ('system','System'), ('achievement','Achievement'),
    ]
    recipient   = models.ForeignKey(User, on_delete=models.CASCADE, related_name='notifications')
    title       = models.CharField(max_length=200)
    message     = models.TextField()
    notif_type  = models.CharField(max_length=20, choices=TYPE_CHOICES, default='system')
    is_read     = models.BooleanField(default=False)
    link        = models.CharField(max_length=300, blank=True)
    created_at  = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"→ {self.recipient.username}: {self.title}"


class CourseReview(models.Model):
    course    = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='reviews')
    student   = models.ForeignKey(User, on_delete=models.CASCADE, related_name='reviews')
    rating    = models.PositiveSmallIntegerField(default=5)   # 1-5
    comment   = models.TextField(blank=True)
    is_verified = models.BooleanField(default=False)
    created_at  = models.DateTimeField(auto_now_add=True)
    updated_at  = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ('course', 'student')
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.student.username} → {self.course.title} ({self.rating}★)"


class DiscussionThread(models.Model):
    course      = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='threads')
    author      = models.ForeignKey(User, on_delete=models.CASCADE, related_name='threads')
    title       = models.CharField(max_length=300)
    content     = models.TextField()
    is_pinned   = models.BooleanField(default=False)
    is_resolved = models.BooleanField(default=False)
    views       = models.PositiveIntegerField(default=0)
    created_at  = models.DateTimeField(auto_now_add=True)
    updated_at  = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-is_pinned', '-created_at']

    def __str__(self):
        return f"{self.course.title} › {self.title}"


class DiscussionReply(models.Model):
    thread    = models.ForeignKey(DiscussionThread, on_delete=models.CASCADE, related_name='replies')
    author    = models.ForeignKey(User, on_delete=models.CASCADE, related_name='replies')
    content   = models.TextField()
    is_solution = models.BooleanField(default=False)
    created_at  = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['created_at']

    def __str__(self):
        return f"Reply by {self.author.username} on {self.thread.title}"



class ChatMessage(models.Model):
    user       = models.ForeignKey(User, on_delete=models.CASCADE, related_name='chat_messages')
    role       = models.CharField(max_length=10, choices=[('user','User'),('assistant','Assistant')])
    content    = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['created_at']
