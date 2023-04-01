from django.db import models


class TelegramUser(models.Model):
    username = models.CharField(max_length=100)
    chat_id = models.PositiveIntegerField(unique=True)

    def __str__(self):
        return f"{self.username} - {self.chat_id}"
