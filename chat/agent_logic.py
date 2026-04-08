"""
Agent logic and AI response generation for Nurva AI agents
"""
from typing import List
import os
from dotenv import load_dotenv

load_dotenv()


def get_agent_response(agent_key: str, user_message: str, conversation_history=None) -> str:
    """
    Generate a response from the specified agent.
    
    This function integrates with your preferred AI provider (Claude, OpenAI, etc.)
    For now, it returns demo responses. Replace with real AI integration.
    
    Args:
        agent_key: The agent type ('flow', 'staff', 'seo', 'strat')
        user_message: The user's input message
        conversation_history: Previous messages in the conversation
    
    Returns:
        AI-generated response text
    """
    
    # Demo responses - Replace with real API calls to Claude, OpenAI, etc.
    agent_responses = {
        'flow': demo_flow_response,
        'staff': demo_staff_response,
        'seo': demo_seo_response,
        'strat': demo_strategist_response,
    }
    
    response_func = agent_responses.get(agent_key, demo_flow_response)
    return response_func(user_message)


def demo_flow_response(message: str) -> str:
    """Demo response for Nurva Flow (PA & Planning)"""
    responses = {
        'task': 'I can help you organize your tasks! 📋 Try saying:\n• "Create a morning routine list"\n• "Help me prioritize my week"\n• "Set reminders for important deadlines"',
        'schedule': 'Let me help with your schedule! 📅 I can:\n• Organize your calendar\n• Find optimal meeting times\n• Create time blocks for deep work',
        'plan': 'Great! Let\'s plan this out. 🎯 Tell me:\n• What\'s your main goal?\n• What\'s your timeline?\n• What resources do you have?',
        'default': 'Hi! I\'m Nurva Flow, your personal assistant. 🌿 I help with:\n• Task management & prioritization\n• Schedule optimization\n• Workflow automation\n\nWhat would you like help with today?'
    }
    
    lower_msg = message.lower()
    if any(word in lower_msg for word in ['task', 'todo', 'do']):
        return responses['task']
    elif any(word in lower_msg for word in ['schedule', 'calendar', 'meeting', 'time']):
        return responses['schedule']
    elif any(word in lower_msg for word in ['plan', 'goal', 'strategy']):
        return responses['plan']
    else:
        return responses['default']


def demo_staff_response(message: str) -> str:
    """Demo response for Nurva Staff (HR & Team)"""
    responses = {
        'hire': 'I can help with recruitment! 👥 I assist with:\n• Job description writing\n• Interview question creation\n• Candidate evaluation frameworks\n• Culture fit assessment',
        'team': 'Team management is my specialty! 👨‍💼 I can help with:\n• Team dynamics & conflict resolution\n• One-on-one meeting agendas\n• Feedback frameworks\n• Team building ideas',
        'culture': 'Building great culture! 🌟 I can help:\n• Define company values\n• Create engagement programs\n• Improve employee satisfaction\n• Design retention strategies',
        'default': 'Hi! I\'m Nurva Staff, your HR expert. 👥 I specialize in:\n• Hiring & recruitment\n• Team management\n• Company culture\n• Employee engagement\n\nHow can I help with your team?'
    }
    
    lower_msg = message.lower()
    if any(word in lower_msg for word in ['hire', 'recruit', 'hire', 'candidate']):
        return responses['hire']
    elif any(word in lower_msg for word in ['team', 'people', 'employee', 'manage']):
        return responses['team']
    elif any(word in lower_msg for word in ['culture', 'value', 'engagement']):
        return responses['culture']
    else:
        return responses['default']


def demo_seo_response(message: str) -> str:
    """Demo response for Nurva SEO (Search & Content)"""
    responses = {
        'keywords': 'Let\'s find your perfect keywords! 🔍 I can:\n• Research high-intent keywords\n• Analyze competitor keywords\n• Find long-tail opportunities\n• Assess keyword difficulty & volume',
        'content': 'Content strategy is my strength! 📝 I offer:\n• Content calendar planning\n• Topic clustering & pillar pages\n• Content briefs & outlines\n• SEO copywriting tips',
        'ranking': 'Want to improve rankings? 📈 I help with:\n• On-page optimization\n• Technical SEO audit\n• Link building strategy\n• Competition analysis',
        'default': 'Hi! I\'m Nurva SEO, your organic growth expert. 🔍 I specialize in:\n• Keyword research\n• Content strategy\n• Technical SEO\n• Ranking optimization\n\nWhat\'s your SEO goal?'
    }
    
    lower_msg = message.lower()
    if any(word in lower_msg for word in ['keyword', 'words', 'search']):
        return responses['keywords']
    elif any(word in lower_msg for word in ['content', 'blog', 'article', 'post']):
        return responses['content']
    elif any(word in lower_msg for word in ['rank', 'ranking', 'seo', 'improve']):
        return responses['ranking']
    else:
        return responses['default']


def demo_strategist_response(message: str) -> str:
    """Demo response for Nurva Strategist (Business Strategy)"""
    responses = {
        'strategy': 'Let\'s build your strategy! ♟️ I can help with:\n• Market positioning\n• Competitive advantage analysis\n• Growth roadmap creation\n• Business model design',
        'growth': 'Growth strategy is key! 🚀 I analyze:\n• Market opportunities\n• Customer acquisition channels\n• Revenue diversification\n• Scaling strategies',
        'compete': 'Competitive strategy matters! 🎯 I provide:\n• Competitor analysis\n• Market benchmarking\n• Differentiation strategies\n• Market gap identification',
        'default': 'Hi! I\'m Nurva Strategist, your business strategy expert. ♟️ I help with:\n• Business strategy & planning\n• Competitive positioning\n• Growth strategy\n• Market analysis\n\nWhat strategic challenge are you facing?'
    }
    
    lower_msg = message.lower()
    if any(word in lower_msg for word in ['strategy', 'plan', 'direction']):
        return responses['strategy']
    elif any(word in lower_msg for word in ['grow', 'growth', 'scale', 'expand']):
        return responses['growth']
    elif any(word in lower_msg for word in ['compet', 'market', 'position', 'advantage']):
        return responses['compete']
    else:
        return responses['default']


def integrate_with_claude_api(agent_key: str, user_message: str, system_prompt: str) -> str:
    """
    Integration with Anthropic Claude API (Premium)
    
    To enable this, set ANTHROPIC_API_KEY in your .env file
    
    Usage:
        pip install anthropic
    """
    try:
        import anthropic
        
        api_key = os.getenv('ANTHROPIC_API_KEY')
        if not api_key:
            return demo_flow_response(user_message)
        
        client = anthropic.Anthropic(api_key=api_key)
        
        message = client.messages.create(
            model="claude-3-5-sonnet-20241022",
            max_tokens=1024,
            system=system_prompt,
            messages=[
                {"role": "user", "content": user_message}
            ]
        )
        
        return message.content[0].text
    
    except ImportError:
        print("Anthropic package not installed. Install with: pip install anthropic")
        return demo_flow_response(user_message)
    except Exception as e:
        print(f"Error calling Claude API: {e}")
        return demo_flow_response(user_message)


def integrate_with_openai_api(user_message: str, system_prompt: str) -> str:
    """
    Integration with OpenAI API (ChatGPT)
    
    To enable this, set OPENAI_API_KEY in your .env file
    
    Usage:
        pip install openai
    """
    try:
        from openai import OpenAI
        
        api_key = os.getenv('OPENAI_API_KEY')
        if not api_key:
            return demo_flow_response(user_message)
        
        client = OpenAI(api_key=api_key)
        
        response = client.chat.completions.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_message}
            ],
            max_tokens=1024,
            temperature=0.7
        )
        
        return response.choices[0].message.content
    
    except ImportError:
        print("OpenAI package not installed. Install with: pip install openai")
        return demo_flow_response(user_message)
    except Exception as e:
        print(f"Error calling OpenAI API: {e}")
        return demo_flow_response(user_message)
