from rest_framework import serializers
from .models import Todo, Feedback

class TodoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Todo
        fields = ['id', 'title', 'description', 'completed', 'created_at', 'user']
        read_only_fields = ['user', 'created_at']

    def create(self, validated_data):
        validated_data['user'] = self.context['request'].data.get('user')
        return super().create(validated_data)

    def update(self, instance, validated_data):
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        return instance

class FeedbackSerializer(serializers.ModelSerializer):
    class Meta:
        model = Feedback
        fields = ['id', 'message', 'created_at', 'admin_reply', 'user']
        read_only_fields = ['user', 'created_at']

    def create(self, validated_data):
        validated_data['user'] = self.context['request'].data.get('user')
        return super().create(validated_data)

class UserActivitySerializer(serializers.Serializer):
    username = serializers.CharField()
    total_todos = serializers.IntegerField()
    completed_todos = serializers.IntegerField()
    recent_todos = serializers.ListField()
    last_activity = serializers.DateTimeField() 