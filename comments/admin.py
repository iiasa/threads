from django.contrib import admin
from .models import Comment

admin.site.site_header = "Accelerator Threads Admin"


class SafeModelAdmin(admin.ModelAdmin):
    def log_deletion(self, request, object, object_repr):
        try:
            super().log_deletion(request, object, object_repr)
        except Exception:
            pass  # skip FK logging error temporarily


@admin.register(Comment)
class CommentAdmin(SafeModelAdmin):
    list_display = ('id', 'user', 'short_text', 'parent', 'thread_id', 'likes_count', 'is_deleted', 'created_at')
    list_filter = ('is_deleted', 'created_at', 'updated_at')
    search_fields = ('user__username', 'text', 'thread_id')
    readonly_fields = ('created_at', 'updated_at', 'likes_count')
    autocomplete_fields = ('user', 'parent', 'liked_by')

    def short_text(self, obj):
        return obj.text[:50] + ('...' if len(obj.text) > 50 else '')
    short_text.short_description = 'Text'

    def likes_count(self, obj):
        return obj.liked_by.count()
    likes_count.short_description = 'Likes'