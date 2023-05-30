from django.db import models


class TelegramUser(models.Model):
    chat_id = models.PositiveBigIntegerField(unique=True)
    username = models.CharField(max_length=100)

    def __str__(self):
        return f"{self.username} - {self.chat_id}"
