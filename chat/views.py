from django.shortcuts import render
from django.views import View
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
import os
from dotenv import load_dotenv

load_dotenv()


class HomeView(View):
    """Renders the home page"""
    def get(self, request):
        context = {
            'app_name': os.getenv('APP_NAME', 'Nurva AI'),
        }
        return render(request, 'chat/home.html', context)


class ChatbotView(View):
    """Renders the chatbot interface"""
    def get(self, request):
        context = {
            'app_name': os.getenv('APP_NAME', 'Nurva AI'),
        }
        return render(request, 'chat/chatbot.html', context)


@csrf_exempt
@require_http_methods(['GET'])
def get_api_key(request):
    """Get Anthropic API key from backend"""
    api_key = os.getenv('ANTHROPIC_API_KEY', '')
    
    if not api_key:
        return JsonResponse({
            'success': False,
            'error': 'API key not configured'
        }, status=400)
    
    return JsonResponse({
        'success': True,
        'api_key': api_key
    })

