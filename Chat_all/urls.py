"""
Definition of urls for Django_mysql.
"""

from datetime import datetime
from django.urls import path
from app.views import LoginAPIView
from app.views import ProcessPromptAPIView
from app.views import ProcessJsonAPIView 
from app.views import GeneratePromptsView 





urlpatterns = [
    path('', LoginAPIView.as_view(), name='api-login'),
    path('prompt/',ProcessPromptAPIView.as_view(), name='api-bot'),
    path('wson/',ProcessJsonAPIView.as_view(), name='json-bot'),
    path('generate-prompts/', GeneratePromptsView.as_view(), name='generate-prompts'),
    

]
