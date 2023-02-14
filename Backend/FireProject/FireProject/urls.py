
from django.urls import path, include

urlpatterns = [
    path('api/fires/', include('FireApp.urls')),
]
