from django.contrib import admin
from django.urls import path, include
from django.http import JsonResponse

def root_view(request):
    return JsonResponse({"message": "API is running"})

urlpatterns = [
    path('', root_view),                # Root message
    path('admin/', admin.site.urls),    # Admin panel
    path('api/', include('todos.urls')),  # Include all app routes under /api/
]
