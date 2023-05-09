import uuid

from django.db import models
from django.urls import reverse


class Device(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4)
    mac = models.GenericIPAddressField()
    site_id = models.CharField(max_length=50)
    ip = models.GenericIPAddressField(null=True)
    logged_at = models.DateTimeField()
    uptime = models.BigIntegerField()

    def __str__(self):
        """String for representing the Model object."""
        return self.site_id

    def get_absolute_url(self):
        """Returns the URL to access a detail record for this network."""
        return reverse('network-detail', args=[str(self.id)])

