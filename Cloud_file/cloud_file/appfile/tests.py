from django.test import TestCase
from django.urls import reverse

from .models import Server, File


class ServerModelTest(TestCase):
    def test_server_creation(self):
        server = Server.objects.create(name='Test Server', type='1')
        self.assertEqual(server.name, 'Test Server')
        self.assertEqual(server.type, '1')


class FileModelTest(TestCase):
    def test_file_creation(self):
        server = Server.objects.create(name='Test Server', type='1')
        file = File.objects.create(server=server, name='Test File', file='test.txt')
        self.assertEqual(file.server, server)
        self.assertEqual(file.name, 'Test File')
        self.assertEqual(file.file, 'test.txt')


class CloudDetailPageTest(TestCase):
    def test_cloud_detail_page(self):
        server = Server.objects.create(name='Test Server', type='1')
        url = reverse('cloud_detail', args=[server.id])
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'html/cloud_detail.html')
        self.assertContains(response, 'Test Server')
