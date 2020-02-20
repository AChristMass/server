from django.test import RequestFactory, TestCase



class IfcViewTestCase(TestCase):
    
    @classmethod
    def setUpData(cls):
        cls.factory = RequestFactory()
        
    def test_get(self):
        self.factory.request()
        
