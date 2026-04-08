from django.db import models
from django.utils.timezone import now
from django.contrib.auth.models import User
from datetime import timedelta

class UserProfile(models.Model):
    """User subscription and usage tracking"""
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    is_paid = models.BooleanField(default=False)
    free_messages_used = models.IntegerField(default=0)
    max_free_messages = models.IntegerField(default=3)
    
    # Stripe info
    stripe_customer_id = models.CharField(max_length=255, null=True, blank=True, unique=True)
    stripe_subscription_id = models.CharField(max_length=255, null=True, blank=True)
    subscription_status = models.CharField(
        max_length=50, 
        choices=[
            ('free', 'Free'),
            ('active', 'Active'),
            ('past_due', 'Past Due'),
            ('canceled', 'Canceled'),
            ('incomplete', 'Incomplete'),
        ],
        default='free'
    )
    
    # Subscription dates
    current_period_start = models.DateTimeField(null=True, blank=True)
    current_period_end = models.DateTimeField(null=True, blank=True)
    subscription_start_date = models.DateTimeField(null=True, blank=True)
    subscription_end_date = models.DateTimeField(null=True, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def messages_remaining(self):
        if self.is_paid:
            return float('inf')
        return max(0, self.max_free_messages - self.free_messages_used)
    
    def can_send_message(self):
        if self.is_paid:
            return True
        return self.free_messages_used < self.max_free_messages
    
    def is_subscription_active(self):
        if not self.is_paid:
            return False
        if self.subscription_status not in ['active', 'past_due']:
            return False
        if self.current_period_end and self.current_period_end < now():
            return False
        return True
    
    def __str__(self):
        return f"{self.user.username}'s Profile"


class Subscription(models.Model):
    """Track user subscriptions"""
    PLAN_CHOICES = [
        ('monthly', 'Monthly - $9.99/month'),
        ('quarterly', 'Quarterly - $24.99/3 months'),
        ('yearly', 'Yearly - $89.99/year'),
    ]
    
    STATUS_CHOICES = [
        ('active', 'Active'),
        ('past_due', 'Past Due'),
        ('canceled', 'Canceled'),
        ('incomplete', 'Incomplete'),
    ]
    
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='subscription')
    stripe_subscription_id = models.CharField(max_length=255, unique=True)
    stripe_customer_id = models.CharField(max_length=255)
    plan = models.CharField(max_length=50, choices=PLAN_CHOICES)
    status = models.CharField(max_length=50, choices=STATUS_CHOICES, default='incomplete')
    
    current_period_start = models.DateTimeField()
    current_period_end = models.DateTimeField()
    
    cancel_at_period_end = models.BooleanField(default=False)
    canceled_at = models.DateTimeField(null=True, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.user.username} - {self.plan} ({self.status})"
    
    def days_remaining(self):
        if self.status == 'canceled':
            return 0
        delta = self.current_period_end - now()
        return max(0, delta.days)


class Payment(models.Model):
    """Track all payments"""
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='payments')
    stripe_payment_id = models.CharField(max_length=255, unique=True)
    stripe_invoice_id = models.CharField(max_length=255, null=True, blank=True)
    
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    currency = models.CharField(max_length=10, default='usd')
    
    plan = models.CharField(max_length=50)
    status = models.CharField(
        max_length=50,
        choices=[
            ('succeeded', 'Succeeded'),
            ('failed', 'Failed'),
            ('processing', 'Processing'),
            ('refunded', 'Refunded'),
        ],
        default='processing'
    )
    
    paid_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.user.username} - ${self.amount} ({self.status})"


class Agent(models.Model):
    """AI Agent configuration"""
    key = models.CharField(max_length=50, unique=True)  # 'flow', 'staff', 'seo', 'strat'
    name = models.CharField(max_length=100)             # Nurva Flow, Nurva Staff, etc.
    role = models.CharField(max_length=100)             # PA & Planning, HR & Team, etc.
    description = models.TextField()
    avatar_color = models.CharField(max_length=7, default='#4B1D5A')  # Hex color
    system_prompt = models.TextField()                  # System prompt for AI
    emoji = models.CharField(max_length=10, default='🤖')
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['key']
    
    def __str__(self):
        return self.name


class ChatSession(models.Model):
    """User chat session"""
    session_id = models.CharField(max_length=255, unique=True)
    agent = models.ForeignKey(Agent, on_delete=models.CASCADE)
    is_paid = models.BooleanField(default=False)
    message_count = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-updated_at']
    
    def __str__(self):
        return f"Session {self.session_id} - {self.agent.name}"


class ChatMessage(models.Model):
    """Individual chat messages"""
    ROLE_CHOICES = [
        ('user', 'User'),
        ('assistant', 'Assistant'),
    ]
    
    session = models.ForeignKey(ChatSession, on_delete=models.CASCADE, related_name='messages')
    role = models.CharField(max_length=10, choices=ROLE_CHOICES)
    content = models.TextField()
    agent_key = models.CharField(max_length=50)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['created_at']
    
    def __str__(self):
        return f"{self.role}: {self.content[:50]}..."
