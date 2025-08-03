from rest_framework import viewsets, permissions, status
from rest_framework.response import Response
from rest_framework.decorators import action

from .models import Comment
from .serializers import CommentCreateSerializer, CommentSerializer


class CommentViewSet(viewsets.ModelViewSet):
    queryset = Comment.objects.all().select_related('user', 'parent').prefetch_related('replies', 'liked_by')
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    def get_serializer_class(self):
        if self.action == 'create':
            return CommentCreateSerializer
        return CommentSerializer

    def get_queryset(self):
        if self.action == 'list':
            return Comment.objects.filter(parent=None)
        return super().get_queryset()

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    @action(detail=True, methods=['post'], permission_classes=[permissions.IsAuthenticated])
    def like(self, request, pk=None):
        comment = self.get_object()
        comment.liked_by.add(request.user)
        return Response({'status': 'liked'}, status=status.HTTP_200_OK)

    @action(detail=True, methods=['post'], permission_classes=[permissions.IsAuthenticated])
    def unlike(self, request, pk=None):
        comment = self.get_object()
        comment.liked_by.remove(request.user)
        return Response({'status': 'unliked'}, status=status.HTTP_200_OK)

    def update(self, request, *args, **kwargs):
        comment = self.get_object()
        if comment.is_deleted:
            return Response({'detail': 'Deleted comments cannot be modified.'}, status=status.HTTP_403_FORBIDDEN)
        if comment.user != request.user:
            return Response({'detail': 'You are not the author of this comment.'}, status=status.HTTP_403_FORBIDDEN)
        return super().update(request, *args, **kwargs)

    def partial_update(self, request, *args, **kwargs):
        comment = self.get_object()
        if comment.is_deleted:
            return Response({'detail': 'Deleted comments cannot be modified.'}, status=status.HTTP_403_FORBIDDEN)
        if comment.user != request.user:
            return Response({'detail': 'You are not the author of this comment.'}, status=status.HTTP_403_FORBIDDEN)
        return super().partial_update(request, *args, **kwargs)

    def destroy(self, request, *args, **kwargs):
        comment = self.get_object()
        if comment.is_deleted:
            return Response({'detail': 'Comment is already deleted.'}, status=status.HTTP_400_BAD_REQUEST)
        if comment.user != request.user:
            return Response({'detail': 'You are not the author of this comment.'}, status=status.HTTP_403_FORBIDDEN)
        comment.is_deleted = True
        comment.save()
        return Response({'status': 'comment marked as deleted'}, status=status.HTTP_204_NO_CONTENT)
