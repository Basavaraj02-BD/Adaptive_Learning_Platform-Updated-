from django.urls import path
from django.contrib.auth import views as auth_views
from . import views

urlpatterns = [
    # Home
    path('', views.home, name='home'),

    # Auth — User
    path('register/', views.user_register, name='user_register'),
    path('login/', views.user_login, name='user_login'),
    path('logout/', views.user_logout, name='logout'),
    path('change-password/', views.change_password, name='change_password'),

    # Auth — Admin
    path('admin-register/', views.admin_register, name='admin_register'),
    path('admin-login/', views.admin_login, name='admin_login'),

    # Dashboards
    path('dashboard/', views.dashboard, name='dashboard'),
    path('admin-dashboard/', views.admin_dashboard, name='admin_dashboard'),

    # Courses
    path('courses/', views.course_list, name='course_list'),
    path('courses/create/', views.create_course, name='create_course'),
    path('courses/<int:course_id>/edit/', views.edit_course, name='edit_course'),
    path('courses/<int:course_id>/delete/', views.delete_course, name='delete_course'),
    path('courses/<slug:slug>/', views.course_detail, name='course_detail'),
    path('courses/<int:course_id>/enroll/', views.enroll_course, name='enroll_course'),
    path('modules/<int:module_id>/', views.module_detail, name='module_detail'),
    path('materials/<int:material_id>/complete/', views.mark_material_complete, name='mark_material_complete'),

    # Exams
    path('exams/', views.exam_list, name='exam_list'),
    path('exams/<int:exam_id>/take/', views.take_exam, name='take_exam'),
    path('exams/<int:exam_id>/manage/', views.manage_exam, name='manage_exam'),
    path('exams/<int:exam_id>/add-question/', views.add_question, name='add_question'),
    path('results/<int:result_id>/', views.exam_result, name='exam_result'),

    # Payment
    path('payment/<int:course_id>/', views.payment_page, name='payment_page'),

    # Certificate
    path('certificate/<int:enrollment_id>/', views.certificate, name='certificate'),

    # Notifications
    path('notifications/', views.notifications, name='notifications'),
    path('notifications/<int:notif_id>/read/', views.mark_notification_read, name='mark_notification_read'),

    # Profile & Analytics
    path('profile/', views.profile, name='profile'),
    path('analytics/', views.analytics, name='analytics'),

    # Instructor
    path('instructor/', views.instructor_dashboard, name='instructor_dashboard'),

    # Reviews
    path('courses/<slug:slug>/reviews/', views.course_reviews, name='course_reviews'),
    path('courses/<int:course_id>/review/', views.submit_review, name='submit_review'),

    # Discussion
    path('courses/<slug:slug>/discussion/', views.discussion, name='discussion'),
    path('courses/<int:course_id>/discussion/post/', views.post_thread, name='post_thread'),
    path('discussion/<int:thread_id>/reply/', views.post_reply, name='post_reply'),

    # Forgot Password (Django Auth Views)
    path('password_reset/', views.password_reset_custom, name='password_reset'),
    path('password_reset/done/', auth_views.PasswordResetDoneView.as_view(), name='password_reset_done'),
    path('reset/<uidb64>/<token>/', auth_views.PasswordResetConfirmView.as_view(), name='password_reset_confirm'),
    path('reset/done/', auth_views.PasswordResetCompleteView.as_view(), name='password_reset_complete'),

    # Progress Report
    path('progress/export/', views.progress_report, name='progress_report'),

    # Search
    path('search/', views.search, name='search'),

    # Chatbot
    path('chatbot/', views.chatbot_page, name='chatbot'),
    path('chatbot/api/', views.chatbot_api, name='chatbot_api'),

    # Leaderboard
    path('leaderboard/', views.leaderboard, name='leaderboard'),

    # Admin Management
    path('admin-panel/users/', views.admin_users, name='admin_users'),
    path('admin-panel/courses/', views.admin_courses, name='admin_courses'),
    path('admin-panel/users/<int:user_id>/toggle/', views.admin_toggle_user, name='admin_toggle_user'),
]
