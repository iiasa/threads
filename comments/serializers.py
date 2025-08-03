from rest_framework import serializers
from .models import Comment

class CommentCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Comment
        fields = ['id', 'text', 'parent', 'thread_id']
        extra_kwargs = {
            'parent': {'required': False, 'allow_null': True},
            'thread_id': {'required': False, 'allow_null': True}
        }

    def validate(self, data):
        parent = data.get('parent', None)
        thread_id = data.get('thread_id', None)

        if parent is not None:
            # It's a reply → thread_id must NOT be provided
            if thread_id:
                raise serializers.ValidationError({
                    'thread_id': 'Replies should not include a thread_id. It is inherited from the parent.'
                })
        else:
            # It's a root comment → thread_id is required
            if not thread_id:
                raise serializers.ValidationError({
                    'thread_id': 'Root comments must include a thread_id.'
                })

        return data

    def create(self, validated_data):
        user = self.context['request'].user
        validated_data.pop('user', None)  
        return Comment.objects.create(user=user, **validated_data)


class RecursiveField(serializers.Serializer):
    def to_representation(self, value):
        serializer = self.parent.parent.__class__(value, context=self.context)
        return serializer.data


class CommentSerializer(serializers.ModelSerializer):
    user = serializers.StringRelatedField()
    replies = RecursiveField(many=True, read_only=True)
    likes_count = serializers.IntegerField(read_only=True)
    liked_by = serializers.StringRelatedField(many=True, read_only=True)
    text = serializers.SerializerMethodField()

    class Meta:
        model = Comment
        fields = ['id', 'user', 'text', 'thread_id', 'parent', 'created_at', 'likes_count', 'replies', 'is_deleted', 'liked_by']
        read_only_fields = ['user', 'likes_count', 'created_at', 'replies', 'liked_by']

    def get_text(self, obj):
        if obj.is_deleted:
            return "This comment has been deleted."
        return obj.text


class CommentListSerializer(serializers.ModelSerializer):
    user = serializers.StringRelatedField()
    likes_count = serializers.IntegerField(read_only=True)
    replies_count = serializers.SerializerMethodField()
    text = serializers.SerializerMethodField()

    class Meta:
        model = Comment
        fields = ['id', 'user', 'text', 'thread_id', 'parent', 'created_at', 'likes_count', 'replies_count', 'is_deleted']
        read_only_fields = ['user', 'likes_count', 'created_at', 'replies_count']

    def get_text(self, obj):
        if obj.is_deleted:
            return "This comment has been deleted."
        return obj.text

    def get_replies_count(self, obj):
        return obj.replies.count()
    

class CommentUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Comment
        fields = ['text']

    def update(self, instance, validated_data):
        instance.text = validated_data['text']
        instance.save()
        return instance