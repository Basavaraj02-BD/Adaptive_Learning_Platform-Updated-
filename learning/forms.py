import phone
from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from .models import UserProfile, Course, Module, LearningMaterial, Exam, Question


# ══════════════════════════════════════════
#  AUTH FORMS
# ══════════════════════════════════════════

class UserRegistrationForm(UserCreationForm):
    first_name = forms.CharField(
        max_length=50,
        widget=forms.TextInput(attrs={'placeholder': 'First Name', 'class': 'form-control glass-input'}),
    )
    last_name = forms.CharField(
        max_length=50,
        widget=forms.TextInput(attrs={'placeholder': 'Last Name', 'class': 'form-control glass-input'}),
    )
    email = forms.EmailField(
        widget=forms.EmailInput(attrs={'placeholder': 'Email Address', 'class': 'form-control glass-input'}),
    )
    username = forms.CharField(
        widget=forms.TextInput(attrs={'placeholder': 'Username', 'class': 'form-control glass-input'}),
    )
    password1 = forms.CharField(
        label='Password',
        widget=forms.PasswordInput(attrs={'placeholder': 'Password', 'class': 'form-control glass-input'}),
    )
    password2 = forms.CharField(
        label='Confirm Password',
        widget=forms.PasswordInput(attrs={'placeholder': 'Confirm Password', 'class': 'form-control glass-input'}),
    )
    phone = forms.CharField(
        max_length=15, required=False,
        widget=forms.TextInput(attrs={'placeholder': 'Phone Number (optional)', 'class': 'form-control glass-input'}),
    )
    role = forms.ChoiceField(
        choices=[('student', 'Student'), ('instructor', 'Instructor')],
        widget=forms.Select(attrs={'class': 'form-select glass-input'}),
    )

    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'username', 'email', 'password1', 'password2', 'phone', 'role']

    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data['email']
        user.first_name = self.cleaned_data['first_name']
        user.last_name = self.cleaned_data['last_name']

        if commit:
            user.save()
            profile, created = UserProfile.objects.get_or_create(user=user)
            profile.role = self.cleaned_data.get('role', 'student')
            profile.phone = self.cleaned_data.get('phone', '')
            profile.save()

        return user


class AdminRegistrationForm(UserCreationForm):
    first_name = forms.CharField(
        max_length=50,
        widget=forms.TextInput(attrs={'placeholder': 'First Name', 'class': 'form-control glass-input'}),
    )
    last_name = forms.CharField(
        max_length=50,
        widget=forms.TextInput(attrs={'placeholder': 'Last Name', 'class': 'form-control glass-input'}),
    )
    email = forms.EmailField(
        widget=forms.EmailInput(attrs={'placeholder': 'Admin Email', 'class': 'form-control glass-input'}),
    )
    username = forms.CharField(
        widget=forms.TextInput(attrs={'placeholder': 'Admin Username', 'class': 'form-control glass-input'}),
    )
    password1 = forms.CharField(
        label='Password',
        widget=forms.PasswordInput(attrs={'placeholder': 'Password', 'class': 'form-control glass-input'}),
    )
    password2 = forms.CharField(
        label='Confirm Password',
        widget=forms.PasswordInput(attrs={'placeholder': 'Confirm Password', 'class': 'form-control glass-input'}),
    )
    admin_secret_key = forms.CharField(
        widget=forms.PasswordInput(attrs={'placeholder': 'Admin Secret Key', 'class': 'form-control glass-input'}),
        help_text='Contact system administrator for this key.',
    )

    ADMIN_SECRET = 'ADAPTIVE_ADMIN_2024'

    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'username', 'email', 'password1', 'password2', 'admin_secret_key']

    def clean_admin_secret_key(self):
        key = self.cleaned_data.get('admin_secret_key')
        if key != self.ADMIN_SECRET:
            raise forms.ValidationError('Invalid admin secret key.')
        return key

    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data['email']
        user.first_name = self.cleaned_data['first_name']
        user.last_name = self.cleaned_data['last_name']
        user.is_staff = True
        user.is_superuser = True
        if commit:
            user.save()
            profile, created = UserProfile.objects.get_or_create(user=user)
            profile.role = 'admin'
            profile.save()
        return user


class UserLoginForm(AuthenticationForm):
    username = forms.CharField(
        widget=forms.TextInput(attrs={'placeholder': 'Username or Email', 'class': 'form-control glass-input', 'autofocus': True}),
    )
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={'placeholder': 'Password', 'class': 'form-control glass-input'}),
    )


class AdminLoginForm(AuthenticationForm):
    username = forms.CharField(
        widget=forms.TextInput(attrs={'placeholder': 'Admin Username', 'class': 'form-control glass-input', 'autofocus': True}),
    )
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={'placeholder': 'Admin Password', 'class': 'form-control glass-input'}),
    )


class UserProfileForm(forms.ModelForm):
    first_name = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control glass-input'}))
    last_name  = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control glass-input'}))
    email      = forms.EmailField(widget=forms.EmailInput(attrs={'class': 'form-control glass-input'}))

    class Meta:
        model = UserProfile
        fields = ['avatar', 'bio', 'phone', 'date_of_birth', 'learning_style', 'skill_level']
        widgets = {
            'bio':            forms.Textarea(attrs={'class': 'form-control glass-input', 'rows': 3}),
            'phone':          forms.TextInput(attrs={'class': 'form-control glass-input'}),
            'date_of_birth':  forms.DateInput(attrs={'class': 'form-control glass-input', 'type': 'date'}),
            'learning_style': forms.Select(attrs={'class': 'form-select glass-input'},
                                           choices=[('','Select Style'),('visual','Visual'),
                                                    ('auditory','Auditory'),('reading','Reading'),
                                                    ('kinesthetic','Kinesthetic')]),
            'skill_level':    forms.Select(attrs={'class': 'form-select glass-input'}),
        }


# ══════════════════════════════════════════
#  COURSE / CONTENT FORMS
# ══════════════════════════════════════════

class CourseForm(forms.ModelForm):
    class Meta:
        model = Course
        fields = ['title', 'slug', 'description', 'thumbnail', 'difficulty',
                  'status', 'price', 'is_free', 'tags', 'duration_hrs', 'language']
        widgets = {
            'title':       forms.TextInput(attrs={'class': 'form-control glass-input'}),
            'slug':        forms.TextInput(attrs={'class': 'form-control glass-input'}),
            'description': forms.Textarea(attrs={'class': 'form-control glass-input', 'rows': 4}),
            'difficulty':  forms.Select(attrs={'class': 'form-select glass-input'}),
            'status':      forms.Select(attrs={'class': 'form-select glass-input'}),
            'price':       forms.NumberInput(attrs={'class': 'form-control glass-input'}),
            'is_free':     forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'tags':        forms.TextInput(attrs={'class': 'form-control glass-input', 'placeholder': 'python, ml, web'}),
            'duration_hrs':forms.NumberInput(attrs={'class': 'form-control glass-input'}),
            'language':    forms.TextInput(attrs={'class': 'form-control glass-input'}),
        }


class ExamForm(forms.ModelForm):
    class Meta:
        model = Exam
        fields = ['title', 'description', 'exam_type', 'duration_mins',
                  'total_marks', 'pass_marks', 'max_attempts', 'shuffle_questions',
                  'is_active', 'start_date', 'end_date']
        widgets = {
            'title':       forms.TextInput(attrs={'class': 'form-control glass-input'}),
            'description': forms.Textarea(attrs={'class': 'form-control glass-input', 'rows': 3}),
            'exam_type':   forms.Select(attrs={'class': 'form-select glass-input'}),
            'duration_mins':forms.NumberInput(attrs={'class': 'form-control glass-input'}),
            'total_marks': forms.NumberInput(attrs={'class': 'form-control glass-input'}),
            'pass_marks':  forms.NumberInput(attrs={'class': 'form-control glass-input'}),
            'max_attempts':forms.NumberInput(attrs={'class': 'form-control glass-input'}),
            'shuffle_questions': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'is_active':   forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'start_date':  forms.DateTimeInput(attrs={'class': 'form-control glass-input', 'type': 'datetime-local'}),
            'end_date':    forms.DateTimeInput(attrs={'class': 'form-control glass-input', 'type': 'datetime-local'}),
        }


class QuestionForm(forms.ModelForm):
    option_a = forms.CharField(required=False, widget=forms.TextInput(attrs={'class': 'form-control glass-input', 'placeholder': 'Option A'}))
    option_b = forms.CharField(required=False, widget=forms.TextInput(attrs={'class': 'form-control glass-input', 'placeholder': 'Option B'}))
    option_c = forms.CharField(required=False, widget=forms.TextInput(attrs={'class': 'form-control glass-input', 'placeholder': 'Option C'}))
    option_d = forms.CharField(required=False, widget=forms.TextInput(attrs={'class': 'form-control glass-input', 'placeholder': 'Option D'}))

    class Meta:
        model = Question
        fields = ['question_text', 'question_type', 'difficulty', 'marks',
                  'correct_answer', 'explanation', 'order']
        widgets = {
            'question_text': forms.Textarea(attrs={'class': 'form-control glass-input', 'rows': 3}),
            'question_type': forms.Select(attrs={'class': 'form-select glass-input'}),
            'difficulty':    forms.Select(attrs={'class': 'form-select glass-input'}),
            'marks':         forms.NumberInput(attrs={'class': 'form-control glass-input'}),
            'correct_answer':forms.TextInput(attrs={'class': 'form-control glass-input'}),
            'explanation':   forms.Textarea(attrs={'class': 'form-control glass-input', 'rows': 2}),
            'order':         forms.NumberInput(attrs={'class': 'form-control glass-input'}),
        }
