from django.db import models

class MedicalAccount(models.Model):
    PLATFORM_CHOICES = [
        ('Reels', 'Instagram Reels'),
        ('TikTok', 'TikTok'),
    ]
    STATUS_CHOICES = [
        ('active', 'Active'),
        ('inactive', 'Inactive'),
    ]
    name = models.CharField(max_length=255)
    platform = models.CharField(max_length=50, choices=PLATFORM_CHOICES, default='Reels')
    status = models.CharField(max_length=50, choices=STATUS_CHOICES, default='active')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.name} ({self.platform})"

class ContentScript(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
    ]
    account = models.ForeignKey(MedicalAccount, on_delete=models.CASCADE, related_name='scripts', null=True, blank=True)
    title = models.CharField(max_length=255)
    script_text = models.TextField()
    video_file = models.FileField(upload_to='videos/', null=True, blank=True)
    status = models.CharField(max_length=50, choices=STATUS_CHOICES, default='pending')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title
