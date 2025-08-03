from rest_framework import serializers
from .models import Comment

class CommentCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Comment
        fields = ['id', 'text', 'parent', 'thread_id']
        extra_kwargs = {
            'parent': {'required': False},
            'thread_id': {'required': False}
        }

    def validate(self, data):
        parent = data.get('parent')
        thread_id = data.get('thread_id')

        if parent:
            # Ensure replies do not get their own thread_id
            if thread_id:
                raise serializers.ValidationError("Replies should not provide a thread_id.")
        else:
            # Root comment must have thread_id
            if not thread_id:
                raise serializers.ValidationError("Root comments must include a thread_id.")

        return data

    def create(self, validated_data):
        user = self.context['request'].user
        return Comment.objects.create(user=user, **validated_data)



class RecursiveField(serializers.Serializer):
    def to_representation(self, value):
        serializer = self.parent.parent.__class__(value, context=self.context)
        return serializer.data


class CommentSerializer(serializers.ModelSerializer):
    user = serializers.StringRelatedField()
    replies = RecursiveField(many=True, read_only=True)
    likes_count = serializers.IntegerField(read_only=True)
    text = serializers.SerializerMethodField()

    class Meta:
        model = Comment
        fields = ['id', 'user', 'text', 'thread_id', 'parent', 'created_at', 'likes_count', 'replies', 'is_deleted']
        read_only_fields = ['user', 'likes_count', 'created_at', 'replies']

    def get_text(self, obj):
        if obj.is_deleted:
            return "This comment has been deleted."
        return obj.text
