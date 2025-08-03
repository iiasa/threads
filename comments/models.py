from django.db import models
from django.contrib.auth.models import User

class Comment(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='comments')
    text = models.TextField()
    parent = models.ForeignKey('self', null=True, blank=True, related_name='replies', on_delete=models.CASCADE)
    thread_id = models.TextField(blank=True)  # Manually provided for root comments only
    liked_by = models.ManyToManyField(User, related_name='liked_comments', blank=True)

    is_deleted = models.BooleanField(default=False)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def save(self, *args, **kwargs):
        if self.parent:
            # Replies must inherit thread_id from parent
            self.thread_id = self.parent.thread_id
        super().save(*args, **kwargs)

    def __str__(self):
        return f'{self.user.username}: {self.text[:30]}'

    @property
    def likes_count(self):
        return self.liked_by.count()

    def is_reply(self):
        return self.parent is not None

    def __str__(self):
        return f'{self.user.username}: {self.text[:30]}' if not self.is_deleted else '[deleted]'

