from django.urls import path
from . import views

app_name = 'chat'

urlpatterns = [
    # Page routes
    path('', views.HomeView.as_view(), name='home'),
    path('login/', views.LoginView.as_view(), name='login'),
    path('register/', views.RegisterView.as_view(), name='register'),
    path('logout/', views.LogoutView.as_view(), name='logout'),
    path('chatbot/', views.ChatbotView.as_view(), name='chatbot'),
    path('profile/', views.UserProfileView.as_view(), name='profile'),
    
    # API routes
    path('api/key/', views.get_api_key, name='api_key'),
    path('api/message-status/', views.get_message_status, name='message_status'),
    path('api/increment-message/', views.increment_message_count, name='increment_message'),
    path('api/verify-payment/', views.verify_payment, name='verify_payment'),
    path('api/cancel-subscription/', views.cancel_subscription, name='cancel_subscription'),
    
    # Webhooks
    path('webhook/stripe/', views.stripe_webhook, name='stripe_webhook'),
]
