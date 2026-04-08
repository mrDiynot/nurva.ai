from django.urls import path
from . import views

app_name = 'chat'

urlpatterns = [
    # Page routes
    path('', views.HomeView.as_view(), name='home'),
    path('chatbot/', views.ChatbotView.as_view(), name='chatbot'),
    
    # API routes
    path('api/key/', views.get_api_key, name='api_key'),
]
