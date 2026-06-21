from rest_framework import serializers
from .models import ResearchResults


class ResearchRequestSerializer(serializers.Serializer):
    topic = serializers.CharField(max_length=800)

class ResearchResponseSerializer(serializers.ModelSerializer):
    class Meta:
        model = ResearchResults
        fields = ['topic','report','confidence']
        