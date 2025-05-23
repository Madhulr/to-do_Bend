from django.contrib import admin
from django.urls import path, include
from rest_framework import routers
from django.http import JsonResponse
from todos.views import TodoViewSet, FeedbackViewSet

router = routers.DefaultRouter()
router.register(r'todos', TodoViewSet, basename='todo')
router.register(r'feedback', FeedbackViewSet, basename='feedback')

def root_view(request):
    return JsonResponse({"message": "API is running"})

urlpatterns = [
    path('', root_view),  # Root URL returns JSON message
    path('admin/', admin.site.urls),
    path('api/', include(router.urls)),
]
