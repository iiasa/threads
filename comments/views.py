from rest_framework import viewsets, permissions, status
from rest_framework.response import Response
from rest_framework.decorators import action

from .models import Comment
from .serializers import CommentCreateSerializer, CommentSerializer, CommentListSerializer, CommentUpdateSerializer
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters

from django.contrib.auth.models import User
from rest_framework.views import APIView
from rest_framework.authtoken.models import Token
import random
import string
import django_filters

from dj_rest_auth.registration.views import SocialLoginView
from allauth.socialaccount.providers.google.views import GoogleOAuth2Adapter
from drf_spectacular.utils import extend_schema, OpenApiParameter, OpenApiTypes


class CommentFilter(django_filters.FilterSet):
    thread_prefix = django_filters.CharFilter(field_name='thread_id', lookup_expr='istartswith')

    class Meta:
        model = Comment
        fields = []

class CommentViewSet(viewsets.ModelViewSet):
    queryset = Comment.objects.all().select_related('user', 'parent').prefetch_related('replies', 'liked_by')
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    search_fields = ['text']
    filterset_class = CommentFilter

    def get_serializer_class(self):
        if self.action == 'create':
            return CommentCreateSerializer
        elif self.action == 'update' or self.action == 'partial_update':
            return CommentUpdateSerializer
        elif self.action == 'list':
            return CommentListSerializer
        return CommentSerializer

    def get_queryset(self):
        if self.action == 'list':
            return Comment.objects.filter(parent=None)
        return super().get_queryset()

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    
    @action(detail=True, methods=['get'], permission_classes=[permissions.IsAuthenticated])
    def like(self, request, pk=None):
        comment = self.get_object()
        comment.liked_by.add(request.user)
        return Response({'status': 'liked'}, status=status.HTTP_200_OK)

    
    @action(detail=True, methods=['get'], permission_classes=[permissions.IsAuthenticated])
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
    


    
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)
    



class GoogleLogin(SocialLoginView):
    adapter_class = GoogleOAuth2Adapter


@extend_schema(
    request={
        "application/json": {
            "type": "object",
            "properties": {
                "username": {"type": "string"},
                "email": {"type": "string", "format": "email"}
            },
            "required": ["username", "email"]
        }
    },
    responses={
        200: {
            "type": "object",
            "properties": {
                "user": {
                    "type": "object",
                    "properties": {
                        "id": {"type": "integer"},
                        "username": {"type": "string"},
                        "email": {"type": "string", "format": "email"}
                    }
                },
                "token": {"type": "string"}
            }
        },
        400: OpenApiTypes.OBJECT,
    }
)
class AnonymousLoginView(APIView):
    
    def post(self, request):
        username = request.data.get("username")
        email = request.data.get("email")

        if not username or not email:
            return Response({"detail": "Username and email are required."}, status=400)

        user, created = User.objects.get_or_create(email=email, defaults={
            "username": username,
            "password": self._generate_random_password()
        })

        token, _ = Token.objects.get_or_create(user=user)

        return Response({
            "user": {
                "id": user.id,
                "username": user.username,
                "email": user.email
            },
            "token": token.key
        })

    def _generate_random_password(self):
        return ''.join(random.choices(string.ascii_letters + string.digits, k=16))
