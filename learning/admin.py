from django.contrib import admin
from .models import *

@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ['user', 'role', 'skill_level', 'total_points', 'created_at']
    list_filter  = ['role', 'skill_level']
    search_fields = ['user__username', 'user__email']

@admin.register(Course)
class CourseAdmin(admin.ModelAdmin):
    list_display = ['title', 'instructor', 'difficulty', 'status', 'price', 'total_enrolled', 'rating']
    list_filter  = ['difficulty', 'status', 'is_free']
    prepopulated_fields = {'slug': ('title',)}
    search_fields = ['title', 'tags']

@admin.register(Module)
class ModuleAdmin(admin.ModelAdmin):
    list_display = ['title', 'course', 'order', 'is_locked']
    list_filter  = ['is_locked']

@admin.register(LearningMaterial)
class LearningMaterialAdmin(admin.ModelAdmin):
    list_display = ['title', 'module', 'material_type', 'order']
    list_filter  = ['material_type']

@admin.register(Enrollment)
class EnrollmentAdmin(admin.ModelAdmin):
    list_display = ['student', 'course', 'status', 'completion_percent', 'enrolled_at']
    list_filter  = ['status']

@admin.register(StudentProgress)
class StudentProgressAdmin(admin.ModelAdmin):
    list_display = ['student', 'material', 'is_completed', 'time_spent_mins']

@admin.register(Exam)
class ExamAdmin(admin.ModelAdmin):
    list_display = ['title', 'course', 'exam_type', 'duration_mins', 'total_marks', 'is_active']
    list_filter  = ['exam_type', 'is_active']

@admin.register(Question)
class QuestionAdmin(admin.ModelAdmin):
    list_display = ['question_text', 'exam', 'question_type', 'difficulty', 'marks']
    list_filter  = ['question_type', 'difficulty']

@admin.register(ExamResult)
class ExamResultAdmin(admin.ModelAdmin):
    list_display = ['student', 'exam', 'score', 'percentage', 'status', 'submitted_at']
    list_filter  = ['status']

@admin.register(StudentAnswer)
class StudentAnswerAdmin(admin.ModelAdmin):
    list_display = ['result', 'question', 'is_correct', 'marks_obtained']

@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = ['student', 'course', 'amount', 'status', 'payment_method', 'paid_at']
    list_filter  = ['status', 'payment_method']

@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = ['recipient', 'title', 'notif_type', 'is_read', 'created_at']
    list_filter  = ['notif_type', 'is_read']

@admin.register(ChatMessage)
class ChatMessageAdmin(admin.ModelAdmin):
    list_display = ['user', 'role', 'created_at']

@admin.register(CourseReview)
class CourseReviewAdmin(admin.ModelAdmin):
    list_display = ['student', 'course', 'rating', 'is_verified', 'created_at']
    list_filter  = ['rating', 'is_verified']
    search_fields = ['student__username', 'course__title']

@admin.register(DiscussionThread)
class DiscussionThreadAdmin(admin.ModelAdmin):
    list_display = ['title', 'course', 'author', 'is_pinned', 'is_resolved', 'created_at']
    list_filter  = ['is_pinned', 'is_resolved']

@admin.register(DiscussionReply)
class DiscussionReplyAdmin(admin.ModelAdmin):
    list_display = ['author', 'thread', 'is_solution', 'created_at']
    list_filter  = ['is_solution']

