from django.shortcuts import render, get_object_or_404
from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.decorators import action, api_view, permission_classes
from rest_framework.permissions import IsAuthenticated, AllowAny
from django.contrib.auth.models import User
from .models import Todo, Feedback
from .serializers import TodoSerializer, FeedbackSerializer, UserActivitySerializer
import logging
from django.http import Http404
from collections import defaultdict

logger = logging.getLogger(__name__)

# Create your views here.

class TodoViewSet(viewsets.ModelViewSet):
    serializer_class = TodoSerializer
    http_method_names = ['get', 'post', 'patch', 'delete']

    def get_permissions(self):
        return [AllowAny()]

    def get_queryset(self):
        username = self.request.query_params.get('username', None)
        logger.info(f"Getting todos for username: {username}")
        if username:
            return Todo.objects.filter(user=username).order_by('-created_at')
        return Todo.objects.none()

    def get_object(self):
        username = self.request.query_params.get('username', None)
        logger.info(f"Getting todo object for username: {username} and pk: {self.kwargs['pk']}")
        try:
            return Todo.objects.get(pk=self.kwargs['pk'], user=username)
        except Todo.DoesNotExist:
            logger.error(f"Todo not found for pk: {self.kwargs['pk']} and username: {username}")
            raise Http404("No Todo matches the given query.")

    def perform_create(self, serializer):
        logger.info(f"Creating todo with data: {serializer.validated_data}")
        serializer.save()

    def partial_update(self, request, *args, **kwargs):
        try:
            logger.info(f"Received PATCH request with data: {request.data}")
            instance = self.get_object()
            logger.info(f"Found todo instance: {instance}")
            
            # Ensure we're only updating the completed status
            data = {'completed': request.data.get('completed')}
            logger.info(f"Updating with data: {data}")
            
            serializer = self.get_serializer(instance, data=data, partial=True)
            if not serializer.is_valid():
                logger.error(f"Serializer errors: {serializer.errors}")
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
            
            self.perform_update(serializer)
            logger.info(f"Update performed successfully. New state: {serializer.data}")
            
            return Response(serializer.data)
        except Http404 as e:
            logger.error(f"Todo not found: {str(e)}")
            return Response(
                {"error": str(e)},
                status=status.HTTP_404_NOT_FOUND
            )
        except Exception as e:
            logger.error(f"Error updating todo: {str(e)}")
            return Response(
                {"error": str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )

    def perform_update(self, serializer):
        logger.info(f"Performing update with data: {serializer.validated_data}")
        instance = serializer.save()
        logger.info(f"Update saved. New instance state: {instance.completed}")
        return instance

    def destroy(self, request, *args, **kwargs):
        try:
            instance = self.get_object()
            self.perform_destroy(instance)
            return Response(status=status.HTTP_204_NO_CONTENT)
        except Http404 as e:
            logger.error(f"Todo not found for deletion: {str(e)}")
            return Response(
                {"error": str(e)},
                status=status.HTTP_404_NOT_FOUND
            )
        except Exception as e:
            logger.error(f"Error deleting todo: {str(e)}")
            return Response(
                {"error": str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )

class FeedbackViewSet(viewsets.ModelViewSet):
    serializer_class = FeedbackSerializer
    http_method_names = ['post', 'get']

    def get_permissions(self):
        return [AllowAny()]

    def get_queryset(self):
        username = self.request.query_params.get('username', None)
        if username:
            return Feedback.objects.filter(user=username).order_by('-created_at')
        return Feedback.objects.none()

    def perform_create(self, serializer):
        logger.info(f"Creating feedback with data: {serializer.validated_data}")
        serializer.save()

class UserActivityViewSet(viewsets.ViewSet):
    permission_classes = [AllowAny]

    def list(self, request):
        try:
            # Get all unique users from todos
            todos = Todo.objects.all()
            users = set(todo.user for todo in todos)
            
            # Get activity stats for each user
            user_stats = []
            for user in users:
                user_todos = todos.filter(user=user)
                total_todos = user_todos.count()
                completed_todos = user_todos.filter(completed=True).count()
                last_activity = user_todos.order_by('-created_at').first()
                
                user_stats.append({
                    'username': user,
                    'total_todos': total_todos,
                    'completed_todos': completed_todos,
                    'last_activity': last_activity.created_at if last_activity else None
                })
            
            # Sort by last activity
            user_stats.sort(key=lambda x: x['last_activity'] if x['last_activity'] else '', reverse=True)
            
            return Response(user_stats)
        except Exception as e:
            logger.error(f"Error getting user stats: {str(e)}")
            return Response(
                {"error": str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )

class UserDetailViewSet(viewsets.ViewSet):
    permission_classes = [AllowAny]

    def retrieve(self, request, pk=None):
        try:
            username = pk
            # Get user's todos
            todos = Todo.objects.filter(user=username).order_by('-created_at')
            todo_serializer = TodoSerializer(todos, many=True)
            
            # Get user's feedback
            feedback = Feedback.objects.filter(user=username).order_by('-created_at')
            feedback_serializer = FeedbackSerializer(feedback, many=True)
            
            # Calculate user stats
            total_todos = todos.count()
            completed_todos = todos.filter(completed=True).count()
            last_activity = todos.first().created_at if todos.exists() else None
            
            user_data = {
                'username': username,
                'total_todos': total_todos,
                'completed_todos': completed_todos,
                'last_activity': last_activity,
                'todos': todo_serializer.data,
                'feedback': feedback_serializer.data
            }
            
            return Response(user_data)
        except Exception as e:
            logger.error(f"Error getting user details: {str(e)}")
            return Response(
                {"error": str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )
