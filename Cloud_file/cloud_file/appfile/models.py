from django.db import models
from django.core.exceptions import ValidationError
from django.utils import timezone
from django.contrib.auth.models import User
from django.utils import timezone


class Server(models.Model):
    education = "Education"
    personal = "Personal"
    code = "Code"
    chs = (
        (education, "Education"),
        (personal, "Personal"),
        (code, "Code"),
    )
    name = models.CharField(max_length=100)
    type = models.CharField(max_length=50, choices=chs)
    created_at = models.DateTimeField(default=timezone.now)
    max_storage = 5 * 1024 * 1024 * 1024  # 5 GB
    user = models.ForeignKey(User, on_delete=models.CASCADE)

    def get_used_space(self):
        used_space = sum(file.size for file in self.files.all())
        return used_space

    def get_free_space(self):
        used_space = self.get_used_space()
        free_space = max(self.max_storage - used_space, 0)
        return free_space

    def get_percentage_free_space(self):
        used_space = self.get_used_space()
        percentage_free_space = (self.get_remaining_space() / (self.size_of_server.size + used_space)) * 100
        return percentage_free_space

    def get_remaining_space(self):
        remaining_space = max(self.size_of_server.size - self.get_used_space(), 0)
        return remaining_space

    @property
    def remaining_space_display(self):
        remaining_space = self.get_remaining_space()
        if remaining_space >= 1024 * 1024 * 1024:
            return f"{remaining_space / (1024 * 1024 * 1024):.2f} GB"
        elif remaining_space >= 1024 * 1024:
            return f"{remaining_space / (1024 * 1024):.2f} MB"
        elif remaining_space >= 1024:
            return f"{remaining_space / 1024:.2f} KB"
        else:
            return f"{remaining_space} bytes"


class File(models.Model):
    server = models.ForeignKey(Server, on_delete=models.CASCADE, related_name='files')
    file = models.FileField(upload_to='files/')
    name = models.CharField(max_length=100)
    size = models.BigIntegerField(blank=True, null=True)
    uploaded_at = models.DateTimeField(default=timezone.now)

    def clean(self):
        file_size = self.file.size
        server = getattr(self, 'server', None)
        if server is not None:
            remaining_space = server.get_free_space()
            if file_size > remaining_space:
                raise ValidationError("Not enough space on the server.")

    def save(self, *args, **kwargs):
        self.clean()
        self.server.full_clean()

        self.size = self.file.size
        super().save(*args, **kwargs)


class FileTransfer(models.Model):
    sender = models.ForeignKey(User, on_delete=models.CASCADE, related_name='file_transfers_sent')
    receiver = models.ForeignKey(User, on_delete=models.CASCADE, related_name='file_transfers_received')
    file = models.ForeignKey(File, on_delete=models.CASCADE)
    server = models.ForeignKey(Server, on_delete=models.CASCADE)
    transferred_at = models.DateTimeField(blank=True, null=True)

    def save(self, *args, **kwargs):
        if self.pk is None:
            self.transferred_at = timezone.now()

        super().save(*args, **kwargs)
