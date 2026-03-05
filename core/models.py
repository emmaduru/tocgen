from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from django.conf import settings


class UserProfile(models.Model):
    PLAN_CHOICES = [
        ('free',    'Free'),
        ('pro',     'Pro'),
        ('premium', 'Premium'),
    ]

    user                   = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    plan                   = models.CharField(max_length=20, choices=PLAN_CHOICES, default='free')
    stripe_customer_id     = models.CharField(max_length=100, blank=True)
    stripe_subscription_id = models.CharField(max_length=100, blank=True)
    subscription_status    = models.CharField(max_length=30, default='inactive')  # active, past_due, canceled, etc.
    subscription_end       = models.DateTimeField(null=True, blank=True)
    created_at             = models.DateTimeField(auto_now_add=True)
    updated_at             = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.user.email} — {self.plan}"

    @property
    def effective_plan(self):
        """Return plan key, falling back to free if subscription lapsed."""
        if self.plan in ('pro', 'premium') and self.subscription_status not in ('active', 'trialing'):
            return 'free'
        return self.plan

    @property
    def limits(self):
        return settings.PLAN_LIMITS[self.effective_plan]

    def uploads_today(self):
        today = timezone.now().date()
        return UploadRecord.objects.filter(user=self.user, created_at__date=today).count()

    def can_upload(self, file_size_bytes):
        limits = self.limits
        # Check file size
        max_bytes = limits['max_mb'] * 1024 * 1024
        if file_size_bytes > max_bytes:
            return False, f"File exceeds {limits['max_mb']} MB limit for your plan."
        # Check daily upload limit
        if limits['daily_uploads'] is not None:
            if self.uploads_today() >= limits['daily_uploads']:
                return False, f"Daily upload limit of {limits['daily_uploads']} reached."
        return True, None


class UploadRecord(models.Model):
    """Lightweight record — stores no file content, just metadata for rate limiting."""
    user       = models.ForeignKey(User, on_delete=models.CASCADE, related_name='uploads')
    filename   = models.CharField(max_length=255)
    file_size  = models.PositiveIntegerField()  # bytes
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.user.email} / {self.filename} @ {self.created_at:%Y-%m-%d %H:%M}"


class AnonymousUploadRecord(models.Model):
    """Rate-limit anonymous users by IP."""
    ip_address = models.GenericIPAddressField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']
