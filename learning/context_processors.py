from django.conf import settings
from .models import Notification

def notifications_processor(request):
    if request.user.is_authenticated:
        count = Notification.objects.filter(recipient=request.user, is_read=False).count()
        return {'unread_notifications_count': count}
    return {'unread_notifications_count': 0}

def google_auth_processor(request):
    return {
        'GOOGLE_CLIENT_ID': getattr(settings, 'GOOGLE_CLIENT_ID', ''),
    }
