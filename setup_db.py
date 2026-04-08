#!/usr/bin/env python
"""
Admin setup script for Nurva AI Chatbot
This script initializes the database with agent data and creates a superuser
"""

import os
import django
from django.conf import settings

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'nurva_config.settings')
django.setup()

from chat.models import Agent
from django.contrib.auth.models import User

def initialize_agents():
    """Create default agents"""
    agents_data = [
        {
            'key': 'flow',
            'name': 'Nurva Flow',
            'role': 'PA & Planning',
            'emoji': '🌿',
            'avatar_color': '#4B1D5A',
            'description': 'Personal Assistant & Planning Expert',
            'system_prompt': 'You are Nurva Flow, a personal assistant and planning expert. Help users with task management, scheduling, and workflow optimization. Be concise, actionable, and focused on productivity.'
        },
        {
            'key': 'staff',
            'name': 'Nurva Staff',
            'role': 'HR & Team',
            'emoji': '👥',
            'avatar_color': '#7B4F8A',
            'description': 'HR & Team Management Expert',
            'system_prompt': 'You are Nurva Staff, an HR and team management expert. Help users with hiring, team dynamics, employee engagement, and workplace culture. Be supportive, strategic, and people-focused.'
        },
        {
            'key': 'seo',
            'name': 'Nurva SEO',
            'role': 'Search & Content',
            'emoji': '🔍',
            'avatar_color': '#C4788A',
            'description': 'SEO & Content Strategy Expert',
            'system_prompt': 'You are Nurva SEO, a search engine optimization and content strategy expert. Help users with keyword research, content planning, and digital visibility. Be data-driven and results-focused.'
        },
        {
            'key': 'strat',
            'name': 'Nurva Strategist',
            'role': 'Business Strategy',
            'emoji': '♟️',
            'avatar_color': '#D4A0B0',
            'description': 'Business Strategy Expert',
            'system_prompt': 'You are Nurva Strategist, a business strategy expert. Help users with competitive analysis, market positioning, and growth strategies. Be analytical, insightful, and forward-thinking.'
        },
    ]
    
    created = 0
    for agent_data in agents_data:
        agent, created_flag = Agent.objects.get_or_create(
            key=agent_data['key'],
            defaults={
                'name': agent_data['name'],
                'role': agent_data['role'],
                'emoji': agent_data['emoji'],
                'avatar_color': agent_data['avatar_color'],
                'description': agent_data['description'],
                'system_prompt': agent_data['system_prompt'],
            }
        )
        if created_flag:
            print(f"✅ Created agent: {agent.name}")
            created += 1
        else:
            print(f"ℹ️  Agent already exists: {agent.name}")
    
    return created

def create_superuser():
    """Create a superuser if none exists"""
    if User.objects.filter(username='admin').exists():
        print("ℹ️  Admin user already exists")
        return
    
    print("\n📝 Creating superuser...")
    User.objects.create_superuser(
        username='admin',
        email='admin@nurva.local',
        password='admin123'
    )
    print("✅ Superuser created!")
    print("   Username: admin")
    print("   Password: admin123")
    print("   Access at: http://localhost:8000/admin/")

if __name__ == '__main__':
    print("🚀 Initializing Nurva AI Agents...\n")
    created = initialize_agents()
    create_superuser()
    print(f"\n✅ Setup complete! {created} agents initialized.")
