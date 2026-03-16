from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import system_status, MedicalAccountViewSet, ContentScriptViewSet, generate_script, generate_video_api

router = DefaultRouter()
router.register(r'accounts', MedicalAccountViewSet)
router.register(r'scripts', ContentScriptViewSet)

urlpatterns = [
    path('', include(router.urls)),
    path('status/', system_status),
    path('generate/', generate_script),
    path('generate-video/<int:script_id>/', generate_video_api),
]
