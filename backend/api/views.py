from django.shortcuts import render
from django.http import JsonResponse
from rest_framework import viewsets, status
from rest_framework.decorators import api_view
from rest_framework.response import Response
from .models import MedicalAccount, ContentScript
from .serializers import MedicalAccountSerializer, ContentScriptSerializer
import random

def system_status(request):
    data = {
        "status": "active",
        "agents_online": 3,
        "daily_limit": 500,
        "generated_today": 128
    }
    return JsonResponse(data)

class MedicalAccountViewSet(viewsets.ModelViewSet):
    queryset = MedicalAccount.objects.all()
    serializer_class = MedicalAccountSerializer

class ContentScriptViewSet(viewsets.ModelViewSet):
    queryset = ContentScript.objects.all().order_by('-created_at')[:5]
    serializer_class = ContentScriptSerializer

@api_view(['POST'])
def generate_script(request):
    topic = request.data.get('topic', 'Новая медицинская процедура')
    account_id = request.data.get('account_id')
    
    # Имитация генерации ИИ
    titles = [
        f"3 причины выбрать {topic}",
        f"Мифы о {topic}, которые пора развеять",
        f"Как подготовиться к {topic}?",
        f"Результаты после {topic}: ожидания vs реальность"
    ]
    
    scripts = [
        f"Сценарий: Привет! Сегодня разберем {topic}. Многие думают, что это сложно, но на самом деле...",
        f"Топ советов по {topic}: 1. Консультация врача. 2. Регулярность. 3. Качество.",
        f"Вы знали, что {topic} может изменить вашу жизнь? Вот почему это важно для вашего здоровья."
    ]
    
    new_script = ContentScript.objects.create(
        account_id=account_id,
        title=random.choice(titles),
        script_text=random.choice(scripts),
        status='completed'
    )
    
    serializer = ContentScriptSerializer(new_script)
    return Response(serializer.data, status=status.HTTP_201_CREATED)
