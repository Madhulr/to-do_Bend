from django.shortcuts import get_object_or_404
from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from django.http import Http404
from .models import Todo, Feedback
from .serializers import TodoSerializer, FeedbackSerializer
import logging

logger = logging.getLogger(__name__)


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
        logger.info(f"Getting todo object for username: {username} and pk: {self.kwargs.get('pk')}")
        try:
            return Todo.objects.get(pk=self.kwargs.get('pk'), user=username)
        except Todo.DoesNotExist:
            logger.error(f"Todo not found for pk: {self.kwargs.get('pk')} and username: {username}")
            raise Http404("No Todo matches the given query.")

    def perform_create(self, serializer):
        logger.info(f"Creating todo with data: {serializer.validated_data}")
        serializer.save()

    def partial_update(self, request, *args, **kwargs):
        try:
            logger.info(f"Received PATCH request with data: {request.data}")
            instance = self.get_object()
            logger.info(f"Found todo instance: {instance}")

            # Update only the completed status
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
            return Response({"error": str(e)}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            logger.error(f"Error updating todo: {str(e)}")
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

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
            return Response({"error": str(e)}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            logger.error(f"Error deleting todo: {str(e)}")
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)


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
            todos = Todo.objects.all()
            users = set(todo.user for todo in todos)

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

            return Response(user_stats)
        except Exception as e:
            logger.error(f"Error fetching user activity stats: {str(e)}")
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)


class UserDetailViewSet(viewsets.ViewSet):
    permission_classes = [AllowAny]

    def retrieve(self, request, pk=None):
        try:
            todo = get_object_or_404(Todo, pk=pk)
            data = {
                'username': todo.user,
                'todos': TodoSerializer(Todo.objects.filter(user=todo.user), many=True).data,
            }
            return Response(data)
        except Exception as e:
            logger.error(f"Error retrieving user details: {str(e)}")
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
