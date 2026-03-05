from django.conf import settings
from .models import UserProfile


def plan_context(request):
    if request.user.is_authenticated:
        profile, _ = UserProfile.objects.get_or_create(user=request.user)
        return {
            'user_profile': profile,
            'user_plan': profile.effective_plan,
            'plan_limits': settings.PLAN_LIMITS,
        }
    return {
        'user_plan': 'anonymous',
        'plan_limits': settings.PLAN_LIMITS,
    }
