from django.urls import path
from .views import get_title, chat, delete_conversation, get_data

urlpatterns = [
    path('chat/get-titles/', get_title, name='get_title'),  # Correct URL pattern
    path('chat/', chat, name='chat'),
    path('chat/delete/', delete_conversation, name='delete_conversation'),
    path('chat/get-data/', get_data, name='get_data'),
]
