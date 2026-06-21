from django.urls import path
from .views import ResearchCreateView

urlpatterns = [
    path('research/', ResearchCreateView.as_view()),
]