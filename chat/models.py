from django.db import models
from django.contrib.auth import get_user_model

# Create your models here.

User = get_user_model()

class Conversation(models.Model):
    title = models.CharField(max_length=128)

    class TypeChoices(models.TextChoices):
        PRIVATE = 'private', 'Private'
        GROUP = 'group', 'Group'
    type = models.CharField(max_length=10, choices=TypeChoices)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f'conversation {self.title}'

class ConversationMember(models.Model):
    conversation = models.ForeignKey(Conversation, on_delete=models.CASCADE, related_name='members')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='conversation_memberships')

    class RoleChoices(models.TextChoices):
        ADMIN = 'admin', 'Admin'
        MEMBER = 'member', 'Member'
    role = models.CharField(max_length=10, choices=RoleChoices)

    joined_at = models.DateTimeField(auto_now_add=True)
    last_read_message = models.ForeignKey('Message', on_delete=models.SET_NULL, null=True, blank=True, related_name='+')

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['conversation', 'user'],
                name='unique_conversation_member'
            )
        ]

    def __str__(self):
        return f'{self.user} -> {self.conversation}'


class Message(models.Model):
    conversation = models.ForeignKey(Conversation, on_delete=models.CASCADE, related_name='messages')
    sender = models.ForeignKey(User, on_delete=models.CASCADE, related_name='messages')
    content = models.TextField()

    class MessageType(models.TextChoices):
        TEXT = "text", "Text"
        IMAGE = "image", "Image"
        FILE = "file", "File"
        SYSTEM = "system", "System"

    message_type = models.CharField(max_length=20, choices=MessageType, default=MessageType.TEXT)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f'message number #{self.pk} | sender: {self.sender}'