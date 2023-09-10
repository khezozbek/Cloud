from django import forms
from django.contrib.auth.models import User

from .models import Server, File, FileTransfer


class FileTransferForm(forms.ModelForm):
    server = forms.ModelChoiceField(queryset=Server.objects.all())

    class Meta:
        model = FileTransfer
        fields = ['receiver', 'server']


class FileCloud(forms.ModelForm):
    class Meta:
        model = File
        fields = ['file']


class CreateCloudForm(forms.ModelForm):
    class Meta:
        model = Server
        fields = ['name', 'type']
