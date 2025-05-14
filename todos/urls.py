from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import TodoViewSet, FeedbackViewSet, UserActivityViewSet, UserDetailViewSet

router = DefaultRouter()
router.register(r'todos', TodoViewSet)
router.register(r'feedback', FeedbackViewSet)
router.register(r'user-activities', UserActivityViewSet, basename='user-activities')
router.register(r'user-details', UserDetailViewSet, basename='user-details')

urlpatterns = [
    path('', include(router.urls)),
] 