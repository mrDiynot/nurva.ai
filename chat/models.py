from django.db import models
from django.utils.timezone import now

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
