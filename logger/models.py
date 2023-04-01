import uuid

from django.db import models
from django.urls import reverse


class Network(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4)
    mac = models.GenericIPAddressField()
    network_name = models.CharField(max_length=50)
    ip = models.GenericIPAddressField(null=True)
    logged_at = models.DateTimeField(auto_now_add=True)
    # last_seen = models.BigIntegerField(default=0)
    # uptime = models.BigIntegerField()
    raw_data = models.JSONField()

    def __str__(self):
        """String for representing the Model object."""
        return self.network_name

    def get_absolute_url(self):
        """Returns the URL to access a detail record for this network."""
        return reverse('network-detail', args=[str(self.id)])

