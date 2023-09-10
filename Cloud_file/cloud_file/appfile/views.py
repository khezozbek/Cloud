from django.shortcuts import get_object_or_404
from django.http import FileResponse, HttpResponseRedirect
from django.urls import reverse
from django.utils import timezone
from django.views.decorators.http import require_POST
from .models import Server, File, FileTransfer
from .forms import CreateCloudForm, FileCloud, FileTransferForm
from django.contrib.auth.forms import UserCreationForm
from django.shortcuts import render, redirect
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from django.core.exceptions import ValidationError
from django.contrib.auth import logout
from django.shortcuts import redirect
import os
import mimetypes
from django.http import HttpResponse
from .models import File
from django.shortcuts import get_object_or_404, render, redirect
from django.contrib import messages
from django.utils import timezone
from django.shortcuts import get_object_or_404, render, redirect
from django.contrib import messages
from django.utils import timezone
from datetime import timedelta

def download_file(request, file_id):
    file = get_object_or_404(File, id=file_id)
    file_path = file.file.path

    if os.path.exists(file_path):
        with open(file_path, 'rb') as f:
            response = HttpResponse(f.read(), content_type=mimetypes.guess_type(file_path)[0])
            response['Content-Disposition'] = 'attachment; filename="{}"'.format(os.path.basename(file_path))
            return response
    else:
        return HttpResponse("File not found.")


def logout_view(request):
    logout(request)
    return redirect('login')


def user_login(request):
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            return redirect('login')
    else:
        form = AuthenticationForm()
    return render(request, 'html/login.html', {'form': form})


def register(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('index')
    else:
        form = UserCreationForm()
    return render(request, 'html/signup.html', {'form': form})


def delete_server(request, server_id):
    server = Server.objects.get(pk=server_id)
    server.delete()
    return redirect('index')


@login_required
def index(request):
    servers = Server.objects.filter(user=request.user)
    context = {'servers': servers}
    return render(request, 'html/index.html', context)


@login_required
def create_cloud(request):
    if request.method == 'POST':
        form = CreateCloudForm(request.POST, request.FILES)
        if form.is_valid():
            server = form.save(commit=False)
            server.user = request.user 
            server.save()
            return redirect('cloud_detail', server_id=server.pk)
    else:
        form = CreateCloudForm()

    return render(request, 'html/create_cloud.html', {'form': form})


@login_required
def cloud_detail(request, server_id):
    server = get_object_or_404(Server, pk=server_id)
    files = server.files.all()
    error_message = ''

    if request.method == 'POST':
        form = FileCloud(request.POST, request.FILES)
        if form.is_valid():
            try:
                uploaded_file = request.FILES['file']
                try:
                    file = File.objects.create(
                        server=server,
                        file=uploaded_file,
                        name=uploaded_file.name,
                        size=uploaded_file.size,
                        uploaded_at=timezone.now()
                    )
                    return HttpResponseRedirect(reverse('cloud_detail', args=[server_id]))
                except ValidationError as e:
                    error_message = str(e)
            except KeyError:
                error_message = 'No file selected.'
    else:
        form = FileCloud()

    return render(request, 'html/cloud_detail.html', {'form': form, 'files': files, 'error_message': error_message})


@login_required
def delete_file(request, file_id, server_id):
    file = get_object_or_404(File, id=file_id)

    if request.method == 'POST':
        file.delete()
        return redirect('cloud_detail', server_id=server_id)

    return render(request, 'html/delete_file.html', {'file': file})


@login_required
@require_POST
def upload_file(request, server_id):
    server = Server.objects.get(pk=server_id)
    file = request.FILES.get('file')
    if file:
        File.objects.create(server=server, file=file, size=file.size)
    return redirect('cloud_detail', server_id=server_id)


@login_required
def download_file(request, file_id):
    file = File.objects.get(pk=file_id)
    response = FileResponse(file.file)
    response['Content-Disposition'] = f'attachment; filename="{file.name}"'
    return response


@login_required
def file_transfer(request, file_id):
    file = get_object_or_404(File, id=file_id)
    form = FileTransferForm()

    if request.method == 'POST':
        form = FileTransferForm(request.POST)
        if form.is_valid():
            receiver = form.cleaned_data['receiver']
            server = form.cleaned_data['server']

            if request.user == receiver:
                transfer_time = (timezone.now() - file.uploaded_at).total_seconds() / 60
                if transfer_time <= 25:
                    file_transfer = FileTransfer(sender=request.user, receiver=receiver, file=file, server=server)
                    file_transfer.save()

                    file.server = server
                    file.save()

                    notification_message = f"You have received a file transfer request from {request.user.username}. Please check your account to accept or decline the transfer."

                    messages.success(request, 'File transfer request sent successfully!')

                    messages.info(request, notification_message)

                    return redirect('cloud_detail', server_id=file.server.id)
                else:
                    messages.error(request, 'File transfer time has expired.')
            else:
                messages.error(request, 'You are not authorized to receive this file.')

    return render(request, 'html/file_transfer.html', {'file': file, 'form': form})
