import os

from django.test import Client, TestCase
from django.urls import reverse
from django.conf import settings

from ifc.models import IfcModel



class IfcViewTestCase(TestCase):
    
    @classmethod
    def setUpTestData(cls):
        cls.client = Client()
        cls.ifc = IfcModel.objects.create(name="test1", file_path="test_path",
                                          graph={"testk": "testv"})
        cls.ifc = IfcModel.objects.create(name="test2", file_path="test_path",
                                          graph={"testk": "testv"})
    
    
    @classmethod
    def tearDownClass(cls):
        pass
    
    
    def test_get(self):
        response = self.client.get(reverse("ifc:single", args=[1]))
        data = '{"id": 1, "name": "test1", "graph": {"testk": "testv"}, "filePath": "test_path"}'
        self.assertContains(response, data, status_code=200)
    
    
    def test_get_not_exist(self):
        response = self.client.get(reverse("ifc:single", args=[0]))
        self.assertContains(response, "Ifc does not exist", status_code=404)
    
    
    def test_post(self):
        with open(os.path.join(settings.APPS_DIR, "ifc/tests/resources/test.ifc")) as ifc:
            data = {"name": "test_post", "ifc_file": ifc}
            response = self.client.post(reverse("ifc:create_ifc"), data)
            self.assertContains(response, "ok", status_code=200)
    
    
    def test_get_list(self):
        response = self.client.get(reverse("ifc:list"))
        self.assertContains(response, "test1", status_code=200)
        self.assertContains(response, "test2", status_code=200)
