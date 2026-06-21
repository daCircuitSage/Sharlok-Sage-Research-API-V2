from django.shortcuts import render
from rest_framework.response import Response
from rest_framework import status

from rest_framework.views import APIView

from .serializers import (ResearchRequestSerializer,
                          ResearchResponseSerializer)
from .models import ResearchResults

from .service import run_research_for_topic


class ResearchCreateView(APIView):
    def post(self, request):
        serializer = ResearchRequestSerializer(data=request.data)
        if not serializer.is_valid(raise_exception=True):
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        topic = serializer.validated_data['topic']

        result = run_research_for_topic(topic=topic)

        research_obj = ResearchResults.objects.create(
            user=request.user if request.user.is_authenticated else None,
            topic = result['topic'],
            report=result['report'],
            confidence=result['confidence'],
            plan=result['plan'],
            verification=result['verification'],
            critic = result['critic'],
            status = 'completed',
        )

        response_serializer = ResearchResponseSerializer(research_obj)

        return Response(response_serializer.data, status=status.HTTP_200_OK)