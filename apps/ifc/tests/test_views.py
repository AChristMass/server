import json
import os
import shutil

from django.test import Client, TestCase, override_settings
from django.urls import reverse
from django.conf import settings

from ifc.models import IfcModel


IFC_FILE_TEST_PATH = os.path.join(settings.APPS_DIR, "ifc", "tests", "resources", "test.ifc")
IFC_TMP_DIR = os.path.join(settings.APPS_DIR, "ifc", "tests", "tmp")
IFC_TMP_FILE = os.path.join(IFC_TMP_DIR, "test_path")



@override_settings(IFC_FILES_DIR=IFC_TMP_DIR)
class IfcViewTestCase(TestCase):
    
    @classmethod
    def setUpTestData(cls):
        cls.client = Client()
        cls.ifc = IfcModel.objects.create(name="test1", file_path="test_path",
                                          data={"testk": "testv"})
        cls.ifc = IfcModel.objects.create(name="test2", file_path="test_path",
                                          data={"testk": "testv"})
        os.mkdir(IFC_TMP_DIR)
        with open(IFC_TMP_FILE, "w") as f:
            print("teeeest", file=f)
    
    
    @classmethod
    def tearDownClass(cls):
        shutil.rmtree(IFC_TMP_DIR)
    
    
    def test_get(self):
        response = self.client.get(reverse("ifc:main_pk", args=[1]))
        data = '"name": "test1", "data": {"testk": "testv"},'
        self.assertContains(response, data, status_code=200)
    
    
    def test_get_not_exist(self):
        response = self.client.get(reverse("ifc:main_pk", args=[0]))
        self.assertContains(response, "Ifc does not exist", status_code=404)
    
    
    def test_post(self):
        with open(IFC_FILE_TEST_PATH) as ifc:
            data = {"name": "test_post", "ifc_file": ifc}
            response = self.client.post(reverse("ifc:main"), data)
            self.assertContains(response, "id", status_code=200)
        data = json.loads(response.content.decode())
        with open(os.path.join(settings.IFC_FILES_DIR, data["path"])) as f1, open(
            IFC_FILE_TEST_PATH) as f2:
            self.assertEqual(f1.read(), f2.read())
        
        with open(IFC_FILE_TEST_PATH) as ifc:
            data = {"name": "test_post", "ifc_file": ifc}
            response = self.client.post(reverse("ifc:main"), data)
            self.assertContains(response, "Name taken", status_code=409)
    
    
    def test_post_error_form(self):
        data = {"name": "test_post"}
        response = self.client.post(reverse("ifc:main"), data)
        self.assertContains(response, "This field is required.", status_code=400)
    
    
    def test_get_list(self):
        response = self.client.get(reverse("ifc:list"))
        self.assertContains(response, "test1", status_code=200)
        self.assertContains(response, "test2", status_code=200)
    
    
    def test_put(self):
        response = self.client.put(reverse("ifc:main_pk", args=[2]), data={"name": "untest"})
        # TODO
    
    
    def test_put_error_form(self):
        data = {"name": "a"}
        response = self.client.put(reverse("ifc:main_pk", args=[2]), data)
        # TODO
