from django.urls import path
from .views import ResearchCreateView
from .authview import GoogleLoginView
from rest_framework_simplejwt.views import TokenRefreshView


urlpatterns = [
    path('research/', ResearchCreateView.as_view()),
    path('auth/google/', GoogleLoginView.as_view()),
    path('auth/token/refresh/', TokenRefreshView.as_view())
]