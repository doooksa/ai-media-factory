from rest_framework import serializers
from .models import MedicalAccount, ContentScript

class MedicalAccountSerializer(serializers.ModelSerializer):
    class Meta:
        model = MedicalAccount
        fields = '__all__'

class ContentScriptSerializer(serializers.ModelSerializer):
    account_name = serializers.CharField(source='account.name', read_only=True)
    
    class Meta:
        model = ContentScript
        fields = ['id', 'account', 'account_name', 'title', 'script_text', 'status', 'created_at']
